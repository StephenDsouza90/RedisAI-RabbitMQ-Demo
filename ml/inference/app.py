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
from ml.inference.decorator import measure_execution_time
from ml.inference.redis_ai_client import RedisAIClient
from ml.inference.redis_client import RedisClient

# Suppress specific warnings
warnings.filterwarnings(
    "ignore",
    message="X does not have valid feature names, but RandomForestRegressor was fitted with feature names",
)


class InferenceAPI:
    """
    InferenceAPI class to handle the FastAPI application and prediction requests.
    """

    def __init__(
        self,
        redis_client: RedisClient,
        redis_ai_client: RedisAIClient,
        categorical_columns: list,
        numerical_columns: list,
    ):
        """
        Initialize the InferenceAPI class.

        Args:
            redis_client (RedisClient): Redis client for managing encoders.
            redis_ai_client (RedisAIClient): RedisAI client for model inference.
            categorical_columns (list): List of categorical column names.
            numerical_columns (list): List of numerical column names.
        """
        self.app = FastAPI()
        self.redis_client = redis_client
        self.redis_ai_client = redis_ai_client
        self.categorical_columns = categorical_columns
        self.numerical_columns = numerical_columns

        self._initialize_models()
        self._setup_routes()

    def _initialize_models(self):
        """
        Load and set models in RedisAI.
        """
        model_keys = ["model_A", "model_B", "model_C"]
        for key in model_keys:
            self.redis_ai_client.set_model(
                model_key=key, model_path=key, file_extension=".onnx"
            )

    def _load_encoder(self, model_group: str) -> OrdinalEncoder:
        """
        Load the OrdinalEncoder for the specified model group.

        Args:
            model_group (str): The model group to load the encoder for.

        Returns:
            OrdinalEncoder: The loaded encoder.
        """
        encoder_key = f"ordinal_encoder_{model_group}"
        encoder = self.redis_client.retrieve_object(encoder_key)

        if not encoder:
            encoder = self.redis_client.store_object(
                key=encoder_key, file_extension=".pkl"
            )

        return encoder

    def _prepare_input_data(
        self,
        request_data: ModelInferenceRequest,
        model_group: str,
    ) -> np.ndarray:
        """
        Prepare input data for model inference.

        Args:
            request_data (ModelInferenceRequest): The input data for prediction.
            model_group (str): The model group to use for encoding.

        Returns:
            np.ndarray: The prepared input data as a NumPy array.
        """
        # Convert input data to a DataFrame
        input_df = pd.DataFrame([request_data.model_dump()])

        # Encode categorical columns
        encoder = self._load_encoder(model_group)
        encoded_categorical_data = encoder.transform(input_df[self.categorical_columns])

        # Replace categorical columns with encoded data
        input_df[self.categorical_columns] = encoded_categorical_data

        # Combine numerical and encoded categorical data
        input_data = np.hstack(
            [input_df[self.numerical_columns].values, encoded_categorical_data]
        )

        return input_data.astype(np.float32)

    def _setup_routes(self):
        """
        Define and set up FastAPI routes.
        """

        @sleep_and_retry
        @limits(calls=20, period=1)  # Limit to 20 requests per second
        @self.app.post("/predict/onnx")
        @measure_execution_time
        async def predict_with_onnx(request_data: ModelInferenceRequest) -> dict:
            """
            Predict using an ONNX model stored in RedisAI.

            Args:
                request_data (ModelInferenceRequest): The input data for prediction.

            Returns:
                dict: The predicted price.
            """
            model_group = request_data.model_group
            model_key = f"model_{model_group}"

            input_data = self._prepare_input_data(request_data, model_group)
            input_tensor_key = "float_input"
            output_tensor_key = "variable"
            self.redis_ai_client.set_tensor(input_tensor_key, input_data)
            self.redis_ai_client.execute_model(
                model_key, input_tensor_key, output_tensor_key
            )
            prediction_output = self.redis_ai_client.get_tensor(output_tensor_key)

            return {"predicted_price": float(prediction_output[0][0])}

        @self.app.post("/predict/pickle")
        @measure_execution_time
        async def predict_with_pickle(request_data: ModelInferenceRequest) -> dict:
            """
            Predict using a Pickle model.

            Args:
                request_data (ModelInferenceRequest): The input data for prediction.

            Returns:
                dict: The predicted price.
            """
            model_group = request_data.model_group
            model_path = f"/ml/data/model_{model_group}.pkl"

            # Load the Pickle model
            with open(model_path, "rb") as model_file:
                model = pickle.load(model_file)

            input_data = self._prepare_input_data(request_data, model_group)
            prediction = model.predict(input_data)

            return {"predicted_price": float(prediction[0])}
