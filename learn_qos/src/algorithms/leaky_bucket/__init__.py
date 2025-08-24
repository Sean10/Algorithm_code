"""
漏桶算法模块

实现了经典的漏桶算法，用于流量整形和平滑输出。
通过固定的漏出速率消除流量突发，提供稳定的输出速率。
"""

from .leaky_bucket import LeakyBucket, LeakyBucketConfig

__all__ = ['LeakyBucket', 'LeakyBucketConfig']
