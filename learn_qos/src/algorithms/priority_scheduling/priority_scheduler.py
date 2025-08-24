"""
优先级调度算法实现

实现多种优先级调度策略，支持静态和动态优先级调度
"""

import time
import threading
from typing import Dict, Any, Optional, List, Deque
from dataclasses import dataclass
from collections import deque, defaultdict
from enum import Enum
from abc import ABC, abstractmethod
import heapq

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from common.base import QoSAlgorithm, Packet, PacketPriority, QoSMetrics


class SchedulingStrategy(Enum):
    """调度策略枚举"""
    STRICT_PRIORITY = "STRICT_PRIORITY"           # 严格优先级
    WEIGHTED_ROUND_ROBIN = "WEIGHTED_ROUND_ROBIN" # 加权轮转
    DEFICIT_ROUND_ROBIN = "DEFICIT_ROUND_ROBIN"   # 缺额轮转
    DYNAMIC_PRIORITY = "DYNAMIC_PRIORITY"         # 动态优先级


@dataclass
class PriorityConfig:
    """优先级调度配置"""
    strategy: SchedulingStrategy
    max_queue_size: int = 1000
    enable_anti_starvation: bool = True
    starvation_threshold: float = 5.0  # 饥饿阈值(秒)
    aging_factor: float = 0.1          # 老化因子
    
    # 权重配置（用于WRR和DRR）
    weights: Dict[PacketPriority, int] = None
    
    # 信用额度配置（用于DRR）
    quantum_size: int = 1500  # 量子大小(字节)
    
    def __post_init__(self):
        if self.weights is None:
            self.weights = {
                PacketPriority.URGENT: 8,
                PacketPriority.HIGH: 4,
                PacketPriority.NORMAL: 2,
                PacketPriority.LOW: 1
            }


@dataclass
class PacketInfo:
    """数据包信息（用于调度）"""
    packet: Packet
    enqueue_time: float
    dynamic_priority: float
    
    def __post_init__(self):
        if not hasattr(self, 'enqueue_time'):
            self.enqueue_time = time.time()
        if not hasattr(self, 'dynamic_priority'):
            self.dynamic_priority = float(self.packet.priority.value)


