#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/25 10:42 PM
# @Author  : sean10
# @Site    : 
# @File    : common.py
# @Software: PyCharm

"""


"""

import enum

class PaxosState(enum.Enum):
    PREPARE = enum.auto()


def template_base(code, msg, data):
    return {
        "code": code,
        "msg": msg,
        "data": data
    }


template_promise = template_base(0, "promise", "promise")
# template_promise_accepted = template_base(0, "promise", )
template_refuse = template_base(1, "refuse", "refuse")
template_timeout = template_base(1, "timeout", "timeout")
