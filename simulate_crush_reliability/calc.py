#!/usr/bin/python
# -*- coding: utf-8 -*-
# 来自netease大佬的代码: https://sq.sf.163.com/blog/article/201113281655402496
import decimal
import math
import time    # 随机分布情况下系统的copyset组合数
def RandomCopySets(N, DiskSize, RepNum, Percent, PartSize):
    setNum = (N * DiskSize * Percent / (RepNum *  PartSize))
    MaxCopySetNum = C(N, RepNum)

    copysetNum = 0
    if setNum > MaxCopySetNum:
      copysetNum = MaxCopySetNum
    else:
      copysetNum =  setNum
    print(f"copyset: {copysetNum}")
    copysetNum = 1000
    return int(copysetNum)    # N 个磁盘存储系统中T时间同时损坏K块盘的概率,年故障率ARF

def KdiskFailRate(N, T, ARF, K):
    # λ 每小时的换盘数量
    lambda1 = decimal.Decimal(str(N*AFR/24/365))
    return poisson(lambda1, T, K)    # 副本数R的N 个磁盘存储系统中T时间内造成数据丢失的概率, 只统计R -> 2R-1个副本情况下的丢失数据概率(大于R个情况下，在一遍情况下对结果影响比较小)
def LossDataInT(S, N, RepNum, T, ARF):
    loosRate = decimal.Decimal(str(0.0))
    for k in range(RepNum, RepNum*2):
        kdrate = KdiskFailRate(N,T,ARF,k)

        singlerate = S * C(N-3, k-3)/C(N,k)

        kdlossrate = kdrate * singlerate
        print("k = " + str(k)  + ", " +str(kdrate) + ", " + str(kdlossrate))

        loosRate += kdlossrate
        print(loosRate)
    return loosRate    # define loseRate in one Year
def LoseRate(S, N, RepNum, T, AFR):
    return 1 - (1 - LossDataInT(S, N, RepNum, T, AFR))**(365*24//T)    #组合运算
def C(n, m):
  return factorial(n) / (factorial(m)*factorial(n-m))    #泊松分布
def poisson(lam, t, R):
    e=decimal.Decimal(str(math.e))
    return ((lam * t) ** R) * (e**(-lam*t)) / factorial(R)    #t时间内损坏R块磁盘的概率
def probability(t, R):
  return poisson(t, R)    #级数
def factorial(n):
  S = decimal.Decimal("1")
  for i in range(1, n+1):
    N = decimal.Decimal(str(i))
    S = S*N
  return S    # case 1
N = 7200
DiskSize = 8*1024
Percent = 0.7
PartSize = 0.004
RepNum = 3
T = 1
AFR = 0.04

S  =  RandomCopySets(N, DiskSize, RepNum, Percent, PartSize)
print(LoseRate(S, N, RepNum, T, AFR))

