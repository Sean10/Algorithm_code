#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-10-13 21:23
# @Author  : sean10
# @Site    : 
# @File    : test_logger.py
# @Software: PyCharm

"""


"""

import logging
from logger_module import s_logger, logger_a, logger_a_b
from logger_module import utils
from logging.config import dictConfig
import yaml

logger_a.test_a()
with open("log.yaml", "r") as f:
    data = yaml.load(f, yaml.Loader)

dictConfig(data)

logger_a_b.test()
print(logging.root)
print(logging.root.manager.loggerDict)
logger_a.test_a()
# print(logging.getLogger())
# print(logging.getLevelName(logging.getLogger().getEffectiveLevel()))
utils.test()

# logging.basicConfig(level=logging.DEBUG)
print(logging.getLevelName(logging.getLogger().getEffectiveLevel()))
print(logging.root)
print(logging.root.manager.loggerDict)
# print(logging._levelToName)
# print(logging._levelNames)
logger = logging.getLogger('root')
logger.setLevel(logging.INFO)
logging.debug("debug 111")
logging.info("info 111")

logger = logging.getLogger("new")
# print(logging._levelToName)
print(logging.getLevelName(logger.getEffectiveLevel()))
logger.debug("debug 222")

logger.info("info 222")
logger.error('hello ')
