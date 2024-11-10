import time
import random
from collections import OrderedDict
from typing import Dict, Any

class StorageLayer:
    def __init__(self, name: str, access_time_us: float):
        """
        access_time_us: 访问延迟（微秒）
        """
        self.name = name
        self.access_time = access_time_us
        self.access_count = 0
    
    def access(self):
        self.access_count += 1
        if self.access_count % 10 == 0:  # 提高模拟频率
            time.sleep(self.access_time / 1_000_000)  # 转换为秒

class LRUCache:
    def __init__(self, capacity: int, next_layer: StorageLayer):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.next_layer = next_layer
        self.hits = 0
        self.total_requests = 0
        self.total_latency_us = 0  # 使用微秒计数
    
    def get(self, key: str) -> Any:
        start_time = time.perf_counter()  # 使用更精确的计时器
        self.total_requests += 1
        
        if key in self.cache:
            self.hits += 1
            self.cache.move_to_end(key)
            value = self.cache[key]
        else:
            # 模拟从下一层读取
            self.next_layer.access()
            value = f"data_{key}"
            self.put(key, value)
            
        self.total_latency_us += (time.perf_counter() - start_time) * 1_000_000  # 转换为微秒
        return value
    
    def put(self, key: str, value: Any):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
    
    @property
    def hit_rate(self) -> float:
        return self.hits / self.total_requests if self.total_requests > 0 else 0
    
    @property
    def avg_latency(self) -> float:
        """返回平均延迟（微秒）"""
        return self.total_latency_us / self.total_requests if self.total_requests > 0 else 0

class WorkloadGenerator:
    def __init__(self, total_data_size: int, hot_data_size: int, hot_data_ratio: float):
        """
        total_data_size: 总数据量
        hot_data_size: 热点数据大小
        hot_data_ratio: 热点数据访问比例 (0-1)
        """
        self.total_data_size = total_data_size
        self.hot_data_size = hot_data_size
        self.hot_data_ratio = hot_data_ratio
        
    def generate_request(self) -> str:
        if random.random() < self.hot_data_ratio:
            # 访问热点数据
            return str(random.randint(0, self.hot_data_size - 1))
        else:
            # 访问冷数据
            return str(random.randint(self.hot_data_size, self.total_data_size - 1)) 