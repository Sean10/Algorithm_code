import functools
import psutil
import rados
import sys
import os

def prefix_function(function, prefunction):
    @functools.wraps(function)
    def run(*args, **kwargs):
        # 1. add hook function
        # prefunction(*args, **kwargs)
        # return function(*args, **kwargs)

        temp_object = function(*args, **kwargs)
        temp = {"rados": temp_object, "sean": "wc"}
        return temp
    return run

def this_is_a_function():
    pid = os.getpid()
    print(f"{psutil.Process(pid).cmdline()}")

rados.Rados = prefix_function(
    rados.Rados, this_is_a_function)





