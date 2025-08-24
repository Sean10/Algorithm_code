"""
QoS算法基础类和工具函数
"""

import time
import threading
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class PacketPriority(Enum):
    """数据包优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Packet:
    """数据包类"""
    id: int
    size: int  # 数据包大小（字节）
    priority: PacketPriority = PacketPriority.NORMAL
    arrival_time: float = 0.0
    departure_time: Optional[float] = None
    
    def __post_init__(self):
        if self.arrival_time == 0.0:
            self.arrival_time = time.time()
    
    @property
    def delay(self) -> Optional[float]:
        """计算数据包延迟"""
        if self.departure_time is not None:
            return self.departure_time - self.arrival_time
        return None


@dataclass
class QoSMetrics:
    """QoS性能指标"""
    total_packets: int = 0
    dropped_packets: int = 0
    total_delay: float = 0.0
    max_delay: float = 0.0
    min_delay: float = float('inf')
    jitter_sum: float = 0.0
    last_delay: Optional[float] = None
    
    @property
    def drop_rate(self) -> float:
        """丢包率"""
        if self.total_packets == 0:
            return 0.0
        return self.dropped_packets / self.total_packets
    
    @property
    def average_delay(self) -> float:
        """平均延迟"""
        delivered_packets = self.total_packets - self.dropped_packets
        if delivered_packets == 0:
            return 0.0
        return self.total_delay / delivered_packets
    
    @property
    def average_jitter(self) -> float:
        """平均抖动"""
        delivered_packets = self.total_packets - self.dropped_packets
        if delivered_packets <= 1:
            return 0.0
        return self.jitter_sum / (delivered_packets - 1)
    
    def update_with_packet(self, packet: Packet, dropped: bool = False):
        """用数据包信息更新指标"""
        self.total_packets += 1
        
        if dropped:
            self.dropped_packets += 1
            return
        
        if packet.delay is not None:
            delay = packet.delay
            self.total_delay += delay
            self.max_delay = max(self.max_delay, delay)
            self.min_delay = min(self.min_delay, delay)
            
            # 计算抖动
            if self.last_delay is not None:
                jitter = abs(delay - self.last_delay)
                self.jitter_sum += jitter
            
            self.last_delay = delay


class QoSAlgorithm(ABC):
    """QoS算法基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.metrics = QoSMetrics()
        self._lock = threading.RLock()
        self._running = False
    
    @abstractmethod
    def enqueue(self, packet: Packet) -> bool:
        """
        将数据包加入队列
        
        Args:
            packet: 要处理的数据包
            
        Returns:
            bool: True表示成功入队，False表示被丢弃
        """
        pass
    
    @abstractmethod
    def dequeue(self) -> Optional[Packet]:
        """
        从队列中取出数据包
        
        Returns:
            Optional[Packet]: 下一个要处理的数据包，None表示队列为空
        """
        pass
    
    @abstractmethod
    def is_empty(self) -> bool:
        """检查队列是否为空"""
        pass
    
    @abstractmethod
    def get_queue_size(self) -> int:
        """获取当前队列长度"""
        pass
    
    def start(self):
        """启动算法（如果需要后台处理）"""
        self._running = True
    
    def stop(self):
        """停止算法"""
        self._running = False
    
    def reset_metrics(self):
        """重置性能指标"""
        with self._lock:
            self.metrics = QoSMetrics()
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        with self._lock:
            return {
                'algorithm': self.name,
                'total_packets': self.metrics.total_packets,
                'dropped_packets': self.metrics.dropped_packets,
                'drop_rate': self.metrics.drop_rate,
                'average_delay': self.metrics.average_delay,
                'max_delay': self.metrics.max_delay,
                'min_delay': self.metrics.min_delay if self.metrics.min_delay != float('inf') else 0.0,
                'average_jitter': self.metrics.average_jitter,
            }


class TrafficGenerator:
    """流量生成器"""
    
    def __init__(self):
        self.packet_id = 0
    
    def generate_packet(self, size: int, priority: PacketPriority = PacketPriority.NORMAL) -> Packet:
        """生成单个数据包"""
        self.packet_id += 1
        return Packet(
            id=self.packet_id,
            size=size,
            priority=priority,
            arrival_time=time.time()
        )
    
    def generate_burst_traffic(
        self,
        num_packets: int,
        packet_size: int,
        priority: PacketPriority = PacketPriority.NORMAL
    ) -> List[Packet]:
        """生成突发流量"""
        return [
            self.generate_packet(packet_size, priority)
            for _ in range(num_packets)
        ]


def current_time_ms() -> int:
    """获取当前时间（毫秒）"""
    return int(time.time() * 1000)


def bytes_to_bits(bytes_val: int) -> int:
    """字节转比特"""
    return bytes_val * 8


def bits_to_bytes(bits_val: int) -> int:
    """比特转字节"""
    return bits_val // 8
