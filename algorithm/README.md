# 背景
没什么心情, 单纯抄录一些模板代码

1. [Jack\-Lee\-Hiter/AlgorithmsByPython: 算法/数据结构/Python/剑指offer/机器学习/leetcode](https://github.com/Jack-Lee-Hiter/AlgorithmsByPython)

# todo
* 完全使用vim mode
* shift+enter有点容易误触(红轴下是的)

# Changelog
* 一些其他人写的模板, 好像主要遵循的命名规范跟我用的不太一致
  * PEP-8标准
    * 模块名尽量小写命名
    * 类名使用驼峰命名
    * 函数名一律小写, 用下划线隔开
    * 变量名, 小写, 用下划线隔开
    * 常量用下划线分割的大写命名.
* python的项目开发规范, 一般推荐用什么扩展来做静态检查呢?
  * 我现在因为我主要想开发python3以后带类型标注的那种, 来做静态分析, 因此我是比较推荐mypy的, 但是
  * pylint ,统一团队的代码风格
  * pyflakes 检查一些代码中的简单的语法错误
  * flake8等于上面两者合并
  * Mypy ,用于对代码进行静态类型检查
  * 所以实际上应该是使用flake8+Mypy
  * [Python 静态分析Pylint、Pyflakes 与 Mypy ——我应该用谁？\_检查](https://www.sohu.com/a/376377878_752099)