class PriorityScheduler(QoSAlgorithm):
    """
    优先级调度器基类
    
    提供统一的优先级调度接口，支持多种调度策略
    """
    
    def __init__(self, config: PriorityConfig):
        super().__init__(f"PriorityScheduler-{config.strategy.value}")
        self.config = config
        
        # 优先级队列
        self.priority_queues: Dict[PacketPriority, Deque[PacketInfo]] = {
            priority: deque() for priority in PacketPriority
        }
        
        # 统计信息
        self.enqueue_counts = defaultdict(int)
        self.dequeue_counts = defaultdict(int)
        self.drop_counts = defaultdict(int)
        self.total_waiting_time = defaultdict(float)
        
        # 饥饿检测
        self.last_service_time = defaultdict(float)
        
        # 线程安全
        self._lock = threading.RLock()
    
    def enqueue(self, packet: Packet) -> bool:
        """
        将数据包加入优先级队列
        
        Args:
            packet: 要入队的数据包
            
        Returns:
            bool: True表示成功入队，False表示队列满被丢弃
        """
        with self._lock:
            priority = packet.priority
            queue = self.priority_queues[priority]
            
            # 检查队列是否已满
            if len(queue) >= self.config.max_queue_size:
                self.drop_counts[priority] += 1
                self.metrics.update_with_packet(packet, dropped=True)
                return False
            
            # 创建数据包信息
            packet_info = PacketInfo(
                packet=packet,
                enqueue_time=time.time(),
                dynamic_priority=float(priority.value)
            )
            
            # 入队
            queue.append(packet_info)
            self.enqueue_counts[priority] += 1
            
            return True
    
    @abstractmethod
    def dequeue(self) -> Optional[Packet]:
        """
        从队列中取出下一个要处理的数据包
        
        Returns:
            Optional[Packet]: 下一个数据包，None表示所有队列为空
        """
        pass
    
    def is_empty(self) -> bool:
        """检查所有队列是否为空"""
        with self._lock:
            return all(len(queue) == 0 for queue in self.priority_queues.values())
    
    def get_queue_size(self) -> int:
        """获取所有队列的总长度"""
        with self._lock:
            return sum(len(queue) for queue in self.priority_queues.values())
    
    def get_priority_queue_sizes(self) -> Dict[PacketPriority, int]:
        """获取各优先级队列的长度"""
        with self._lock:
            return {
                priority: len(queue) 
                for priority, queue in self.priority_queues.items()
            }
    
    def _update_packet_metrics(self, packet_info: PacketInfo):
        """更新数据包指标"""
        packet = packet_info.packet
        packet.departure_time = time.time()
        
        # 计算等待时间
        waiting_time = packet.departure_time - packet_info.enqueue_time
        self.total_waiting_time[packet.priority] += waiting_time
        
        # 更新服务时间
        self.last_service_time[packet.priority] = time.time()
        self.dequeue_counts[packet.priority] += 1
        
        # 更新基类指标
        self.metrics.update_with_packet(packet)
    
    def _check_starvation(self, priority: PacketPriority) -> bool:
        """检查指定优先级是否发生饥饿"""
        if not self.config.enable_anti_starvation:
            return False
        
        queue = self.priority_queues[priority]
        if not queue:
            return False
        
        # 检查最老的数据包等待时间
        oldest_packet = queue[0]
        waiting_time = time.time() - oldest_packet.enqueue_time
        
        return waiting_time > self.config.starvation_threshold
    
    def get_scheduling_stats(self) -> Dict[str, Any]:
        """获取调度统计信息"""
        with self._lock:
            stats = {
                'strategy': self.config.strategy.value,
                'total_enqueued': sum(self.enqueue_counts.values()),
                'total_dequeued': sum(self.dequeue_counts.values()),
                'total_dropped': sum(self.drop_counts.values()),
                'queue_sizes': self.get_priority_queue_sizes(),
                'priority_stats': {}
            }
            
            for priority in PacketPriority:
                enqueued = self.enqueue_counts[priority]
                dequeued = self.dequeue_counts[priority]
                dropped = self.drop_counts[priority]
                avg_waiting_time = (
                    self.total_waiting_time[priority] / dequeued 
                    if dequeued > 0 else 0.0
                )
                
                stats['priority_stats'][priority.name] = {
                    'enqueued': enqueued,
                    'dequeued': dequeued,
                    'dropped': dropped,
                    'drop_rate': dropped / enqueued if enqueued > 0 else 0.0,
                    'avg_waiting_time': avg_waiting_time,
                    'queue_size': len(self.priority_queues[priority])
                }
            
            return stats


class StrictPriorityScheduler(PriorityScheduler):
    """
    严格优先级调度器
    
    总是优先处理最高优先级的数据包，
    只有高优先级队列为空时才处理低优先级队列
    """
    
    def __init__(self, config: Optional[PriorityConfig] = None):
        if config is None:
            config = PriorityConfig(strategy=SchedulingStrategy.STRICT_PRIORITY)
        super().__init__(config)
    
    def dequeue(self) -> Optional[Packet]:
        """严格按优先级顺序出队"""
        with self._lock:
            # 检查饥饿情况
            if self.config.enable_anti_starvation:
                for priority in [PacketPriority.LOW, PacketPriority.NORMAL]:
                    if self._check_starvation(priority):
                        queue = self.priority_queues[priority]
                        if queue:
                            packet_info = queue.popleft()
                            self._update_packet_metrics(packet_info)
                            return packet_info.packet
            
            # 正常的严格优先级调度
            for priority in [PacketPriority.URGENT, PacketPriority.HIGH, 
                           PacketPriority.NORMAL, PacketPriority.LOW]:
                queue = self.priority_queues[priority]
                if queue:
                    packet_info = queue.popleft()
                    self._update_packet_metrics(packet_info)
                    return packet_info.packet
            
            return None


