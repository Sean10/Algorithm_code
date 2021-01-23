#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-10-13 21:46
# @Author  : sean10
# @Site    : 
# @File    : s_logger.py
# @Software: PyCharm

"""


"""
import logging
logger = logging.getLogger("s_logger")
# print(logger)
# print(logger.loggerDict)
# print(logging.getLogger())
logger.setLevel(logging.CRITICAL)
# logging.basicConfig(level=logging.ERROR)

# logging.error("error inner lib")
# logging.info("error inner lib")
# logging.critical("error inner lib")
# logging.debug("error inner lib")
# logger = logging.getLogger(__name__)

