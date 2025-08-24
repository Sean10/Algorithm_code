#!/usr/bin/env python3
"""
漏桶算法的单元测试
"""

import pytest
import time
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from algorithms.leaky_bucket import LeakyBucket, LeakyBucketConfig
from common.base import Packet, PacketPriority, TrafficGenerator


class TestLeakyBucketConfig:
    """漏桶配置测试"""
    
    def test_valid_config(self):
        """测试有效配置"""
        config = LeakyBucketConfig(
            leak_rate=1000.0,
            bucket_size=5000,
            output_interval=0.01
        )
        assert config.leak_rate == 1000.0
        assert config.bucket_size == 5000
        assert config.output_interval == 0.01
    
    def test_default_output_interval(self):
        """测试默认输出间隔"""
        config = LeakyBucketConfig(leak_rate=1000.0, bucket_size=5000)
        assert config.output_interval == 0.01
    
    def test_invalid_leak_rate(self):
        """测试无效的漏出速率"""
        with pytest.raises(ValueError, match="漏出速率必须大于0"):
            LeakyBucketConfig(leak_rate=0, bucket_size=5000)
        
        with pytest.raises(ValueError, match="漏出速率必须大于0"):
            LeakyBucketConfig(leak_rate=-100, bucket_size=5000)
    
    def test_invalid_bucket_size(self):
        """测试无效的桶容量"""
        with pytest.raises(ValueError, match="桶容量必须大于0"):
            LeakyBucketConfig(leak_rate=1000, bucket_size=0)
        
        with pytest.raises(ValueError, match="桶容量必须大于0"):
            LeakyBucketConfig(leak_rate=1000, bucket_size=-100)
    
    def test_invalid_output_interval(self):
        """测试无效的输出间隔"""
        with pytest.raises(ValueError, match="输出间隔必须大于0"):
            LeakyBucketConfig(leak_rate=1000, bucket_size=5000, output_interval=0)
        
        with pytest.raises(ValueError, match="输出间隔必须大于0"):
            LeakyBucketConfig(leak_rate=1000, bucket_size=5000, output_interval=-0.1)


