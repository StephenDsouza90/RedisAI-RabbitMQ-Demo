import os

from ml.inference.app import InferenceAPI
from ml.inference.const import (
    CategoricalColumns,
    NumericalColumns,
    Columns,
    ModelInferenceRequest,
)
from ml.inference.redis_ai_client import RedisAIClient
from ml.inference.redis_client import RedisClient


def validate_column_configuration():
    """
    Validates that the total number of columns matches the sum of categorical and numerical columns.
    Raises:
        ValueError: If the column configuration is invalid.
    """
    categorical_columns = CategoricalColumns().to_list()
    numerical_columns = NumericalColumns().to_list()

    if len(Columns.X) != len(categorical_columns) + len(numerical_columns):
        raise ValueError(
            "The total columns must equal the sum of categorical and numerical columns."
        )

    return categorical_columns, numerical_columns


def validate_model_request():
    """
    Validates the keys in the model inference request.
    Raises:
        ValueError: If the keys are invalid.
    """
    ModelInferenceRequest().validate_keys()


def initialize_redis_client(host, port):
    """
    Initializes and validates the connection to the Redis server.
    Args:
        host (str): Redis server host.
        port (str): Redis server port.
    Returns:
        RedisClient: An instance of RedisClient.
    Raises:
        ConnectionError: If the Redis server is not reachable.
    """
    redis_client = RedisClient(host, port)
    if redis_client.is_server_alive():
        print("Redis server is alive.")
    else:
        raise ConnectionError("Redis server is not reachable.")
    return redis_client


def initialize_redis_ai_client(host, port):
    """
    Initializes and validates the connection to the RedisAI server.
    Args:
        host (str): RedisAI server host.
        port (str): RedisAI server port.
    Returns:
        RedisAIClient: An instance of RedisAIClient.
    Raises:
        ConnectionError: If the RedisAI server is not reachable.
    """
    redis_ai_client = RedisAIClient(host, port)
    if redis_ai_client.is_server_alive():
        print("RedisAI server is alive.")
    else:
        raise ConnectionError("RedisAI server is not reachable.")
    return redis_ai_client


def main() -> InferenceAPI:
    """
    Main entry point for the application. Initializes dependencies and starts the API.
    """
    # Validate column configuration
    categorical_columns, numerical_columns = validate_column_configuration()

    # Validate model inference request
    validate_model_request()

    # Retrieve Redis and RedisAI configuration from environment variables
    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT")
    redis_ai_host = os.getenv("REDISAI_HOST")
    redis_ai_port = os.getenv("REDISAI_PORT")

    # Initialize Redis and RedisAI clients
    redis_client = initialize_redis_client(redis_host, redis_port)
    redis_ai_client = initialize_redis_ai_client(redis_ai_host, redis_ai_port)

    # Start the inference API
    print("Starting API...")
    inference_api = InferenceAPI(
        redis_client=redis_client,
        redis_ai_client=redis_ai_client,
        categorical_columns=categorical_columns,
        numerical_columns=numerical_columns,
    )
    return inference_api.app


app = main()
