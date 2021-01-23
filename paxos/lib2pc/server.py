#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/23 9:57 PM
# @Author  : sean10
# @Site    : 
# @File    : server.py
# @Software: PyCharm

"""


"""

import flask
from .service import service


def create_server(hostname):
    server = flask.Flask(__name__)
    server.register_blueprint(service)
    server.config["hostname"] = hostname
    return server
