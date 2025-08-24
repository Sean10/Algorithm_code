#!/usr/bin/env python3
"""
基础模块的单元测试
"""

import pytest
import time
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from common.base import (
    Packet, PacketPriority, QoSMetrics, 
    TrafficGenerator, current_time_ms, 
    bytes_to_bits, bits_to_bytes
)


class TestPacket:
    """数据包类测试"""
    
    def test_packet_creation(self):
        """测试数据包创建"""
        packet = Packet(id=1, size=1024)
        assert packet.id == 1
        assert packet.size == 1024
        assert packet.priority == PacketPriority.NORMAL
        assert packet.arrival_time > 0
        assert packet.departure_time is None
        assert packet.delay is None
    
    def test_packet_delay_calculation(self):
        """测试延迟计算"""
        packet = Packet(id=1, size=1024)
        initial_time = packet.arrival_time
        
        time.sleep(0.01)  # 等待10ms
        packet.departure_time = time.time()
        
        delay = packet.delay
        assert delay is not None
        assert delay > 0.009  # 应该大于9ms
        assert delay < 0.02   # 应该小于20ms
    
    def test_packet_priority(self):
        """测试数据包优先级"""
        packet_high = Packet(id=1, size=1024, priority=PacketPriority.HIGH)
        packet_low = Packet(id=2, size=512, priority=PacketPriority.LOW)
        
        assert packet_high.priority == PacketPriority.HIGH
        assert packet_low.priority == PacketPriority.LOW


class TestQoSMetrics:
    """QoS指标测试"""
    
    def test_empty_metrics(self):
        """测试空指标"""
        metrics = QoSMetrics()
        assert metrics.total_packets == 0
        assert metrics.dropped_packets == 0
        assert metrics.drop_rate == 0.0
        assert metrics.average_delay == 0.0
        assert metrics.average_jitter == 0.0
    
    def test_metrics_with_packets(self):
        """测试有数据包的指标"""
        metrics = QoSMetrics()
        
        # 创建测试数据包
        packet1 = Packet(id=1, size=1024)
        packet1.departure_time = packet1.arrival_time + 0.01  # 10ms延迟
        
        packet2 = Packet(id=2, size=512)
        packet2.departure_time = packet2.arrival_time + 0.02  # 20ms延迟
        
        # 更新指标
        metrics.update_with_packet(packet1)
        metrics.update_with_packet(packet2)
        
        assert metrics.total_packets == 2
        assert metrics.dropped_packets == 0
        assert metrics.drop_rate == 0.0
        assert 0.01 < metrics.average_delay < 0.02  # 平均延迟在10-20ms之间
        assert metrics.max_delay >= 0.019  # 最大延迟接近20ms
        assert metrics.min_delay <= 0.011  # 最小延迟接近10ms
    
    def test_metrics_with_dropped_packets(self):
        """测试丢包指标"""
        metrics = QoSMetrics()
        
        # 正常包
        packet1 = Packet(id=1, size=1024)
        packet1.departure_time = packet1.arrival_time + 0.01
        metrics.update_with_packet(packet1)
        
        # 丢弃的包
        packet2 = Packet(id=2, size=512)
        metrics.update_with_packet(packet2, dropped=True)
        
        assert metrics.total_packets == 2
        assert metrics.dropped_packets == 1
        assert metrics.drop_rate == 0.5  # 50%丢包率


class TestTrafficGenerator:
    """流量生成器测试"""
    
    def test_single_packet_generation(self):
        """测试单个数据包生成"""
        generator = TrafficGenerator()
        packet = generator.generate_packet(1024, PacketPriority.HIGH)
        
        assert packet.id == 1
        assert packet.size == 1024
        assert packet.priority == PacketPriority.HIGH
        assert packet.arrival_time > 0
    
    def test_burst_traffic_generation(self):
        """测试突发流量生成"""
        generator = TrafficGenerator()
        packets = generator.generate_burst_traffic(5, 512, PacketPriority.NORMAL)
        
        assert len(packets) == 5
        for i, packet in enumerate(packets, 1):
            assert packet.id == i
            assert packet.size == 512
            assert packet.priority == PacketPriority.NORMAL
    
    def test_packet_id_increment(self):
        """测试数据包ID递增"""
        generator = TrafficGenerator()
        
        packet1 = generator.generate_packet(100)
        packet2 = generator.generate_packet(200)
        
        assert packet2.id == packet1.id + 1


class TestUtilityFunctions:
    """工具函数测试"""
    
    def test_current_time_ms(self):
        """测试毫秒时间获取"""
        time_ms = current_time_ms()
        assert isinstance(time_ms, int)
        assert time_ms > 0
        
        # 测试时间递增
        time.sleep(0.001)
        time_ms2 = current_time_ms()
        assert time_ms2 >= time_ms
    
    def test_bytes_to_bits(self):
        """测试字节到比特转换"""
        assert bytes_to_bits(1) == 8
        assert bytes_to_bits(0) == 0
        assert bytes_to_bits(1024) == 8192
    
    def test_bits_to_bytes(self):
        """测试比特到字节转换"""
        assert bits_to_bytes(8) == 1
        assert bits_to_bytes(0) == 0
        assert bits_to_bytes(8192) == 1024
        assert bits_to_bytes(9) == 1  # 整数除法


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
