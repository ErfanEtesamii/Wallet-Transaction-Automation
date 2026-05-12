import time
import random
from functools import wraps

def retry(max_attempts=3, base_delay=0.7, backoff=1.8, exceptions=(Exception,)):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            delay = base_delay
            for _ in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    time.sleep(delay + random.uniform(0, 0.2))
                    delay *= backoff
            raise last_exc
        return wrapper
    return decorator

def clamp(n, low, high):
    return max(low, min(n, high))