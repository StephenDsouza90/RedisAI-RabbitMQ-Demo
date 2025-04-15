"""
Main module for the FastAPI application to handle model inference requests.
This module sets up the FastAPI application, defines the API routes,
and handles the model inference logic.
"""

import warnings
import pickle
import numpy as np
import pandas as pd
from fastapi import FastAPI
from sklearn.preprocessing import OrdinalEncoder
from ratelimit import limits, sleep_and_retry

from ml.inference.const import ModelInferenceRequest
from ml.inference.decorator import time_checker
from ml.inference.redis_ai_client import RedisAIClient
from ml.inference.redis_client import RedisClient


warnings.filterwarnings(
    "ignore",
    message="X does not have valid feature names, but RandomForestRegressor was fitted with feature names",
)


class API:
    """
    API class to handle the FastAPI application and prediction requests.
    """

    def __init__(
        self,
        redis: RedisClient,
        redis_ai: RedisAIClient,
        cat_cols: list,
        num_cols: list,
    ):
        self.app = FastAPI()
        self.r = redis
        self.rai = redis_ai
        self.cat_cols = cat_cols
        self.num_cols = num_cols
        self._setup_routes()
        self.rai.set_model(key="model_A", path="model_A", ext=".onnx")
        self.rai.set_model(key="model_B", path="model_B", ext=".onnx")
        self.rai.set_model(key="model_C", path="model_C", ext=".onnx")

    def _load_encoder(self, model_group: str) -> OrdinalEncoder:
        """
        Load the OrdinalEncoder from the specified path and model group.
        Args:
            model_group (str): The model group to load the encoder for.
        Returns:
            encoder (OrdinalEncoder): The loaded OrdinalEncoder.
        """
        key = f"ordinal_encoder_{model_group}"

        encoder = self.r.get_encoder(key)
        if not encoder:
            encoder = self.r.set_encoder(key=key, ext=".pkl")

        return encoder

    def _get_input_data(
        self,
        data: ModelInferenceRequest,
        model_group: str,
        cat_cols: list,
        num_cols: list,
    ) -> np.ndarray:
        """
        Convert the input data to a NumPy array suitable for prediction.
        Args:
            data (ModelInferenceRequest): The input data for prediction.
            model_group (str): The model group to use for encoding.
            cat_cols (list): List of categorical columns.
            num_cols (list): List of numerical columns.
        Returns:
            input_data (np.ndarray): The input data as a NumPy array.
        """
        # Convert the input data to a DataFrame
        df = pd.DataFrame([data.model_dump()])

        # Convert the categorical columns to the appropriate type
        encoder = self._load_encoder(model_group)
        encoded_data = encoder.transform(df[cat_cols])

        # Convert the encoded data to a DataFrame
        df[cat_cols] = encoded_data

        # Drop the original categorical columns
        df.drop(columns=cat_cols, inplace=True)

        # Convert the DataFrame to a NumPy array
        input_data = np.hstack([df[num_cols].values, encoded_data])

        return input_data

    def _setup_routes(self):
        """
        Setup the FastAPI routes.
        """

        @sleep_and_retry
        @limits(calls=20, period=1)  # 20 requests per second
        @self.app.post("/predict/onnx")
        @time_checker
        async def predict_onnx(data: ModelInferenceRequest) -> dict:
            """
            Predict the price using the ONNX model in RedisAI.
            Args:
                data (ModelInferenceRequest): The input data for prediction.
            Returns:
                dict: The predicted price.
            """
            model_group = data.model_group

            # Key for the model in Redis
            key = f"model_{model_group}"

            input_data = self._get_input_data(
                data, model_group, self.cat_cols, self.num_cols
            )
            input_data = input_data.astype(np.float32)

            # Set the input tensor in RedisAI
            output = self.rai.tensor_set(key=key, input_data=input_data)

            return {"predicted_price": float(output[0][0])}

        @self.app.post("/predict/pickle")
        @time_checker
        async def predict_pickle(data: ModelInferenceRequest) -> dict:
            """
            Predict the price using the Pickle model.
            Args:
                data (ModelInferenceRequest): The input data for prediction.
            Returns:
                dict: The predicted price.
            """
            model_group = data.model_group

            # Load the model from the file
            with open(f"/ml/data/model_{model_group}.pkl", "rb") as f:
                model = pickle.load(f)

            input_data = self._get_input_data(
                data, model_group, self.cat_cols, self.num_cols
            )
            input_data = input_data.astype(np.float32)

            prediction = model.predict(input_data)

            return {"predicted_price": float(prediction[0])}
