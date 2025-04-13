"""
"""

import time
import joblib
import redis
import pickle
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from redisai import Client


class PredictionRequest(BaseModel):
    """
    Request model for prediction.
    """
    brand: str
    year: int
    engine_size: float
    fuel_type: str
    transmission: str
    mileage: int
    condition: str
    model: str


class API:
    
    def __init__(self, ordinal_encoder_path: str):
        self.app = FastAPI()

        self.r = redis.Redis(host='redis', port=6379, db=0)
        self.rai = Client(host='redisai', port=6379)

        self.ordinal_encoder_path = ordinal_encoder_path

        self._load_encoder()
        self._setup_routes()

    def _load_encoder(self):
        """
        Load the OrdinalEncoder from the specified path.
        """
        print(f"Loading OrdinalEncoder from {self.ordinal_encoder_path}...")

        with open(self.ordinal_encoder_path, 'rb') as f:
            self.encoder = pickle.load(f)

        print("Encoder loaded successfully.")

    def _get_input_data(self, data: PredictionRequest) -> np.ndarray:
        """
        """
        # Convert the input data to a DataFrame
        df = pd.DataFrame([data.model_dump()])

        # Rename the columns to match the model's input
        df.rename(columns={
            "engine_size": "engine size",
            "fuel_type": "fuel type"
        }, inplace=True)

        # Define the categorical and numerical columns
        categorical_cols = ['brand', 'fuel type', 'transmission', 'condition', 'model']
        numerical_cols = ['year', 'mileage', 'engine size']

        # Ensure the categorical columns are of type 'category'
        encoded_data = self.encoder.transform(df[categorical_cols])

        # Convert the encoded data to a DataFrame
        df[categorical_cols] = encoded_data

        # Drop the original categorical columns
        df.drop(columns=categorical_cols, inplace=True)

        # Convert the DataFrame to a NumPy array
        input_data = np.hstack([df[numerical_cols].values, encoded_data])

        return input_data

    def _setup_routes(self):
        """
        Setup the FastAPI routes.
        """
        @self.app.post("/predict/pkl")
        async def predict_with_pkl(data: PredictionRequest) -> dict: 
            """
            """
            start = time.time()

            model_with_pkl = "model_with_pkl"

            model_data = self.r.get(model_with_pkl)
            if model_data:
                model = pickle.loads(model_data)
            else:
                with open(f"/data/{model_with_pkl}.pkl", 'rb') as f:
                    model = pickle.load(f)
                self.r.set(model_with_pkl, pickle.dumps(model), ex=60*60*24) # 1 day expiration

            input_data = self._get_input_data(data)
            output = model.predict(input_data)

            end = time.time()

            time_taken = end - start

            print(f"time taken: {time_taken}")

            return {"predicted_price": output.tolist()}

        @self.app.post("/predict/joblib")
        async def predict_with_joblib(data: PredictionRequest) -> dict:
            """
            """
            start = time.time()

            model_with_joblib = "model_with_joblib"

            model_data = self.r.get(model_with_joblib)
            if model_data:
                model = pickle.loads(model_data)
            else:
                with open(f"/data/{model_with_joblib}.pkl", 'rb') as f:
                    model = joblib.load(f)
                self.r.set(model_with_joblib, pickle.dumps(model), ex=60*60*24)
            
            input_data = self._get_input_data(data)
            output = model.predict(input_data)

            end = time.time()

            time_taken = end - start

            print(f"time taken: {time_taken}")

            return {"predicted_price": output.tolist()}

        @self.app.post("/predict/onnx")
        async def predict_with_onnx(data: PredictionRequest) -> dict:
            """
            """
            print("Predicting with ONNX model...")

            start = time.time()

            model_with_onnx = "model_with_onnx"

            if not self.rai.exists(model_with_onnx):
                with open(f"/data/{model_with_onnx}.onnx", 'rb') as f:
                    model_bytes = f.read()
                self.rai.modelset(
                    key=model_with_onnx,
                    backend="ONNX",
                    device="cpu",
                    data=model_bytes,
                    inputs=["float_input"],
                    outputs=["variable"]
                )
            

            input_data = self._get_input_data(data)
            input_data = input_data.astype(np.float32)

            self.rai.tensorset("input_tensor", input_data)
            self.rai.modelexecute(model_with_onnx, inputs=["input_tensor"], outputs=["output_tensor"])
            output = self.rai.tensorget("output_tensor")

            end = time.time()

            time_taken = end - start

            print(f"time taken: {time_taken}")

            return {"predicted_price": float(output[0][0])}
