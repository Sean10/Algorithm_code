#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/23 5:27 PM
# @Author  : sean10
# @Site    : 
# @File    : main.py.py
# @Software: PyCharm

"""


"""
import sys
sys.path.append("../..")
from lib2pc.server import create_server
import argparse

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--hostname", type=str, help="hostname of different server")
    argparser.add_argument("--port", "-p", type=int, help="the listen port")
    args = argparser.parse_args()
    server = create_server(args.hostname)
    server.run(host="0.0.0.0", port=args.port, debug=True)