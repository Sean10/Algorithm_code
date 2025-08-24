"""
服务端负载监控模块

提供系统负载监控、评估和分级功能
"""

import time
import psutil
import threading
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque
import statistics

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class LoadLevel(Enum):
    """负载等级枚举"""
    GREEN = "GREEN"      # 负载正常，可以接受更多请求
    YELLOW = "YELLOW"    # 负载适中，维持当前速率
    ORANGE = "ORANGE"    # 负载偏高，建议减少请求
    RED = "RED"          # 负载过载，需要大幅限流
    BLACK = "BLACK"      # 系统濒临崩溃，停止发送请求


@dataclass
class LoadMetrics:
    """负载指标数据类"""
    timestamp: float
    cpu_usage: float        # CPU使用率 (0.0-1.0)
    memory_usage: float     # 内存使用率 (0.0-1.0)
    queue_depth: int        # 当前队列长度
    avg_response_time: float # 平均响应时间(ms)
    requests_per_second: float # 每秒请求数
    error_rate: float       # 错误率 (0.0-1.0)
    active_connections: int # 活跃连接数
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LoadMetrics':
        """从字典创建实例"""
        return cls(**data)


class LoadMonitor:
    """
    系统负载监控器
    
    功能：
    - 实时监控系统资源使用情况
    - 计算综合负载评分
    - 确定负载等级
    - 提供负载趋势分析
    """
    
    def __init__(self, 
                 sample_interval: float = 1.0,
                 history_size: int = 60,
                 max_queue_size: int = 1000,
                 max_response_time: float = 1000.0):
        """
        初始化负载监控器
        
        Args:
            sample_interval: 采样间隔(秒)
            history_size: 历史数据保存数量
            max_queue_size: 最大队列长度(用于归一化)
            max_response_time: 最大响应时间(ms，用于归一化)
        """
        self.sample_interval = sample_interval
        self.history_size = history_size
        self.max_queue_size = max_queue_size
        self.max_response_time = max_response_time
        
        # 历史数据存储
        self.metrics_history = deque(maxlen=history_size)
        
        # 实时统计数据
        self.current_queue_depth = 0
        self.response_times = deque(maxlen=100)  # 最近100个响应时间
        self.request_timestamps = deque(maxlen=1000)  # 最近1000个请求时间戳
        self.error_count = 0
        self.total_requests = 0
        self.active_connections = 0
        
        # 负载等级阈值配置
        self.load_thresholds = {
            LoadLevel.GREEN: 0.3,
            LoadLevel.YELLOW: 0.5,
            LoadLevel.ORANGE: 0.7,
            LoadLevel.RED: 0.9,
            LoadLevel.BLACK: 1.0
        }
        
        # 权重配置
        self.weights = {
            'cpu': 0.25,
            'memory': 0.2,
            'queue': 0.2,
            'response_time': 0.2,
            'error_rate': 0.1,
            'connections': 0.05
        }
        
        # 监控线程
        self._monitor_thread = None
        self._stop_monitoring = threading.Event()
        self._running = False
        self._lock = threading.RLock()
        
    def start_monitoring(self):
        """启动负载监控"""
        if self._monitor_thread is None or not self._monitor_thread.is_alive():
            self._running = True
            self._stop_monitoring.clear()
            self._monitor_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self._monitor_thread.start()
    
    def stop_monitoring(self):
        """停止负载监控"""
        self._running = False
        self._stop_monitoring.set()
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2.0)
    
    def _monitoring_loop(self):
        """监控循环"""
        while not self._stop_monitoring.is_set():
            try:
                metrics = self._collect_metrics()
                with self._lock:
                    self.metrics_history.append(metrics)
                
                time.sleep(self.sample_interval)
            except Exception as e:
                print(f"负载监控错误: {e}")
                time.sleep(self.sample_interval)
    
    def _collect_metrics(self) -> LoadMetrics:
        """收集系统指标"""
        current_time = time.time()
        
        # 收集系统资源指标
        cpu_usage = psutil.cpu_percent() / 100.0
        memory_info = psutil.virtual_memory()
        memory_usage = memory_info.percent / 100.0
        
        # 计算平均响应时间
        with self._lock:
            avg_response_time = (
                statistics.mean(self.response_times) 
                if self.response_times else 0.0
            )
            
            # 计算每秒请求数
            recent_requests = [
                t for t in self.request_timestamps
                if current_time - t <= 1.0
            ]
            requests_per_second = len(recent_requests)
            
            # 计算错误率
            error_rate = (
                self.error_count / self.total_requests 
                if self.total_requests > 0 else 0.0
            )
            
            queue_depth = self.current_queue_depth
            active_connections = self.active_connections
        
        return LoadMetrics(
            timestamp=current_time,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            queue_depth=queue_depth,
            avg_response_time=avg_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            active_connections=active_connections
        )
    
    def record_request_start(self):
        """记录请求开始"""
        with self._lock:
            self.request_timestamps.append(time.time())
            self.current_queue_depth += 1
            self.total_requests += 1
    
    def record_request_end(self, response_time_ms: float, is_error: bool = False):
        """记录请求结束"""
        with self._lock:
            self.current_queue_depth = max(0, self.current_queue_depth - 1)
            self.response_times.append(response_time_ms)
            if is_error:
                self.error_count += 1
    
    def record_connection_change(self, delta: int):
        """记录连接数变化"""
        with self._lock:
            self.active_connections = max(0, self.active_connections + delta)
    
    def calculate_load_score(self, metrics: Optional[LoadMetrics] = None) -> float:
        """
        计算综合负载评分
        
        Args:
            metrics: 负载指标，如果为None则使用最新指标
            
        Returns:
            float: 负载评分 (0.0-1.0)
        """
        if metrics is None:
            metrics = self.get_current_metrics()
        
        if metrics is None:
            return 0.0
        
        # 归一化各项指标
        normalized_queue = min(metrics.queue_depth / self.max_queue_size, 1.0)
        normalized_response_time = min(
            metrics.avg_response_time / self.max_response_time, 1.0
        )
        normalized_connections = min(metrics.active_connections / 1000.0, 1.0)
        
        # 计算加权综合评分
        score = (
            self.weights['cpu'] * metrics.cpu_usage +
            self.weights['memory'] * metrics.memory_usage +
            self.weights['queue'] * normalized_queue +
            self.weights['response_time'] * normalized_response_time +
            self.weights['error_rate'] * metrics.error_rate +
            self.weights['connections'] * normalized_connections
        )
        
        return min(score, 1.0)
    
    def determine_load_level(self, load_score: float) -> LoadLevel:
        """
        根据负载评分确定负载等级
        
        Args:
            load_score: 负载评分
            
        Returns:
            LoadLevel: 负载等级
        """
        if load_score <= self.load_thresholds[LoadLevel.GREEN]:
            return LoadLevel.GREEN
        elif load_score <= self.load_thresholds[LoadLevel.YELLOW]:
            return LoadLevel.YELLOW
        elif load_score <= self.load_thresholds[LoadLevel.ORANGE]:
            return LoadLevel.ORANGE
        elif load_score <= self.load_thresholds[LoadLevel.RED]:
            return LoadLevel.RED
        else:
            return LoadLevel.BLACK
    
    def get_current_metrics(self) -> Optional[LoadMetrics]:
        """获取当前负载指标"""
        with self._lock:
            if self.metrics_history:
                return self.metrics_history[-1]
            return None
    
    def get_load_status(self) -> Dict[str, Any]:
        """
        获取完整的负载状态信息
        
        Returns:
            Dict: 包含指标、评分、等级等信息的状态字典
        """
        metrics = self.get_current_metrics()
        if metrics is None:
            return {
                'available': False,
                'message': '负载监控数据不可用'
            }
        
        load_score = self.calculate_load_score(metrics)
        load_level = self.determine_load_level(load_score)
        
        return {
            'available': True,
            'timestamp': metrics.timestamp,
            'metrics': metrics.to_dict(),
            'load_score': load_score,
            'load_level': load_level.value,
            'trend': self._analyze_trend(),
            'suggestions': self._generate_suggestions(load_level, load_score)
        }
    
    def _analyze_trend(self) -> str:
        """分析负载趋势"""
        with self._lock:
            if len(self.metrics_history) < 3:
                return "STABLE"
            
            recent_scores = [
                self.calculate_load_score(metrics)
                for metrics in list(self.metrics_history)[-3:]
            ]
            
            if recent_scores[-1] > recent_scores[0] + 0.1:
                return "INCREASING"
            elif recent_scores[-1] < recent_scores[0] - 0.1:
                return "DECREASING"
            else:
                return "STABLE"
    
    def _generate_suggestions(self, load_level: LoadLevel, load_score: float) -> Dict[str, Any]:
        """生成负载优化建议"""
        suggestions = {
            'rate_adjustment': 1.0,  # 建议的速率调整系数
            'actions': []
        }
        
        if load_level == LoadLevel.GREEN:
            suggestions['rate_adjustment'] = 1.2
            suggestions['actions'].append("可以适当增加请求速率")
            
        elif load_level == LoadLevel.YELLOW:
            suggestions['rate_adjustment'] = 1.0
            suggestions['actions'].append("维持当前请求速率")
            
        elif load_level == LoadLevel.ORANGE:
            suggestions['rate_adjustment'] = 0.8
            suggestions['actions'].append("建议适当降低请求速率")
            
        elif load_level == LoadLevel.RED:
            suggestions['rate_adjustment'] = 0.5
            suggestions['actions'].extend([
                "需要显著降低请求速率",
                "考虑启用请求队列",
                "检查系统资源使用情况"
            ])
            
        else:  # BLACK
            suggestions['rate_adjustment'] = 0.1
            suggestions['actions'].extend([
                "立即停止或大幅减少请求",
                "系统需要紧急干预",
                "检查是否有异常进程或内存泄漏"
            ])
        
        return suggestions
    
    def get_history(self, count: int = None) -> List[LoadMetrics]:
        """获取历史负载数据"""
        with self._lock:
            history = list(self.metrics_history)
            if count is not None:
                history = history[-count:]
            return history
    
    def update_thresholds(self, thresholds: Dict[LoadLevel, float]):
        """更新负载等级阈值"""
        self.load_thresholds.update(thresholds)
    
    def update_weights(self, weights: Dict[str, float]):
        """更新指标权重"""
        self.weights.update(weights)
    
    def __str__(self) -> str:
        status = self.get_load_status()
        if not status['available']:
            return "LoadMonitor(状态: 不可用)"
        
        return (f"LoadMonitor("
               f"等级: {status['load_level']}, "
               f"评分: {status['load_score']:.2f}, "
               f"趋势: {status['trend']})")
    
    def __del__(self):
        """析构函数，确保监控线程停止"""
        try:
            self.stop_monitoring()
        except:
            pass
