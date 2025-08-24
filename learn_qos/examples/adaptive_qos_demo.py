#!/usr/bin/env python3
"""
负载感知自适应限流系统演示

展示客户端和服务端协同工作的自适应QoS系统，
包括负载监控、反馈传输和自适应限流的完整流程。
"""

import sys
import os
import time
import threading
import random
import matplotlib.pyplot as plt
from typing import List, Dict, Any
from collections import defaultdict
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from algorithms.adaptive_qos import (
    LoadMonitor, AdaptiveRateLimiter, AIMDRateLimiter, 
    PIDRateLimiter, FeedbackGenerator, FeedbackReceiver,
    FeedbackSystem, AdaptiveStrategy, create_adaptive_limiter
)
from common.base import Packet, TrafficGenerator


class MockServer:
    """模拟服务器"""
    
    def __init__(self, server_id: str, base_capacity: float = 100.0):
        self.server_id = server_id
        self.base_capacity = base_capacity
        self.load_monitor = LoadMonitor(sample_interval=0.5)
        self.feedback_generator = FeedbackGenerator(
            server_id, self.load_monitor, base_capacity
        )
        
        # 模拟负载生成
        self._background_load = 0.0
        self._load_thread = None
        self._stop_simulation = threading.Event()
    
    def start(self):
        """启动服务器"""
        self.load_monitor.start_monitoring()
        self._start_load_simulation()
    
    def stop(self):
        """停止服务器"""
        self.load_monitor.stop_monitoring()
        self._stop_load_simulation()
    
    def _start_load_simulation(self):
        """启动负载模拟"""
        self._stop_simulation.clear()
        self._load_thread = threading.Thread(target=self._simulate_background_load, daemon=True)
        self._load_thread.start()
    
    def _stop_load_simulation(self):
        """停止负载模拟"""
        self._stop_simulation.set()
        if self._load_thread:
            self._load_thread.join(timeout=1.0)
    
    def _simulate_background_load(self):
        """模拟后台负载变化"""
        while not self._stop_simulation.is_set():
            # 模拟负载波动
            self._background_load += random.uniform(-0.1, 0.1)
            self._background_load = max(0.0, min(1.0, self._background_load))
            
            # 模拟一些系统事件导致的负载突增
            if random.random() < 0.05:  # 5%概率
                self._background_load = min(1.0, self._background_load + random.uniform(0.2, 0.5))
            
            time.sleep(1.0)
    
    def process_request(self, client_id: str) -> Dict[str, Any]:
        """处理客户端请求"""
        # 记录请求开始
        start_time = time.time()
        self.load_monitor.record_request_start()
        
        # 模拟处理时间（受负载影响）
        current_load = self.load_monitor.get_current_metrics()
        if current_load:
            load_factor = max(0.1, 1.0 - current_load.cpu_usage)
            processing_time = (1.0 / load_factor) * random.uniform(0.01, 0.05)
        else:
            processing_time = random.uniform(0.01, 0.03)
        
        # 模拟处理延迟
        time.sleep(processing_time)
        
        # 记录请求结束
        response_time_ms = (time.time() - start_time) * 1000
        is_error = random.random() < 0.02  # 2%错误率
        self.load_monitor.record_request_end(response_time_ms, is_error)
        
        # 生成反馈
        feedback_headers = self.feedback_generator.get_feedback_for_http_headers(client_id)
        
        return {
            'status': 'error' if is_error else 'success',
            'response_time_ms': response_time_ms,
            'feedback_headers': feedback_headers,
            'data': f"Response from {self.server_id}"
        }


