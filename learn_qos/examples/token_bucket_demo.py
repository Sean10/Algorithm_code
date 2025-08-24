#!/usr/bin/env python3
"""
令牌桶算法演示

这个示例展示了令牌桶算法的基本使用方法和特性验证
"""

import sys
import os
import time
import random
import matplotlib.pyplot as plt
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from algorithms.token_bucket import TokenBucket, TokenBucketConfig
from common.base import Packet, PacketPriority, TrafficGenerator


def demo_basic_usage():
    """演示基本使用方法"""
    print("🪣 令牌桶算法 - 基本使用演示")
    print("=" * 50)
    
    # 创建令牌桶配置
    config = TokenBucketConfig(
        token_rate=1000.0,  # 1000 tokens/s
        bucket_size=5000,   # 5000 tokens容量
        initial_tokens=5000,
        token_size=1        # 1 token = 1 byte
    )
    
    print(f"📋 配置:")
    print(f"   令牌生成速率: {config.token_rate} tokens/s")
    print(f"   桶容量: {config.bucket_size} tokens")
    print(f"   初始令牌数: {config.initial_tokens} tokens")
    
    # 创建令牌桶
    bucket = TokenBucket(config)
    print(f"\n🪣 {bucket}")
    
    # 创建流量生成器
    generator = TrafficGenerator()
    
    print(f"\n📦 处理数据包:")
    
    # 处理一些数据包
    for i in range(5):
        size = random.randint(500, 1500)
        packet = generator.generate_packet(size, PacketPriority.NORMAL)
        
        success = bucket.enqueue(packet)
        current_tokens = bucket.get_current_tokens()
        
        print(f"   包{packet.id}: {size}字节, "
              f"处理{'成功' if success else '失败'}, "
              f"剩余令牌: {current_tokens:.0f}")
    
    # 显示最终指标
    print(f"\n📈 性能指标:")
    metrics = bucket.get_metrics()
    print(f"   总数据包: {metrics['total_packets']}")
    print(f"   通过数据包: {metrics['packets_passed']}")
    print(f"   丢弃数据包: {metrics['packets_dropped']}")
    print(f"   丢包率: {metrics['drop_rate']*100:.1f}%")
    print(f"   令牌填充比例: {metrics['token_fill_ratio']*100:.1f}%")


def demo_burst_handling():
    """演示突发流量处理"""
    print(f"\n💥 突发流量处理演示")
    print("=" * 30)
    
    # 小桶配置，更容易看到突发效果
    config = TokenBucketConfig(
        token_rate=500.0,   # 500 tokens/s
        bucket_size=3000,   # 3000 tokens容量
        token_size=1
    )
    
    bucket = TokenBucket(config)
    generator = TrafficGenerator()
    
    print(f"🪣 配置: {bucket}")
    print(f"   桶容量允许的最大突发: {config.bucket_size} 字节")
    
    # 测试突发能力
    burst_sizes = [2000, 3000, 4000, 5000]
    
    print(f"\n🔍 突发能力测试:")
    for burst_size in burst_sizes:
        can_handle = bucket.can_handle_burst(burst_size)
        print(f"   {burst_size}字节突发: {'✅ 可处理' if can_handle else '❌ 无法处理'}")
    
    # 生成突发流量
    print(f"\n💥 生成突发流量:")
    burst_packets = generator.generate_burst_traffic(
        num_packets=6,
        packet_size=800,  # 总共4800字节
        priority=PacketPriority.HIGH
    )
    
    successful_packets = 0
    for packet in burst_packets:
        success = bucket.enqueue(packet)
        if success:
            successful_packets += 1
        
        print(f"   包{packet.id}: {packet.size}字节, "
              f"{'✅' if success else '❌'}, "
              f"剩余令牌: {bucket.get_current_tokens():.0f}")
    
    print(f"\n📊 突发处理结果:")
    print(f"   突发包总数: {len(burst_packets)}")
    print(f"   成功处理: {successful_packets}")
    print(f"   成功率: {successful_packets/len(burst_packets)*100:.1f}%")


def demo_token_regeneration():
    """演示令牌重新生成"""
    print(f"\n🔄 令牌重新生成演示")
    print("=" * 30)
    
    config = TokenBucketConfig(
        token_rate=1000.0,  # 1000 tokens/s
        bucket_size=2000,   # 2000 tokens容量
        token_size=1
    )
    
    bucket = TokenBucket(config)
    generator = TrafficGenerator()
    
    print(f"🪣 {bucket}")
    print(f"   令牌生成速率: {config.token_rate} tokens/s")
    
    # 耗尽所有令牌
    print(f"\n🗑️ 耗尽所有令牌:")
    big_packet = generator.generate_packet(2000, PacketPriority.HIGH)
    success = bucket.enqueue(big_packet)
    print(f"   处理2000字节大包: {'✅' if success else '❌'}")
    print(f"   剩余令牌: {bucket.get_current_tokens():.0f}")
    
    # 尝试处理新包（应该失败）
    print(f"\n❌ 令牌耗尽时的处理:")
    small_packet = generator.generate_packet(500, PacketPriority.NORMAL)
    success = bucket.enqueue(small_packet)
    print(f"   处理500字节包: {'✅' if success else '❌'} (预期失败)")
    
    # 等待令牌重新生成
    print(f"\n⏰ 等待令牌重新生成...")
    time_steps = [0.5, 1.0, 1.5, 2.0]
    
    for wait_time in time_steps:
        time.sleep(0.5)  # 每次等待0.5秒
        current_tokens = bucket.get_current_tokens()
        expected_tokens = min(config.bucket_size, wait_time * config.token_rate)
        print(f"   {wait_time:.1f}秒后: {current_tokens:.0f} tokens "
              f"(期望约{expected_tokens:.0f})")
        
        # 尝试处理包
        test_packet = generator.generate_packet(400, PacketPriority.NORMAL)
        can_process = bucket.can_handle_burst(400)
        print(f"   现在能处理400字节包: {'✅' if can_process else '❌'}")


