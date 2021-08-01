#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/2 12:14 AM
# @Author  : sean10
# @Site    : 
# @File    : logger_public.py
# @Software: PyCharm

"""


"""
import logging

def logger():
    logger = logging.getLogger("*.public")
    logger.debug("test public")
    logger.info("test public")