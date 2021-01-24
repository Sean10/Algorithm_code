#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/24 12:09 AM
# @Author  : sean10
# @Site    : 
# @File    : client.py
# @Software: PyCharm

"""


"""
import sys
sys.path.append("..")

import logging
# from logging import StreamHandler
from lib2pc import coordinator
import argparse
import sys

logger = logging.getLogger("root")
logger.handlers = []
handler = logging.StreamHandler()
format = logging.Formatter("[client] %(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s")
handler.setFormatter(format)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
# print(logging.root.manager.loggerDict)



if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--shutdown", help="shutdown ", action='store_true')
    args = argparser.parse_args()
    if args.shutdown:
        coordinator.shutdown()
        sys.exit(0)
    logger.info("debug client init")
    coordinator.write("new", "123")