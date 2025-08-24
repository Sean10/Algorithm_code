"""
优先级调度算法模块

实现多种优先级调度策略，包括：
- 严格优先级调度
- 加权轮转调度
- 动态优先级调度
- 防饥饿机制
"""

from .priority_scheduler import (
    PriorityScheduler, StrictPriorityScheduler, 
    WeightedRoundRobinScheduler, DynamicPriorityScheduler,
    DeficitRoundRobinScheduler, HybridPriorityScheduler,
    SchedulingStrategy, PriorityConfig, create_priority_scheduler
)

__all__ = [
    'PriorityScheduler', 'StrictPriorityScheduler',
    'WeightedRoundRobinScheduler', 'DynamicPriorityScheduler',
    'DeficitRoundRobinScheduler', 'HybridPriorityScheduler',
    'SchedulingStrategy', 'PriorityConfig', 'create_priority_scheduler'
]
