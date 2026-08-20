import time
import random
from functools import wraps


def retry(max_attempts=3, base_delay=0.7, backoff=1.8, exceptions=(Exception,)):
    """Retry decorator with exponential backoff + jitter."""
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


def wait_until(condition_fn, timeout=30, interval=0.2, stop_fn=None):
    """Poll ``condition_fn`` until it returns True.

    Returns True as soon as the condition is met, or False once ``timeout``
    seconds have elapsed or ``stop_fn`` reports that the caller wants to
    abort. Used in place of bare ``while True`` polling loops so a page that
    never finishes loading can no longer hang the whole script forever and
    still responds to ESC/pause.
    """
    start = time.time()
    while True:
        if condition_fn():
            return True
        if stop_fn is not None and stop_fn():
            return False
        if time.time() - start > timeout:
            return False
        time.sleep(interval)
