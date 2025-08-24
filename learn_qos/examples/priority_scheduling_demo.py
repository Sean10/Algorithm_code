#!/usr/bin/env python3
"""
优先级调度算法演示

展示不同优先级调度策略的工作原理和效果对比
"""

import sys
import os
import time
import random
import threading
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
from typing import List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from algorithms.priority_scheduling import (
    StrictPriorityScheduler, WeightedRoundRobinScheduler,
    DynamicPriorityScheduler, DeficitRoundRobinScheduler,
    SchedulingStrategy, PriorityConfig, create_priority_scheduler
)
from common.base import Packet, PacketPriority, TrafficGenerator


def demo_basic_priority_scheduling():
    """演示基本优先级调度"""
    print("🎯 基本优先级调度演示")
    print("=" * 50)
    
    scheduler = StrictPriorityScheduler()
    generator = TrafficGenerator()
    
    print(f"📋 调度策略: {scheduler.config.strategy.value}")
    print(f"🔧 防饥饿机制: {'启用' if scheduler.config.enable_anti_starvation else '禁用'}")
    
    # 创建不同优先级的数据包
    packets = []
    priorities = [PacketPriority.LOW, PacketPriority.HIGH, PacketPriority.NORMAL, PacketPriority.URGENT]
    
    print(f"\n📦 创建测试数据包:")
    for i, priority in enumerate(priorities):
        packet = generator.generate_packet(random.randint(100, 500), priority)
        packets.append(packet)
        print(f"   包{packet.id}: {packet.size}字节, 优先级={priority.name}")
    
    # 入队
    print(f"\n⬆️  数据包入队:")
    for packet in packets:
        success = scheduler.enqueue(packet)
        print(f"   包{packet.id} ({packet.priority.name}): {'✅ 成功' if success else '❌ 失败'}")
    
    print(f"\n📊 队列状态:")
    queue_sizes = scheduler.get_priority_queue_sizes()
    for priority, size in queue_sizes.items():
        if size > 0:
            print(f"   {priority.name}: {size}个数据包")
    
    # 出队
    print(f"\n⬇️  数据包出队 (按优先级顺序):")
    dequeue_order = []
    while not scheduler.is_empty():
        packet = scheduler.dequeue()
        if packet:
            dequeue_order.append(packet)
            print(f"   包{packet.id}: 优先级={packet.priority.name}, "
                  f"延迟={packet.delay*1000:.1f}ms")
    
    # 分析结果
    print(f"\n📈 处理结果分析:")
    priority_order = [p.priority.name for p in dequeue_order]
    print(f"   处理顺序: {' → '.join(priority_order)}")
    
    # 验证优先级顺序
    expected_order = ['URGENT', 'HIGH', 'NORMAL', 'LOW']
    actual_order = [p.priority.name for p in dequeue_order]
    is_correct = all(
        actual_order.index(p1) <= actual_order.index(p2)
        for p1, p2 in zip(expected_order[:-1], expected_order[1:])
        if p1 in actual_order and p2 in actual_order
    )
    print(f"   优先级顺序: {'✅ 正确' if is_correct else '❌ 错误'}")


