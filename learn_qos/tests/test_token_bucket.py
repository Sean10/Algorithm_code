#!/usr/bin/env python3
"""
令牌桶算法的单元测试
"""

import pytest
import time
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from algorithms.token_bucket import TokenBucket, TokenBucketConfig
from common.base import Packet, PacketPriority, TrafficGenerator


class TestTokenBucketConfig:
    """令牌桶配置测试"""
    
    def test_valid_config(self):
        """测试有效配置"""
        config = TokenBucketConfig(
            token_rate=1000.0,
            bucket_size=5000,
            initial_tokens=2500,
            token_size=1
        )
        assert config.token_rate == 1000.0
        assert config.bucket_size == 5000
        assert config.initial_tokens == 2500
        assert config.token_size == 1
    
    def test_default_initial_tokens(self):
        """测试默认初始令牌数"""
        config = TokenBucketConfig(token_rate=1000.0, bucket_size=5000)
        assert config.initial_tokens == 5000  # 应该等于桶容量
    
    def test_invalid_token_rate(self):
        """测试无效的令牌生成速率"""
        with pytest.raises(ValueError, match="令牌生成速率必须大于0"):
            TokenBucketConfig(token_rate=0, bucket_size=5000)
        
        with pytest.raises(ValueError, match="令牌生成速率必须大于0"):
            TokenBucketConfig(token_rate=-100, bucket_size=5000)
    
    def test_invalid_bucket_size(self):
        """测试无效的桶容量"""
        with pytest.raises(ValueError, match="桶容量必须大于0"):
            TokenBucketConfig(token_rate=1000, bucket_size=0)
        
        with pytest.raises(ValueError, match="桶容量必须大于0"):
            TokenBucketConfig(token_rate=1000, bucket_size=-100)
    
    def test_invalid_initial_tokens(self):
        """测试无效的初始令牌数"""
        with pytest.raises(ValueError, match="初始令牌数必须在0到桶容量之间"):
            TokenBucketConfig(token_rate=1000, bucket_size=5000, initial_tokens=-1)
        
        with pytest.raises(ValueError, match="初始令牌数必须在0到桶容量之间"):
            TokenBucketConfig(token_rate=1000, bucket_size=5000, initial_tokens=6000)


