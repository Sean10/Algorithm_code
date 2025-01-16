import asyncio
import grpc
import time
import logging
from collections import deque
from google.protobuf import empty_pb2
import producer_consumer_pb2
import producer_consumer_pb2_grpc

# 配置日志
logging.basicConfig(level=logging.INFO)

# 性能统计
class PerformanceStats:
    def __init__(self, window_size=10000):  # 增加窗口大小以获得更准确的统计
        self.latencies = deque(maxlen=window_size)
        self.request_times = deque(maxlen=window_size)
        self.window_size = window_size
        self.total_requests = 0  # 添加总请求计数
        self.start_time = time.time()

    def add_latency(self, latency):
        self.latencies.append(latency)
        self.request_times.append(time.time())
        self.total_requests += 1

    def get_average_latency(self):
        if not self.latencies:
            return 0
        return sum(self.latencies) / len(self.latencies)

    def get_iops(self):
        if len(self.request_times) < 2:
            return 0
        # 计算最近一秒内的请求数
        current_time = time.time()
        recent_requests = sum(1 for t in self.request_times if current_time - t <= 1)
        return recent_requests

    def get_total_stats(self):
        elapsed_time = time.time() - self.start_time
        return {
            'total_requests': self.total_requests,
            'average_iops': self.total_requests / elapsed_time if elapsed_time > 0 else 0
        }

async def get_id(stub, stats):
    start_time = time.time()
    try:
        response = await stub.GetNextId(empty_pb2.Empty())
        latency = (time.time() - start_time) * 1000  # 转换为毫秒
        stats.add_latency(latency)
        return response.id
    except grpc.RpcError as e:
        logging.error(f"RPC错误: {e}")
        return None

async def monitor_performance(stats):
    while True:
        avg_latency = stats.get_average_latency()
        iops = stats.get_iops()
        total_stats = stats.get_total_stats()
        logging.info(
            f"平均延迟: {avg_latency:.2f}ms, 实时IOPS: {iops}, "
            f"总请求数: {total_stats['total_requests']}, "
            f"平均IOPS: {total_stats['average_iops']:.2f}"
        )
        await asyncio.sleep(1)

async def main():
    # 创建异步gRPC通道，添加性能优化选项
    channel = grpc.aio.insecure_channel(
        'localhost:50051',
        options=[
            ('grpc.max_send_message_length', 10 * 1024 * 1024),
            ('grpc.max_receive_message_length', 10 * 1024 * 1024),
            ('grpc.keepalive_time_ms', 10000),
            ('grpc.keepalive_timeout_ms', 5000),
        ]
    )
    stub = producer_consumer_pb2_grpc.ProducerConsumerServiceStub(channel)
    stats = PerformanceStats()

    # 启动性能监控
    monitor_task = asyncio.create_task(monitor_performance(stats))

    # 创建多个并发请求
    tasks = []
    try:
        while True:
            # 增加并发数到500
            while len(tasks) < 500:
                tasks.append(asyncio.create_task(get_id(stub, stats)))
            await asyncio.gather(*tasks)
            tasks = []
            # 移除请求间隔，让系统自然控制速率
    except KeyboardInterrupt:
        logging.info("正在关闭客户端...")
        total_stats = stats.get_total_stats()
        logging.info(f"总统计信息: {total_stats}")
    finally:
        monitor_task.cancel()
        await channel.close()

if __name__ == '__main__':
    asyncio.run(main()) 