def demo_scheduling_strategies_comparison():
    """演示不同调度策略的对比"""
    print(f"\n⚖️  调度策略对比演示")
    print("=" * 40)
    
    # 创建不同策略的调度器
    strategies = [
        (SchedulingStrategy.STRICT_PRIORITY, "严格优先级"),
        (SchedulingStrategy.WEIGHTED_ROUND_ROBIN, "加权轮转"),
        (SchedulingStrategy.DYNAMIC_PRIORITY, "动态优先级"),
        (SchedulingStrategy.DEFICIT_ROUND_ROBIN, "缺额轮转")
    ]
    
    schedulers = []
    for strategy, name in strategies:
        config = PriorityConfig(strategy=strategy)
        scheduler = create_priority_scheduler(strategy, config)
        schedulers.append((scheduler, name))
    
    # 生成相同的测试流量
    generator = TrafficGenerator()
    test_packets = []
    
    # 为每个优先级生成多个数据包
    for priority in PacketPriority:
        for _ in range(5):
            size = random.randint(200, 800)
            packet = generator.generate_packet(size, priority)
            test_packets.append(packet)
    
    print(f"📊 测试流量: {len(test_packets)}个数据包")
    priority_counts = Counter(p.priority.name for p in test_packets)
    for priority, count in priority_counts.items():
        print(f"   {priority}: {count}个")
    
    print(f"\n🔄 各策略处理结果:")
    print(f"{'策略':<15} {'处理顺序':<30} {'平均延迟':<10} {'公平性':<10}")
    print("-" * 70)
    
    for scheduler, name in schedulers:
        # 重新创建数据包副本（避免时间戳问题）
        test_packets_copy = []
        for original_packet in test_packets:
            new_packet = generator.generate_packet(original_packet.size, original_packet.priority)
            test_packets_copy.append(new_packet)
        
        # 入队所有数据包
        for packet in test_packets_copy:
            scheduler.enqueue(packet)
        
        # 出队并记录顺序
        dequeue_order = []
        total_delay = 0.0
        
        while not scheduler.is_empty():
            packet = scheduler.dequeue()
            if packet:
                dequeue_order.append(packet.priority.name)
                if packet.delay:
                    total_delay += packet.delay
        
        # 分析结果
        avg_delay = total_delay / len(dequeue_order) if dequeue_order else 0.0
        
        # 计算处理顺序模式
        order_pattern = " → ".join(dequeue_order[:6]) + ("..." if len(dequeue_order) > 6 else "")
        
        # 计算公平性（各优先级处理比例的方差）
        priority_processed = Counter(dequeue_order)
        fairness_score = min(priority_processed.values()) / max(priority_processed.values()) if priority_processed else 0.0
        
        print(f"{name:<15} {order_pattern:<30} {avg_delay*1000:.1f}ms{'':<5} {fairness_score:.2f}")


def demo_anti_starvation_mechanism():
    """演示防饥饿机制"""
    print(f"\n🛡️  防饥饿机制演示")
    print("=" * 30)
    
    # 创建启用和禁用防饥饿的调度器
    config_with_anti_starvation = PriorityConfig(
        strategy=SchedulingStrategy.STRICT_PRIORITY,
        enable_anti_starvation=True,
        starvation_threshold=0.5  # 0.5秒阈值
    )
    
    config_without_anti_starvation = PriorityConfig(
        strategy=SchedulingStrategy.STRICT_PRIORITY,
        enable_anti_starvation=False
    )
    
    schedulers = [
        (StrictPriorityScheduler(config_with_anti_starvation), "启用防饥饿"),
        (StrictPriorityScheduler(config_without_anti_starvation), "禁用防饥饿")
    ]
    
    generator = TrafficGenerator()
    
    for scheduler, description in schedulers:
        print(f"\n📋 测试场景: {description}")
        
        # 先添加低优先级数据包
        low_packet = generator.generate_packet(100, PacketPriority.LOW)
        scheduler.enqueue(low_packet)
        print(f"   添加低优先级包: 包{low_packet.id}")
        
        # 等待一段时间
        print(f"   等待 0.6秒...")
        time.sleep(0.6)
        
        # 添加高优先级数据包
        high_packet = generator.generate_packet(100, PacketPriority.HIGH)
        scheduler.enqueue(high_packet)
        print(f"   添加高优先级包: 包{high_packet.id}")
        
        # 查看处理顺序
        print(f"   处理顺序:")
        while not scheduler.is_empty():
            packet = scheduler.dequeue()
            if packet:
                print(f"     包{packet.id} ({packet.priority.name})")


