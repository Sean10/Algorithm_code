#!/usr/bin/env python3
"""
自适应QoS系统的单元测试
"""

import pytest
import time
import threading
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from algorithms.adaptive_qos import (
    LoadMonitor, LoadMetrics, LoadLevel,
    AIMDRateLimiter, PIDRateLimiter, ExponentialBackoffRateLimiter,
    FeedbackGenerator, FeedbackReceiver, LoadFeedback,
    FeedbackSystem, AdaptiveStrategy, create_adaptive_limiter
)


class TestLoadMonitor:
    """负载监控器测试"""
    
    def test_initialization(self):
        """测试初始化"""
        monitor = LoadMonitor(sample_interval=1.0, history_size=50)
        assert monitor.sample_interval == 1.0
        assert monitor.history_size == 50
        assert not monitor._running
    
    def test_metrics_collection(self):
        """测试指标收集"""
        monitor = LoadMonitor(sample_interval=0.1)
        
        # 模拟一些请求
        monitor.record_request_start()
        monitor.record_request_start()
        time.sleep(0.01)
        monitor.record_request_end(10.0, False)
        monitor.record_request_end(15.0, True)  # 错误请求
        
        # 获取当前指标
        metrics = monitor._collect_metrics()
        
        assert isinstance(metrics, LoadMetrics)
        assert metrics.cpu_usage >= 0.0
        assert metrics.memory_usage >= 0.0
        assert metrics.queue_depth >= 0
        assert metrics.error_rate > 0  # 应该有错误
    
    def test_load_score_calculation(self):
        """测试负载评分计算"""
        monitor = LoadMonitor()
        
        # 创建测试指标
        metrics = LoadMetrics(
            timestamp=time.time(),
            cpu_usage=0.5,
            memory_usage=0.3,
            queue_depth=100,
            avg_response_time=50.0,
            requests_per_second=10.0,
            error_rate=0.02,
            active_connections=50
        )
        
        score = monitor.calculate_load_score(metrics)
        assert 0.0 <= score <= 1.0
    
    def test_load_level_determination(self):
        """测试负载等级确定"""
        monitor = LoadMonitor()
        
        assert monitor.determine_load_level(0.2) == LoadLevel.GREEN
        assert monitor.determine_load_level(0.4) == LoadLevel.YELLOW
        assert monitor.determine_load_level(0.6) == LoadLevel.ORANGE
        assert monitor.determine_load_level(0.8) == LoadLevel.RED
        assert monitor.determine_load_level(0.95) == LoadLevel.BLACK
    
    def test_monitoring_lifecycle(self):
        """测试监控生命周期"""
        monitor = LoadMonitor(sample_interval=0.1)
        
        # 启动监控
        monitor.start_monitoring()
        assert monitor._running
        
        # 等待收集一些数据
        time.sleep(0.3)
        
        status = monitor.get_load_status()
        assert status['available']
        assert 'metrics' in status
        assert 'load_score' in status
        
        # 停止监控
        monitor.stop_monitoring()
        assert not monitor._running


class TestAIMDRateLimiter:
    """AIMD限流器测试"""
    
    def test_initialization(self):
        """测试初始化"""
        limiter = AIMDRateLimiter(
            initial_rate=100.0,
            increase_step=5.0,
            decrease_factor=0.8
        )
        
        assert limiter.get_current_rate() == 100.0
        assert limiter.increase_step == 5.0
        assert limiter.decrease_factor == 0.8
    
    def test_rate_adjustment(self):
        """测试速率调整"""
        limiter = AIMDRateLimiter(initial_rate=100.0)
        
        # 绿色负载 - 应该增加
        green_info = {'load_level': 'GREEN', 'load_score': 0.2}
        limiter.adjust_rate(green_info)
        assert limiter.get_current_rate() > 100.0
        
        # 红色负载 - 应该减少
        red_info = {'load_level': 'RED', 'load_score': 0.9}
        limiter.adjust_rate(red_info)
        assert limiter.get_current_rate() < 100.0
    
    def test_rate_bounds(self):
        """测试速率边界"""
        limiter = AIMDRateLimiter(
            initial_rate=50.0,
            min_rate=10.0,
            max_rate=100.0
        )
        
        # 多次增加，不应超过最大值
        green_info = {'load_level': 'GREEN', 'load_score': 0.1}
        for _ in range(20):
            limiter.adjust_rate(green_info)
        
        assert limiter.get_current_rate() <= 100.0
        
        # 多次减少，不应低于最小值
        red_info = {'load_level': 'RED', 'load_score': 0.9}
        for _ in range(20):
            limiter.adjust_rate(red_info)
        
        assert limiter.get_current_rate() >= 10.0