class TestTokenBucket:
    """令牌桶算法测试"""
    
    def test_initialization(self):
        """测试初始化"""
        config = TokenBucketConfig(token_rate=1000.0, bucket_size=5000)
        bucket = TokenBucket(config)
        
        assert bucket.name == "TokenBucket"
        assert bucket.config == config
        assert bucket.get_current_tokens() == 5000.0
        assert bucket.is_empty()
        assert bucket.get_queue_size() == 0
    
    def test_basic_packet_processing(self):
        """测试基本数据包处理"""
        config = TokenBucketConfig(token_rate=1000.0, bucket_size=5000)
        bucket = TokenBucket(config)
        
        # 创建测试数据包
        packet = Packet(id=1, size=1000)
        
        # 应该能成功处理（令牌充足）
        assert bucket.enqueue(packet) is True
        assert bucket.get_queue_size() == 1
        assert bucket.get_current_tokens() == pytest.approx(4000.0, abs=1.0)  # 消耗了1000个令牌
        
        # 取出数据包
        dequeued_packet = bucket.dequeue()
        assert dequeued_packet is not None
        assert dequeued_packet.id == 1
        assert bucket.get_queue_size() == 0
    
    def test_token_exhaustion(self):
        """测试令牌耗尽情况"""
        config = TokenBucketConfig(token_rate=1000.0, bucket_size=2000)
        bucket = TokenBucket(config)
        
        # 第一个大数据包应该成功
        packet1 = Packet(id=1, size=1500)
        assert bucket.enqueue(packet1) is True
        assert bucket.get_current_tokens() == pytest.approx(500.0, abs=1.0)
        
        # 第二个数据包应该被丢弃（令牌不足）
        packet2 = Packet(id=2, size=1000)
        assert bucket.enqueue(packet2) is False
        assert bucket.get_queue_size() == 1  # 只有第一个包
        
        # 验证指标
        metrics = bucket.get_metrics()
        assert metrics['total_packets'] == 2
        assert metrics['dropped_packets'] == 1
        assert metrics['drop_rate'] == 0.5
    
    def test_token_regeneration(self):
        """测试令牌重新生成"""
        config = TokenBucketConfig(token_rate=1000.0, bucket_size=2000)
        bucket = TokenBucket(config)
        
        # 消耗所有令牌
        packet1 = Packet(id=1, size=2000)
        assert bucket.enqueue(packet1) is True
        assert bucket.get_current_tokens() == pytest.approx(0.0, abs=1.0)
        
        # 等待令牌重新生成
        time.sleep(0.5)  # 等待0.5秒
        
        # 应该有大约500个新令牌
        current_tokens = bucket.get_current_tokens()
        assert 400 < current_tokens < 600  # 允许一定误差
        
        # 现在应该能处理新的数据包
        packet2 = Packet(id=2, size=400)
        assert bucket.enqueue(packet2) is True
    
    def test_burst_handling(self):
        """测试突发流量处理"""
        config = TokenBucketConfig(token_rate=1000.0, bucket_size=10000)
        bucket = TokenBucket(config)
        
        # 生成突发流量
        generator = TrafficGenerator()
        burst_packets = generator.generate_burst_traffic(
            num_packets=5,
            packet_size=1500,
            priority=PacketPriority.HIGH
        )
        
        # 突发流量应该能被处理（因为桶有足够容量）
        processed_count = 0
        for packet in burst_packets:
            if bucket.enqueue(packet):
                processed_count += 1
        
        assert processed_count == 5  # 所有包都应该被处理
        assert bucket.get_queue_size() == 5
        assert bucket.get_current_tokens() == pytest.approx(2500.0, abs=2.0)  # 消耗了7500个令牌
    
    def test_can_handle_burst(self):
        """测试突发处理能力检查"""
        config = TokenBucketConfig(token_rate=1000.0, bucket_size=5000)
        bucket = TokenBucket(config)
        
        # 应该能处理5000字节的突发
        assert bucket.can_handle_burst(5000) is True
        
        # 不应该能处理10000字节的突发
        assert bucket.can_handle_burst(10000) is False
        
        # 处理一些数据后重新检查
        packet = Packet(id=1, size=2000)
        bucket.enqueue(packet)
        
        assert bucket.can_handle_burst(3000) is True
        assert bucket.can_handle_burst(4000) is False
    
    def test_metrics_calculation(self):
        """测试指标计算"""
        config = TokenBucketConfig(token_rate=1000.0, bucket_size=5000)
        bucket = TokenBucket(config)
        
        # 处理一些数据包
        packets = [
            Packet(id=1, size=1000),
            Packet(id=2, size=1500),
            Packet(id=3, size=8000),  # 这个应该被丢弃
        ]
        
        for packet in packets:
            bucket.enqueue(packet)
        
        metrics = bucket.get_metrics()
        
        # 基本指标
        assert metrics['total_packets'] == 3
        assert metrics['dropped_packets'] == 1
        assert metrics['drop_rate'] == pytest.approx(1/3, rel=1e-2)
        
        # 令牌桶特定指标
        assert 'current_tokens' in metrics
        assert 'token_fill_ratio' in metrics
        assert 'average_processing_rate' in metrics
        assert metrics['packets_passed'] == 2
        assert metrics['packets_dropped'] == 1
        assert metrics['queue_size'] == 2
    
    def test_token_fill_ratio(self):
        """测试令牌桶填充比例"""
        config = TokenBucketConfig(token_rate=1000.0, bucket_size=1000)
        bucket = TokenBucket(config)
        
        assert bucket.get_token_fill_ratio() == 1.0  # 满桶
        
        # 消耗一半令牌
        packet = Packet(id=1, size=500)
        bucket.enqueue(packet)
        
        assert bucket.get_token_fill_ratio() == pytest.approx(0.5, abs=0.001)
    
    def test_different_token_sizes(self):
        """测试不同的令牌大小"""
        # 每个令牌代表10字节
        config = TokenBucketConfig(
            token_rate=100.0,
            bucket_size=1000,
            token_size=10
        )
        bucket = TokenBucket(config)
        
        # 100字节的包需要10个令牌
        packet = Packet(id=1, size=100)
        assert bucket.enqueue(packet) is True
        assert bucket.get_current_tokens() == pytest.approx(990.0, abs=1.0)
        
        # 150字节的包需要15个令牌（向上取整）
        packet2 = Packet(id=2, size=150)
        assert bucket.enqueue(packet2) is True
        assert bucket.get_current_tokens() == pytest.approx(975.0, abs=1.0)
    
    def test_thread_safety(self):
        """测试线程安全性"""
        import threading
        import random
        
        config = TokenBucketConfig(token_rate=10000.0, bucket_size=50000)
        bucket = TokenBucket(config)
        
        results = []
        
        def worker():
            """工作线程函数"""
            for i in range(10):
                packet = Packet(id=i, size=random.randint(100, 1000))
                result = bucket.enqueue(packet)
                results.append(result)
                time.sleep(0.001)  # 小延迟
        
        # 创建多个线程
        threads = []
        for _ in range(5):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        # 验证结果
        assert len(results) == 50  # 5个线程，每个10次操作
        assert any(results)  # 至少有一些操作成功
        
        metrics = bucket.get_metrics()
        assert metrics['total_packets'] == 50
    
    def test_reset_metrics(self):
        """测试指标重置"""
        config = TokenBucketConfig(token_rate=1000.0, bucket_size=5000)
        bucket = TokenBucket(config)
        
        # 处理一些数据包
        packet = Packet(id=1, size=1000)
        bucket.enqueue(packet)
        
        # 验证有指标数据
        metrics_before = bucket.get_metrics()
        assert metrics_before['total_packets'] > 0
        
        # 重置指标
        bucket.reset_metrics()
        
        # 验证指标被重置
        metrics_after = bucket.get_metrics()
        assert metrics_after['total_packets'] == 0
        assert metrics_after['dropped_packets'] == 0
        assert metrics_after['packets_passed'] == 0
        assert metrics_after['packets_dropped'] == 0
    
    def test_string_representations(self):
        """测试字符串表示"""
        config = TokenBucketConfig(token_rate=1000.0, bucket_size=5000)
        bucket = TokenBucket(config)
        
        str_repr = str(bucket)
        assert "TokenBucket" in str_repr
        assert "1000.0" in str_repr
        assert "5000" in str_repr
        
        repr_str = repr(bucket)
        assert "TokenBucket" in repr_str
        assert "token_rate=1000.0" in repr_str
        assert "bucket_size=5000" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
