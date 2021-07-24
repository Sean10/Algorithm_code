#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/24 4:22 PM
# @Author  : sean10
# @Site    : 
# @File    : logger_a_b.py
# @Software: PyCharm

"""


"""

import logging


logger = logging.getLogger("a.b")

def test():
    logger.debug("1234")

