from enum import IntEnum, unique
import logging
import inspect

@unique
class STATUS(IntEnum):
    E_OK = 0
    E_ERR = 1
    ERR_PARAMETER = 2

class UserException(Exception):
    code = 0x00000001
    msg = "sorry, something you write is wrong."
    ret = STATUS.E_ERR

    # @functools.wraps(f)
    def __init__(self, msg=None, code=None, ret=None):
        if msg:
            self.msg = msg
        if code is not None:
            self.code = code
        if ret is not None:
            self.ret = ret
        print(inspect.stack()[1][3])
        # 这里原计划直接修改logging内部的stack里的funcName, 但是这部分原作者禁止了. 所以要用就只能自定义LogRecord
        # logging.error(f"msg: {msg} ret: {ret}", extra={"funcName": inspect.stack()[1][3]})
        # 暂时通过在打印的msg中增加函数名来绕过
        logging.error(f"func:{inspect.stack()[1][3]} msg: {msg} ret: {ret}")

    def __str__(self):
        return self.msg

class ParameterException(UserException):
    code = 0x00130002
    msg = "User input Wrong"
    ret = STATUS.ERR_PARAMETER