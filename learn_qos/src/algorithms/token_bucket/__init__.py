"""
令牌桶算法模块

实现了经典的令牌桶算法，用于流量整形和速率限制。
支持突发流量处理和平均速率控制。
"""

from .token_bucket import TokenBucket, TokenBucketConfig

__all__ = ['TokenBucket', 'TokenBucketConfig']
