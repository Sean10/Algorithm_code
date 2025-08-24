"""
令牌桶算法实现

实现经典的令牌桶算法，支持流量整形和速率限制。
"""

import time
import threading
from typing import Optional, Dict, Any
from dataclasses import dataclass
from collections import deque

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from common.base import QoSAlgorithm, Packet, QoSMetrics


@dataclass
class TokenBucketConfig:
    """令牌桶算法配置"""
    token_rate: float  # 令牌生成速率 (tokens/second)
    bucket_size: int   # 桶容量 (tokens)
    initial_tokens: Optional[int] = None  # 初始令牌数，None表示满桶
    token_size: int = 1  # 每个令牌代表的字节数，1表示每字节一个令牌
    
    def __post_init__(self):
        if self.initial_tokens is None:
            self.initial_tokens = self.bucket_size
        
        # 参数验证
        if self.token_rate <= 0:
            raise ValueError("令牌生成速率必须大于0")
        if self.bucket_size <= 0:
            raise ValueError("桶容量必须大于0")
        if self.initial_tokens < 0 or self.initial_tokens > self.bucket_size:
            raise ValueError("初始令牌数必须在0到桶容量之间")
        if self.token_size <= 0:
            raise ValueError("令牌大小必须大于0")


class TokenBucket(QoSAlgorithm):
    """
    令牌桶算法实现
    
    特性：
    - 支持突发流量处理
    - 平均速率控制
    - 可配置令牌生成速率和桶容量
    - 线程安全
    """
    
    def __init__(self, config: TokenBucketConfig):
        super().__init__("TokenBucket")
        self.config = config
        
        # 算法状态
        self._current_tokens = float(config.initial_tokens)
        self._last_update_time = time.time()
        self._packet_queue = deque()
        
        # 统计信息
        self._total_tokens_consumed = 0
        self._total_tokens_generated = 0
        self._packets_passed = 0
        self._packets_dropped = 0
        
        # 线程安全锁
        self._lock = threading.RLock()
    
    def _update_tokens(self) -> None:
        """更新令牌数量"""
        current_time = time.time()
        time_elapsed = current_time - self._last_update_time
        
        if time_elapsed > 0:
            # 计算新生成的令牌数
            tokens_to_add = self.config.token_rate * time_elapsed
            self._total_tokens_generated += tokens_to_add
            
            # 更新令牌数，不能超过桶容量
            self._current_tokens = min(
                self.config.bucket_size,
                self._current_tokens + tokens_to_add
            )
            
            self._last_update_time = current_time
    
    def _consume_tokens(self, num_tokens: int) -> bool:
        """
        消耗令牌
        
        Args:
            num_tokens: 需要消耗的令牌数
            
        Returns:
            bool: True表示令牌充足并已消耗，False表示令牌不足
        """
        if self._current_tokens >= num_tokens:
            self._current_tokens -= num_tokens
            self._total_tokens_consumed += num_tokens
            return True
        return False
    
    def _calculate_required_tokens(self, packet: Packet) -> int:
        """计算数据包需要的令牌数"""
        return max(1, packet.size // self.config.token_size)
    
    def enqueue(self, packet: Packet) -> bool:
        """
        将数据包加入队列处理
        
        Args:
            packet: 要处理的数据包
            
        Returns:
            bool: True表示成功处理，False表示被丢弃
        """
        with self._lock:
            # 更新令牌
            self._update_tokens()
            
            # 计算所需令牌数
            required_tokens = self._calculate_required_tokens(packet)
            
            # 尝试消耗令牌
            if self._consume_tokens(required_tokens):
                # 令牌充足，允许传输
                packet.departure_time = time.time()
                self._packet_queue.append(packet)
                self._packets_passed += 1
                
                # 更新指标
                self.metrics.update_with_packet(packet)
                return True
            else:
                # 令牌不足，丢弃数据包
                self._packets_dropped += 1
                self.metrics.update_with_packet(packet, dropped=True)
                return False
    
    def dequeue(self) -> Optional[Packet]:
        """
        从队列中取出数据包
        
        Returns:
            Optional[Packet]: 下一个数据包，None表示队列为空
        """
        with self._lock:
            if self._packet_queue:
                return self._packet_queue.popleft()
            return None
    
    def is_empty(self) -> bool:
        """检查队列是否为空"""
        with self._lock:
            return len(self._packet_queue) == 0
    
    def get_queue_size(self) -> int:
        """获取当前队列长度"""
        with self._lock:
            return len(self._packet_queue)
    
    def get_current_tokens(self) -> float:
        """获取当前令牌数"""
        with self._lock:
            self._update_tokens()
            return self._current_tokens
    
    def get_token_fill_ratio(self) -> float:
        """获取令牌桶填充比例 (0.0-1.0)"""
        return self.get_current_tokens() / self.config.bucket_size
    
    def get_average_rate(self) -> float:
        """获取实际平均处理速率 (tokens/second)"""
        with self._lock:
            elapsed_time = time.time() - (self._last_update_time - 
                                        self._total_tokens_generated / self.config.token_rate)
            if elapsed_time > 0:
                return self._total_tokens_consumed / elapsed_time
            return 0.0
    
    def can_handle_burst(self, burst_size: int) -> bool:
        """
        检查是否能处理指定大小的突发流量
        
        Args:
            burst_size: 突发流量大小（字节）
            
        Returns:
            bool: True表示能处理，False表示不能
        """
        required_tokens = max(1, burst_size // self.config.token_size)
        return self.get_current_tokens() >= required_tokens
    
    def reset_metrics(self):
        """重置性能指标和统计信息"""
        with self._lock:
            super().reset_metrics()
            self._total_tokens_consumed = 0
            self._total_tokens_generated = 0
            self._packets_passed = 0
            self._packets_dropped = 0
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取详细的性能指标"""
        base_metrics = super().get_metrics()
        
        with self._lock:
            base_metrics.update({
                'config': {
                    'token_rate': self.config.token_rate,
                    'bucket_size': self.config.bucket_size,
                    'token_size': self.config.token_size
                },
                'current_tokens': self.get_current_tokens(),
                'token_fill_ratio': self.get_token_fill_ratio(),
                'average_processing_rate': self.get_average_rate(),
                'total_tokens_generated': self._total_tokens_generated,
                'total_tokens_consumed': self._total_tokens_consumed,
                'packets_passed': self._packets_passed,
                'packets_dropped': self._packets_dropped,
                'queue_size': self.get_queue_size()
            })
        
        return base_metrics
    
    def __str__(self) -> str:
        return (f"TokenBucket(rate={self.config.token_rate:.1f} tokens/s, "
               f"size={self.config.bucket_size}, "
               f"current={self.get_current_tokens():.1f})")
    
    def __repr__(self) -> str:
        return (f"TokenBucket(token_rate={self.config.token_rate}, "
               f"bucket_size={self.config.bucket_size}, "
               f"token_size={self.config.token_size})")
