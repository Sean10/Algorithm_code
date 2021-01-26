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
import json
import os
service = Blueprint("service", __name__, url_prefix="/service")


class FileNoSQL:
    def __init__(self):
        self.file = f"data/{current_app.config['hostname']}_db"
        self.log = f"data/{current_app.config['hostname']}.log"

    @classmethod
    def init_app(self, hostname):
        log_file = f"data/{hostname}.log"
        db_file = f"data/{hostname}_db"
        init_format = {
            "last_id": 0,
            "log": []
        }
        with open(log_file, "w") as f:
            json.dump(init_format, f)
        with open(db_file, "w") as f:
            json.dump({}, f)

    def set(self, key, value):
        ret = 0
        with open(self.file, "r") as f:
            data = json.loads(f.read())
            data[key] = value
            # except Exception as e:
            #     logging.error(f'fail to set data: {str(e)}')
            #     ret = 1
        with open(self.file, "w") as f:
            json.dump(data, f)
        return ret

    def get(self, key):
        """
        if get error, raise something
        :param key:
        :return: value: str
        """
        with open(self.file, "r") as f:
            data = json.loads(f.read())
        return data.get(key)

    @staticmethod
    def get_task_log(data, id):
        """

        :param data:
        :param id:
        :return: return {} if not found
        """
        for item in data:
            if item["id"] == id:
                return item
        return {}

    def redo(self, id):
        """
        deprecated
        :param task:
        :param key:
        :param value:
        :return:
        """
        ret = 0
        with open(self.log, "r") as f:
            log_list = json.loads(f.read())
        task = self.get_task_log(log_list["log"], id)
        ret = self.set(task["redo"]["key"], task["redo"]["value"])
        return ret

    def undo(self, id):
        """
        deprecated
        :param task:
        :param key:
        :return:
        """
        ret = 0
        with open(self.log, "r") as f:
            content = f.read()
            logging.error(f"content {content}")
            log_list = json.loads(content)

        task = self.get_task_log(log_list["log"], id)
        ret = self.set(task["undo"]["key"], task["undo"]["value"])
        return ret

    def record_log(self, key, value):
        """

        :param key:
        :param value:
        :return: id if succeed , else return -1
        """
        id = -1
        with open(self.file, "r") as f:
            data = f.read()
            print(f"before data: {data}")
            old_value = json.loads(data).get(key, "not existed")
            print(old_value)
        with open(self.log, "r") as f:
            data = f.read()
            print(f'data: {data}')
            log_list = json.loads(data)
            id = log_list["last_id"] + 1
            log_list["last_id"] += 1
            do_log = {
                "id": id,
                "undo": {
                    "key": key,
                    "value": old_value
                },
                "redo": {
                    "key": key,
                    "value": value
                }
            }
            log_list["log"].append(do_log)
        with open(self.log, "w") as f:
            json.dump(log_list, f)
        return id


@service.route("/prepare", methods=["POST"])
def prepare():
    """
    应该只有修改需要prepare+commit, 所以在客户端层应该已经判定了是读还是写了.
    :return:
    """
    data = request.json
    print(request.data)
    logging.debug(f"receive data: {data}")
    id = FileNoSQL().record_log(data["key"], data["value"])
    if id > 0:
        return {"code": 0, "msg": "succeed to prepare", "data": {"id": id}}
    else:
        return {"code": 1, "msg": "fail to prepare", "data": {"id": id}}


@service.route("/commit", methods=['POST'])
def commit():
    data = request.json
    if "id" not in data:
        raise Exception("fail to get id in commit.")
    id = data['id']
    ret = FileNoSQL().redo(id)
    return {"code": ret, "msg": "succeed to commit", "data": {}}


@service.route("/rollback", methods=['POST'])
def rollback():
    data = request.json
    if "id" not in data:
        raise Exception("fail to get id in commit.")
    id = data['id']
    ret = FileNoSQL().undo(id)
    return {"code": 0, "msg": "succeed to rollback", "data": {}}