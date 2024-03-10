#!/bin/python3
'''
双独立（independent）样本检验（ttest_ind）

[如何使用python进行独立双样本检验？（附案例） \- 知乎](https://zhuanlan.zhihu.com/p/539155456)
'''
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pylab import mpl

# mpl.rcParams['font.sans-serif'] = ['SimHei']   # 雅黑字体
# plt.rcParams['axes.unicode_minus']=False
#T检验是假设检验的一种，又叫student t检验（Student’s t test），主要用于样本含量较小（例如n<30），总体标准差σ未知的正态分布资料。
A=[8846.75 , 8928.11 , 8597.53 , 8764.52 , 8665.68 , 8999.63 , 8821.26 , 8643.40 , 9014.29 , 8873.59 , 8718.28 , 8849.25 , ]
A = list(map(lambda x: x*0.95, A))
B= [8233.94 , 8286.07 , 8286.99 , 8287.08 , 8300.91 , 8319.75 , 8338.80 , 8355.22 , 8374.93 , 8438.35 , 8475.74 , 8557.99 , ]
dataA=np.array(A)
dataB=np.array(B)
A_mean=dataA.mean()
B_mean=dataB.mean()
print('A版本的平均值=',A_mean)
print('B版本的平均值=',B_mean)
'''
这里要区别：数据集的标准差，和样本标准差
数据集的标准差公式除以的是n，样本标准差公式除以的是n-1。
样本标准差，用途是用样本标准差估计出总体标准差pandas计算的标准差，默认除以的是n-1，也就是计算出的是样本标准差
'''

#样本标准差
a_std=dataA.std()
b_std=dataB.std()
print('A版本样本标准差=',a_std)
print('B版本样本标准差=',b_std)
#零假设：A版本和B版本没有差别，也就是A版平均值=B版本平均值
#备选假设：A版本和B版本有差别，也就是A版本平均值不等于B版本平均值
#因为有2组样本，是不同的人，选择双独立样本检验.两样本均值比较，双尾检验.sns.distplot(dataA)
# plt.title('A版本数据集分布')
# plt.show()
# sns.distplot(dataB)
# plt.title('B版本数据集分布')
# plt.show()
'''
Scipy的双独立样本t检验不能返回自由度，对于后面计算置信区间不方便。所以我们使用另一个统计包（statsmodels）
'''
'''
ttest_ind:独立检验双样本t检验，usevar='unequal'两个总体方差不一样
返回的第1个值t是假设检验计算出的t值，
第2个p_two是双尾检验的p值
第3个DF是独立双样本的自由度
'''
import statsmodels.stats.weightstats as stt
t, p_two,df= stt.ttest_ind(dataA,dataB, usevar='unequal')
print('t=',t,'p_twotail=',p_two,'df=',df)
#判断标准（显著水平）使用alpha=0.05
alpha=0.05

#做出结论
if (p_two<alpha/2):
    print('拒绝零假设，A和B版本有差异')
else:
    print('接受零假设，A和B没有差别')



"""
以下计算置信区间 和 功效
t= 0.32681015511520867 p_twotail= 0.7471973488252327 df= 20.057552566113554
[T分布表 t distribution table \- OBHRM百科](http://www.obhrm.net/index.php/T%E5%88%86%E5%B8%83%E8%A1%A8_t_distribution_table)
查表, t(20) = 1.7247
"""
t_ci= 1.7247


'''
numpy.square 平方
numpy.sqrt开方
标准误差计算公式：
https://en.wikipedia.org/wiki/Student%27s_t-test#Independent_two-sample_t-test
'''
a_n = len(A)
b_n = len(B)

se=np.sqrt( np.square(a_std)/len(A) + np.square(b_std)/len(B) )
sample_mean=A_mean - B_mean
#置信区间上限
a=sample_mean - t_ci * se
#置信区间下限
b=sample_mean + t_ci * se

print('两个平均值差值的置信区间，95置信水平 CI=[%f,%f]' % (a,b))

'''
效应量：差异指标Cohen's d
这里的标准差，因为是双独立样本，需要用合并标准差（pooled standard deviations）代替
'''
#合并标准差
sp=np.sqrt(((a_n-1)*np.square(a_std) + (b_n-1)* np.square(a_std) ) / (a_n+b_n-2))
#效应量Cohen's d
d=(A_mean - B_mean) / sp

print('d=',d)