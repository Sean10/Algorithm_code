import grpc
from concurrent import futures
import queue
import threading
import time
import logging
from google.protobuf import empty_pb2
import producer_consumer_pb2
import producer_consumer_pb2_grpc

# 配置日志
logging.basicConfig(level=logging.INFO)

# 线程安全的队列，设置较大的队列大小
id_queue = queue.Queue(maxsize=10000)
current_id = 0

class ProducerConsumerService(producer_consumer_pb2_grpc.ProducerConsumerServiceServicer):
    def GetNextId(self, request, context):
        try:
            id_value = id_queue.get(timeout=0.1)  # 减少超时时间到100ms
            return producer_consumer_pb2.IdResponse(id=id_value)
        except queue.Empty:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('No ID available')
            return producer_consumer_pb2.IdResponse()

def producer_thread():
    global current_id
    while True:
        try:
            current_id += 1
            id_queue.put(current_id, block=False)  # 非阻塞方式
        except queue.Full:
            time.sleep(0.0001)  # 队列满时短暂等待
            continue

def serve():
    # 启动生产者线程
    producer = threading.Thread(target=producer_thread, daemon=True)
    producer.start()

    # 启动gRPC服务器，增加工作线程数
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=50),
        options=[
            ('grpc.max_send_message_length', 10 * 1024 * 1024),
            ('grpc.max_receive_message_length', 10 * 1024 * 1024),
            ('grpc.keepalive_time_ms', 10000),
            ('grpc.keepalive_timeout_ms', 5000),
        ]
    )
    producer_consumer_pb2_grpc.add_ProducerConsumerServiceServicer_to_server(
        ProducerConsumerService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("Server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve() 