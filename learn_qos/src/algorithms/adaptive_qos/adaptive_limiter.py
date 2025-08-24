"""
自适应限流器模块

实现多种自适应限流算法，根据服务端负载反馈动态调整发送速率
"""

import time
import threading
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum
from collections import deque
import math

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from common.base import QoSAlgorithm, Packet
from .load_monitor import LoadLevel


@dataclass
class RateAdjustment:
    """速率调整记录"""
    timestamp: float
    old_rate: float
    new_rate: float
    reason: str
    load_level: LoadLevel


class AdaptiveStrategy(Enum):
    """自适应策略枚举"""
    AIMD = "AIMD"              # 加性增长乘性减少
    PID = "PID"                # PID控制
    EXPONENTIAL_BACKOFF = "EXPONENTIAL_BACKOFF"  # 指数退避
    GRADIENT_DESCENT = "GRADIENT_DESCENT"        # 梯度下降


class AdaptiveRateLimiter(QoSAlgorithm):
    """
    自适应限流器基类
    
    根据服务端负载反馈动态调整发送速率，
    可以与令牌桶、漏桶等基础算法结合使用
    """
    
    def __init__(self, 
                 name: str,
                 initial_rate: float = 100.0,
                 min_rate: float = 1.0,
                 max_rate: float = 1000.0,
                 adjustment_history_size: int = 100):
        """
        初始化自适应限流器
        
        Args:
            name: 限流器名称
            initial_rate: 初始发送速率 (requests/second)
            min_rate: 最小速率
            max_rate: 最大速率
            adjustment_history_size: 调整历史记录大小
        """
        super().__init__(name)
        
        self.initial_rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        
        # 当前状态
        self.current_rate = initial_rate
        self.last_adjustment_time = time.time()
        self.last_load_level = LoadLevel.GREEN
        
        # 历史记录
        self.adjustment_history = deque(maxlen=adjustment_history_size)
        
        # 统计信息
        self.total_adjustments = 0
        self.total_increases = 0
        self.total_decreases = 0
        
        # 线程安全
        self._lock = threading.RLock()
    
    @abstractmethod
    def calculate_new_rate(self, 
                          current_rate: float, 
                          load_info: Dict[str, Any]) -> float:
        """
        根据负载信息计算新的发送速率
        
        Args:
            current_rate: 当前速率
            load_info: 负载信息
            
        Returns:
            float: 新的发送速率
        """
        pass
    
    def adjust_rate(self, load_info: Dict[str, Any]) -> bool:
        """
        调整发送速率
        
        Args:
            load_info: 服务端负载信息
            
        Returns:
            bool: 是否进行了调整
        """
        with self._lock:
            old_rate = self.current_rate
            new_rate = self.calculate_new_rate(old_rate, load_info)
            
            # 限制在合理范围内
            new_rate = max(self.min_rate, min(self.max_rate, new_rate))
            
            # 检查是否需要调整
            rate_change_ratio = abs(new_rate - old_rate) / old_rate
            if rate_change_ratio < 0.01:  # 变化小于1%则不调整
                return False
            
            # 执行调整
            self.current_rate = new_rate
            current_time = time.time()
            
            # 记录调整
            load_level = LoadLevel(load_info.get('load_level', 'GREEN'))
            adjustment = RateAdjustment(
                timestamp=current_time,
                old_rate=old_rate,
                new_rate=new_rate,
                reason=f"负载等级: {load_level.value}",
                load_level=load_level
            )
            
            self.adjustment_history.append(adjustment)
            self.last_adjustment_time = current_time
            self.last_load_level = load_level
            self.total_adjustments += 1
            
            if new_rate > old_rate:
                self.total_increases += 1
            else:
                self.total_decreases += 1
            
            return True
    
    def get_current_rate(self) -> float:
        """获取当前发送速率"""
        with self._lock:
            return self.current_rate
    
    def reset_rate(self):
        """重置速率到初始值"""
        with self._lock:
            self.current_rate = self.initial_rate
            self.adjustment_history.clear()
            self.total_adjustments = 0
            self.total_increases = 0
            self.total_decreases = 0
    
    def get_adjustment_stats(self) -> Dict[str, Any]:
        """获取调整统计信息"""
        with self._lock:
            recent_adjustments = list(self.adjustment_history)[-10:]
            
            return {
                'current_rate': self.current_rate,
                'initial_rate': self.initial_rate,
                'rate_change_ratio': self.current_rate / self.initial_rate,
                'total_adjustments': self.total_adjustments,
                'total_increases': self.total_increases,
                'total_decreases': self.total_decreases,
                'last_adjustment_time': self.last_adjustment_time,
                'last_load_level': self.last_load_level.value,
                'recent_adjustments': [
                    {
                        'timestamp': adj.timestamp,
                        'old_rate': adj.old_rate,
                        'new_rate': adj.new_rate,
                        'reason': adj.reason
                    }
                    for adj in recent_adjustments
                ]
            }
    
    def enqueue(self, packet: Packet) -> bool:
        """基类方法实现 - 简单通过"""
        return True
    
    def dequeue(self) -> Optional[Packet]:
        """基类方法实现"""
        return None
    
    def is_empty(self) -> bool:
        """基类方法实现"""
        return True
    
    def get_queue_size(self) -> int:
        """基类方法实现"""
        return 0