def demo_weighted_round_robin():
    """演示加权轮转调度"""
    print(f"\n🔄 加权轮转调度演示")
    print("=" * 30)
    
    # 自定义权重配置
    custom_weights = {
        PacketPriority.URGENT: 4,
        PacketPriority.HIGH: 3,
        PacketPriority.NORMAL: 2,
        PacketPriority.LOW: 1
    }
    
    config = PriorityConfig(
        strategy=SchedulingStrategy.WEIGHTED_ROUND_ROBIN,
        weights=custom_weights
    )
    
    scheduler = WeightedRoundRobinScheduler(config)
    generator = TrafficGenerator()
    
    print(f"⚖️  权重配置:")
    for priority, weight in custom_weights.items():
        print(f"   {priority.name}: {weight}")
    
    # 为每个优先级添加足够的数据包
    print(f"\n📦 添加测试数据包:")
    for priority in PacketPriority:
        for i in range(8):  # 每个优先级8个包
            packet = generator.generate_packet(100, priority)
            scheduler.enqueue(packet)
        print(f"   {priority.name}: 8个数据包")
    
    # 处理一轮并统计
    print(f"\n🔄 处理一轮 (权重总和: {sum(custom_weights.values())}):")
    round_results = []
    
    for round_num in range(3):  # 处理3轮
        print(f"\n   第{round_num + 1}轮:")
        round_count = {priority: 0 for priority in PacketPriority}
        
        # 处理一轮的数据包
        for _ in range(sum(custom_weights.values())):
            packet = scheduler.dequeue()
            if packet:
                round_count[packet.priority] += 1
        
        # 显示这一轮的结果
        for priority, count in round_count.items():
            expected = custom_weights[priority]
            print(f"     {priority.name}: {count}个 (期望{expected}个)")
        
        round_results.append(round_count)
    
    # 验证权重比例
    print(f"\n📊 权重比例验证:")
    total_processed = {priority: sum(round_result[priority] for round_result in round_results) 
                      for priority in PacketPriority}
    
    for priority, total in total_processed.items():
        expected_ratio = custom_weights[priority] / sum(custom_weights.values())
        actual_ratio = total / sum(total_processed.values()) if sum(total_processed.values()) > 0 else 0
        print(f"   {priority.name}: 实际比例{actual_ratio:.2f}, 期望比例{expected_ratio:.2f}")


def demo_dynamic_priority_aging():
    """演示动态优先级老化机制"""
    print(f"\n⏰ 动态优先级老化演示")
    print("=" * 35)
    
    config = PriorityConfig(
        strategy=SchedulingStrategy.DYNAMIC_PRIORITY,
        aging_factor=2.0  # 较大的老化因子便于观察
    )
    
    scheduler = DynamicPriorityScheduler(config)
    generator = TrafficGenerator()
    
    print(f"🔧 配置: 老化因子={config.aging_factor}")
    
    # 创建测试场景
    packets_info = []
    
    # 添加低优先级数据包
    low_packet = generator.generate_packet(100, PacketPriority.LOW)
    scheduler.enqueue(low_packet)
    packets_info.append((low_packet, "低优先级包", time.time()))
    print(f"   添加: 包{low_packet.id} (LOW)")
    
    # 等待一段时间
    time.sleep(0.3)
    
    # 添加普通优先级数据包
    normal_packet = generator.generate_packet(100, PacketPriority.NORMAL)
    scheduler.enqueue(normal_packet)
    packets_info.append((normal_packet, "普通优先级包", time.time()))
    print(f"   添加: 包{normal_packet.id} (NORMAL)")
    
    # 等待一段时间
    time.sleep(0.2)
    
    # 添加高优先级数据包
    high_packet = generator.generate_packet(100, PacketPriority.HIGH)
    scheduler.enqueue(high_packet)
    packets_info.append((high_packet, "高优先级包", time.time()))
    print(f"   添加: 包{high_packet.id} (HIGH)")
    
    print(f"\n🔄 动态调度结果:")
    dequeue_time = time.time()
    
    while not scheduler.is_empty():
        packet = scheduler.dequeue()
        if packet:
            # 找到对应的包信息
            for p, desc, enqueue_time in packets_info:
                if p.id == packet.id:
                    waiting_time = dequeue_time - enqueue_time
                    print(f"   处理: 包{packet.id} ({packet.priority.name}), "
                          f"等待时间: {waiting_time:.2f}s")
                    break


