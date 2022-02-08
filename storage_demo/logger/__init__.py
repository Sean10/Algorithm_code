import logging
import time


def log(level=logging.INFO, msg=""):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))} {level} {msg}")