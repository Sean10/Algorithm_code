"""
反馈系统模块

处理服务端到客户端的负载信息传递，支持多种传输方式
"""

import json
import time
import threading
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque
from abc import ABC, abstractmethod

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from .load_monitor import LoadMonitor, LoadLevel


@dataclass
class LoadFeedback:
    """负载反馈数据结构"""
    timestamp: float
    server_id: str
    load_level: LoadLevel
    load_score: float
    suggested_rate: float
    metrics: Dict[str, Any]
    trend: str
    suggestions: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['load_level'] = self.load_level.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LoadFeedback':
        """从字典创建实例"""
        data['load_level'] = LoadLevel(data['load_level'])
        return cls(**data)
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'LoadFeedback':
        """从JSON字符串创建实例"""
        return cls.from_dict(json.loads(json_str))


class FeedbackChannel(Enum):
    """反馈传输通道类型"""
    HTTP_HEADER = "HTTP_HEADER"        # HTTP响应头
    HTTP_BODY = "HTTP_BODY"            # HTTP响应体
    WEBSOCKET = "WEBSOCKET"            # WebSocket
    SSE = "SSE"                        # Server-Sent Events
    MQTT = "MQTT"                      # MQTT消息队列
    REDIS_PUBSUB = "REDIS_PUBSUB"      # Redis发布订阅
    CUSTOM = "CUSTOM"                  # 自定义通道


class FeedbackGenerator:
    """
    服务端反馈生成器
    
    负责：
    - 收集负载监控数据
    - 生成客户端反馈信息
    - 计算建议的发送速率
    """
    
    def __init__(self, 
                 server_id: str,
                 load_monitor: LoadMonitor,
                 base_capacity: float = 1000.0):
        """
        初始化反馈生成器
        
        Args:
            server_id: 服务器标识
            load_monitor: 负载监控器
            base_capacity: 服务器基础处理能力 (requests/second)
        """
        self.server_id = server_id
        self.load_monitor = load_monitor
        self.base_capacity = base_capacity
        
        # 客户端管理
        self.active_clients = set()
        self._lock = threading.RLock()
    
    def register_client(self, client_id: str):
        """注册客户端"""
        with self._lock:
            self.active_clients.add(client_id)
    
    def unregister_client(self, client_id: str):
        """注销客户端"""
        with self._lock:
            self.active_clients.discard(client_id)
    
    def generate_feedback(self, client_id: Optional[str] = None) -> LoadFeedback:
        """
        生成负载反馈信息
        
        Args:
            client_id: 客户端ID（用于个性化建议）
            
        Returns:
            LoadFeedback: 反馈信息
        """
        # 获取当前负载状态
        load_status = self.load_monitor.get_load_status()
        
        if not load_status['available']:
            # 负载信息不可用，返回保守建议
            return LoadFeedback(
                timestamp=time.time(),
                server_id=self.server_id,
                load_level=LoadLevel.YELLOW,
                load_score=0.5,
                suggested_rate=self.base_capacity * 0.5,
                metrics={},
                trend='UNKNOWN',
                suggestions={'rate_adjustment': 0.5, 'actions': ['负载信息不可用，保守限流']}
            )
        
        # 计算建议速率
        suggested_rate = self._calculate_suggested_rate(
            load_status['load_score'],
            load_status['load_level'],
            client_id
        )
        
        return LoadFeedback(
            timestamp=load_status['timestamp'],
            server_id=self.server_id,
            load_level=LoadLevel(load_status['load_level']),
            load_score=load_status['load_score'],
            suggested_rate=suggested_rate,
            metrics=load_status['metrics'],
            trend=load_status['trend'],
            suggestions=load_status['suggestions']
        )
    
    def _calculate_suggested_rate(self, 
                                 load_score: float, 
                                 load_level: str,
                                 client_id: Optional[str] = None) -> float:
        """计算建议的发送速率"""
        with self._lock:
            client_count = max(len(self.active_clients), 1)
        
        # 基于负载评分计算总可用容量
        load_level_enum = LoadLevel(load_level)
        
        if load_level_enum == LoadLevel.GREEN:
            available_capacity = self.base_capacity * 1.2
        elif load_level_enum == LoadLevel.YELLOW:
            available_capacity = self.base_capacity * 1.0
        elif load_level_enum == LoadLevel.ORANGE:
            available_capacity = self.base_capacity * 0.7
        elif load_level_enum == LoadLevel.RED:
            available_capacity = self.base_capacity * 0.3
        else:  # BLACK
            available_capacity = self.base_capacity * 0.1
        
        # 考虑负载评分进行微调
        capacity_multiplier = max(0.1, 1.0 - load_score)
        available_capacity *= capacity_multiplier
        
        # 平均分配给各个客户端
        per_client_rate = available_capacity / client_count
        
        return max(1.0, per_client_rate)
    
    def get_feedback_for_http_headers(self, client_id: Optional[str] = None) -> Dict[str, str]:
        """生成用于HTTP响应头的反馈信息"""
        feedback = self.generate_feedback(client_id)
        
        return {
            'X-Load-Level': feedback.load_level.value,
            'X-Load-Score': f"{feedback.load_score:.3f}",
            'X-Suggested-Rate': f"{feedback.suggested_rate:.1f}",
            'X-Server-Id': feedback.server_id,
            'X-Timestamp': str(int(feedback.timestamp)),
            'X-Trend': feedback.trend
        }
    
    def get_feedback_for_http_body(self, client_id: Optional[str] = None) -> Dict[str, Any]:
        """生成用于HTTP响应体的反馈信息"""
        feedback = self.generate_feedback(client_id)
        return {
            'load_feedback': feedback.to_dict()
        }


