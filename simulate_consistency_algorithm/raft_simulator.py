import random
import time

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

def simulate(algorithm, num_replicas, consistency_level, num_operations=100, network_delay=0.01, async_delay=0.05):
    if algorithm == "raft":
        cluster = RaftCluster(num_replicas, consistency_level, network_delay, async_delay)
    elif algorithm == "paxos":
        cluster = PaxosCluster(num_replicas, consistency_level, network_delay, async_delay)
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
