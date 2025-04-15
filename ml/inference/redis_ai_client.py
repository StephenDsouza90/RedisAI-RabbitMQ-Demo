"""
This module provides a client for interacting with RedisAI, a Redis module for executing deep learning models.
It includes methods for setting models, executing them, and handling tensors.
"""

from typing import Union

import redis
import numpy as np
from redisai import Client


class RedisAIClient:
    """
    A client for interacting with RedisAI.
    """

    def __init__(self, host: str, port: int, max_connections=10):
        """
        Initialize the RedisAIClient.
        Args:
            host (str): The RedisAI client host.
            port (int): The RedisAI client port.
        """
        self.pool = redis.ConnectionPool(
            host=host, port=port, max_connections=max_connections
        )
        self.client = Client(connection_pool=self.pool)

    def ping(self):
        """
        Ping the RedisAI server to check if it is alive.
        """
        try:
            self.client.ping()
            return True
        except Exception as e:
            print(f"RedisAI ping failed: {e}")
            return False

    def set_model(self, key: str, path: str, ext: str):
        """
        Set the model in RedisAI.
        Args:
            key (str): The key to store the model under.
            path (str): The path to the model file.
            ext (str): The file extension of the model file.
        """
        pre_fix = "/ml/data/"

        if not self.client.exists(key):
            with open(f"{pre_fix}{path}{ext}", "rb") as f:
                model_bytes = f.read()

            self.client.modelset(
                key=key,
                backend="ONNX",
                device="cpu",
                data=model_bytes,
                inputs=["float_input"],
                outputs=["variable"],
            )

    def tensor_set(self, key: str, input_data: np.ndarray) -> Union[dict, np.ndarray]:
        """
        Set the tensor in RedisAI.
        Args:
            key (str): The key to store the tensor under.
            input_data (np.ndarray): The input data to set as a tensor.
        """
        self.client.tensorset("input_tensor", input_data)
        self.client.modelexecute(
            key, inputs=["input_tensor"], outputs=["output_tensor"]
        )
        return self.client.tensorget("output_tensor")
