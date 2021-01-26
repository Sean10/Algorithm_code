# 架构
* 基于http,使用flask

# 调试
* mac上端口未配置SO_REUSEADDR, 服务端直接退出后,端口一直占用问题
[python \- How to stop flask application without using ctrl\-c \- Stack Overflow](https://stackoverflow.com/questions/15562446/how-to-stop-flask-application-without-using-ctrl-c)
* json.load为什么一直报错呢? json.loads就没有
* 我忘记a+是在末尾了, 所以没读到
# 后端存储
## 文件系统
对于我实现一个一致性来说, 暂时应该open和write可以先放一放? (感觉对于分布式文件系统, 这部分有点麻烦的样子. 我open了以后, 这个变量怎么维持呢?毕竟肯定是走了一层转发的.)

emm, 如果是以实现文件系统的方式, 位置等描述较为麻烦. 

暂时还是针对key-value的形式来专门处理吧.

### Posix接口
* open
* write
* read
* close


## rocksdb
### 主要接口
* get
* put




### install rocksdb

``` bash
brew install rocksdb
```


# log
基于json的结构, 来实现一个这样的log描述吧.

``` json
[{
    "task": "redo",
    "value": "123",
    "key": "1234"
},
{
    "task": "undo",
    "key": "key",
    "value": "1234
}]

```

## redo, undo与task关系
如何记录下来, 理论上应该是同时被记录, 如何维持在文件中?
只针对Task.
需要一个任务对应的id, 这样知道要rollback哪条, 


`WAL`实现思路

### undo的日志去读取之前的这个key的值

### redo的日志就是当前的设置

## redo, undo如何被Commit执行?


# 2pc
# 准备
* 多节点数据一致
* 现在2pc单纯模拟了一个基本的prepare, commit的实现
* 要考虑一下底层到底用什么东西来承接, 是用fs的接口, 还是用数据库. 比如nosql的一些k-v处理? set, get.
* 什么时候进行加锁.
* 实现事务
# 3pc

# paxos
## promise阶段, 收到相同的提案的时候呢?
## 当提案被接收, 是向所有的节点发送任务,还是只向接受的部分发送呢?
## accepted_value这个值怎么理解呢? 为什么我看到的文章里写的都是整数, 这个东西到底是不是提案内容呢?
### 应该可以是任意内容, 主要指代的是一个对象
## accepted之后的, done,是否还需要proposaler节点发送done请求给其他节点呢?还是说各节点给出phase2_accpted的响应时就进行了存储操作?
### 这个learner的过程到底怎么实现呢?

# todo

* 基于文件系统的分布式写入一致.
* 基于rocksdb的分布式写入一致.
* 实现基本的2PC
* 实现基本的3PC
* 实现基本的Paxos
* 实现基本的Raft
* 实现基本的Zab
* 实现Multi-Paxos

# 测试场景
* 调用一个单节点任务, 全节点数据一致.
* 写一个pytest的单元测试, 模拟失败和成功场景吧
  * 怎么让代码内进入timeout逻辑呢?
  * 主动只运行部分节点, 让部分节点的服务离线?
  * 那运行过程中呢?通过主动发送信号让指定的服务自停?
  * 但是这样其实算不上是单元测试,而是业务逻辑真实测试了? 不过自停这个其实还是模拟. 所以只是模拟下的效果.







# Reference
1. [理解分布式一致性:Paxos协议之Basic Paxos \- flydean \- 博客园](https://www.cnblogs.com/flydean/p/12680415.html)