#!/usr/bin/env python3
"""
漏桶算法演示

这个示例展示了漏桶算法的基本使用方法和特性验证，
并与令牌桶算法进行对比分析。
"""

import sys
import os
import time
import random
import matplotlib.pyplot as plt
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from algorithms.leaky_bucket import LeakyBucket, LeakyBucketConfig
from algorithms.token_bucket import TokenBucket, TokenBucketConfig
from common.base import Packet, PacketPriority, TrafficGenerator


def demo_basic_usage():
    """演示基本使用方法"""
    print("🪣 漏桶算法 - 基本使用演示")
    print("=" * 50)
    
    # 创建漏桶配置
    config = LeakyBucketConfig(
        leak_rate=1000.0,    # 1000 bytes/s
        bucket_size=5000,    # 5000 bytes容量
        output_interval=0.1  # 100ms输出间隔
    )
    
    print(f"📋 配置:")
    print(f"   漏出速率: {config.leak_rate} bytes/s")
    print(f"   桶容量: {config.bucket_size} bytes")
    print(f"   输出间隔: {config.output_interval}s")
    
    # 创建漏桶
    bucket = LeakyBucket(config)
    print(f"\n🪣 {bucket}")
    
    # 创建流量生成器
    generator = TrafficGenerator()
    
    print(f"\n📦 处理数据包:")
    
    # 处理一些数据包
    for i in range(6):
        size = random.randint(800, 1200)
        packet = generator.generate_packet(size, PacketPriority.NORMAL)
        
        success = bucket.enqueue(packet)
        current_volume = bucket.get_current_volume()
        fill_ratio = bucket.get_fill_ratio()
        
        print(f"   包{packet.id}: {size}字节, "
              f"入队{'成功' if success else '失败'}, "
              f"桶容量: {current_volume}字节 ({fill_ratio*100:.1f}%)")
    
    # 显示延迟信息
    print(f"\n⏰ 延迟信息:")
    print(f"   最大可能延迟: {bucket.get_max_delay():.1f}秒")
    print(f"   当前预期延迟: {bucket.get_current_delay():.1f}秒")
    
    # 显示最终指标
    print(f"\n📈 性能指标:")
    metrics = bucket.get_metrics()
    print(f"   总数据包: {metrics['total_packets']}")
    print(f"   入队成功: {metrics['packets_queued']}")
    print(f"   丢弃数据包: {metrics['packets_dropped']}")
    print(f"   丢包率: {metrics['drop_rate']*100:.1f}%")
    print(f"   桶填充比例: {metrics['fill_ratio']*100:.1f}%")


def demo_smooth_output():
    """演示平滑输出特性"""
    print(f"\n🌊 平滑输出特性演示")
    print("=" * 30)
    
    config = LeakyBucketConfig(
        leak_rate=500.0,     # 500 bytes/s
        bucket_size=2000,    # 2000 bytes容量
        output_interval=0.05 # 50ms输出间隔
    )
    
    bucket = LeakyBucket(config)
    generator = TrafficGenerator()
    
    print(f"🪣 配置: {bucket}")
    print(f"   理论最大延迟: {bucket.get_max_delay():.1f}秒")
    
    # 启动输出调度器
    bucket.start()
    
    try:
        # 添加突发数据
        print(f"\n💥 添加突发数据:")
        burst_packets = generator.generate_burst_traffic(
            num_packets=3,
            packet_size=600,  # 总共1800字节
            priority=PacketPriority.HIGH
        )
        
        for packet in burst_packets:
            success = bucket.enqueue(packet)
            print(f"   包{packet.id}: {packet.size}字节, "
                  f"{'✅' if success else '❌'}, "
                  f"桶容量: {bucket.get_current_volume()}字节")
        
        print(f"\n🌊 观察平滑输出过程:")
        print(f"   (数据将以{config.leak_rate} bytes/s的速率平滑输出)")
        
        # 观察输出过程
        start_time = time.time()
        for i in range(8):
            time.sleep(0.5)  # 每500ms观察一次
            
            current_time = time.time() - start_time
            current_volume = bucket.get_current_volume()
            current_delay = bucket.get_current_delay()
            
            print(f"   {current_time:.1f}s: 桶容量={current_volume}字节, "
                  f"预期延迟={current_delay:.1f}s")
            
            if current_volume == 0:
                print(f"   ✅ 所有数据已输出完毕")
                break
    
    finally:
        bucket.stop()


