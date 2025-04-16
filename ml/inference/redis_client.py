"""
RedisClient class for interacting with a Redis server.
This class provides methods to store and retrieve serialized objects (e.g., encoders) in Redis.
It also includes a method to check the connectivity to the Redis server.
"""

from typing import Any, Optional
import pickle
import redis


class RedisClient:
    """
    A wrapper around the Redis client for simplified interaction.
    """

    def __init__(self, host: str, port: int):
        """
        Initialize the Redis client.

        Args:
            host (str): The Redis server hostname or IP address.
            port (int): The Redis server port.
        """
        self.client = redis.Redis(host=host, port=port, db=0)

    def is_server_alive(self) -> bool:
        """
        Check if the Redis server is reachable.

        Returns:
            bool: True if the server responds to a ping, False otherwise.
        """
        try:
            self.client.ping()
            return True
        except redis.ConnectionError as error:
            print(f"Failed to ping Redis server: {error}")
            return False

    def store_object(
        self, key: str, file_extension: str, expiration_seconds: int = 86400
    ) -> Any:
        """
        Store a serialized object in Redis.

        Args:
            key (str): The key under which the object will be stored.
            file_extension (str): The file extension of the object file (e.g., '.pkl').
            expiration_seconds (int): The expiration time in seconds (default is 1 day).

        Returns:
            Any: The deserialized object that was stored.
        """
        file_path = f"/ml/data/encoder/{key}{file_extension}"

        with open(file_path, "rb") as file:
            obj = pickle.load(file)

        self.client.set(key, pickle.dumps(obj), ex=expiration_seconds)
        return obj

    def retrieve_object(self, key: str) -> Optional[Any]:
        """
        Retrieve a serialized object from Redis.

        Args:
            key (str): The key of the object to retrieve.

        Returns:
            Optional[Any]: The deserialized object if found, otherwise None.
        """
        serialized_data = self.client.get(key)
        return pickle.loads(serialized_data) if serialized_data else None
