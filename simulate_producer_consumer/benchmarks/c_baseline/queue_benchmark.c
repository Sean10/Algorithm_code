#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>
#include <stdatomic.h>
#include <sys/time.h>

#define QUEUE_SIZE 10000
#define TEST_COUNT 10000
#define CONSUMER_COUNT 50  // 可调整消费者数量

typedef struct {
    int64_t data[QUEUE_SIZE];
    int head;
    int tail;
    int count;
    pthread_mutex_t mutex;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} Queue;

typedef struct {
    Queue* queue;
    int thread_id;
    double* latencies;
    atomic_int* completed_count;
} ThreadArg;

// 初始化队列
void queue_init(Queue* q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    pthread_mutex_init(&q->mutex, NULL);
    pthread_cond_init(&q->not_empty, NULL);
    pthread_cond_init(&q->not_full, NULL);
}

// 入队
int queue_push(Queue* q, int64_t value) {
    pthread_mutex_lock(&q->mutex);
    while (q->count == QUEUE_SIZE) {
        pthread_cond_wait(&q->not_full, &q->mutex);
    }
    
    q->data[q->tail] = value;
    q->tail = (q->tail + 1) % QUEUE_SIZE;
    q->count++;
    
    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->mutex);
    return 0;
}

// 出队
int queue_pop(Queue* q, int64_t* value) {
    pthread_mutex_lock(&q->mutex);
    while (q->count == 0) {
        pthread_cond_wait(&q->not_empty, &q->mutex);
    }
    
    *value = q->data[q->head];
    q->head = (q->head + 1) % QUEUE_SIZE;
    q->count--;
    
    pthread_cond_signal(&q->not_full);
    pthread_mutex_unlock(&q->mutex);
    return 0;
}

// 生产者线程
void* producer(void* arg) {
    Queue* q = (Queue*)arg;
    int64_t value = 0;
    
    while (1) {
        queue_push(q, value++);
    }
    return NULL;
}

// 消费者线程
void* consumer(void* arg) {
    ThreadArg* thread_arg = (ThreadArg*)arg;
    Queue* q = thread_arg->queue;
    int thread_id = thread_arg->thread_id;
    double* latencies = thread_arg->latencies;
    atomic_int* completed_count = thread_arg->completed_count;
    
    int64_t value;
    struct timeval start, end;
    
    for (int i = 0; i < TEST_COUNT; i++) {
        gettimeofday(&start, NULL);
        queue_pop(q, &value);
        gettimeofday(&end, NULL);
        
        // 计算微秒级延迟
        double latency = (end.tv_sec - start.tv_sec) * 1000000.0 + 
                        (end.tv_usec - start.tv_usec);
        latencies[i] = latency;
    }
    
    atomic_fetch_add(completed_count, 1);
    return NULL;
}

int main() {
    Queue queue;
    queue_init(&queue);
    
    // 启动生产者线程
    pthread_t producer_thread;
    pthread_create(&producer_thread, NULL, producer, &queue);
    
    // 为每个消费者分配延迟数组
    double** all_latencies = malloc(CONSUMER_COUNT * sizeof(double*));
    for (int i = 0; i < CONSUMER_COUNT; i++) {
        all_latencies[i] = malloc(TEST_COUNT * sizeof(double));
    }
    
    // 启动消费者线程
    pthread_t consumers[CONSUMER_COUNT];
    ThreadArg thread_args[CONSUMER_COUNT];
    atomic_int completed_count = 0;
    
    for (int i = 0; i < CONSUMER_COUNT; i++) {
        thread_args[i].queue = &queue;
        thread_args[i].thread_id = i;
        thread_args[i].latencies = all_latencies[i];
        thread_args[i].completed_count = &completed_count;
        pthread_create(&consumers[i], NULL, consumer, &thread_args[i]);
    }
    
    // 等待所有消费者完成
    while (atomic_load(&completed_count) < CONSUMER_COUNT) {
        usleep(1000);
    }
    
    // 计算统计信息
    double total_latency = 0;
    double min_latency = 1e9;
    double max_latency = 0;
    int total_samples = CONSUMER_COUNT * TEST_COUNT;
    
    for (int i = 0; i < CONSUMER_COUNT; i++) {
        for (int j = 0; j < TEST_COUNT; j++) {
            double latency = all_latencies[i][j];
            total_latency += latency;
            if (latency < min_latency) min_latency = latency;
            if (latency > max_latency) max_latency = latency;
        }
    }
    
    double avg_latency = total_latency / total_samples;
    printf("测试结果 (微秒):\n");
    printf("线程数: %d\n", CONSUMER_COUNT);
    printf("每线程测试次数: %d\n", TEST_COUNT);
    printf("平均延迟: %.2f\n", avg_latency);
    printf("最小延迟: %.2f\n", min_latency);
    printf("最大延迟: %.2f\n", max_latency);
    printf("理论每秒处理能力: %.2f\n", 1000000.0 / avg_latency * CONSUMER_COUNT);
    
    // 清理资源
    for (int i = 0; i < CONSUMER_COUNT; i++) {
        free(all_latencies[i]);
    }
    free(all_latencies);
    
    // 强制退出（因为生产者是死循环）
    exit(0);
    return 0;
} 