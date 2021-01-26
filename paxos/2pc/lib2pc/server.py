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
from flask import request
from .service import service, FileNoSQL


def create_server(hostname):
    server = flask.Flask(__name__)
    server.config["hostname"] = hostname
    FileNoSQL.init_app(hostname)
    server.register_blueprint(service)

    def shutdown_server():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()


    @server.route("/shutdown", methods=['POST'])
    def shutdown():
        shutdown_server()
        return 'Server shutting down...'


    return server
