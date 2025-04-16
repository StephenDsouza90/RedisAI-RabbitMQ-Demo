"""
This module provides a client for interacting with RedisAI, a Redis module for executing deep learning models.
It includes methods for setting models, executing them, and handling tensors.
"""

import redis
import numpy as np
from redisai import Client


class RedisAIClient:
    """
    A client for interacting with RedisAI to manage models and tensors.
    """

    def __init__(self, host: str, port: int, max_connections: int = 10):
        """
        Initialize the RedisAIClient with connection details.

        Args:
            host (str): The RedisAI server host.
            port (int): The RedisAI server port.
            max_connections (int): Maximum number of connections in the pool. Default is 10.
        """
        self.connection_pool = redis.ConnectionPool(
            host=host, port=port, max_connections=max_connections
        )
        self.client = Client(connection_pool=self.connection_pool)

    def is_server_alive(self) -> bool:
        """
        Check if the RedisAI server is reachable.

        Returns:
            bool: True if the server is reachable, False otherwise.
        """
        try:
            self.client.ping()
            return True
        except Exception as error:
            print(f"RedisAI ping failed: {error}")
            return False

    def set_model(self, model_key: str, model_path: str, file_extension: str) -> None:
        """
        Upload a model to RedisAI.

        Args:
            model_key (str): The key under which the model will be stored.
            model_path (str): The relative path to the model file.
            file_extension (str): The file extension of the model file (e.g., '.onnx').
        """
        model_directory = "/ml/data/models/"

        if not self.client.exists(model_key):
            full_model_path = f"{model_directory}{model_path}{file_extension}"
            with open(full_model_path, "rb") as model_file:
                model_data = model_file.read()

            self.client.modelset(
                key=model_key,
                backend="ONNX",
                device="cpu",
                data=model_data,
                inputs=["float_input"],
                outputs=["variable"],
            )

    def execute_model(
        self, model_key: str, input_tensor_key: str, output_tensor_key: str
    ) -> np.ndarray:
        """
        Execute a model stored in RedisAI with the given input tensor.

        Args:
            model_key (str): The key of the model to execute.
            input_tensor_key (str): The key of the input tensor.
            output_tensor_key (str): The key where the output tensor will be stored.

        Returns:
            np.ndarray: The output tensor retrieved from RedisAI.
        """
        self.client.modelexecute(
            model_key, inputs=[input_tensor_key], outputs=[output_tensor_key]
        )
        return self.client.tensorget(output_tensor_key)

    def set_tensor(self, tensor_key: str, tensor_data: np.ndarray) -> None:
        """
        Store a tensor in RedisAI.

        Args:
            tensor_key (str): The key under which the tensor will be stored.
            tensor_data (np.ndarray): The tensor data to store.
        """
        self.client.tensorset(tensor_key, tensor_data)

    def get_tensor(self, tensor_key: str) -> np.ndarray:
        """
        Retrieve a tensor from RedisAI.

        Args:
            tensor_key (str): The key of the tensor to retrieve.

        Returns:
            np.ndarray: The retrieved tensor data.
        """
        return self.client.tensorget(tensor_key)