def demo_rate_limiting():
    """演示速率限制效果"""
    print(f"\n🚦 速率限制效果演示")
    print("=" * 30)
    
    # 不同速率的令牌桶
    configs = [
        TokenBucketConfig(token_rate=500.0, bucket_size=1000, token_size=1),
        TokenBucketConfig(token_rate=1000.0, bucket_size=2000, token_size=1),
        TokenBucketConfig(token_rate=2000.0, bucket_size=4000, token_size=1),
    ]
    
    buckets = [TokenBucket(config) for config in configs]
    generator = TrafficGenerator()
    
    # 生成相同的测试流量
    test_packets = [
        generator.generate_packet(800, PacketPriority.NORMAL)
        for _ in range(10)
    ]
    
    print(f"📊 处理相同流量的不同速率限制效果:")
    print(f"   测试流量: {len(test_packets)}个包，每包800字节")
    
    for i, bucket in enumerate(buckets):
        print(f"\n🪣 令牌桶{i+1} (速率: {bucket.config.token_rate} tokens/s):")
        
        passed = 0
        dropped = 0
        
        for packet in test_packets:
            # 重新创建包避免时间戳问题
            new_packet = generator.generate_packet(packet.size, packet.priority)
            if bucket.enqueue(new_packet):
                passed += 1
            else:
                dropped += 1
        
        print(f"   通过: {passed}个包")
        print(f"   丢弃: {dropped}个包")
        print(f"   通过率: {passed/(passed+dropped)*100:.1f}%")
        print(f"   剩余令牌: {bucket.get_current_tokens():.0f}")


def demo_with_visualization():
    """带可视化的演示"""
    print(f"\n📈 可视化演示")
    print("=" * 20)
    
    config = TokenBucketConfig(
        token_rate=1000.0,
        bucket_size=3000,
        token_size=1
    )
    
    bucket = TokenBucket(config)
    generator = TrafficGenerator()
    
    # 记录数据用于可视化
    times = []
    tokens = []
    packets_processed = []
    packet_sizes = []
    
    start_time = time.time()
    
    print("🎬 开始模拟...")
    
    # 模拟一段时间的流量处理
    for i in range(20):
        # 随机生成数据包
        if random.random() < 0.7:  # 70%概率生成包
            size = random.randint(200, 1000)
            packet = generator.generate_packet(size, PacketPriority.NORMAL)
            success = bucket.enqueue(packet)
        else:
            success = False
            size = 0
        
        # 记录状态
        current_time = time.time() - start_time
        times.append(current_time)
        tokens.append(bucket.get_current_tokens())
        packets_processed.append(1 if success else 0)
        packet_sizes.append(size if success else 0)
        
        time.sleep(0.1)  # 等待100ms
    
    # 创建可视化图表
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle('令牌桶算法演示', fontsize=16, fontweight='bold')
    
    # 令牌数量变化
    ax1.plot(times, tokens, 'b-', linewidth=2, label='令牌数量')
    ax1.axhline(y=config.bucket_size, color='r', linestyle='--', alpha=0.7, label='桶容量')
    ax1.set_ylabel('令牌数量')
    ax1.set_title('令牌数量随时间变化')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 数据包处理情况
    colors = ['green' if p else 'red' for p in packets_processed]
    ax2.scatter(times, packets_processed, c=colors, alpha=0.7, s=50)
    ax2.set_ylabel('包处理状态')
    ax2.set_title('数据包处理情况 (绿色=成功, 红色=丢弃)')
    ax2.set_ylim(-0.2, 1.2)
    ax2.grid(True, alpha=0.3)
    
    # 包大小分布
    processed_times = [t for t, success in zip(times, packets_processed) if success]
    processed_sizes = [s for s, success in zip(packet_sizes, packets_processed) if success]
    
    if processed_sizes:
        ax3.bar(range(len(processed_sizes)), processed_sizes, alpha=0.7, color='blue')
        ax3.set_ylabel('数据包大小 (字节)')
        ax3.set_xlabel('成功处理的数据包')
        ax3.set_title('成功处理的数据包大小')
        ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图表
    output_file = '/Users/sean10/Code/Algorithm_code/learn_qos/token_bucket_demo.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"📊 可视化图表已保存至: {output_file}")
    
    # 显示最终统计
    metrics = bucket.get_metrics()
    print(f"\n📈 最终统计:")
    print(f"   总处理时间: {times[-1]:.1f}秒")
    print(f"   总数据包: {metrics['total_packets']}")
    print(f"   成功处理: {metrics['packets_passed']}")
    print(f"   丢弃数量: {metrics['packets_dropped']}")
    print(f"   成功率: {(metrics['packets_passed']/metrics['total_packets']*100 if metrics['total_packets'] > 0 else 0):.1f}%")
    print(f"   平均处理速率: {metrics['average_processing_rate']:.1f} tokens/s")
    
    plt.show()


def main():
    """主函数"""
    print("🚀 令牌桶算法完整演示")
    print("=" * 60)
    
    # 运行所有演示
    demo_basic_usage()
    demo_burst_handling()
    demo_token_regeneration()
    demo_rate_limiting()
    
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
    print(f"🎯 下一步建议:")
    print(f"   1. 运行单元测试: pytest tests/test_token_bucket.py -v")
    print(f"   2. 查看算法理论: docs/algorithms/token_bucket.md")
    print(f"   3. 尝试不同的配置参数")
    print(f"   4. 开始学习漏桶算法进行对比")


if __name__ == "__main__":
    main()
