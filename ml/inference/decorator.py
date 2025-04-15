import time
from functools import wraps


def time_checker(f):
    """
    Decorator to check the time taken by the function.
    """

    @wraps(f)
    async def wrapper(*args, **kwargs):
        """
        Wrapper function to check the time taken by the function.
        """
        start = time.time()
        result = await f(*args, **kwargs)
        end = time.time()
        print(f"Time taken: {end - start} seconds")
        return result

    return wrapper
