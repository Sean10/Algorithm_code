import random
import time
from collections import defaultdict

class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.is_leader = False
        self.log = []

class RaftNode(Node):
    def __init__(self, node_id):
        super().__init__(node_id)

class RaftCluster:
    def __init__(self, num_nodes, consistency_level, network_delay, async_delay):
        self.nodes = [RaftNode(i) for i in range(num_nodes)]
        self.leader = random.choice(self.nodes)
        self.leader.is_leader = True
        self.consistency_level = consistency_level
        self.network_delay = network_delay
        self.async_delay = async_delay

    def write(self, data):
        start_time = time.time()
        
        if self.consistency_level == "strong":
            # 模拟强一致性写入
            for node in self.nodes:
                node.log.append(data)
                time.sleep(self.network_delay)  # 模拟网络延迟
        elif self.consistency_level == "eventual":
            # 模拟最终一致性写入
            self.leader.log.append(data)
            for node in self.nodes:
                if node != self.leader:
                    if random.random() < 0.8:  # 80%的概率立即同步
                        node.log.append(data)
                    else:
                        time.sleep(self.async_delay)  # 模拟延迟同步
                        node.log.append(data)
        
        end_time = time.time()
        return end_time - start_time

class PaxosNode(Node):
    def __init__(self, node_id):
        super().__init__(node_id)
        self.promised_id = -1
        self.accepted_id = -1
        self.accepted_value = None

class PaxosCluster:
    def __init__(self, num_nodes, consistency_level, network_delay, async_delay):
        self.nodes = [PaxosNode(i) for i in range(num_nodes)]
        self.consistency_level = consistency_level
        self.network_delay = network_delay
        self.async_delay = async_delay

    def write(self, data):
        start_time = time.time()
        
        if self.consistency_level == "strong":
            # 模拟强一致性写入 (两阶段提交)
            proposer = random.choice(self.nodes)
            proposal_id = time.time()  # 使用时间戳作为提议ID
            
            # 准备阶段
            promises = 0
            for node in self.nodes:
                if proposal_id > node.promised_id:
                    node.promised_id = proposal_id
                    promises += 1
                time.sleep(self.network_delay / 2)  # 模拟网络延迟
            
            # 接受阶段
            if promises > len(self.nodes) // 2:
                accepts = 0
                for node in self.nodes:
                    if proposal_id >= node.promised_id:
                        node.accepted_id = proposal_id
                        node.accepted_value = data
                        node.log.append(data)
                        accepts += 1
                    time.sleep(self.network_delay / 2)  # 模拟网络延迟
                
                # 如果大多数节点接受,则写入成功
                if accepts > len(self.nodes) // 2:
                    pass
                else:
                    # 写入失败,清理日志
                    for node in self.nodes:
                        if node.accepted_id == proposal_id:
                            node.log.pop()
        
        elif self.consistency_level == "eventual":
            # 模拟最终一致性写入
            leader = random.choice(self.nodes)
            leader.log.append(data)
            for node in self.nodes:
                if node != leader:
                    if random.random() < 0.8:  # 80%的概率立即同步
                        node.log.append(data)
                    else:
                        time.sleep(self.async_delay)  # 模拟延迟同步
                        node.log.append(data)
        
        end_time = time.time()
        return end_time - start_time

class MultiRaftNode(Node):
    def __init__(self, node_id, shard_count):
        super().__init__(node_id)
        self.shard_logs = defaultdict(list)  # 每个分片维护独立的日志
        self.is_leader_for_shards = [False] * shard_count  # 记录节点在每个分片中的角色

