#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/23 9:51 PM
# @Author  : sean10
# @Site    : 
# @File    : utils.py
# @Software: PyCharm

"""


"""

import logging


def test():
    logging.error('logging stest utils')
    logerr = logging.getLogger()
    logerr.error(f"print utils: {logerr.root.manager.loggerDict}")
    logerr.error(f"utils: logerr: {logerr.level} {logerr}")
    logerr.error(f"utils: {logging.root}")