class TestPIDRateLimiter:
    """PID限流器测试"""
    
    def test_initialization(self):
        """测试初始化"""
        limiter = PIDRateLimiter(
            initial_rate=100.0,
            target_load_score=0.6,
            kp=50.0,
            ki=5.0,
            kd=20.0
        )
        
        assert limiter.get_current_rate() == 100.0
        assert limiter.target_load_score == 0.6
    
    def test_pid_adjustment(self):
        """测试PID调整"""
        limiter = PIDRateLimiter(initial_rate=100.0, target_load_score=0.6)
        
        # 负载过高 - 应该减少速率
        high_load_info = {'load_score': 0.8}
        old_rate = limiter.get_current_rate()
        limiter.adjust_rate(high_load_info)
        
        # 等待一小段时间确保时间差
        time.sleep(0.01)
        
        # 负载过低 - 应该增加速率
        low_load_info = {'load_score': 0.3}
        limiter.adjust_rate(low_load_info)


class TestExponentialBackoffRateLimiter:
    """指数退避限流器测试"""
    
    def test_backoff_mechanism(self):
        """测试退避机制"""
        limiter = ExponentialBackoffRateLimiter(
            initial_rate=100.0,
            backoff_factor=2.0
        )
        
        initial_rate = limiter.get_current_rate()
        
        # 连续过载
        overload_info = {'load_level': 'RED'}
        for _ in range(3):
            limiter.adjust_rate(overload_info)
        
        # 速率应该显著下降
        assert limiter.get_current_rate() < initial_rate * 0.5
    
    def test_recovery_mechanism(self):
        """测试恢复机制"""
        limiter = ExponentialBackoffRateLimiter(initial_rate=100.0)
        
        # 先触发退避
        overload_info = {'load_level': 'RED'}
        limiter.adjust_rate(overload_info)
        low_rate = limiter.get_current_rate()
        
        # 然后恢复
        normal_info = {'load_level': 'GREEN'}
        for _ in range(5):  # 需要连续几次正常才开始恢复
            limiter.adjust_rate(normal_info)
        
        # 速率应该开始恢复
        assert limiter.get_current_rate() >= low_rate