class AIMDRateLimiter(AdaptiveRateLimiter):
    """
    AIMD (Additive Increase, Multiplicative Decrease) 自适应限流器
    
    特点：
    - 负载正常时线性增加速率
    - 负载过高时指数减少速率
    - 类似TCP拥塞控制算法
    """
    
    def __init__(self, 
                 initial_rate: float = 100.0,
                 increase_step: float = 5.0,
                 decrease_factor: float = 0.7,
                 **kwargs):
        """
        初始化AIMD限流器
        
        Args:
            initial_rate: 初始速率
            increase_step: 每次增加的步长
            decrease_factor: 减少时的乘数因子
        """
        super().__init__("AIMD", initial_rate, **kwargs)
        self.increase_step = increase_step
        self.decrease_factor = decrease_factor
    
    def calculate_new_rate(self, current_rate: float, load_info: Dict[str, Any]) -> float:
        """实现AIMD算法"""
        load_level = LoadLevel(load_info.get('load_level', 'GREEN'))
        
        if load_level == LoadLevel.GREEN:
            # 加性增长
            return current_rate + self.increase_step
        elif load_level == LoadLevel.YELLOW:
            # 维持不变
            return current_rate
        elif load_level in [LoadLevel.ORANGE, LoadLevel.RED]:
            # 乘性减少
            return current_rate * self.decrease_factor
        else:  # BLACK
            # 急剧减少
            return current_rate * (self.decrease_factor ** 2)


class PIDRateLimiter(AdaptiveRateLimiter):
    """
    PID控制器自适应限流器
    
    特点：
    - 比例项：响应当前误差
    - 积分项：消除稳态误差
    - 微分项：预测未来趋势
    """
    
    def __init__(self, 
                 initial_rate: float = 100.0,
                 target_load_score: float = 0.6,
                 kp: float = 100.0,
                 ki: float = 10.0,
                 kd: float = 50.0,
                 **kwargs):
        """
        初始化PID限流器
        
        Args:
            initial_rate: 初始速率
            target_load_score: 目标负载评分
            kp: 比例系数
            ki: 积分系数
            kd: 微分系数
        """
        super().__init__("PID", initial_rate, **kwargs)
        self.target_load_score = target_load_score
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
        # PID状态
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = time.time()
    
    def calculate_new_rate(self, current_rate: float, load_info: Dict[str, Any]) -> float:
        """实现PID控制算法"""
        current_time = time.time()
        dt = current_time - self.last_time
        
        if dt <= 0:
            return current_rate
        
        # 计算误差
        current_load_score = load_info.get('load_score', 0.0)
        error = self.target_load_score - current_load_score
        
        # 积分项
        self.integral += error * dt
        
        # 微分项
        derivative = (error - self.last_error) / dt if dt > 0 else 0.0
        
        # PID输出
        output = (
            self.kp * error +
            self.ki * self.integral +
            self.kd * derivative
        )
        
        # 更新状态
        self.last_error = error
        self.last_time = current_time
        
        # 计算新速率
        new_rate = current_rate + output
        
        return new_rate


class ExponentialBackoffRateLimiter(AdaptiveRateLimiter):
    """
    指数退避自适应限流器
    
    特点：
    - 连续过载时指数减少速率
    - 负载恢复时逐渐恢复速率
    - 简单有效的保护机制
    """
    
    def __init__(self, 
                 initial_rate: float = 100.0,
                 backoff_factor: float = 2.0,
                 recovery_factor: float = 1.1,
                 max_backoff_level: int = 6,
                 **kwargs):
        """
        初始化指数退避限流器
        
        Args:
            initial_rate: 初始速率
            backoff_factor: 退避因子
            recovery_factor: 恢复因子
            max_backoff_level: 最大退避级别
        """
        super().__init__("ExponentialBackoff", initial_rate, **kwargs)
        self.backoff_factor = backoff_factor
        self.recovery_factor = recovery_factor
        self.max_backoff_level = max_backoff_level
        
        # 退避状态
        self.consecutive_overloads = 0
        self.consecutive_normals = 0
    
    def calculate_new_rate(self, current_rate: float, load_info: Dict[str, Any]) -> float:
        """实现指数退避算法"""
        load_level = LoadLevel(load_info.get('load_level', 'GREEN'))
        
        if load_level in [LoadLevel.ORANGE, LoadLevel.RED, LoadLevel.BLACK]:
            # 过载情况
            self.consecutive_overloads += 1
            self.consecutive_normals = 0
            
            # 计算退避级别
            backoff_level = min(self.consecutive_overloads, self.max_backoff_level)
            backoff_multiplier = self.backoff_factor ** backoff_level
            
            return current_rate / backoff_multiplier
        
        else:
            # 正常情况
            self.consecutive_normals += 1
            self.consecutive_overloads = 0
            
            if self.consecutive_normals >= 3:  # 连续3次正常才开始恢复
                return min(current_rate * self.recovery_factor, self.max_rate)
            else:
                return current_rate


