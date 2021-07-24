#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/24 3:32 PM
# @Author  : sean10
# @Site    : 
# @File    : logger_a.py
# @Software: PyCharm

"""


"""

import logging

def test_a():
    logger_a = logging.getLogger("a")
    logger_a.error(f'logger_a: {logger_a.level}')
    logger_a.info('logger_a: test_a ')
    logger_a.error('logger_a: test_a error')
    logger_a.debug(f"root logger: {logging.getLogger('root')}")