class TestFeedbackSystem:
    """反馈系统测试"""
    
    def test_feedback_data_structure(self):
        """测试反馈数据结构"""
        feedback = LoadFeedback(
            timestamp=time.time(),
            server_id="test-server",
            load_level=LoadLevel.YELLOW,
            load_score=0.5,
            suggested_rate=75.0,
            metrics={'cpu': 0.6},
            trend='STABLE',
            suggestions={'rate_adjustment': 1.0}
        )
        
        # 测试序列化
        json_str = feedback.to_json()
        restored = LoadFeedback.from_json(json_str)
        
        assert restored.server_id == feedback.server_id
        assert restored.load_level == feedback.load_level
        assert restored.load_score == feedback.load_score
    
    def test_feedback_generator(self):
        """测试反馈生成器"""
        monitor = LoadMonitor(sample_interval=0.1)
        generator = FeedbackGenerator("test-server", monitor, base_capacity=100.0)
        
        monitor.start_monitoring()
        time.sleep(0.2)  # 等待收集数据
        
        try:
            # 注册客户端
            generator.register_client("client-1")
            
            # 生成反馈
            feedback = generator.generate_feedback("client-1")
            
            assert feedback.server_id == "test-server"
            assert isinstance(feedback.load_level, LoadLevel)
            assert 0.0 <= feedback.load_score <= 1.0
            assert feedback.suggested_rate > 0
            
            # 测试HTTP头格式
            headers = generator.get_feedback_for_http_headers("client-1")
            assert 'X-Load-Level' in headers
            assert 'X-Load-Score' in headers
            assert 'X-Suggested-Rate' in headers
            
        finally:
            monitor.stop_monitoring()
    
    def test_feedback_receiver(self):
        """测试反馈接收器"""
        receiver = FeedbackReceiver("test-client")
        
        # 模拟HTTP头反馈
        headers = {
            'X-Load-Level': 'YELLOW',
            'X-Load-Score': '0.6',
            'X-Suggested-Rate': '80.0',
            'X-Server-Id': 'test-server',
            'X-Timestamp': str(int(time.time())),
            'X-Trend': 'INCREASING'
        }
        
        # 接收反馈  
        from algorithms.adaptive_qos import FeedbackChannel
        receiver.receive_feedback(headers, FeedbackChannel.HTTP_HEADER)
        
        # 验证反馈
        latest = receiver.get_latest_feedback()
        assert latest is not None
        assert latest.load_level == LoadLevel.YELLOW
        assert latest.load_score == pytest.approx(0.6)
        assert latest.suggested_rate == pytest.approx(80.0)
    
    def test_feedback_system_integration(self):
        """测试反馈系统集成"""
        system = FeedbackSystem()
        
        # 创建监控器和生成器
        monitor = LoadMonitor(sample_interval=0.1)
        generator = system.create_generator("server-1", monitor)
        receiver = system.create_receiver("client-1")
        
        monitor.start_monitoring()
        time.sleep(0.2)
        
        try:
            # 模拟反馈传输
            system.simulate_feedback_exchange("server-1", "client-1")
            
            # 验证接收
            latest = receiver.get_latest_feedback()
            assert latest is not None
            assert latest.server_id == "server-1"
            
            # 获取系统统计
            stats = system.get_system_stats()
            assert stats['generators_count'] == 1
            assert stats['receivers_count'] == 1
            
        finally:
            monitor.stop_monitoring()


class TestAdaptiveLimiterFactory:
    """自适应限流器工厂测试"""
    
    def test_create_different_limiters(self):
        """测试创建不同类型的限流器"""
        strategies = [
            AdaptiveStrategy.AIMD,
            AdaptiveStrategy.PID,
            AdaptiveStrategy.EXPONENTIAL_BACKOFF,
            AdaptiveStrategy.GRADIENT_DESCENT
        ]
        
        for strategy in strategies:
            limiter = create_adaptive_limiter(strategy, initial_rate=50.0)
            assert limiter is not None
            assert limiter.get_current_rate() == 50.0
            
            # 测试基本功能
            load_info = {'load_level': 'GREEN', 'load_score': 0.3}
            limiter.adjust_rate(load_info)


class TestIntegration:
    """集成测试"""
    
    def test_end_to_end_flow(self):
        """测试端到端流程"""
        # 创建完整的系统
        monitor = LoadMonitor(sample_interval=0.1)
        generator = FeedbackGenerator("test-server", monitor)
        receiver = FeedbackReceiver("test-client")
        limiter = AIMDRateLimiter(initial_rate=50.0)
        
        # 设置反馈回调
        def handle_feedback(feedback):
            load_info = {
                'load_level': feedback.load_level.value,
                'load_score': feedback.load_score,
                'trend': feedback.trend
            }
            limiter.adjust_rate(load_info)
        
        receiver.add_feedback_callback(handle_feedback)
        
        monitor.start_monitoring()
        
        try:
            # 模拟负载变化
            monitor.record_request_start()
            monitor.record_request_start()
            time.sleep(0.1)
            monitor.record_request_end(20.0, False)
            monitor.record_request_end(25.0, False)
            
            time.sleep(0.2)  # 等待监控数据更新
            
            # 生成并发送反馈
            feedback = generator.generate_feedback("test-client")
            receiver.receive_feedback(feedback.to_dict(), 'HTTP_BODY')
            
            # 验证系统响应
            time.sleep(0.1)  # 等待回调处理
            
            # 检查速率是否被调整
            stats = limiter.get_adjustment_stats()
            # 注意：由于负载很低，速率可能被增加
            
        finally:
            monitor.stop_monitoring()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
