from functools import wraps
from logger import log
import logging
import time

def time_count(func):
    """
    统计io函数, IOPS以及延时
    """
    @wraps(func)
    def wrapper(file, count, *args, **kwargs):
        start = time.monotonic() 
        res = func(file, count, *args, **kwargs)
        end = time.monotonic()
        duration = end - start
        # count = args[1]
        avg = duration / count
        log(logging.INFO, f"count lat: {avg} IOPS: {count/duration}")
        return res
    return wrapper