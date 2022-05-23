import logging
import time

temp_level = logging.INFO


def log(level=logging.INFO, msg=""):
    if level < temp_level:
        return
    print(
        f"{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))} {level} {msg}"
    )
