"""
RedisClient class for setting and getting values in Redis.
This class provides methods to set and get encoders in Redis.
It uses the redis-py library to interact with the Redis server.
It also provides a ping method to check if the Redis server is alive.
"""

from typing import Union

import pickle
import redis


class RedisClient:
    """
    A simple Redis client wrapper for setting and getting values.
    """

    def __init__(self, host: str, port: int):
        self.client = redis.Redis(host=host, port=port, db=0)

    def ping(self):
        """
        Ping the Redis server to check if it is alive.
        """
        try:
            self.client.ping()
            return True
        except redis.ConnectionError as e:
            print(f"Redis ping failed: {e}")
            return False

    def set_encoder(self, key: str, ext: str) -> any:
        """
        Set the encoder in Redis.
        Gets the encoder from the specified file and stores it in Redis.
        Args:
            key (str): The key to set the encoder.
            ext (str): The file extension of the encoder file.
        """
        pre_fix = "/ml/data/"

        with open(f"{pre_fix}{key}{ext}", "rb") as f:
            encoder = pickle.load(f)

        self.client.set(key, pickle.dumps(encoder), ex=60 * 60 * 24)  # 1 day expiration
        return encoder

    def get_encoder(self, key: str) -> Union[None, any]:
        """
        Get the encoder from Redis.
        Args:
            key (str): The key to retrieve the encoder from.
        Returns:
            encoder (any): The encoder object if found, otherwise None.
        """
        value = self.client.get(key)
        return pickle.loads(value) if value else None
