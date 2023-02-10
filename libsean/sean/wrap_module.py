from rados import *
from .error import *
import functools

def prefix_function(function, prefunction):
    @functools.wraps(function)
    def run(*args, **kwargs):
        # 1. add hook function
        # prefunction(*args, **kwargs)
        # return function(*args, **kwargs)
        raise WrapError
        return function(*args, **kwargs)
    return run


def this_is_a_function():
    pass

Rados = prefix_function(
    Rados, this_is_a_function)
