#!/usr/bin/env python3
"""
QoS算法基本使用示例

这个示例演示了如何使用QoS算法框架的基础功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from common.base import Packet, PacketPriority, TrafficGenerator, QoSMetrics

def main():
    """主函数 - 演示基础用法"""
    
    print("🚀 QoS学习项目 - 基础使用示例")
    print("=" * 50)
    
    # 1. 创建流量生成器
    print("\n📦 1. 创建流量生成器")
    traffic_gen = TrafficGenerator()
    
    # 2. 生成不同优先级的数据包
    print("\n📊 2. 生成测试数据包")
    packets = [
        traffic_gen.generate_packet(1024, PacketPriority.HIGH),
        traffic_gen.generate_packet(512, PacketPriority.NORMAL),
        traffic_gen.generate_packet(2048, PacketPriority.LOW),
        traffic_gen.generate_packet(800, PacketPriority.URGENT),
    ]
    
    for packet in packets:
        print(f"   包ID: {packet.id}, 大小: {packet.size}字节, 优先级: {packet.priority.name}")
    
    # 3. 模拟数据包处理（设置departure_time）
    print("\n⏱️  3. 模拟数据包处理")
    import time
    for i, packet in enumerate(packets):
        time.sleep(0.001 * (i + 1))  # 模拟不同的处理时间
        packet.departure_time = time.time()
        print(f"   包{packet.id}处理完成，延迟: {packet.delay*1000:.2f}ms")
    
    # 4. 计算QoS指标
    print("\n📈 4. 计算性能指标")
    metrics = QoSMetrics()
    
    for packet in packets:
        metrics.update_with_packet(packet)
    
    print(f"   总数据包数: {metrics.total_packets}")
    print(f"   平均延迟: {metrics.average_delay*1000:.2f}ms")
    print(f"   最大延迟: {metrics.max_delay*1000:.2f}ms")
    print(f"   最小延迟: {metrics.min_delay*1000:.2f}ms")
    print(f"   平均抖动: {metrics.average_jitter*1000:.2f}ms")
    print(f"   丢包率: {metrics.drop_rate*100:.2f}%")
    
    # 5. 生成突发流量
    print("\n💥 5. 生成突发流量测试")
    burst_packets = traffic_gen.generate_burst_traffic(
        num_packets=10,
        packet_size=1000,
        priority=PacketPriority.HIGH
    )
    
    print(f"   生成{len(burst_packets)}个突发数据包")
    for packet in burst_packets[:3]:  # 只显示前3个
        print(f"   突发包ID: {packet.id}, 大小: {packet.size}字节")
    print("   ...")
    
    print("\n✅ 示例运行完成！")
    print("\n📝 下一步:")
    print("   1. 运行 token_bucket_demo.py 了解令牌桶算法")
    print("   2. 运行 leaky_bucket_demo.py 了解漏桶算法") 
    print("   3. 查看 docs/qos_theory.md 学习理论知识")


if __name__ == "__main__":
    main()