class WeightedRoundRobinScheduler(PriorityScheduler):
    """
    加权轮转调度器
    
    按照权重比例轮流处理各优先级队列，
    避免低优先级队列饥饿问题
    """
    
    def __init__(self, config: Optional[PriorityConfig] = None):
        if config is None:
            config = PriorityConfig(strategy=SchedulingStrategy.WEIGHTED_ROUND_ROBIN)
        super().__init__(config)
        
        # WRR状态
        self.current_credits = {priority: 0 for priority in PacketPriority}
        self.round_counter = 0
    
    def dequeue(self) -> Optional[Packet]:
        """加权轮转出队"""
        with self._lock:
            # 开始新一轮时重置信用额度
            if all(credit <= 0 for credit in self.current_credits.values()):
                for priority in PacketPriority:
                    self.current_credits[priority] = self.config.weights[priority]
                self.round_counter += 1
            
            # 按优先级顺序检查，但受信用额度限制
            for priority in [PacketPriority.URGENT, PacketPriority.HIGH,
                           PacketPriority.NORMAL, PacketPriority.LOW]:
                queue = self.priority_queues[priority]
                
                if queue and self.current_credits[priority] > 0:
                    packet_info = queue.popleft()
                    self.current_credits[priority] -= 1
                    self._update_packet_metrics(packet_info)
                    return packet_info.packet
            
            return None


class DynamicPriorityScheduler(PriorityScheduler):
    """
    动态优先级调度器
    
    根据等待时间和系统负载动态调整数据包优先级，
    实现更智能的调度决策
    """
    
    def __init__(self, config: Optional[PriorityConfig] = None):
        if config is None:
            config = PriorityConfig(strategy=SchedulingStrategy.DYNAMIC_PRIORITY)
        super().__init__(config)
    
    def _calculate_dynamic_priority(self, packet_info: PacketInfo) -> float:
        """计算动态优先级"""
        base_priority = float(packet_info.packet.priority.value)
        current_time = time.time()
        waiting_time = current_time - packet_info.enqueue_time
        
        # 基于等待时间的优先级提升
        aging_boost = self.config.aging_factor * waiting_time
        
        # 基于系统负载的调整
        system_load = self.get_queue_size() / (self.config.max_queue_size * len(PacketPriority))
        load_factor = 1.0 + system_load * 0.5
        
        dynamic_priority = (base_priority + aging_boost) * load_factor
        
        return dynamic_priority
    
    def dequeue(self) -> Optional[Packet]:
        """基于动态优先级出队"""
        with self._lock:
            # 收集所有非空队列中的候选数据包
            candidates = []
            
            for priority, queue in self.priority_queues.items():
                if queue:
                    packet_info = queue[0]  # 队列头部的数据包
                    dynamic_priority = self._calculate_dynamic_priority(packet_info)
                    candidates.append((dynamic_priority, priority, packet_info))
            
            if not candidates:
                return None
            
            # 选择动态优先级最高的数据包
            candidates.sort(key=lambda x: x[0], reverse=True)
            _, selected_priority, selected_packet_info = candidates[0]
            
            # 从对应队列中移除并返回
            self.priority_queues[selected_priority].popleft()
            self._update_packet_metrics(selected_packet_info)
            
            return selected_packet_info.packet