def demo_overflow_behavior():
    """演示溢出行为"""
    print(f"\n💧 溢出行为演示")
    print("=" * 25)
    
    # 小桶配置，容易触发溢出
    config = LeakyBucketConfig(
        leak_rate=200.0,   # 200 bytes/s (较慢)
        bucket_size=1000,  # 1000 bytes (较小)
        output_interval=0.1
    )
    
    bucket = LeakyBucket(config)
    generator = TrafficGenerator()
    
    print(f"🪣 小桶配置: {bucket}")
    print(f"   容量限制: {config.bucket_size} bytes")
    print(f"   漏出速率: {config.leak_rate} bytes/s")
    
    print(f"\n🔄 逐步填充桶:")
    
    # 逐步添加数据包，观察溢出
    packet_sizes = [300, 400, 350, 200, 150]
    
    for i, size in enumerate(packet_sizes, 1):
        packet = generator.generate_packet(size, PacketPriority.NORMAL)
        success = bucket.enqueue(packet)
        
        current_volume = bucket.get_current_volume()
        fill_ratio = bucket.get_fill_ratio()
        
        status = "✅ 成功" if success else "❌ 溢出"
        print(f"   包{i}: {size}字节 → {status}")
        print(f"        桶状态: {current_volume}/{config.bucket_size}字节 "
              f"({fill_ratio*100:.1f}%)")
        
        if not success:
            print(f"        💧 桶已满，数据包被丢弃")
    
    # 显示溢出统计
    metrics = bucket.get_metrics()
    print(f"\n📊 溢出统计:")
    print(f"   尝试入队: {metrics['total_packets']}个包")
    print(f"   成功入队: {metrics['packets_queued']}个包")
    print(f"   溢出丢弃: {metrics['packets_dropped']}个包")
    print(f"   溢出率: {metrics['drop_rate']*100:.1f}%")


def demo_vs_token_bucket():
    """漏桶 vs 令牌桶对比演示"""
    print(f"\n⚖️  漏桶 vs 令牌桶对比演示")
    print("=" * 40)
    
    # 相似的配置参数
    leak_config = LeakyBucketConfig(
        leak_rate=1000.0,
        bucket_size=3000,
        output_interval=0.05
    )
    
    token_config = TokenBucketConfig(
        token_rate=1000.0,
        bucket_size=3000,
        token_size=1
    )
    
    leaky_bucket = LeakyBucket(leak_config)
    token_bucket = TokenBucket(token_config)
    generator = TrafficGenerator()
    
    print(f"📋 测试配置:")
    print(f"   速率: 1000 bytes/s")
    print(f"   容量: 3000 bytes")
    
    # 生成相同的测试流量
    test_packets = [
        generator.generate_packet(800, PacketPriority.NORMAL)
        for _ in range(5)
    ]
    
    print(f"\n🧪 处理相同的突发流量 (5个800字节包):")
    
    # 漏桶处理
    print(f"\n🪣 漏桶算法:")
    leaky_accepted = 0
    leaky_dropped = 0
    
    for packet in test_packets:
        # 创建新包避免时间戳问题
        new_packet = generator.generate_packet(packet.size, packet.priority)
        if leaky_bucket.enqueue(new_packet):
            leaky_accepted += 1
        else:
            leaky_dropped += 1
    
    print(f"   接受: {leaky_accepted}个包")
    print(f"   丢弃: {leaky_dropped}个包")
    print(f"   桶状态: {leaky_bucket.get_current_volume()}字节")
    print(f"   特点: 数据被缓存，将以固定速率输出")
    
    # 令牌桶处理
    print(f"\n🪣 令牌桶算法:")
    token_accepted = 0
    token_dropped = 0
    
    for packet in test_packets:
        # 创建新包避免时间戳问题
        new_packet = generator.generate_packet(packet.size, packet.priority)
        if token_bucket.enqueue(new_packet):
            token_accepted += 1
        else:
            token_dropped += 1
    
    print(f"   接受: {token_accepted}个包")
    print(f"   丢弃: {token_dropped}个包")
    print(f"   令牌状态: {token_bucket.get_current_tokens():.0f}个")
    print(f"   特点: 立即处理，消耗令牌")
    
    print(f"\n🔍 关键差异:")
    print(f"   📤 输出模式:")
    print(f"      漏桶: 平滑输出，固定速率")
    print(f"      令牌桶: 立即输出，允许突发")
    print(f"   ⏱️  延迟特性:")
    print(f"      漏桶: 固定缓冲延迟 ({leaky_bucket.get_current_delay():.1f}s)")
    print(f"      令牌桶: 低延迟或零延迟")
    print(f"   🚀 突发处理:")
    print(f"      漏桶: 缓存突发，平滑输出")
    print(f"      令牌桶: 立即处理突发")


def demo_parameter_effects():
    """演示参数对性能的影响"""
    print(f"\n🎛️  参数影响演示")
    print("=" * 25)
    
    # 不同参数配置
    configs = [
        ("小桶快漏", LeakyBucketConfig(leak_rate=2000.0, bucket_size=1000)),
        ("大桶慢漏", LeakyBucketConfig(leak_rate=500.0, bucket_size=4000)),
        ("平衡配置", LeakyBucketConfig(leak_rate=1000.0, bucket_size=2000)),
    ]
    
    generator = TrafficGenerator()
    
    # 生成测试流量
    test_packets = [
        generator.generate_packet(600, PacketPriority.NORMAL)
        for _ in range(6)
    ]
    
    print(f"📊 不同配置处理相同流量的效果:")
    print(f"   测试流量: {len(test_packets)}个包，每包600字节")
    
    for name, config in configs:
        bucket = LeakyBucket(config)
        
        print(f"\n🪣 {name}:")
        print(f"   配置: 速率={config.leak_rate} bytes/s, 容量={config.bucket_size} bytes")
        print(f"   最大延迟: {bucket.get_max_delay():.1f}秒")
        
        accepted = 0
        dropped = 0
        
        for packet in test_packets:
            new_packet = generator.generate_packet(packet.size, packet.priority)
            if bucket.enqueue(new_packet):
                accepted += 1
            else:
                dropped += 1
        
        print(f"   结果: 接受{accepted}个, 丢弃{dropped}个")
        print(f"   当前延迟: {bucket.get_current_delay():.1f}秒")
        print(f"   填充率: {bucket.get_fill_ratio()*100:.1f}%")


