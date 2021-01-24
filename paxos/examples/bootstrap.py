#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/24 1:59 AM
# @Author  : sean10
# @Site    : 
# @File    : bootstrap.py
# @Software: PyCharm

"""


"""

import subprocess
import yaml
import signal

def main():
    with open("nodes.yaml", "r") as f:
        nodes = yaml.load(f, yaml.SafeLoader)
    for i, node in enumerate(nodes["nodes"]):
        # signal.signal(signal.SIGHUP, )
        process = subprocess.Popen(f"python3 main.py --hostname node{i} -p {node.split(':')[-1]}", shell=True, stdin=subprocess.DEVNULL)
        # process.

if __name__ == "__main__":
    main()