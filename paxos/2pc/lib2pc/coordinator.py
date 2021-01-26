#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/24 12:08 AM
# @Author  : sean10
# @Site    : 
# @File    : coordinator.py
# @Software: PyCharm

"""


"""


import yaml
import json
import logging
import requests


def init_nodes():
    with open("nodes.yaml", "r") as f:
        data = yaml.load(f, yaml.SafeLoader)
    logging.debug(data)
    return data['nodes']

def write(key, value):
    server_nodes = init_nodes()
    result_map = dict()
    for node in server_nodes:
        result_map[node] = prepare(node, key, value)
    logging.info(f"result map: {result_map}")
    ret = all(map(lambda x:x > 0, result_map.values()))
    logging.info("prepare result: {}".format(ret))
    if ret:
        for node in server_nodes:
            result_map[node] = commit(node, result_map[node])
        logging.info(f"commit result: {result_map}")
    else:
        rollback(node, result_map[node])


def prepare(node, key, value):
    """
    id > 0, success, else: fail
    :param node:
    :param data:
    :return:
    """
    client = requests.post("http://{}{}".format(node, '/service/prepare'), json={"key": key, "value": value})
    if 200 == client.status_code:
        id = json.loads(client.text)['data']["id"]
        return id
    else:
        return -1

def commit(node, task_id):
    client = requests.post("http://{}{}".format(node, '/service/commit'), json={"id": task_id})
    if 200 == client.status_code:
        return 0
    else:
        return 1


def rollback(node, task_id):
    client = requests.post("http://{}{}".format(node, '/service/rollback'), json={"id": task_id})
    if 200 == client.status_code:
        return 0
    else:
        return 1


def shutdown():
    server_nodes = init_nodes()
    for node in server_nodes:
        try:
            client = requests.post("http://{}{}".format(node, '/shutdown'))
        except Exception as e:
            client = None
        if client and 200 == client.status_code:
            logging.info(f"succeed to shutdown node {node}")
        else:
            logging.info(f"fail to shutdown node {node}")
    return 0