def demo_with_visualization():
    """带可视化的演示"""
    print(f"\n📈 可视化演示")
    print("=" * 20)
    
    config = LeakyBucketConfig(
        leak_rate=800.0,
        bucket_size=2400,
        output_interval=0.05
    )
    
    bucket = LeakyBucket(config)
    generator = TrafficGenerator()
    
    # 启动调度器
    bucket.start()
    
    try:
        # 记录数据用于可视化
        times = []
        volumes = []
        input_events = []
        
        start_time = time.time()
        
        print("🎬 开始模拟...")
        
        # 模拟过程
        for i in range(30):
            current_time = time.time() - start_time
            
            # 随机生成输入
            if random.random() < 0.4:  # 40%概率生成包
                size = random.randint(200, 600)
                packet = generator.generate_packet(size, PacketPriority.NORMAL)
                success = bucket.enqueue(packet)
                input_events.append((current_time, size if success else 0))
            else:
                input_events.append((current_time, 0))
            
            # 记录状态
            times.append(current_time)
            volumes.append(bucket.get_current_volume())
            
            time.sleep(0.1)  # 100ms间隔
        
        # 创建可视化图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle('漏桶算法演示', fontsize=16, fontweight='bold')
        
        # 桶容量变化
        ax1.plot(times, volumes, 'b-', linewidth=2, label='桶中数据量')
        ax1.axhline(y=config.bucket_size, color='r', linestyle='--', alpha=0.7, label='桶容量')
        ax1.fill_between(times, volumes, alpha=0.3, color='blue')
        ax1.set_ylabel('数据量 (bytes)')
        ax1.set_title('桶中数据量随时间变化')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 输入事件
        input_times = [event[0] for event in input_events if event[1] > 0]
        input_sizes = [event[1] for event in input_events if event[1] > 0]
        
        if input_sizes:
            ax2.scatter(input_times, input_sizes, alpha=0.7, color='green', s=50)
            ax2.set_ylabel('输入包大小 (bytes)')
            ax2.set_xlabel('时间 (秒)')
            ax2.set_title('输入数据包时间分布')
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图表
        output_file = '/Users/sean10/Code/Algorithm_code/learn_qos/leaky_bucket_demo.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"📊 可视化图表已保存至: {output_file}")
        
        # 显示最终统计
        metrics = bucket.get_metrics()
        print(f"\n📈 最终统计:")
        print(f"   运行时间: {times[-1]:.1f}秒")
        print(f"   总数据包: {metrics['total_packets']}")
        print(f"   成功入队: {metrics['packets_queued']}")
        print(f"   丢弃数量: {metrics['packets_dropped']}")
        print(f"   成功率: {(metrics['packets_queued']/metrics['total_packets']*100 if metrics['total_packets'] > 0 else 0):.1f}%")
        print(f"   平均输出速率: {metrics.get('output_rate', 0):.1f} bytes/s")
        
        plt.show()
    
    finally:
        bucket.stop()


def main():
    """主函数"""
    print("🚀 漏桶算法完整演示")
    print("=" * 60)
    
    # 运行所有演示
    demo_basic_usage()
    demo_smooth_output()
    demo_overflow_behavior()
    demo_vs_token_bucket()
    demo_parameter_effects()
    
    # 询问是否运行可视化演示
    print(f"\n" + "=" * 60)
    response = input("是否运行可视化演示? (y/n): ").lower().strip()
    if response in ['y', 'yes', 'Y']:
        try:
            demo_with_visualization()
        except ImportError:
            print("❌ matplotlib未安装，跳过可视化演示")
            print("💡 提示: 运行 'pip install matplotlib' 安装可视化库")
        except Exception as e:
            print(f"❌ 可视化演示出错: {e}")
    
    print(f"\n✅ 演示完成!")
    print(f"🎯 关键学习点:")
    print(f"   1. 漏桶提供固定速率的平滑输出")
    print(f"   2. 输入可以突发，但输出始终平滑")
    print(f"   3. 桶容量决定最大缓冲和延迟")
    print(f"   4. 与令牌桶相比，更适合需要平滑输出的场景")
    print(f"\n📚 下一步建议:")
    print(f"   1. 运行单元测试: pytest tests/test_leaky_bucket.py -v")
    print(f"   2. 查看算法理论: docs/algorithms/leaky_bucket.md")
    print(f"   3. 对比两种算法的适用场景")
    print(f"   4. 开始学习优先级调度算法")


if __name__ == "__main__":
    main()
