"""
漏桶算法实现

实现经典的漏桶算法，提供固定速率的平滑输出。
"""

import time
import threading
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from collections import deque
import heapq

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from common.base import QoSAlgorithm, Packet, QoSMetrics


@dataclass
class LeakyBucketConfig:
    """漏桶算法配置"""
    leak_rate: float  # 漏出速率 (bytes/second)
    bucket_size: int  # 桶容量 (bytes)
    output_interval: float = 0.01  # 输出检查间隔 (seconds)
    
    def __post_init__(self):
        # 参数验证
        if self.leak_rate <= 0:
            raise ValueError("漏出速率必须大于0")
        if self.bucket_size <= 0:
            raise ValueError("桶容量必须大于0")
        if self.output_interval <= 0:
            raise ValueError("输出间隔必须大于0")


class LeakyBucket(QoSAlgorithm):
    """
    漏桶算法实现
    
    特性：
    - 固定速率输出，平滑流量
    - 消除输入突发
    - 可预测的延迟特性
    - 线程安全
    """
    
    def __init__(self, config: LeakyBucketConfig):
        super().__init__("LeakyBucket")
        self.config = config
        
        # 算法状态
        self._current_volume = 0  # 当前桶中的数据量 (bytes)
        self._packet_queue = deque()  # 数据包队列
        self._last_leak_time = time.time()
        
        # 输出调度
        self._output_scheduler = None
        self._stop_scheduler = threading.Event()
        
        # 统计信息
        self._total_input_bytes = 0
        self._total_output_bytes = 0
        self._packets_dropped = 0
        self._packets_queued = 0
        self._packets_output = 0
        
        # 线程安全锁
        self._lock = threading.RLock()
    
    def _leak_data(self) -> None:
        """执行漏出操作，更新桶状态"""
        current_time = time.time()
        time_elapsed = current_time - self._last_leak_time
        
        if time_elapsed > 0:
            # 计算应该漏出的字节数
            bytes_to_leak = self.config.leak_rate * time_elapsed
            
            # 实际漏出的字节数不能超过桶中现有数据
            actual_leaked = min(bytes_to_leak, self._current_volume)
            
            self._current_volume -= actual_leaked
            self._total_output_bytes += actual_leaked
            
            self._last_leak_time = current_time
    
    def _can_accept_packet(self, packet: Packet) -> bool:
        """检查是否能接受新数据包"""
        return self._current_volume + packet.size <= self.config.bucket_size
    
    def _schedule_output(self) -> None:
        """输出调度器，定期处理数据包输出"""
        while not self._stop_scheduler.is_set():
            try:
                with self._lock:
                    self._leak_data()
                    self._process_output_queue()
                
                # 等待下一个调度周期
                self._stop_scheduler.wait(self.config.output_interval)
                
            except Exception as e:
                # 记录错误但继续运行
                print(f"输出调度器错误: {e}")
    
    def _process_output_queue(self) -> None:
        """处理输出队列，按漏出速率输出数据包"""
        current_time = time.time()
        
        # 计算从上次处理到现在应该输出的字节数
        time_since_last = current_time - getattr(self, '_last_output_time', current_time)
        bytes_can_output = self.config.leak_rate * time_since_last
        
        bytes_output = 0
        packets_to_output = []
        
        # 收集可以输出的数据包
        while self._packet_queue and bytes_output < bytes_can_output:
            packet = self._packet_queue[0]
            if bytes_output + packet.size <= bytes_can_output:
                packet = self._packet_queue.popleft()
                packet.departure_time = current_time
                packets_to_output.append(packet)
                bytes_output += packet.size
                self._packets_output += 1
                
                # 更新指标
                self.metrics.update_with_packet(packet)
            else:
                break
        
        # 更新桶状态
        self._current_volume -= bytes_output
        self._last_output_time = current_time
    
    def enqueue(self, packet: Packet) -> bool:
        """
        将数据包加入漏桶
        
        Args:
            packet: 要处理的数据包
            
        Returns:
            bool: True表示成功入队，False表示被丢弃
        """
        with self._lock:
            # 先执行漏出操作
            self._leak_data()
            
            # 检查是否能接受新数据包
            if self._can_accept_packet(packet):
                # 数据包入队
                self._packet_queue.append(packet)
                self._current_volume += packet.size
                self._total_input_bytes += packet.size
                self._packets_queued += 1
                
                # 更新基类指标（入队时不设置departure_time，因为输出由调度器控制）
                self.metrics.total_packets += 1
                
                return True
            else:
                # 桶满，丢弃数据包
                self._packets_dropped += 1
                self.metrics.update_with_packet(packet, dropped=True)
                return False
    
    def dequeue(self) -> Optional[Packet]:
        """
        从输出队列中取出数据包
        
        注意：在漏桶算法中，数据包的输出由内部调度器控制
        此方法主要用于测试和兼容性
        
        Returns:
            Optional[Packet]: 已处理完成的数据包，None表示无可用数据包
        """
        with self._lock:
            self._leak_data()
            self._process_output_queue()
            
            # 这里我们返回None，因为输出由调度器控制
            # 实际应用中应该通过回调或其他机制获取输出数据包
            return None
    
    def is_empty(self) -> bool:
        """检查桶是否为空"""
        with self._lock:
            return len(self._packet_queue) == 0
    
    def get_queue_size(self) -> int:
        """获取当前队列长度"""
        with self._lock:
            return len(self._packet_queue)
    
    def get_current_volume(self) -> int:
        """获取当前桶中的数据量 (bytes)"""
        with self._lock:
            self._leak_data()
            return self._current_volume
    
    def get_fill_ratio(self) -> float:
        """获取桶填充比例 (0.0-1.0)"""
        return self.get_current_volume() / self.config.bucket_size
    
    def get_max_delay(self) -> float:
        """获取最大可能延迟 (seconds)"""
        return self.config.bucket_size / self.config.leak_rate
    
    def get_current_delay(self) -> float:
        """获取当前预期延迟 (seconds)"""
        return self.get_current_volume() / self.config.leak_rate
    
    def get_output_rate(self) -> float:
        """获取实际输出速率 (bytes/second)"""
        with self._lock:
            elapsed_time = time.time() - (self._last_leak_time - 
                                        self._total_output_bytes / self.config.leak_rate)
            if elapsed_time > 0:
                return self._total_output_bytes / elapsed_time
            return 0.0
    
    def start(self):
        """启动漏桶算法（启动输出调度器）"""
        if self._output_scheduler is None or not self._output_scheduler.is_alive():
            self._running = True
            self._stop_scheduler.clear()
            self._output_scheduler = threading.Thread(
                target=self._schedule_output,
                daemon=True
            )
            self._output_scheduler.start()
    
    def stop(self):
        """停止漏桶算法"""
        self._running = False
        self._stop_scheduler.set()
        if self._output_scheduler and self._output_scheduler.is_alive():
            self._output_scheduler.join(timeout=1.0)
    
    def reset_metrics(self):
        """重置性能指标和统计信息"""
        with self._lock:
            super().reset_metrics()
            self._total_input_bytes = 0
            self._total_output_bytes = 0
            self._packets_dropped = 0
            self._packets_queued = 0
            self._packets_output = 0
            # 重置时间戳，避免计算错误
            self._last_leak_time = time.time()
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取详细的性能指标"""
        base_metrics = super().get_metrics()
        
        with self._lock:
            base_metrics.update({
                'config': {
                    'leak_rate': self.config.leak_rate,
                    'bucket_size': self.config.bucket_size,
                    'output_interval': self.config.output_interval
                },
                'current_volume': self.get_current_volume(),
                'fill_ratio': self.get_fill_ratio(),
                'max_delay': self.get_max_delay(),
                'current_delay': self.get_current_delay(),
                'output_rate': self.get_output_rate(),
                'total_input_bytes': self._total_input_bytes,
                'total_output_bytes': self._total_output_bytes,
                'packets_queued': self._packets_queued,
                'packets_output': self._packets_output,
                'packets_dropped': self._packets_dropped,
                'queue_size': self.get_queue_size(),
                'utilization': self._total_output_bytes / (self.config.leak_rate * 
                    (time.time() - (self._last_leak_time - self._total_output_bytes / self.config.leak_rate)))
                    if self._total_output_bytes > 0 else 0.0
            })
        
        return base_metrics
    
    def __str__(self) -> str:
        return (f"LeakyBucket(rate={self.config.leak_rate:.1f} bytes/s, "
               f"size={self.config.bucket_size}, "
               f"current={self.get_current_volume()})")
    
    def __repr__(self) -> str:
        return (f"LeakyBucket(leak_rate={self.config.leak_rate}, "
               f"bucket_size={self.config.bucket_size})")
    
    def __del__(self):
        """析构函数，确保线程正确停止"""
        try:
            self.stop()
        except:
            pass