class MultiRaftCluster:
    def __init__(self, num_nodes, shard_count, consistency_level, network_delay, async_delay):
        self.nodes = [MultiRaftNode(i, shard_count) for i in range(num_nodes)]
        self.shard_count = shard_count
        self.consistency_level = consistency_level
        self.network_delay = network_delay
        self.async_delay = async_delay
        
        # 为每个分片选择leader
        for shard_id in range(shard_count):
            leader = random.choice(self.nodes)
            leader.is_leader_for_shards[shard_id] = True

    def get_shard_id(self, data):
        # 简单的分片策略: 根据数据hash值分配到不同分片
        return hash(data) % self.shard_count

    def get_shard_leader(self, shard_id):
        for node in self.nodes:
            if node.is_leader_for_shards[shard_id]:
                return node
        return None

    def write(self, data):
        start_time = time.time()
        shard_id = self.get_shard_id(data)
        shard_leader = self.get_shard_leader(shard_id)
        
        if self.consistency_level == "strong":
            # 只在相关分片的节点间同步
            for node in self.nodes:
                node.shard_logs[shard_id].append(data)
                time.sleep(self.network_delay)  # 模拟网络延迟
        
        elif self.consistency_level == "eventual":
            # 最终一致性写入
            shard_leader.shard_logs[shard_id].append(data)
            for node in self.nodes:
                if node != shard_leader:
                    if random.random() < 0.8:  # 80%的概率立即同步
                        node.shard_logs[shard_id].append(data)
                    else:
                        time.sleep(self.async_delay)  # 模拟延迟同步
                        node.shard_logs[shard_id].append(data)
        
        end_time = time.time()
        return end_time - start_time

def simulate(algorithm, num_replicas, consistency_level, num_operations=100, network_delay=0.01, async_delay=0.05, shard_count=3):
    if algorithm == "raft":
        cluster = RaftCluster(num_replicas, consistency_level, network_delay, async_delay)
    elif algorithm == "paxos":
        cluster = PaxosCluster(num_replicas, consistency_level, network_delay, async_delay)
    elif algorithm == "multi-raft":
        cluster = MultiRaftCluster(num_replicas, shard_count, consistency_level, network_delay, async_delay)
    else:
        raise ValueError("不支持的算法")
    
    total_time = 0
    
    for _ in range(num_operations):
        total_time += cluster.write(f"Data_{_}")
    
    return total_time / num_operations

# 运行模拟
print("Raft算法:")
print("3副本(强一致性)平均响应时间:", simulate("raft", 3, "strong"))
print("3副本(最终一致性)平均响应时间:", simulate("raft", 3, "eventual"))
print("2副本(强一致性)平均响应时间:", simulate("raft", 2, "strong"))
print("单副本平均响应时间:", simulate("raft", 1, "strong"))

print("\nPaxos算法:")
print("3副本(强一致性)平均响应时间:", simulate("paxos", 3, "strong"))
print("3副本(最终一致性)平均响应时间:", simulate("paxos", 3, "eventual"))
print("2副本(强一致性)平均响应时间:", simulate("paxos", 2, "strong"))
print("单副本平均响应时间:", simulate("paxos", 1, "strong"))

# 使用不同的延时参数运行模拟
print("\n使用自定义延时参数:")
# print("Raft (高延迟):", simulate("raft", 3, "strong", network_delay=0.05, async_delay=0.1))
print("Raft (高网络延迟):", simulate("raft", 3, "eventual", network_delay=1, async_delay=0.1))
print("Raft (2副本高网络延迟):", simulate("raft", 2, "strong", network_delay=1, async_delay=0.1))
# print("Paxos (低延迟):", simulate("paxos", 3, "strong", network_delay=0.05, async_delay=0.01))
print("Paxos (高网络延迟):", simulate("paxos", 3, "eventual", network_delay=1, async_delay=0.02))
print("Paxos (2副本高网络延迟):", simulate("paxos", 2, "strong", network_delay=1, async_delay=0.02))

# 添加Multi-Raft的模拟
print("\nMulti-Raft算法:")
print("3副本3分片(强一致性)平均响应时间:", simulate("multi-raft", 3, "strong", shard_count=3))
print("3副本3分片(最终一致性)平均响应时间:", simulate("multi-raft", 3, "eventual", shard_count=3))
print("2副本2分片(强一致性)平均响应时间:", simulate("multi-raft", 2, "strong", shard_count=2))

# 高延迟场景下的Multi-Raft测试
print("\n使用自定义延时参数(Multi-Raft):")
print("Multi-Raft (高网络延迟):", 
      simulate("multi-raft", 3, "eventual", network_delay=1, async_delay=0.1, shard_count=3))
print("Multi-Raft (2副本高网络延迟):", 
      simulate("multi-raft", 2, "strong", network_delay=1, async_delay=0.1, shard_count=2))