class DeficitRoundRobinScheduler(PriorityScheduler):
    """
    缺额轮转调度器
    
    为每个队列维护信用额度，支持可变长度数据包的公平调度
    """
    
    def __init__(self, config: Optional[PriorityConfig] = None):
        if config is None:
            config = PriorityConfig(strategy=SchedulingStrategy.DEFICIT_ROUND_ROBIN)
        super().__init__(config)
        
        # DRR状态
        self.deficit_counters = {priority: 0 for priority in PacketPriority}
        self.quantum_sizes = {
            priority: self.config.quantum_size * self.config.weights[priority]
            for priority in PacketPriority
        }
    
    def dequeue(self) -> Optional[Packet]:
        """缺额轮转出队"""
        with self._lock:
            # 轮转处理各个队列
            for priority in [PacketPriority.URGENT, PacketPriority.HIGH,
                           PacketPriority.NORMAL, PacketPriority.LOW]:
                queue = self.priority_queues[priority]
                
                if not queue:
                    continue
                
                # 增加信用额度
                self.deficit_counters[priority] += self.quantum_sizes[priority]
                
                # 尽可能多地处理数据包
                while queue and self.deficit_counters[priority] > 0:
                    packet_info = queue[0]
                    packet_size = packet_info.packet.size
                    
                    if self.deficit_counters[priority] >= packet_size:
                        # 有足够信用额度，处理数据包
                        packet_info = queue.popleft()
                        self.deficit_counters[priority] -= packet_size
                        self._update_packet_metrics(packet_info)
                        return packet_info.packet
                    else:
                        # 信用额度不足，跳过此队列
                        break
                
                # 如果队列为空，重置信用额度
                if not queue:
                    self.deficit_counters[priority] = 0
            
            return None


def create_priority_scheduler(strategy: SchedulingStrategy, 
                            config: Optional[PriorityConfig] = None) -> PriorityScheduler:
    """
    工厂函数：创建指定策略的优先级调度器
    
    Args:
        strategy: 调度策略
        config: 调度配置
        
    Returns:
        PriorityScheduler: 调度器实例
    """
    if config is None:
        config = PriorityConfig(strategy=strategy)
    
    if strategy == SchedulingStrategy.STRICT_PRIORITY:
        return StrictPriorityScheduler(config)
    elif strategy == SchedulingStrategy.WEIGHTED_ROUND_ROBIN:
        return WeightedRoundRobinScheduler(config)
    elif strategy == SchedulingStrategy.DYNAMIC_PRIORITY:
        return DynamicPriorityScheduler(config)
    elif strategy == SchedulingStrategy.DEFICIT_ROUND_ROBIN:
        return DeficitRoundRobinScheduler(config)
    else:
        raise ValueError(f"不支持的调度策略: {strategy}")


class HybridPriorityScheduler(PriorityScheduler):
    """
    混合优先级调度器
    
    根据系统状态动态选择最适合的调度策略
    """
    
    def __init__(self, config: Optional[PriorityConfig] = None):
        if config is None:
            config = PriorityConfig(strategy=SchedulingStrategy.DYNAMIC_PRIORITY)
        super().__init__(config)
        
        # 内部调度器
        self.strict_scheduler = StrictPriorityScheduler(config)
        self.wrr_scheduler = WeightedRoundRobinScheduler(config)
        self.dynamic_scheduler = DynamicPriorityScheduler(config)
        
        self.current_strategy = SchedulingStrategy.STRICT_PRIORITY
        self.strategy_switch_threshold = 0.7  # 负载阈值
    
    def _select_strategy(self) -> SchedulingStrategy:
        """根据系统状态选择调度策略"""
        total_capacity = self.config.max_queue_size * len(PacketPriority)
        current_load = self.get_queue_size() / total_capacity
        
        # 检查是否有饥饿情况
        has_starvation = any(
            self._check_starvation(priority) 
            for priority in [PacketPriority.LOW, PacketPriority.NORMAL]
        )
        
        if has_starvation:
            return SchedulingStrategy.DYNAMIC_PRIORITY
        elif current_load > self.strategy_switch_threshold:
            return SchedulingStrategy.WEIGHTED_ROUND_ROBIN
        else:
            return SchedulingStrategy.STRICT_PRIORITY
    
    def dequeue(self) -> Optional[Packet]:
        """混合策略出队"""
        with self._lock:
            # 选择当前最适合的策略
            selected_strategy = self._select_strategy()
            
            if selected_strategy != self.current_strategy:
                self.current_strategy = selected_strategy
            
            # 使用选定的策略进行调度
            if self.current_strategy == SchedulingStrategy.STRICT_PRIORITY:
                return self.strict_scheduler.dequeue()
            elif self.current_strategy == SchedulingStrategy.WEIGHTED_ROUND_ROBIN:
                return self.wrr_scheduler.dequeue()
            else:
                return self.dynamic_scheduler.dequeue()