class TestLeakyBucket:
    """漏桶算法测试"""
    
    def test_initialization(self):
        """测试初始化"""
        config = LeakyBucketConfig(leak_rate=1000.0, bucket_size=5000)
        bucket = LeakyBucket(config)
        
        assert bucket.name == "LeakyBucket"
        assert bucket.config == config
        assert bucket.get_current_volume() == 0
        assert bucket.is_empty()
        assert bucket.get_queue_size() == 0
        assert bucket.get_fill_ratio() == 0.0
    
    def test_basic_packet_processing(self):
        """测试基本数据包处理"""
        config = LeakyBucketConfig(leak_rate=1000.0, bucket_size=5000)
        bucket = LeakyBucket(config)
        
        # 创建测试数据包
        packet = Packet(id=1, size=1000)
        
        # 应该能成功入队
        assert bucket.enqueue(packet) is True
        assert bucket.get_queue_size() == 1
        assert bucket.get_current_volume() == pytest.approx(1000, abs=1.0)
        assert bucket.get_fill_ratio() == pytest.approx(0.2, abs=0.04)  # 1000/5000，允许漏出导致的误差
    
    def test_bucket_overflow(self):
        """测试桶溢出情况"""
        config = LeakyBucketConfig(leak_rate=1000.0, bucket_size=2000)
        bucket = LeakyBucket(config)
        
        # 填满桶
        packet1 = Packet(id=1, size=1500)
        assert bucket.enqueue(packet1) is True
        assert bucket.get_current_volume() == pytest.approx(1500, abs=1.0)
        
        # 再添加一个小包，应该成功
        packet2 = Packet(id=2, size=400)
        assert bucket.enqueue(packet2) is True
        assert bucket.get_current_volume() == pytest.approx(1900, abs=1.0)
        
        # 添加一个会导致溢出的包，应该被丢弃
        packet3 = Packet(id=3, size=200)
        assert bucket.enqueue(packet3) is False
        assert bucket.get_current_volume() == pytest.approx(1900, abs=1.0)  # 没有变化
        
        # 验证指标
        metrics = bucket.get_metrics()
        assert metrics['total_packets'] == 3
        assert metrics['dropped_packets'] == 1
        assert metrics['packets_dropped'] == 1
    
    def test_leaking_behavior(self):
        """测试漏出行为"""
        config = LeakyBucketConfig(leak_rate=1000.0, bucket_size=5000)
        bucket = LeakyBucket(config)
        
        # 添加数据包
        packet = Packet(id=1, size=2000)
        assert bucket.enqueue(packet) is True
        assert bucket.get_current_volume() == pytest.approx(2000, abs=1.0)
        
        # 等待一段时间让数据漏出
        time.sleep(1.0)  # 等待1秒
        
        # 检查漏出效果（应该漏出大约1000字节）
        current_volume = bucket.get_current_volume()
        assert 900 < current_volume < 1100  # 允许一定误差
    
    def test_delay_calculation(self):
        """测试延迟计算"""
        config = LeakyBucketConfig(leak_rate=1000.0, bucket_size=5000)
        bucket = LeakyBucket(config)
        
        # 最大延迟应该是桶容量除以漏出速率
        assert bucket.get_max_delay() == 5.0  # 5000/1000 = 5秒
        
        # 添加数据包后检查当前延迟
        packet = Packet(id=1, size=2000)
        bucket.enqueue(packet)
        
        current_delay = bucket.get_current_delay()
        assert current_delay == pytest.approx(2.0, abs=0.1)  # 2000/1000 = 2秒
    
    def test_fill_ratio(self):
        """测试填充比例"""
        config = LeakyBucketConfig(leak_rate=1000.0, bucket_size=1000)
        bucket = LeakyBucket(config)
        
        assert bucket.get_fill_ratio() == 0.0  # 空桶
        
        # 添加数据包
        packet = Packet(id=1, size=500)
        bucket.enqueue(packet)
        
        assert bucket.get_fill_ratio() == pytest.approx(0.5, abs=0.01)  # 半满
        
        # 填满桶
        packet2 = Packet(id=2, size=500)
        bucket.enqueue(packet2)
        
        assert bucket.get_fill_ratio() == pytest.approx(1.0, abs=0.01)  # 满桶
    
    def test_output_scheduling(self):
        """测试输出调度"""
        config = LeakyBucketConfig(
            leak_rate=1000.0, 
            bucket_size=5000,
            output_interval=0.1  # 较大的间隔便于测试
        )
        bucket = LeakyBucket(config)
        
        # 启动调度器
        bucket.start()
        
        try:
            # 添加一些数据包
            for i in range(3):
                packet = Packet(id=i+1, size=800)
                bucket.enqueue(packet)
            
            initial_volume = bucket.get_current_volume()
            assert initial_volume == pytest.approx(2400, abs=2.0)
            
            # 等待调度器工作
            time.sleep(0.5)
            
            # 检查是否有数据被处理
            final_volume = bucket.get_current_volume()
            assert final_volume < initial_volume  # 应该有数据被漏出
            
        finally:
            bucket.stop()
    
    def test_burst_traffic_handling(self):
        """测试突发流量处理"""
        config = LeakyBucketConfig(leak_rate=1000.0, bucket_size=10000)
        bucket = LeakyBucket(config)
        
        # 生成突发流量
        generator = TrafficGenerator()
        burst_packets = generator.generate_burst_traffic(
            num_packets=8,
            packet_size=1200,  # 总共9600字节
            priority=PacketPriority.HIGH
        )
        
        # 突发流量应该能被缓存（因为桶容量足够）
        accepted_count = 0
        for packet in burst_packets:
            if bucket.enqueue(packet):
                accepted_count += 1
        
        assert accepted_count == 8  # 所有包都应该被接受
        assert bucket.get_current_volume() == pytest.approx(9600, abs=2.0)
        assert bucket.get_queue_size() == 8
    
    def test_smooth_output_rate(self):
        """测试输出速率的平滑性"""
        config = LeakyBucketConfig(leak_rate=500.0, bucket_size=2000)
        bucket = LeakyBucket(config)
        
        # 添加数据包
        packet = Packet(id=1, size=1500)
        bucket.enqueue(packet)
        
        # 记录多个时间点的体积
        volumes = []
        times = []
        
        start_time = time.time()
        for i in range(5):
            time.sleep(0.2)  # 每200ms记录一次
            volumes.append(bucket.get_current_volume())
            times.append(time.time() - start_time)
        
        # 检查漏出速率是否接近配置值
        if len(volumes) >= 2:
            # 计算平均漏出速率
            volume_diff = volumes[0] - volumes[-1]
            time_diff = times[-1] - times[0]
            
            if time_diff > 0 and volume_diff > 0:
                actual_rate = volume_diff / time_diff
                expected_rate = config.leak_rate
                
                # 允许20%的误差
                assert 0.8 * expected_rate <= actual_rate <= 1.2 * expected_rate
    
    def test_metrics_calculation(self):
        """测试指标计算"""
        config = LeakyBucketConfig(leak_rate=1000.0, bucket_size=5000)
        bucket = LeakyBucket(config)
        
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
        assert metrics['packets_dropped'] == 1
        assert metrics['packets_queued'] == 2
        
        # 漏桶特定指标
        assert 'current_volume' in metrics
        assert 'fill_ratio' in metrics
        assert 'max_delay' in metrics
        assert 'current_delay' in metrics
        assert metrics['queue_size'] == 2
        assert metrics['total_input_bytes'] == 2500  # 只有前两个包被接受
    
    def test_thread_safety(self):
        """测试线程安全性"""
        import threading
        import random
        
        config = LeakyBucketConfig(leak_rate=5000.0, bucket_size=20000)
        bucket = LeakyBucket(config)
        
        results = []
        
        def worker():
            """工作线程函数"""
            for i in range(5):
                packet = Packet(id=i, size=random.randint(100, 500))
                result = bucket.enqueue(packet)
                results.append(result)
                time.sleep(0.01)  # 小延迟
        
        # 创建多个线程
        threads = []
        for _ in range(3):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        # 验证结果
        assert len(results) == 15  # 3个线程，每个5次操作
        assert any(results)  # 至少有一些操作成功
        
        metrics = bucket.get_metrics()
        assert metrics['total_packets'] == 15
    
    def test_reset_metrics(self):
        """测试指标重置"""
        config = LeakyBucketConfig(leak_rate=1000.0, bucket_size=5000)
        bucket = LeakyBucket(config)
        
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
        assert metrics_after['packets_queued'] == 0
        assert metrics_after['packets_dropped'] == 0
        assert metrics_after['total_input_bytes'] == 0
        assert metrics_after['total_output_bytes'] == pytest.approx(0, abs=0.1)
    
    def test_start_stop_scheduler(self):
        """测试调度器启动和停止"""
        config = LeakyBucketConfig(leak_rate=1000.0, bucket_size=5000)
        bucket = LeakyBucket(config)
        
        # 初始状态应该是停止的
        assert not bucket._running
        
        # 启动调度器
        bucket.start()
        assert bucket._running
        assert bucket._output_scheduler is not None
        assert bucket._output_scheduler.is_alive()
        
        # 停止调度器
        bucket.stop()
        assert not bucket._running
        
        # 等待线程结束
        time.sleep(0.1)
        if bucket._output_scheduler:
            assert not bucket._output_scheduler.is_alive()
    
    def test_string_representations(self):
        """测试字符串表示"""
        config = LeakyBucketConfig(leak_rate=1000.0, bucket_size=5000)
        bucket = LeakyBucket(config)
        
        str_repr = str(bucket)
        assert "LeakyBucket" in str_repr
        assert "1000.0" in str_repr
        assert "5000" in str_repr
        
        repr_str = repr(bucket)
        assert "LeakyBucket" in repr_str
        assert "leak_rate=1000.0" in repr_str
        assert "bucket_size=5000" in repr_str
    
    def test_comparison_with_token_bucket_behavior(self):
        """测试与令牌桶的行为差异"""
        # 这个测试展示漏桶和令牌桶的不同特性
        config = LeakyBucketConfig(leak_rate=1000.0, bucket_size=3000)
        bucket = LeakyBucket(config)
        
        # 漏桶：突发输入会被缓存，但输出是平滑的
        # 添加突发数据
        for i in range(3):
            packet = Packet(id=i+1, size=800)
            result = bucket.enqueue(packet)
            assert result is True  # 漏桶会缓存突发数据
        
        # 检查所有数据都被缓存
        assert bucket.get_current_volume() == pytest.approx(2400, abs=2.0)
        assert bucket.get_queue_size() == 3
        
        # 输出是受速率限制的，不会立即全部输出
        # 这与令牌桶不同，令牌桶可能会立即处理（如果有足够令牌）


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
