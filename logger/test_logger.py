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
from logger_module import s_logger, logger_a, logger_a_b, progate_logger, logger_public
from logger_module import utils
from logging.config import dictConfig
import yaml


with open("log.yaml", "r") as f:
    data = yaml.load(f, yaml.Loader)

dictConfig(data)


def test_logger_a_b_with_propagate():
    logger = logging.getLogger("a")
    logger_a.test_a()
    temp = logging.getLogger("*.b")
    temp.setLevel(logging.DEBUG)
    logger_a_b.test()
    test_dynamic_modify_logger_chilren(logger)

    logger_public.logger()


def test_root():
    print(logging.root)
    print(logging.root.manager.loggerDict)
    # print(logging.getLogger())
    # print(logging.getLevelName(logging.getLogger().getEffectiveLevel()))
    utils.test()


def test_dynamic_modify_logger_chilren(logger):
    for name in logging.root.manager.loggerDict:
        if name.startswith("*."):
            # logging.getLogger(name).setLevel(logging.INFO)
            logging.getLogger(name).parent = logger


def test_logger():

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



def test_propagate_logger():
    logger = logging.getLogger("propagate_logger")
    test_dynamic_modify_logger_chilren(logger)
    progate_logger.sub_logger()
    logger_public.logger()



print(logging.getLevelName(logging.getLogger().getEffectiveLevel()))
print(logging.root)
print(logging.root.manager.loggerDict)
# test_propagate_logger()
test_logger_a_b_with_propagate()