class FeedbackReceiver:
    """
    客户端反馈接收器
    
    负责：
    - 接收服务端反馈信息
    - 解析和验证反馈数据
    - 管理反馈缓存和超时
    """
    
    def __init__(self, 
                 client_id: str,
                 feedback_timeout: float = 10.0,
                 max_cache_size: int = 100):
        """
        初始化反馈接收器
        
        Args:
            client_id: 客户端ID
            feedback_timeout: 反馈超时时间(秒)
            max_cache_size: 最大缓存大小
        """
        self.client_id = client_id
        self.feedback_timeout = feedback_timeout
        self.max_cache_size = max_cache_size
        
        # 反馈缓存
        self.feedback_cache = deque(maxlen=max_cache_size)
        self.latest_feedback: Optional[LoadFeedback] = None
        self.last_feedback_time = 0.0
        
        # 回调函数
        self.feedback_callbacks: List[Callable[[LoadFeedback], None]] = []
        
        # 统计信息
        self.total_feedbacks_received = 0
        self.total_timeouts = 0
        self.total_parse_errors = 0
        
        self._lock = threading.RLock()
    
    def add_feedback_callback(self, callback: Callable[[LoadFeedback], None]):
        """添加反馈处理回调函数"""
        self.feedback_callbacks.append(callback)
    
    def receive_feedback(self, feedback_data: Any, channel: FeedbackChannel = FeedbackChannel.HTTP_BODY):
        """
        接收反馈数据
        
        Args:
            feedback_data: 反馈数据（格式取决于通道类型）
            channel: 反馈通道类型
        """
        try:
            # 根据通道类型解析数据
            if channel == FeedbackChannel.HTTP_HEADER:
                feedback = self._parse_http_headers(feedback_data)
            elif channel == FeedbackChannel.HTTP_BODY:
                feedback = self._parse_http_body(feedback_data)
            elif channel == FeedbackChannel.WEBSOCKET:
                feedback = self._parse_websocket_message(feedback_data)
            else:
                feedback = self._parse_generic(feedback_data)
            
            if feedback:
                self._process_feedback(feedback)
                
        except Exception as e:
            with self._lock:
                self.total_parse_errors += 1
            print(f"解析反馈数据时出错: {e}")
    
    def _parse_http_headers(self, headers: Dict[str, str]) -> Optional[LoadFeedback]:
        """解析HTTP响应头中的反馈信息"""
        try:
            return LoadFeedback(
                timestamp=float(headers.get('X-Timestamp', time.time())),
                server_id=headers.get('X-Server-Id', 'unknown'),
                load_level=LoadLevel(headers.get('X-Load-Level', 'YELLOW')),
                load_score=float(headers.get('X-Load-Score', '0.5')),
                suggested_rate=float(headers.get('X-Suggested-Rate', '50.0')),
                metrics={},
                trend=headers.get('X-Trend', 'STABLE'),
                suggestions={'rate_adjustment': 1.0, 'actions': []}
            )
        except (ValueError, KeyError) as e:
            print(f"解析HTTP头部反馈失败: {e}")
            return None
    
    def _parse_http_body(self, body: Dict[str, Any]) -> Optional[LoadFeedback]:
        """解析HTTP响应体中的反馈信息"""
        try:
            if 'load_feedback' in body:
                return LoadFeedback.from_dict(body['load_feedback'])
            return None
        except (ValueError, KeyError) as e:
            print(f"解析HTTP响应体反馈失败: {e}")
            return None
    
    def _parse_websocket_message(self, message: str) -> Optional[LoadFeedback]:
        """解析WebSocket消息中的反馈信息"""
        try:
            return LoadFeedback.from_json(message)
        except (ValueError, json.JSONDecodeError) as e:
            print(f"解析WebSocket反馈失败: {e}")
            return None
    
    def _parse_generic(self, data: Any) -> Optional[LoadFeedback]:
        """通用解析方法"""
        try:
            if isinstance(data, str):
                return LoadFeedback.from_json(data)
            elif isinstance(data, dict):
                return LoadFeedback.from_dict(data)
            elif isinstance(data, LoadFeedback):
                return data
            else:
                return None
        except Exception as e:
            print(f"通用解析反馈失败: {e}")
            return None
    
    def _process_feedback(self, feedback: LoadFeedback):
        """处理接收到的反馈"""
        with self._lock:
            # 更新缓存
            self.feedback_cache.append(feedback)
            self.latest_feedback = feedback
            self.last_feedback_time = time.time()
            self.total_feedbacks_received += 1
        
        # 执行回调
        for callback in self.feedback_callbacks:
            try:
                callback(feedback)
            except Exception as e:
                print(f"反馈回调执行失败: {e}")
    
    def get_latest_feedback(self) -> Optional[LoadFeedback]:
        """获取最新的反馈信息"""
        with self._lock:
            # 检查反馈是否超时
            if (self.latest_feedback and 
                time.time() - self.last_feedback_time > self.feedback_timeout):
                self.total_timeouts += 1
                return None
            
            return self.latest_feedback
    
    def get_feedback_history(self, count: Optional[int] = None) -> List[LoadFeedback]:
        """获取反馈历史"""
        with self._lock:
            history = list(self.feedback_cache)
            if count is not None:
                history = history[-count:]
            return history
    
    def is_feedback_available(self) -> bool:
        """检查是否有可用的反馈信息"""
        return self.get_latest_feedback() is not None
    
    def get_stats(self) -> Dict[str, Any]:
        """获取接收器统计信息"""
        with self._lock:
            return {
                'client_id': self.client_id,
                'total_feedbacks_received': self.total_feedbacks_received,
                'total_timeouts': self.total_timeouts,
                'total_parse_errors': self.total_parse_errors,
                'last_feedback_time': self.last_feedback_time,
                'feedback_available': self.is_feedback_available(),
                'cache_size': len(self.feedback_cache)
            }


