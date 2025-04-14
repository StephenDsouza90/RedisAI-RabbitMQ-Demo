"""
"""

import time
import redis
import pickle
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from redisai import Client
from sklearn.preprocessing import OrdinalEncoder


class PredictionRequest(BaseModel):
    """
    Request model for prediction.
    """
    modelGroup: str
    model: str
    kilometers: int
    fueltype: str
    geartype: str
    vehicletype: str
    ageinmonths: int
    color: str
    line: str
    doors: str
    seats: str
    climate: str


class API:
    
    def __init__(self, cat_cols: list, num_cols: list):
        self.app = FastAPI()

        self.r = redis.Redis(host='redis', port=6379, db=0)
        self.rai = Client(host='redisai', port=6379)

        self.cat_cols = cat_cols
        self.num_cols = num_cols

        self._setup_routes()

    def _load_encoder(self, model_group: str) -> OrdinalEncoder:
        """
        Load the OrdinalEncoder from the specified path and model group.

        Args:
            model_group (str): The model group to load the encoder for.
        
        Returns:
            encoder (OrdinalEncoder): The loaded OrdinalEncoder.
        """
        key = f"ordinal_encoder_{model_group}"

        encoder = self.r.get(key)
        if encoder:
            encoder = pickle.loads(encoder)

        else:
            with open(f"/data/{key}.pkl", 'rb') as f:
                encoder = pickle.load(f)
            
            # Store the encoder in Redis
            self.r.set(key, pickle.dumps(encoder), ex=60*60*24) # 1 day expiration

        return encoder

    def _get_input_data(self, data: PredictionRequest, model_group: str, cat_cols: list, num_cols: list) -> np.ndarray:
        """
        Convert the input data to a NumPy array suitable for prediction.

        Args:
            data (PredictionRequest): The input data for prediction.
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
        @self.app.post("/predict/onnx")
        async def predict_onnx(data: PredictionRequest) -> dict:
            """
            """
            start = time.time()

            model_group = data.modelGroup

            # Key for the model in Redis
            key = f"model_{model_group}"
            if not self.rai.exists(key):
                # Load the model from the file
                with open(f"/data/{key}.onnx", 'rb') as f:
                    model_bytes = f.read()

                # Store the model in RedisAI
                self.rai.modelset(
                    key=key,
                    backend="ONNX",
                    device="cpu",
                    data=model_bytes,
                    inputs=["float_input"],
                    outputs=["variable"]
                )

            input_data = self._get_input_data(data, model_group, self.cat_cols, self.num_cols)
            input_data = input_data.astype(np.float32)

            self.rai.tensorset("input_tensor", input_data)
            self.rai.modelexecute(key, inputs=["input_tensor"], outputs=["output_tensor"])
            output = self.rai.tensorget("output_tensor")

            end = time.time()

            time_taken = end - start

            print(f"time taken: {time_taken}")

            return {"predicted_price": float(output[0][0])}

        @self.app.post("/predict/pickle")
        async def predict_pickle(data: PredictionRequest) -> dict:
            """
            """
            start = time.time()

            model_group = data.modelGroup

            # Load the model from the file
            with open(f"/data/model_{model_group}.pkl", 'rb') as f:
                model = pickle.load(f)

            input_data = self._get_input_data(data, model_group, self.cat_cols, self.num_cols)
            input_data = input_data.astype(np.float32)

            prediction = model.predict(input_data)

            end = time.time()

            time_taken = end - start

            print(f"time taken: {time_taken}")

            return {"predicted_price": float(prediction[0])}