def demo_performance_comparison():
    """演示性能对比"""
    print(f"\n⚡ 性能对比演示")
    print("=" * 25)
    
    strategies = [
        SchedulingStrategy.STRICT_PRIORITY,
        SchedulingStrategy.WEIGHTED_ROUND_ROBIN,
        SchedulingStrategy.DYNAMIC_PRIORITY,
        SchedulingStrategy.DEFICIT_ROUND_ROBIN
    ]
    
    num_packets = 1000
    generator = TrafficGenerator()
    
    print(f"📊 测试规模: {num_packets}个数据包")
    print(f"{'策略':<20} {'入队时间':<10} {'出队时间':<10} {'总时间':<10}")
    print("-" * 50)
    
    for strategy in strategies:
        scheduler = create_priority_scheduler(strategy)
        
        # 生成测试数据包
        test_packets = []
        for _ in range(num_packets):
            priority = random.choice(list(PacketPriority))
            size = random.randint(100, 1500)
            packet = generator.generate_packet(size, priority)
            test_packets.append(packet)
        
        # 测试入队性能
        start_time = time.time()
        for packet in test_packets:
            scheduler.enqueue(packet)
        enqueue_time = time.time() - start_time
        
        # 测试出队性能
        start_time = time.time()
        processed_count = 0
        while not scheduler.is_empty():
            packet = scheduler.dequeue()
            if packet:
                processed_count += 1
        dequeue_time = time.time() - start_time
        
        total_time = enqueue_time + dequeue_time
        
        print(f"{strategy.value:<20} {enqueue_time:.3f}s{'':<4} "
              f"{dequeue_time:.3f}s{'':<4} {total_time:.3f}s")


def demo_with_visualization():
    """带可视化的演示"""
    print(f"\n📈 可视化演示")
    print("=" * 20)
    
    try:
        # 创建测试数据
        scheduler = StrictPriorityScheduler()
        generator = TrafficGenerator()
        
        # 生成混合流量
        packets_data = []
        priorities = list(PacketPriority)
        
        for i in range(50):
            priority = random.choice(priorities)
            size = random.randint(100, 1000)
            packet = generator.generate_packet(size, priority)
            
            # 模拟到达时间
            arrival_time = i * 0.1  # 每100ms一个包
            
            packets_data.append({
                'id': packet.id,
                'priority': priority.name,
                'priority_value': priority.value,
                'size': size,
                'arrival_time': arrival_time
            })
            
            scheduler.enqueue(packet)
        
        # 处理数据包并记录
        processing_data = []
        current_time = 0.0
        
        while not scheduler.is_empty():
            packet = scheduler.dequeue()
            if packet:
                processing_data.append({
                    'id': packet.id,
                    'priority': packet.priority.name,
                    'priority_value': packet.priority.value,
                    'size': packet.size,
                    'processing_time': current_time,
                    'delay': packet.delay * 1000 if packet.delay else 0  # 转换为毫秒
                })
                current_time += 0.05  # 假设每个包处理需要50ms
        
        # 创建可视化
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('优先级调度算法效果分析', fontsize=16, fontweight='bold')
        
        # 1. 到达时间 vs 优先级
        priority_colors = {
            'URGENT': 'red',
            'HIGH': 'orange', 
            'NORMAL': 'blue',
            'LOW': 'green'
        }
        
        for priority in priority_colors:
            priority_packets = [p for p in packets_data if p['priority'] == priority]
            if priority_packets:
                arrival_times = [p['arrival_time'] for p in priority_packets]
                priority_values = [p['priority_value'] for p in priority_packets]
                ax1.scatter(arrival_times, priority_values, 
                           c=priority_colors[priority], label=priority, alpha=0.7)
        
        ax1.set_xlabel('到达时间 (秒)')
        ax1.set_ylabel('优先级')
        ax1.set_title('数据包到达模式')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 处理顺序
        processing_order = [p['priority_value'] for p in processing_data]
        ax2.plot(range(len(processing_order)), processing_order, 'b-', alpha=0.7)
        ax2.set_xlabel('处理顺序')
        ax2.set_ylabel('优先级')
        ax2.set_title('数据包处理顺序')
        ax2.grid(True, alpha=0.3)
        
        # 3. 优先级分布
        priority_counts = Counter(p['priority'] for p in packets_data)
        priorities = list(priority_counts.keys())
        counts = list(priority_counts.values())
        colors = [priority_colors[p] for p in priorities]
        
        ax3.bar(priorities, counts, color=colors, alpha=0.7)
        ax3.set_xlabel('优先级')
        ax3.set_ylabel('数据包数量')
        ax3.set_title('优先级分布')
        ax3.grid(True, alpha=0.3)
        
        # 4. 延迟分析
        for priority in priority_colors:
            priority_delays = [p['delay'] for p in processing_data if p['priority'] == priority]
            if priority_delays:
                ax4.hist(priority_delays, bins=10, alpha=0.6, 
                        label=priority, color=priority_colors[priority])
        
        ax4.set_xlabel('延迟 (毫秒)')
        ax4.set_ylabel('频次')
        ax4.set_title('延迟分布')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图表
        output_file = '/Users/sean10/Code/Algorithm_code/learn_qos/priority_scheduling_demo.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"📊 可视化图表已保存至: {output_file}")
        
        # 显示统计信息
        print(f"\n📈 统计分析:")
        print(f"   总数据包: {len(packets_data)}")
        print(f"   处理完成: {len(processing_data)}")
        
        avg_delays = {}
        for priority in priority_colors:
            priority_delays = [p['delay'] for p in processing_data if p['priority'] == priority]
            if priority_delays:
                avg_delays[priority] = sum(priority_delays) / len(priority_delays)
        
        print(f"   平均延迟:")
        for priority, delay in avg_delays.items():
            print(f"     {priority}: {delay:.1f}ms")
        
        plt.show()
        
    except ImportError:
        print("❌ matplotlib未安装，跳过可视化演示")
    except Exception as e:
        print(f"❌ 可视化演示出错: {e}")


