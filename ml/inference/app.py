import os

from ml.inference.main import API
from ml.inference.const import CategoricalColumns, NumericalColumns, Columns
from ml.inference.redis_ai_client import RedisAIClient
from ml.inference.redis_client import RedisClient


cat_cols = CategoricalColumns().to_list()
num_cols = NumericalColumns().to_list()

if len(Columns.X) != len(cat_cols) + len(num_cols):
    raise ValueError("x_cols must be the sum of cat_cols and num_cols")

redis_host = os.getenv("REDIS_HOST")
if not redis_host:
    raise ValueError("REDIS_HOST environment variable is not set")

redis_port = os.getenv("REDIS_PORT")
if not redis_port:
    raise ValueError("REDIS_PORT environment variable is not set")

redis_ai_host = os.getenv("REDISAI_HOST")
if not redis_ai_host:
    raise ValueError("REDISAI_HOST environment variable is not set")

redis_ai_port = os.getenv("REDISAI_PORT")
if not redis_ai_port:
    raise ValueError("REDISAI_PORT environment variable is not set")

r = RedisClient(redis_host, redis_port)
if r.ping():
    print("Redis server is alive.")
else:
    raise ConnectionError("Redis server is not reachable.")

rai = RedisAIClient(redis_ai_host, redis_ai_port)
if rai.ping():
    print("RedisAI server is alive.")
else:
    raise ConnectionError("RedisAI server is not reachable.")

backend = API(redis=r, redis_ai=rai, cat_cols=cat_cols, num_cols=num_cols)
app = backend.app