class GradientDescentRateLimiter(AdaptiveRateLimiter):
    """
    梯度下降自适应限流器
    
    特点：
    - 基于负载评分梯度调整速率
    - 学习率自适应调整
    - 平滑的速率变化
    """
    
    def __init__(self, 
                 initial_rate: float = 100.0,
                 learning_rate: float = 0.1,
                 target_load_score: float = 0.6,
                 momentum: float = 0.9,
                 **kwargs):
        """
        初始化梯度下降限流器
        
        Args:
            initial_rate: 初始速率
            learning_rate: 学习率
            target_load_score: 目标负载评分
            momentum: 动量参数
        """
        super().__init__("GradientDescent", initial_rate, **kwargs)
        self.learning_rate = learning_rate
        self.target_load_score = target_load_score
        self.momentum = momentum
        
        # 梯度状态
        self.velocity = 0.0
        self.last_load_score = 0.0
        self.last_rate = initial_rate
    
    def calculate_new_rate(self, current_rate: float, load_info: Dict[str, Any]) -> float:
        """实现梯度下降算法"""
        current_load_score = load_info.get('load_score', 0.0)
        
        # 计算梯度（负载评分对速率的导数）
        if self.last_rate != current_rate and current_load_score != self.last_load_score:
            gradient = (current_load_score - self.last_load_score) / (current_rate - self.last_rate)
        else:
            # 使用负载评分与目标的差异作为梯度
            gradient = current_load_score - self.target_load_score
        
        # 更新速度（带动量）
        self.velocity = self.momentum * self.velocity - self.learning_rate * gradient
        
        # 更新速率
        new_rate = current_rate + self.velocity
        
        # 更新历史
        self.last_load_score = current_load_score
        self.last_rate = current_rate
        
        return new_rate


class HybridRateLimiter(AdaptiveRateLimiter):
    """
    混合自适应限流器
    
    根据不同情况选择不同的调整策略
    """
    
    def __init__(self, 
                 initial_rate: float = 100.0,
                 **kwargs):
        super().__init__("Hybrid", initial_rate, **kwargs)
        
        # 内部限流器
        self.aimd_limiter = AIMDRateLimiter(initial_rate, **kwargs)
        self.pid_limiter = PIDRateLimiter(initial_rate, **kwargs)
        self.backoff_limiter = ExponentialBackoffRateLimiter(initial_rate, **kwargs)
        
        self.current_strategy = AdaptiveStrategy.AIMD
    
    def calculate_new_rate(self, current_rate: float, load_info: Dict[str, Any]) -> float:
        """根据负载情况选择策略"""
        load_level = LoadLevel(load_info.get('load_level', 'GREEN'))
        load_score = load_info.get('load_score', 0.0)
        trend = load_info.get('trend', 'STABLE')
        
        # 选择策略
        if load_level == LoadLevel.BLACK or (load_level == LoadLevel.RED and trend == 'INCREASING'):
            # 危急情况，使用指数退避
            self.current_strategy = AdaptiveStrategy.EXPONENTIAL_BACKOFF
            return self.backoff_limiter.calculate_new_rate(current_rate, load_info)
        elif load_level in [LoadLevel.GREEN, LoadLevel.YELLOW] and trend == 'STABLE':
            # 稳定情况，使用PID控制
            self.current_strategy = AdaptiveStrategy.PID
            return self.pid_limiter.calculate_new_rate(current_rate, load_info)
        else:
            # 其他情况，使用AIMD
            self.current_strategy = AdaptiveStrategy.AIMD
            return self.aimd_limiter.calculate_new_rate(current_rate, load_info)


def create_adaptive_limiter(strategy: AdaptiveStrategy, **kwargs) -> AdaptiveRateLimiter:
    """
    工厂函数：创建指定类型的自适应限流器
    
    Args:
        strategy: 限流策略
        **kwargs: 初始化参数
        
    Returns:
        AdaptiveRateLimiter: 限流器实例
    """
    if strategy == AdaptiveStrategy.AIMD:
        return AIMDRateLimiter(**kwargs)
    elif strategy == AdaptiveStrategy.PID:
        return PIDRateLimiter(**kwargs)
    elif strategy == AdaptiveStrategy.EXPONENTIAL_BACKOFF:
        return ExponentialBackoffRateLimiter(**kwargs)
    elif strategy == AdaptiveStrategy.GRADIENT_DESCENT:
        return GradientDescentRateLimiter(**kwargs)
    else:
        return HybridRateLimiter(**kwargs)

