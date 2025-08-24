#!/usr/bin/env python3
"""
优先级调度算法的单元测试
"""

import pytest
import time
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from algorithms.priority_scheduling import (
    PriorityScheduler, StrictPriorityScheduler, WeightedRoundRobinScheduler,
    DynamicPriorityScheduler, DeficitRoundRobinScheduler,
    SchedulingStrategy, PriorityConfig, create_priority_scheduler
)
from common.base import Packet, PacketPriority, TrafficGenerator


class TestPriorityConfig:
    """优先级配置测试"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = PriorityConfig(strategy=SchedulingStrategy.STRICT_PRIORITY)
        
        assert config.strategy == SchedulingStrategy.STRICT_PRIORITY
        assert config.max_queue_size == 1000
        assert config.enable_anti_starvation is True
        assert config.weights is not None
        assert len(config.weights) == 4  # 四个优先级
    
    def test_custom_config(self):
        """测试自定义配置"""
        custom_weights = {
            PacketPriority.URGENT: 10,
            PacketPriority.HIGH: 5,
            PacketPriority.NORMAL: 2,
            PacketPriority.LOW: 1
        }
        
        config = PriorityConfig(
            strategy=SchedulingStrategy.WEIGHTED_ROUND_ROBIN,
            max_queue_size=500,
            weights=custom_weights,
            starvation_threshold=3.0
        )
        
        assert config.max_queue_size == 500
        assert config.weights == custom_weights
        assert config.starvation_threshold == 3.0


class TestStrictPriorityScheduler:
    """严格优先级调度器测试"""
    
    def test_initialization(self):
        """测试初始化"""
        scheduler = StrictPriorityScheduler()
        
        assert scheduler.config.strategy == SchedulingStrategy.STRICT_PRIORITY
        assert scheduler.is_empty()
        assert scheduler.get_queue_size() == 0
    
    def test_basic_priority_ordering(self):
        """测试基本优先级排序"""
        scheduler = StrictPriorityScheduler()
        generator = TrafficGenerator()
        
        # 创建不同优先级的数据包
        packets = [
            generator.generate_packet(100, PacketPriority.LOW),
            generator.generate_packet(100, PacketPriority.HIGH),
            generator.generate_packet(100, PacketPriority.NORMAL),
            generator.generate_packet(100, PacketPriority.URGENT)
        ]
        
        # 入队
        for packet in packets:
            assert scheduler.enqueue(packet) is True
        
        assert scheduler.get_queue_size() == 4
        
        # 出队应该按优先级顺序
        dequeued_priorities = []
        while not scheduler.is_empty():
            packet = scheduler.dequeue()
            assert packet is not None
            dequeued_priorities.append(packet.priority)
        
        expected_order = [
            PacketPriority.URGENT,
            PacketPriority.HIGH,
            PacketPriority.NORMAL,
            PacketPriority.LOW
        ]
        
        assert dequeued_priorities == expected_order
    
    def test_same_priority_fifo(self):
        """测试相同优先级的FIFO顺序"""
        scheduler = StrictPriorityScheduler()
        generator = TrafficGenerator()
        
        # 创建相同优先级的数据包
        packets = [
            generator.generate_packet(100, PacketPriority.NORMAL),
            generator.generate_packet(200, PacketPriority.NORMAL),
            generator.generate_packet(300, PacketPriority.NORMAL)
        ]
        
        # 入队
        for packet in packets:
            scheduler.enqueue(packet)
        
        # 出队应该按FIFO顺序
        dequeued_sizes = []
        while not scheduler.is_empty():
            packet = scheduler.dequeue()
            dequeued_sizes.append(packet.size)
        
        assert dequeued_sizes == [100, 200, 300]
    
    def test_queue_overflow(self):
        """测试队列溢出"""
        config = PriorityConfig(
            strategy=SchedulingStrategy.STRICT_PRIORITY,
            max_queue_size=2
        )
        scheduler = StrictPriorityScheduler(config)
        generator = TrafficGenerator()
        
        # 填满队列
        packet1 = generator.generate_packet(100, PacketPriority.NORMAL)
        packet2 = generator.generate_packet(100, PacketPriority.NORMAL)
        packet3 = generator.generate_packet(100, PacketPriority.NORMAL)  # 应该被丢弃
        
        assert scheduler.enqueue(packet1) is True
        assert scheduler.enqueue(packet2) is True
        assert scheduler.enqueue(packet3) is False  # 队列满
        
        assert scheduler.get_queue_size() == 2
        
        # 检查统计信息
        stats = scheduler.get_scheduling_stats()
        assert stats['total_dropped'] == 1


class TestWeightedRoundRobinScheduler:
    """加权轮转调度器测试"""
    
    def test_weighted_scheduling(self):
        """测试加权调度"""
        config = PriorityConfig(
            strategy=SchedulingStrategy.WEIGHTED_ROUND_ROBIN,
            weights={
                PacketPriority.URGENT: 4,
                PacketPriority.HIGH: 2,
                PacketPriority.NORMAL: 1,
                PacketPriority.LOW: 1
            }
        )
        scheduler = WeightedRoundRobinScheduler(config)
        generator = TrafficGenerator()
        
        # 为每个优先级添加多个数据包
        for priority in PacketPriority:
            for i in range(5):
                packet = generator.generate_packet(100, priority)
                scheduler.enqueue(packet)
        
        # 统计各优先级的出队次数
        dequeue_counts = {priority: 0 for priority in PacketPriority}
        
        # 处理一轮（应该按权重比例处理）
        for _ in range(8):  # 4+2+1+1 = 8
            packet = scheduler.dequeue()
            if packet:
                dequeue_counts[packet.priority] += 1
        
        # 验证权重比例
        assert dequeue_counts[PacketPriority.URGENT] == 4
        assert dequeue_counts[PacketPriority.HIGH] == 2
        assert dequeue_counts[PacketPriority.NORMAL] == 1
        assert dequeue_counts[PacketPriority.LOW] == 1
    
    def test_empty_queue_handling(self):
        """测试空队列处理"""
        scheduler = WeightedRoundRobinScheduler()
        generator = TrafficGenerator()
        
        # 只为部分优先级添加数据包
        packet_high = generator.generate_packet(100, PacketPriority.HIGH)
        packet_normal = generator.generate_packet(100, PacketPriority.NORMAL)
        
        scheduler.enqueue(packet_high)
        scheduler.enqueue(packet_normal)
        
        # 应该能正常处理，跳过空队列
        dequeued_packets = []
        while not scheduler.is_empty():
            packet = scheduler.dequeue()
            if packet:
                dequeued_packets.append(packet)
        
        assert len(dequeued_packets) == 2


class TestDynamicPriorityScheduler:
    """动态优先级调度器测试"""
    
    def test_aging_mechanism(self):
        """测试老化机制"""
        config = PriorityConfig(
            strategy=SchedulingStrategy.DYNAMIC_PRIORITY,
            aging_factor=1.0  # 较大的老化因子便于测试
        )
        scheduler = DynamicPriorityScheduler(config)
        generator = TrafficGenerator()
        
        # 先添加低优先级数据包
        low_packet = generator.generate_packet(100, PacketPriority.LOW)
        scheduler.enqueue(low_packet)
        
        # 等待一段时间
        time.sleep(0.1)
        
        # 再添加高优先级数据包
        high_packet = generator.generate_packet(100, PacketPriority.HIGH)
        scheduler.enqueue(high_packet)
        
        # 由于老化，低优先级数据包可能会被优先处理
        first_packet = scheduler.dequeue()
        
        # 验证动态优先级计算有效
        assert first_packet is not None
    
    def test_load_based_adjustment(self):
        """测试基于负载的调整"""
        scheduler = DynamicPriorityScheduler()
        generator = TrafficGenerator()
        
        # 添加大量数据包增加系统负载
        for _ in range(50):
            for priority in PacketPriority:
                packet = generator.generate_packet(100, priority)
                scheduler.enqueue(packet)
        
        # 在高负载下，动态优先级应该有所调整
        packet = scheduler.dequeue()
        assert packet is not None


class TestDeficitRoundRobinScheduler:
    """缺额轮转调度器测试"""
    
    def test_variable_packet_sizes(self):
        """测试可变长度数据包处理"""
        config = PriorityConfig(
            strategy=SchedulingStrategy.DEFICIT_ROUND_ROBIN,
            quantum_size=1000
        )
        scheduler = DeficitRoundRobinScheduler(config)
        generator = TrafficGenerator()
        
        # 添加不同大小的数据包
        packets = [
            generator.generate_packet(500, PacketPriority.HIGH),   # 小包
            generator.generate_packet(1500, PacketPriority.HIGH),  # 大包
            generator.generate_packet(800, PacketPriority.NORMAL), # 中包
        ]
        
        for packet in packets:
            scheduler.enqueue(packet)
        
        # DRR应该能公平处理不同大小的数据包
        dequeued_count = 0
        while not scheduler.is_empty():
            packet = scheduler.dequeue()
            if packet:
                dequeued_count += 1
        
        assert dequeued_count == 3
    
    def test_deficit_counter_management(self):
        """测试信用额度管理"""
        config = PriorityConfig(
            strategy=SchedulingStrategy.DEFICIT_ROUND_ROBIN,
            quantum_size=500,  # 较小的量子大小
            weights={
                PacketPriority.HIGH: 2,
                PacketPriority.NORMAL: 1,
                PacketPriority.LOW: 1,
                PacketPriority.URGENT: 4
            }
        )
        scheduler = DeficitRoundRobinScheduler(config)
        generator = TrafficGenerator()
        
        # 添加一些数据包
        for priority in [PacketPriority.HIGH, PacketPriority.NORMAL]:
            for _ in range(3):
                packet = generator.generate_packet(400, priority)
                scheduler.enqueue(packet)
        
        # 处理数据包，验证信用额度机制
        processed_count = 0
        max_iterations = 10  # 防止无限循环
        
        while not scheduler.is_empty() and processed_count < max_iterations:
            packet = scheduler.dequeue()
            if packet:
                processed_count += 1
        
        assert processed_count > 0


class TestSchedulerFactory:
    """调度器工厂测试"""
    
    def test_create_all_schedulers(self):
        """测试创建所有类型的调度器"""
        strategies = [
            SchedulingStrategy.STRICT_PRIORITY,
            SchedulingStrategy.WEIGHTED_ROUND_ROBIN,
            SchedulingStrategy.DYNAMIC_PRIORITY,
            SchedulingStrategy.DEFICIT_ROUND_ROBIN
        ]
        
        for strategy in strategies:
            scheduler = create_priority_scheduler(strategy)
            assert scheduler is not None
            assert scheduler.config.strategy == strategy
            
            # 测试基本功能
            generator = TrafficGenerator()
            packet = generator.generate_packet(100, PacketPriority.NORMAL)
            
            assert scheduler.enqueue(packet) is True
            assert scheduler.get_queue_size() == 1
            
            dequeued_packet = scheduler.dequeue()
            assert dequeued_packet is not None
            assert dequeued_packet.id == packet.id


class TestAntiStarvationMechanism:
    """防饥饿机制测试"""
    
    def test_starvation_detection(self):
        """测试饥饿检测"""
        config = PriorityConfig(
            strategy=SchedulingStrategy.STRICT_PRIORITY,
            enable_anti_starvation=True,
            starvation_threshold=0.1  # 很短的阈值便于测试
        )
        scheduler = StrictPriorityScheduler(config)
        generator = TrafficGenerator()
        
        # 添加低优先级数据包
        low_packet = generator.generate_packet(100, PacketPriority.LOW)
        scheduler.enqueue(low_packet)
        
        # 等待超过饥饿阈值
        time.sleep(0.15)
        
        # 添加高优先级数据包
        high_packet = generator.generate_packet(100, PacketPriority.HIGH)
        scheduler.enqueue(high_packet)
        
        # 由于防饥饿机制，低优先级数据包应该被优先处理
        first_packet = scheduler.dequeue()
        assert first_packet.priority == PacketPriority.LOW
        
        # 然后处理高优先级数据包
        second_packet = scheduler.dequeue()
        assert second_packet.priority == PacketPriority.HIGH
    
    def test_anti_starvation_disabled(self):
        """测试禁用防饥饿机制"""
        config = PriorityConfig(
            strategy=SchedulingStrategy.STRICT_PRIORITY,
            enable_anti_starvation=False
        )
        scheduler = StrictPriorityScheduler(config)
        generator = TrafficGenerator()
        
        # 添加低优先级数据包
        low_packet = generator.generate_packet(100, PacketPriority.LOW)
        scheduler.enqueue(low_packet)
        
        time.sleep(0.1)
        
        # 添加高优先级数据包
        high_packet = generator.generate_packet(100, PacketPriority.HIGH)
        scheduler.enqueue(high_packet)
        
        # 应该严格按优先级处理
        first_packet = scheduler.dequeue()
        assert first_packet.priority == PacketPriority.HIGH
        
        second_packet = scheduler.dequeue()
        assert second_packet.priority == PacketPriority.LOW


class TestSchedulingStatistics:
    """调度统计测试"""
    
    def test_comprehensive_statistics(self):
        """测试全面的统计信息"""
        scheduler = StrictPriorityScheduler()
        generator = TrafficGenerator()
        
        # 添加各种优先级的数据包
        packet_counts = {
            PacketPriority.URGENT: 2,
            PacketPriority.HIGH: 3,
            PacketPriority.NORMAL: 4,
            PacketPriority.LOW: 1
        }
        
        for priority, count in packet_counts.items():
            for _ in range(count):
                packet = generator.generate_packet(100, priority)
                scheduler.enqueue(packet)
        
        # 处理所有数据包
        while not scheduler.is_empty():
            scheduler.dequeue()
        
        # 检查统计信息
        stats = scheduler.get_scheduling_stats()
        
        assert stats['total_enqueued'] == sum(packet_counts.values())
        assert stats['total_dequeued'] == sum(packet_counts.values())
        assert stats['total_dropped'] == 0
        
        # 检查各优先级统计
        for priority, expected_count in packet_counts.items():
            priority_stats = stats['priority_stats'][priority.name]
            assert priority_stats['enqueued'] == expected_count
            assert priority_stats['dequeued'] == expected_count
            assert priority_stats['drop_rate'] == 0.0


class TestPerformance:
    """性能测试"""
    
    def test_large_scale_processing(self):
        """测试大规模数据包处理"""
        scheduler = StrictPriorityScheduler()
        generator = TrafficGenerator()
        
        # 添加大量数据包
        num_packets = 1000
        start_time = time.time()
        
        for i in range(num_packets):
            priority = list(PacketPriority)[i % 4]
            packet = generator.generate_packet(100, priority)
            scheduler.enqueue(packet)
        
        enqueue_time = time.time() - start_time
        
        # 处理所有数据包
        start_time = time.time()
        processed_count = 0
        
        while not scheduler.is_empty():
            packet = scheduler.dequeue()
            if packet:
                processed_count += 1
        
        dequeue_time = time.time() - start_time
        
        assert processed_count == num_packets
        
        # 性能应该在合理范围内
        assert enqueue_time < 1.0  # 入队应该在1秒内完成
        assert dequeue_time < 1.0  # 出队应该在1秒内完成
        
        print(f"处理{num_packets}个数据包: 入队{enqueue_time:.3f}s, 出队{dequeue_time:.3f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
