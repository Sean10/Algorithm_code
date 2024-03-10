#!/bin/python
"""
基于k-s正态性检验
kstest方法：KS检验，参数分别是：待检验的数据，检验方法（这里设置成norm正态分布），均值与标准差
结果返回两个值：statistic → D值，pvalue → P值
p值大于0.05，为正态分布
H0:样本符合  
H1:样本不符合 
如何p>0.05接受H0 ,反之 

绘图, 通过pip3 install seaborn=0.11.1
"""
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

s = [8233.94 , 8286.07 , 8286.99 , 8287.08 , 8300.91 , 8319.75 , 8338.80 , 8355.22 , 8374.93 , 8438.35 , 8475.74 , 8557.99 , ]
u = np.average(s)
std = np.std(s)
print(stats.kstest(s, 'norm', (u, std)))


import seaborn as sns
sns.distplot(s, kde=True, fit=stats.norm)
plt.show()
