#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/25 10:38 PM
# @Author  : sean10
# @Site    : 
# @File    : service.py
# @Software: PyCharm

"""


"""
from flask import current_app, Blueprint, request
import logging
import requests
import yaml
import json
import os
from .common import *
service = Blueprint("service", __name__, url_prefix="/service")
from collections import defaultdict

def zero():
    return 0
g = defaultdict(zero)

@service.route("/prepare", methods=["POST"])
def on_repare():
    data = request.json
    proposal = data['proposal']
    if g["prepared_n"] <= proposal:
        g["prepared_n"] = proposal
        result = template_promise.copy()
        result["data"] = {"proposal": g["accepted_n"],"value": g["accepted_value"]}
        return result
        # else:
        #     return template_promise
    else:
        return template_refuse



def init_nodes():
    with open("nodes.yaml", "r") as f:
        data = yaml.load(f, yaml.SafeLoader)
    logging.debug(data)
    return data['nodes']


def prepare_single_node(node, proposal):
    """

    :param node:
    :param proposal:
    :return: 0: succeed not 0 : fail
    """
    client = requests.post("http://{}{}".format(node, '/service/prepare'), json={"proposal": proposal})
    if 200 == client.status_code:
        result = json.loads(client.text)
        return result
    else:
        return -1

def prepare(proposal: int):
    nodes = init_nodes()
    ret_map = {}
    for node in nodes:
        ret_map[node] = prepare_single_node(node, proposal)
    return ret_map

@service.route("/accept", methods=['POST'])
def on_accept():
    data  = request.json
    n = data['proposal']
    v = data['value']
    if n == g["prepared_n"]:
        g["accepted_n"] = n
        g["accepted_value"] = v
        return template_promise
    return template_refuse


@service.route('/learn', methods=['POST'])
def on_learn():
    data = request.json
    n = data['proposal']
    v = data['value']
    if n == g["accepted_n"]:
        with open(current_app.config["hostname"]+".db" , "w") as f:
            json.dump({"value": v}, f)
        return template_promise
    return template_refuse


def retry():
    pass



def accept_single_node(node, n, value):
    client = requests.post("http://{}{}".format(node, '/service/accept'), json={"proposal": n, "value": value})
    if 200 == client.status_code:
        result = json.loads(client.text)
        return result
    else:
        return -1

def accept(ret_map, n, value):
    nodes = init_nodes()
    return_map = {}
    for node in nodes:
        if ret_map[node]['code'] == 0:
            return_map[node] = accept_single_node(node, n, value)
    return return_map


def learn(node, n, value):
    client = requests.post("http://{}{}".format(node, '/service/learn'), json={"proposal": n, "value": value})
    if 200 == client.status_code:
        result = json.loads(client.text)
        return result
    else:
        return -1

def done(n, value):
    # done应该是需要跟其他节点进行通信的吧.
    nodes = init_nodes()
    ret_map = {}
    for node in nodes:
        ret_map[node] = learn(node, n, value)
    return ret_map


def init_g():
    g["max_n"] = 0
    g["last_prepare_n"] = 0
    # 先假设这个value不为0
    g["accepted_value"] = None
    g["accepted_n"] = 0
    g["prepared_n"] = 0

@service.route("/proposal", methods=["POST"])
def proposal_prepare():
    data = request.json
    real_value = data['value']
    if not hasattr(g, "max_n"):
        init_g()

    current_proposal = g["max_n"] + 1
    ret_map = prepare(current_proposal)
    result_code = list(map(lambda x: x['code'], list(ret_map.values())))
    for result in ret_map.values():
        if result['code'] != 0:
            continue
        accept_n = result['data']['proposal']
        accept_value = result['data']['value']
        if accept_n > g["max_n"] and accept_value:
            g["max_n"] = accept_n
            real_value = accept_value
    if result_code.count(0) > len(ret_map.values()) // 2:
        ret_map = accept(ret_map, current_proposal, real_value)
        print(f"ret_map: {ret_map}")
    result_code = list(map(lambda x: x['code'], list(ret_map.values())))
    if result_code.count(0) > len(ret_map.values()) // 2:
        # 这一轮投票通过, 是应该怎么样呢? 还是说这一轮其实应该有一个rollback逻辑?
        done(current_proposal, real_value)
        # ret_map = accept(current_proposal, real_value)
    # 匹配失败, 应该会进入重试逻辑, 不然的话事务是不是就算有问题了? 或者事务应该直接返回失败.
    retry()
    return {"123":"456"}