def main():
    """主函数"""
    print("🚀 优先级调度算法完整演示")
    print("=" * 80)
    
    try:
        # 1. 基本优先级调度演示
        demo_basic_priority_scheduling()
        
        # 2. 调度策略对比
        demo_scheduling_strategies_comparison()
        
        # 3. 防饥饿机制演示
        demo_anti_starvation_mechanism()
        
        # 4. 加权轮转调度演示
        demo_weighted_round_robin()
        
        # 5. 动态优先级老化演示
        demo_dynamic_priority_aging()
        
        # 6. 性能对比
        demo_performance_comparison()
        
        # 7. 可视化演示
        print(f"\n" + "=" * 80)
        response = input("是否运行可视化演示? (y/n): ").lower().strip()
        if response in ['y', 'yes', 'Y']:
            demo_with_visualization()
        
        print(f"\n✅ 演示完成!")
        print(f"\n🎯 关键学习点:")
        print(f"   1. 严格优先级确保高优先级流量的低延迟")
        print(f"   2. 加权轮转避免低优先级流量饥饿")
        print(f"   3. 动态优先级通过老化机制提高公平性")
        print(f"   4. 防饥饿机制是保证系统公平性的重要手段")
        print(f"   5. 不同策略适用于不同的应用场景")
        
        print(f"\n📚 应用建议:")
        print(f"   - 实时系统: 使用严格优先级调度")
        print(f"   - 多媒体应用: 使用加权轮转调度") 
        print(f"   - 通用系统: 使用动态优先级调度")
        print(f"   - 大数据处理: 使用缺额轮转调度")
        
        print(f"\n📝 下一步建议:")
        print(f"   1. 运行单元测试: pytest tests/test_priority_scheduling.py -v")
        print(f"   2. 尝试调整权重和参数配置")
        print(f"   3. 集成到实际应用中测试效果")
        print(f"   4. 学习加权公平队列(WFQ)算法")
        
    except KeyboardInterrupt:
        print(f"\n演示被用户中断")
    except Exception as e:
        print(f"演示过程中出现错误: {e}")


if __name__ == "__main__":
    main()
