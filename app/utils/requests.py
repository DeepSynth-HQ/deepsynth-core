import time
from phi.utils.log import logger


def retry_request(func, retries=3, delay=5):
    """
    Retry a function call multiple times with delay between attempts.

    Args:
        func: The function to retry
        retries: Number of retry attempts
        delay: Delay between retries in seconds

    Returns:
        A wrapper function that implements the retry logic
    """

    def wrapper(*args, **kwargs):
        last_exception = None
        for i in range(retries):
            try:
                logger.debug(f"[RETRY] Attempt {i+1} of {retries}")
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.error(f"[RETRY] Request failed: {e}")
                if i < retries - 1:  # Don't sleep on the last iteration
                    time.sleep(delay)
        raise last_exception or Exception(f"Failed after {retries} retries")

    return wrapper
