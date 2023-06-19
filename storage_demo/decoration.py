import importlib
import logging
import time
from functools import wraps

from logger import log


def time_count(func):
    """
    统计io函数, IOPS以及延时

    随着引入多进程, 统计的误差会越来越大

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        res = func(*args, **kwargs)
        end = time.monotonic()
        duration = end - start
        # count =`` args[1]
        avg = duration / kwargs["count"] * kwargs["image_count"]
        log(logging.INFO, f"count lat: {avg} IOPS: {kwargs['count']*kwargs['image_count'] /duration}")
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
