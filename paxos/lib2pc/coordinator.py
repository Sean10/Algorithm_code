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
import logging
import requests


def init_nodes():
    with open("nodes.yaml", "r") as f:
        data = yaml.load(f, yaml.SafeLoader)
    logging.debug(data)
    return data['nodes']

def write(data):
    server_nodes = init_nodes()
    result_map = dict()
    for node in server_nodes:
        result_map[node] = prepare(node, data)
    logging.info(f"result map: {result_map}")
    ret = any(result_map.values())
    logging.info("prepare result: {}".format(ret))
    if not ret:
        for node in server_nodes:
            result_map[node] = commit(node)
        logging.info(f"commit result: {result_map}")
    else:
        rollback(node)


def prepare(node, data):
    client = requests.post("http://{}{}".format(node, '/service/prepare'), json={"data": data})
    if 200 == client.status_code:
        return 0
    else:
        return 1

def commit(node):
    client = requests.post("http://{}{}".format(node, '/service/commit'))
    if 200 == client.status_code:
        return 0
    else:
        return 1


def rollback(node):
    pass