#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/2 12:08 AM
# @Author  : sean10
# @Site    : 
# @File    : progate_logger.py
# @Software: PyCharm

"""


"""
import logging

logger = logging.getLogger("propagate_logger")

logger.debug("test logger")
logger.error('test logger')


def sub_logger():
    logger = logging.getLogger("propagate_logger.child")
    logger.debug("test logger child")
    logger.info("test logger child")
