import time
from functools import wraps


def measure_execution_time(func):
    """
    Asynchronous decorator to measure and log the execution time of a function.

    Args:
        func (Callable): The asynchronous function to be wrapped.

    Returns:
        Callable: The wrapped function with execution time measurement.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        """
        Wrapper function that measures and logs the execution time of the decorated function.

        Args:
            *args: Positional arguments for the decorated function.
            **kwargs: Keyword arguments for the decorated function.

        Returns:
            Any: The result of the decorated function.
        """
        start_time = time.time()
        result = await func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(f"Execution time: {elapsed_time:.4f} seconds")
        return result

    return wrapper
