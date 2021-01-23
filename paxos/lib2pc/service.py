#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/23 11:38 PM
# @Author  : sean10
# @Site    : 
# @File    : service.py
# @Software: PyCharm

"""


"""

from flask import current_app, Blueprint, request
import logging

service = Blueprint("service", __name__, url_prefix="/service")


def persist_redo_log(data):
    with open(current_app.config['hostname'], "w") as f:
        f.write(f"write {data}")
    return 0


@service.route("/prepare", methods=["POST"])
def prepare():
    data = request.json
    logging.debug(f"receive data: {data}")
    persist_redo_log(data['data'])
    return {"code": 0, "msg": "succeed to perpare", "data": {}}


@service.route("/commit", methods=['POST'])
def commit():
    with open(current_app.config['hostname'], "r") as f:
        task = f.read()
    if "write" in task:
        with open(f"{current_app.config['hostname']}_db", "w") as f:
            f.write(task.split("write ")[-1])
    return {"code": 0, "msg": "succeed to commit", "data": {}}