class FeedbackSystem:
    """
    完整的反馈系统
    
    整合服务端生成器和客户端接收器，提供统一的接口
    """
    
    def __init__(self):
        self.generators: Dict[str, FeedbackGenerator] = {}
        self.receivers: Dict[str, FeedbackReceiver] = {}
        self._lock = threading.RLock()
    
    def create_generator(self, 
                        server_id: str, 
                        load_monitor: LoadMonitor,
                        **kwargs) -> FeedbackGenerator:
        """创建服务端反馈生成器"""
        with self._lock:
            generator = FeedbackGenerator(server_id, load_monitor, **kwargs)
            self.generators[server_id] = generator
            return generator
    
    def create_receiver(self, client_id: str, **kwargs) -> FeedbackReceiver:
        """创建客户端反馈接收器"""
        with self._lock:
            receiver = FeedbackReceiver(client_id, **kwargs)
            self.receivers[client_id] = receiver
            return receiver
    
    def get_generator(self, server_id: str) -> Optional[FeedbackGenerator]:
        """获取服务端生成器"""
        return self.generators.get(server_id)
    
    def get_receiver(self, client_id: str) -> Optional[FeedbackReceiver]:
        """获取客户端接收器"""
        return self.receivers.get(client_id)
    
    def simulate_feedback_exchange(self, 
                                  server_id: str, 
                                  client_id: str,
                                  channel: FeedbackChannel = FeedbackChannel.HTTP_BODY):
        """模拟服务端到客户端的反馈传输"""
        generator = self.get_generator(server_id)
        receiver = self.get_receiver(client_id)
        
        if not generator or not receiver:
            raise ValueError("生成器或接收器不存在")
        
        # 生成反馈
        feedback = generator.generate_feedback(client_id)
        
        # 传输反馈（根据通道类型）
        if channel == FeedbackChannel.HTTP_HEADER:
            headers = generator.get_feedback_for_http_headers(client_id)
            receiver.receive_feedback(headers, channel)
        elif channel == FeedbackChannel.HTTP_BODY:
            body = generator.get_feedback_for_http_body(client_id)
            receiver.receive_feedback(body, channel)
        else:
            receiver.receive_feedback(feedback.to_json(), channel)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        with self._lock:
            return {
                'generators_count': len(self.generators),
                'receivers_count': len(self.receivers),
                'generators': {
                    server_id: {
                        'server_id': gen.server_id,
                        'active_clients': len(gen.active_clients),
                        'base_capacity': gen.base_capacity
                    }
                    for server_id, gen in self.generators.items()
                },
                'receivers': {
                    client_id: receiver.get_stats()
                    for client_id, receiver in self.receivers.items()
                }
            }
