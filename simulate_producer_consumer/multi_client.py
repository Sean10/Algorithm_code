import asyncio
import multiprocessing as mp
import grpc
import time
import logging
from collections import deque
from google.protobuf import empty_pb2
import producer_consumer_pb2
import producer_consumer_pb2_grpc

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - 进程%(process)d - %(message)s'
)

class PerformanceStats:
    def __init__(self, window_size=1000):  # 减小窗口大小
        self.latencies = deque(maxlen=window_size)
        self.request_times = deque(maxlen=window_size)
        self.window_size = window_size
        self.total_requests = 0
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
        latency = (time.time() - start_time) * 1000
        stats.add_latency(latency)
        return response.id
    except grpc.RpcError as e:
        logging.error(f"RPC错误: {e}")
        return None

async def monitor_performance(stats, process_id):
    while True:
        avg_latency = stats.get_average_latency()
        iops = stats.get_iops()
        total_stats = stats.get_total_stats()
        logging.info(
            f"进程 {process_id} - 平均延迟: {avg_latency:.2f}ms, 实时IOPS: {iops}, "
            f"总请求数: {total_stats['total_requests']}, "
            f"平均IOPS: {total_stats['average_iops']:.2f}"
        )
        await asyncio.sleep(1)

async def worker(process_id, concurrent_requests=20):  # 降低单进程并发数到20
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

    monitor_task = asyncio.create_task(monitor_performance(stats, process_id))
    
    # 使用信号量控制并发
    sem = asyncio.Semaphore(concurrent_requests)
    
    async def controlled_get_id():
        async with sem:
            return await get_id(stub, stats)
    
    try:
        while True:
            # 创建新请求时不等待之前的请求完成
            asyncio.create_task(controlled_get_id())
            # 添加小延迟，使请求更平滑
            await asyncio.sleep(0.001)
    except KeyboardInterrupt:
        logging.info(f"进程 {process_id} 正在关闭...")
    finally:
        monitor_task.cancel()
        await channel.close()

def process_worker(process_id):
    asyncio.run(worker(process_id))

def main():
    # 减少进程数到5个，每个进程20个并发，总并发100
    processes = []
    for i in range(5):
        p = mp.Process(target=process_worker, args=(i,))
        p.start()
        processes.append(p)

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        logging.info("正在关闭所有进程...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()

if __name__ == '__main__':
    mp.set_start_method('spawn')  # 使用spawn方式启动进程，更安全
    main() 