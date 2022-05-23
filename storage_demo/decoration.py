from functools import wraps
from logger import log
import logging
import time
import importlib

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
        # count =`` args[1]
        avg = duration / count
        log(logging.INFO, f"count lat: {avg} IOPS: {count/duration}")
        return res

    return wrapper


class LazyImport:
    def __init__(self, module_name):
        self.module = None
        self.module_name = module_name

    def __getattr__(self, funcname):
        log(logging.INFO, f"funcname: {funcname}")

        if self.module is None:
            self.module = importlib.import_module(self.module_name)
            log(logging.INFO, f"lazy import: {self.module_name}")
        return getattr(self.module, funcname)
