#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-10-16 22:19
# @Author  : sean10
# @Site    : 
# @File    : sudoku_tuili.py
# @Software: PyCharm

"""
sudoku for tui li.
http://www.sudokufans.org.cn/lx/tl.index.php

"""

"""
from the most line connected as start point, in the clockwise to the end point.

line graph problem.

Kruskal algorithm.
"""
import logging

logging.basicConfig(filename="sudoku.log", filemode='w', format="%(message)s")

logger = logging.getLogger(__name__)

handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

graph_g = (
    (1, 2, 5, 6,),
    (0, 4,),
    (0, 3, 8,),
    (2, 5, 7,),
    (1, 8,),
    (0, 3, 7,),
    (0, 8,),
    (3, 5,),
    (2, 4, 6,)
)
# q = [16, 18, 8, 15, 4, 16, 12, 16, 14]
q = [13, 17, 13, 9, 23, 15, 17, 18, 8]

ans = (8, 9, 2, 3, 6, 1, 4, 5, 7,)
sign = False
num = [-1 for i in range(9)]

def tuple2list(src: tuple)->list:
    return [list(line) for line in src]


def dfs(n: int):
    logger.debug(f"dfs:{n}")
    if n > 8:
        global sign
        logger.debug("signed")
        sign = True
        return True

    if num[n] != -1:
        dfs(n+1)
        return True

    for i in range(9):
        if check_num(n, i):
            num[n] = i
            logger.debug(f"ensure {n}:{i}\n")
            logger.debug(f"current list:{num}")
            dfs(n+1)
            if sign:
                return True
            num[n] = -1

def check_sum(n: int, key: int)->bool:
    sum = 0
    full = True
    for i in graph_g[n]:
        # logger.debug("graph:{}, {}".format(i, num[i]))
        if num[i] == -1:
            sum += 0
            full = False
        else:
            sum += num[i] + 1
        logger.debug("key:{} sum:{}".format(q[key], sum))
    if not (full and q[key] == sum or not full and q[key] > sum):
        return False

    num[n] = key

    for j in range(9):
        if num[j] == -1:
            continue
        sum = 0
        full = True
        for i in graph_g[j]:
            # logger.debug("graph:{}, {}".format(i, num[i]))
            if num[i] == -1:
                sum += 0
                full = False
            else:
                sum += num[i] + 1
            logger.debug("calculate sum, pos:{} num:{}".format(i, num[i]))
        logger.debug("pos:{} num:{} key:{} sum:{}".format(j, num[j], q[num[j]],sum))
        if not (full and q[num[j]] == sum or not full and q[num[j]] > sum):
            num[n] = -1
            return False
    num[n] = -1
    return True


def check_num(n: int, key: int):
    logger.debug(f"check:{n}: key:{key}")
    for i in range(9):
        if key == num[i]:
            logger.debug("key reuse:{}".format(i))
            return False

    ret = check_sum(n, key)
    if not ret:
        logger.debug(f"check_sum:{ret}")
        return False

    return True




if __name__ == "__main__":
    # main()
    dfs(0)

    logger.info(list(map(lambda a: a+1, num)))

    # ans = map(lambda a: a - 1, list(ans))
    # logger.info(num == list(ans))