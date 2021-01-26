#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/25 10:38 PM
# @Author  : sean10
# @Site    : 
# @File    : main.py
# @Software: PyCharm

"""


"""

import requests
import logging
import json
import yaml

def init_nodes():
    with open("nodes.yaml", "r") as f:
        data = yaml.load(f, yaml.SafeLoader)
    logging.debug(data)
    return data['nodes']


def prepare_single_node(node, proposal, value):
    client = requests.post("http://{}{}".format(node, '/service/proposal'), json={"proposal": proposal, "value": value})
    if 200 == client.status_code:
        id = json.loads(client.text)
        logging.info(f"id: {id}")
        return id
    else:
        return -1

def prepare(proposal: int, value: str):
    nodes = init_nodes()
    # for node in nodes:
    prepare_single_node(nodes[0], proposal, value)


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