class MockClient:
    """模拟客户端"""
    
    def __init__(self, client_id: str, strategy: AdaptiveStrategy = AdaptiveStrategy.AIMD):
        self.client_id = client_id
        self.strategy = strategy
        
        # 自适应限流器
        self.rate_limiter = create_adaptive_limiter(
            strategy,
            initial_rate=50.0,
            min_rate=1.0,
            max_rate=200.0
        )
        
        # 反馈接收器
        self.feedback_receiver = FeedbackReceiver(client_id, feedback_timeout=5.0)
        self.feedback_receiver.add_feedback_callback(self._handle_feedback)
        
        # 请求统计
        self.total_requests = 0
        self.successful_requests = 0
        self.total_response_time = 0.0
        self.rate_history = []
        self.load_level_history = []
        
        self._lock = threading.Lock()
    
    def _handle_feedback(self, feedback):
        """处理接收到的负载反馈"""
        # 调整发送速率
        load_info = {
            'load_level': feedback.load_level.value,
            'load_score': feedback.load_score,
            'trend': feedback.trend
        }
        
        self.rate_limiter.adjust_rate(load_info)
    
    def send_request(self, server: MockServer) -> Dict[str, Any]:
        """向服务器发送请求"""
        with self._lock:
            self.total_requests += 1
        
        # 处理请求
        response = server.process_request(self.client_id)
        
        # 接收反馈
        self.feedback_receiver.receive_feedback(
            response['feedback_headers'], 
            channel='HTTP_HEADER'
        )
        
        # 更新统计
        with self._lock:
            if response['status'] == 'success':
                self.successful_requests += 1
                self.total_response_time += response['response_time_ms']
            
            # 记录历史
            self.rate_history.append({
                'timestamp': time.time(),
                'rate': self.rate_limiter.get_current_rate()
            })
            
            latest_feedback = self.feedback_receiver.get_latest_feedback()
            if latest_feedback:
                self.load_level_history.append({
                    'timestamp': time.time(),
                    'load_level': latest_feedback.load_level.value,
                    'load_score': latest_feedback.load_score
                })
        
        return response
    
    def get_current_rate(self) -> float:
        """获取当前发送速率"""
        return self.rate_limiter.get_current_rate()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取客户端统计信息"""
        with self._lock:
            success_rate = (
                self.successful_requests / self.total_requests 
                if self.total_requests > 0 else 0.0
            )
            avg_response_time = (
                self.total_response_time / self.successful_requests
                if self.successful_requests > 0 else 0.0
            )
            
            return {
                'client_id': self.client_id,
                'strategy': self.strategy.value,
                'total_requests': self.total_requests,
                'successful_requests': self.successful_requests,
                'success_rate': success_rate,
                'avg_response_time_ms': avg_response_time,
                'current_rate': self.get_current_rate(),
                'rate_adjustments': self.rate_limiter.get_adjustment_stats()
            }


def demo_single_client_server():
    """演示单个客户端和服务端的交互"""
    print("🔄 单客户端-服务端自适应限流演示")
    print("=" * 50)
    
    # 创建服务端和客户端
    server = MockServer("server-1", base_capacity=80.0)
    client = MockClient("client-1", AdaptiveStrategy.AIMD)
    
    server.start()
    
    try:
        print(f"🖥️  服务端: {server.server_id} (容量: {server.base_capacity} req/s)")
        print(f"👤 客户端: {client.client_id} (策略: {client.strategy.value})")
        print(f"📊 初始发送速率: {client.get_current_rate():.1f} req/s")
        
        print(f"\n⏳ 开始发送请求...")
        
        # 模拟请求发送
        for i in range(30):
            current_rate = client.get_current_rate()
            
            # 根据当前速率控制发送间隔
            interval = 1.0 / max(current_rate, 1.0)
            
            response = client.send_request(server)
            
            if i % 5 == 0:  # 每5次请求显示一次状态
                latest_feedback = client.feedback_receiver.get_latest_feedback()
                if latest_feedback:
                    print(f"   第{i+1}次请求: "
                          f"速率={current_rate:.1f} req/s, "
                          f"负载={latest_feedback.load_level.value}, "
                          f"评分={latest_feedback.load_score:.2f}, "
                          f"响应时间={response['response_time_ms']:.1f}ms")
            
            time.sleep(interval)
        
        # 显示最终统计
        print(f"\n📈 最终统计:")
        client_stats = client.get_stats()
        for key, value in client_stats.items():
            if key != 'rate_adjustments':
                print(f"   {key}: {value}")
        
        print(f"\n🔧 速率调整统计:")
        rate_stats = client_stats['rate_adjustments']
        print(f"   总调整次数: {rate_stats['total_adjustments']}")
        print(f"   增加次数: {rate_stats['total_increases']}")
        print(f"   减少次数: {rate_stats['total_decreases']}")
        print(f"   最终速率: {rate_stats['current_rate']:.1f} req/s")
        
    finally:
        server.stop()


def demo_multiple_strategies():
    """演示不同自适应策略的效果对比"""
    print(f"\n🆚 多策略对比演示")
    print("=" * 40)
    
    # 创建服务端
    server = MockServer("server-multi", base_capacity=100.0)
    
    # 创建不同策略的客户端
    strategies = [
        AdaptiveStrategy.AIMD,
        AdaptiveStrategy.PID,
        AdaptiveStrategy.EXPONENTIAL_BACKOFF
    ]
    
    clients = [
        MockClient(f"client-{strategy.value.lower()}", strategy)
        for strategy in strategies
    ]
    
    server.start()
    
    try:
        print(f"🖥️  服务端: {server.server_id} (容量: {server.base_capacity} req/s)")
        print(f"👥 客户端策略: {[c.strategy.value for c in clients]}")
        
        # 模拟并发请求
        def client_worker(client: MockClient, num_requests: int):
            for _ in range(num_requests):
                try:
                    current_rate = client.get_current_rate()
                    interval = 1.0 / max(current_rate, 1.0)
                    
                    client.send_request(server)
                    time.sleep(interval + random.uniform(0, 0.1))  # 添加随机抖动
                except Exception as e:
                    print(f"客户端 {client.client_id} 请求失败: {e}")
        
        # 启动并发请求线程
        threads = []
        for client in clients:
            thread = threading.Thread(
                target=client_worker, 
                args=(client, 20),
                daemon=True
            )
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 显示对比结果
        print(f"\n📊 策略效果对比:")
        print(f"{'策略':<20} {'成功率':<10} {'平均响应时间':<15} {'最终速率':<15}")
        print("-" * 60)
        
        for client in clients:
            stats = client.get_stats()
            print(f"{stats['strategy']:<20} "
                  f"{stats['success_rate']*100:.1f}%{'':<5} "
                  f"{stats['avg_response_time_ms']:.1f}ms{'':<10} "
                  f"{stats['current_rate']:.1f} req/s")
        
    finally:
        server.stop()


def demo_load_surge_handling():
    """演示负载突增情况的处理"""
    print(f"\n💥 负载突增处理演示")
    print("=" * 35)
    
    server = MockServer("server-surge", base_capacity=60.0)
    client = MockClient("client-surge", AdaptiveStrategy.AIMD)
    
    server.start()
    
    try:
        print(f"🖥️  服务端: {server.server_id}")
        print(f"👤 客户端: {client.client_id}")
        print(f"⚡ 将在第10秒模拟负载突增...")
        
        # 记录数据用于可视化
        timestamps = []
        rates = []
        load_scores = []
        response_times = []
        
        start_time = time.time()
        
        for i in range(25):
            current_time = time.time() - start_time
            
            # 第10秒开始模拟负载突增
            if 10 <= current_time < 15:
                server._background_load = 0.8  # 高负载
                # 模拟更多的并发请求处理
                for _ in range(3):
                    server.load_monitor.record_request_start()
                    time.sleep(0.01)
                    server.load_monitor.record_request_end(100.0, False)
            
            current_rate = client.get_current_rate()
            response = client.send_request(server)
            
            # 记录数据
            timestamps.append(current_time)
            rates.append(current_rate)
            
            latest_feedback = client.feedback_receiver.get_latest_feedback()
            if latest_feedback:
                load_scores.append(latest_feedback.load_score)
            else:
                load_scores.append(0.0)
                
            response_times.append(response['response_time_ms'])
            
            if i % 5 == 0:
                print(f"   {current_time:.1f}s: 速率={current_rate:.1f}, "
                      f"负载评分={load_scores[-1]:.2f}, "
                      f"响应时间={response['response_time_ms']:.1f}ms")
            
            # 控制发送间隔
            interval = 1.0 / max(current_rate, 1.0)
            time.sleep(interval)
        
        # 创建可视化图表
        try:
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
            
            # 发送速率变化
            ax1.plot(timestamps, rates, 'b-', linewidth=2, label='发送速率')
            ax1.axvspan(10, 15, alpha=0.3, color='red', label='负载突增期')
            ax1.set_ylabel('速率 (req/s)')
            ax1.set_title('负载突增情况下的自适应限流效果')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 负载评分变化
            ax2.plot(timestamps, load_scores, 'r-', linewidth=2, label='负载评分')
            ax2.axvspan(10, 15, alpha=0.3, color='red', label='负载突增期')
            ax2.set_ylabel('负载评分')
            ax2.set_ylim(0, 1)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # 响应时间变化
            ax3.plot(timestamps, response_times, 'g-', linewidth=2, label='响应时间')
            ax3.axvspan(10, 15, alpha=0.3, color='red', label='负载突增期')
            ax3.set_ylabel('响应时间 (ms)')
            ax3.set_xlabel('时间 (秒)')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # 保存图表
            output_file = '/Users/sean10/Code/Algorithm_code/learn_qos/adaptive_qos_demo.png'
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"\n📊 可视化图表已保存至: {output_file}")
            
            plt.show()
            
        except ImportError:
            print("❌ matplotlib未安装，跳过可视化")
        except Exception as e:
            print(f"❌ 可视化生成失败: {e}")
        
    finally:
        server.stop()


def demo_system_integration():
    """演示完整系统集成"""
    print(f"\n🌐 完整系统集成演示")
    print("=" * 35)
    
    # 创建反馈系统
    feedback_system = FeedbackSystem()
    
    # 创建多个服务端
    servers = [
        MockServer(f"server-{i}", base_capacity=80.0 + i*20)
        for i in range(1, 4)
    ]
    
    # 创建反馈生成器
    for server in servers:
        feedback_system.create_generator(
            server.server_id,
            server.load_monitor,
            base_capacity=server.base_capacity
        )
        server.start()
    
    # 创建多个客户端
    clients = []
    strategies = [AdaptiveStrategy.AIMD, AdaptiveStrategy.PID, AdaptiveStrategy.EXPONENTIAL_BACKOFF]
    
    for i, strategy in enumerate(strategies):
        client = MockClient(f"client-{i+1}", strategy)
        feedback_system.create_receiver(client.client_id)
        clients.append(client)
    
    try:
        print(f"🖥️  服务端: {[s.server_id for s in servers]}")
        print(f"👥 客户端: {[c.client_id for c in clients]}")
        
        # 模拟负载均衡场景
        def simulate_requests():
            for round_num in range(10):
                print(f"\n--- 第 {round_num + 1} 轮请求 ---")
                
                for client in clients:
                    # 随机选择服务端
                    server = random.choice(servers)
                    
                    try:
                        response = client.send_request(server)
                        
                        # 使用反馈系统传输反馈
                        feedback_system.simulate_feedback_exchange(
                            server.server_id,
                            client.client_id
                        )
                        
                        print(f"{client.client_id} -> {server.server_id}: "
                              f"速率={client.get_current_rate():.1f}, "
                              f"响应={response['response_time_ms']:.1f}ms")
                        
                    except Exception as e:
                        print(f"请求失败: {e}")
                
                time.sleep(2)
        
        simulate_requests()
        
        # 显示系统统计
        print(f"\n📈 系统整体统计:")
        system_stats = feedback_system.get_system_stats()
        
        print(f"服务端数量: {system_stats['generators_count']}")
        print(f"客户端数量: {system_stats['receivers_count']}")
        
        for client in clients:
            stats = client.get_stats()
            print(f"\n{stats['client_id']} ({stats['strategy']}):")
            print(f"  成功率: {stats['success_rate']*100:.1f}%")
            print(f"  平均响应时间: {stats['avg_response_time_ms']:.1f}ms")
            print(f"  当前速率: {stats['current_rate']:.1f} req/s")
        
    finally:
        for server in servers:
            server.stop()


def main():
    """主函数"""
    print("🚀 负载感知自适应限流系统完整演示")
    print("=" * 80)
    
    try:
        # 1. 单客户端演示
        demo_single_client_server()
        
        # 2. 多策略对比演示
        demo_multiple_strategies()
        
        # 3. 负载突增处理演示
        print(f"\n" + "=" * 80)
        response = input("是否运行负载突增演示? (包含可视化) (y/n): ").lower().strip()
        if response in ['y', 'yes', 'Y']:
            demo_load_surge_handling()
        
        # 4. 系统集成演示
        print(f"\n" + "=" * 80)
        response = input("是否运行系统集成演示? (y/n): ").lower().strip()
        if response in ['y', 'yes', 'Y']:
            demo_system_integration()
        
        print(f"\n✅ 演示完成!")
        print(f"\n🎯 关键学习点:")
        print(f"   1. 服务端实时监控系统负载并生成反馈")
        print(f"   2. 客户端根据负载反馈自适应调整发送速率")
        print(f"   3. 不同算法策略适用于不同的场景")
        print(f"   4. 系统能够自动应对负载突增等异常情况")
        print(f"   5. 整体系统实现了负载均衡和性能优化")
        
        print(f"\n📚 进阶学习建议:")
        print(f"   1. 尝试调整不同的算法参数")
        print(f"   2. 实现更复杂的负载预测算法")
        print(f"   3. 集成到实际的Web服务中")
        print(f"   4. 添加更多的性能指标监控")
        
    except KeyboardInterrupt:
        print(f"\n演示被用户中断")
    except Exception as e:
        print(f"演示过程中出现错误: {e}")


if __name__ == "__main__":
    main()

