#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>
#include <atomic>
#include <sys/time.h>
#include <boost/lockfree/queue.hpp>
#include <iostream>
#include <signal.h>

#define QUEUE_SIZE 100    // 减小队列大小
#define TEST_COUNT 100    // 减小测试次数
#define CONSUMER_COUNT 10 // 减小消费者数量
#define SPIN_YIELD_COUNT 32

// 原有的互斥锁队列实现
typedef struct {
    int64_t data[QUEUE_SIZE];
    int head;
    int tail;
    int count;
    pthread_mutex_t mutex;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} MutexQueue;

// Boost无锁队列包装
class LockFreeQueue {
private:
    boost::lockfree::queue<int64_t> queue;
public:
    LockFreeQueue() : queue(QUEUE_SIZE) {}
    
    bool push(int64_t value) {
        return queue.push(value);
    }
    
    bool pop(int64_t& value) {
        return queue.pop(value);
    }
};

// 线程参数结构体
struct ThreadArg {
    void* queue;
    int thread_id;
    double* latencies;
    std::atomic<int>* completed_count;
    std::atomic<bool>* should_stop;
    bool is_lockfree;
};

// 初始化互斥锁队列
void mutex_queue_init(MutexQueue* q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    pthread_mutexattr_t attr;
    pthread_mutexattr_init(&attr);
    pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_ERRORCHECK);
    pthread_mutex_init(&q->mutex, &attr);
    pthread_mutexattr_destroy(&attr);
    pthread_cond_init(&q->not_empty, NULL);
    pthread_cond_init(&q->not_full, NULL);
}

// 互斥锁队列的入队
int mutex_queue_push(MutexQueue* q, int64_t value) {
    int ret = pthread_mutex_lock(&q->mutex);
    if (ret != 0) {
        printf("互斥锁获取失败: %d\n", ret);
        return -1;
    }

    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_sec += 1; // 1秒超时

    while (q->count == QUEUE_SIZE) {
        ret = pthread_cond_timedwait(&q->not_full, &q->mutex, &ts);
        if (ret == ETIMEDOUT) {
            pthread_mutex_unlock(&q->mutex);
            return -1;
        }
    }
    
    q->data[q->tail] = value;
    q->tail = (q->tail + 1) % QUEUE_SIZE;
    q->count++;
    
    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->mutex);
    return 0;
}

// 互斥锁队列的出队
int mutex_queue_pop(MutexQueue* q, int64_t* value) {
    int ret = pthread_mutex_lock(&q->mutex);
    if (ret != 0) {
        printf("互斥锁获取失败: %d\n", ret);
        return -1;
    }

    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_sec += 1; // 1秒超时

    while (q->count == 0) {
        ret = pthread_cond_timedwait(&q->not_empty, &q->mutex, &ts);
        if (ret == ETIMEDOUT) {
            pthread_mutex_unlock(&q->mutex);
            return -1;
        }
    }
    
    *value = q->data[q->head];
    q->head = (q->head + 1) % QUEUE_SIZE;
    q->count--;
    
    pthread_cond_signal(&q->not_full);
    pthread_mutex_unlock(&q->mutex);
    return 0;
}

// 生产者线程函数
void* producer(void* arg) {
    ThreadArg* thread_arg = (ThreadArg*)arg;
    int64_t value = 0;
    int failed_pushes = 0;
    const int max_failed_pushes = 1000;
    
    if (thread_arg->is_lockfree) {
        LockFreeQueue* q = (LockFreeQueue*)thread_arg->queue;
        while (!thread_arg->should_stop->load()) {
            if (q->push(value)) {
                value++;
                failed_pushes = 0;
            } else {
                if (++failed_pushes > max_failed_pushes) {
                    usleep(1000);
                    failed_pushes = 0;
                }
                if (failed_pushes % SPIN_YIELD_COUNT == 0) {
                    sched_yield();
                }
            }
        }
    } else {
        MutexQueue* q = (MutexQueue*)thread_arg->queue;
        while (!thread_arg->should_stop->load()) {
            if (mutex_queue_push(q, value) == 0) {
                value++;
                failed_pushes = 0;
            } else {
                if (++failed_pushes > max_failed_pushes) {
                    usleep(1000);
                    failed_pushes = 0;
                }
            }
        }
    }
    return NULL;
}

// 消费者线程函数
void* consumer(void* arg) {
    ThreadArg* thread_arg = (ThreadArg*)arg;
    int thread_id = thread_arg->thread_id;
    double* latencies = thread_arg->latencies;
    std::atomic<int>* completed_count = thread_arg->completed_count;
    
    int64_t value;
    struct timeval start, end;
    int failed_pops = 0;
    const int max_failed_pops = 1000;
    int completed_tests = 0;
    
    if (thread_arg->is_lockfree) {
        LockFreeQueue* q = (LockFreeQueue*)thread_arg->queue;
        while (completed_tests < TEST_COUNT && failed_pops < max_failed_pops) {
            gettimeofday(&start, NULL);
            if (q->pop(value)) {
                gettimeofday(&end, NULL);
                double latency = (end.tv_sec - start.tv_sec) * 1000000.0 + 
                               (end.tv_usec - start.tv_usec);
                latencies[completed_tests++] = latency;
                failed_pops = 0;
            } else {
                failed_pops++;
                if (failed_pops % SPIN_YIELD_COUNT == 0) {
                    sched_yield();
                }
                if (failed_pops % (SPIN_YIELD_COUNT * 32) == 0) {
                    usleep(100);
                }
            }
        }
    } else {
        MutexQueue* q = (MutexQueue*)thread_arg->queue;
        while (completed_tests < TEST_COUNT && failed_pops < max_failed_pops) {
            gettimeofday(&start, NULL);
            if (mutex_queue_pop(q, &value) == 0) {
                gettimeofday(&end, NULL);
                double latency = (end.tv_sec - start.tv_sec) * 1000000.0 + 
                               (end.tv_usec - start.tv_usec);
                latencies[completed_tests++] = latency;
                failed_pops = 0;
            } else {
                failed_pops++;
                if (failed_pops % (SPIN_YIELD_COUNT * 32) == 0) {
                    usleep(100);
                }
            }
        }
    }
    
    if (completed_tests > 0) {
        printf("消费者 %d 完成 %d 次测试\n", thread_id, completed_tests);
    } else {
        printf("消费者 %d 未完成任何测试\n", thread_id);
    }
    
    completed_count->fetch_add(1);
    return NULL;
}

void run_benchmark(bool use_lockfree) {
    const char* queue_type = use_lockfree ? "无锁队列" : "互斥锁队列";
    printf("\n测试 %s:\n", queue_type);
    
    void* queue;
    if (use_lockfree) {
        queue = new LockFreeQueue();
    } else {
        queue = new MutexQueue();
        mutex_queue_init((MutexQueue*)queue);
    }
    
    // 为每个消费者分配延迟数组
    double** all_latencies = new double*[CONSUMER_COUNT];
    for (int i = 0; i < CONSUMER_COUNT; i++) {
        all_latencies[i] = new double[TEST_COUNT];
        // 初始化为-1表示未完成的测试
        for (int j = 0; j < TEST_COUNT; j++) {
            all_latencies[i][j] = -1;
        }
    }
    
    // 启动消费者线程
    pthread_t consumers[CONSUMER_COUNT];
    ThreadArg thread_args[CONSUMER_COUNT];
    std::atomic<int> completed_count(0);
    std::atomic<bool> should_stop(false);
    
    // 启动生产者线程
    pthread_t producer_thread;
    ThreadArg producer_arg;
    producer_arg.queue = queue;
    producer_arg.is_lockfree = use_lockfree;
    producer_arg.should_stop = &should_stop;
    pthread_create(&producer_thread, NULL, producer, &producer_arg);
    
    for (int i = 0; i < CONSUMER_COUNT; i++) {
        thread_args[i].queue = queue;
        thread_args[i].thread_id = i;
        thread_args[i].latencies = all_latencies[i];
        thread_args[i].completed_count = &completed_count;
        thread_args[i].should_stop = &should_stop;
        thread_args[i].is_lockfree = use_lockfree;
        pthread_create(&consumers[i], NULL, consumer, &thread_args[i]);
    }
    
    // 等待所有消费者完成或超时
    struct timeval start_time, current_time;
    gettimeofday(&start_time, NULL);
    const int timeout_seconds = 10;  // 减少超时时间到10秒
    
    while (completed_count.load() < CONSUMER_COUNT) {
        usleep(1000);
        gettimeofday(&current_time, NULL);
        if (current_time.tv_sec - start_time.tv_sec > timeout_seconds) {
            printf("测试超时，强制结束\n");
            break;
        }
    }
    
    // 通知生产者停止
    should_stop.store(true);
    pthread_join(producer_thread, NULL);
    
    // 等待所有消费者线程结束
    for (int i = 0; i < CONSUMER_COUNT; i++) {
        pthread_join(consumers[i], NULL);
    }
    
    // 计算统计信息
    double total_latency = 0;
    double min_latency = 1e9;
    double max_latency = 0;
    int total_samples = 0;
    
    for (int i = 0; i < CONSUMER_COUNT; i++) {
        for (int j = 0; j < TEST_COUNT; j++) {
            double latency = all_latencies[i][j];
            if (latency >= 0) {  // 只统计有效的延迟数据
                total_latency += latency;
                if (latency < min_latency) min_latency = latency;
                if (latency > max_latency) max_latency = latency;
                total_samples++;
            }
        }
    }
    
    if (total_samples > 0) {
        double avg_latency = total_latency / total_samples;
        printf("线程数: %d\n", CONSUMER_COUNT);
        printf("每线程测试次数: %d\n", TEST_COUNT);
        printf("成功完成的样本数: %d\n", total_samples);
        printf("平均延迟: %.2f 微秒\n", avg_latency);
        printf("最小延迟: %.2f 微秒\n", min_latency);
        printf("最大延迟: %.2f 微秒\n", max_latency);
        printf("理论每秒处理能力: %.2f\n", (1000000.0 / avg_latency * CONSUMER_COUNT));
    } else {
        printf("没有成功完成的测试样本\n");
    }
    
    // 清理资源
    for (int i = 0; i < CONSUMER_COUNT; i++) {
        delete[] all_latencies[i];
    }
    delete[] all_latencies;
    
    if (use_lockfree) {
        delete static_cast<LockFreeQueue*>(queue);
    } else {
        MutexQueue* mq = static_cast<MutexQueue*>(queue);
        pthread_mutex_destroy(&mq->mutex);
        pthread_cond_destroy(&mq->not_empty);
        pthread_cond_destroy(&mq->not_full);
        delete mq;
    }
}

int main() {
    // 测试互斥锁队列
    run_benchmark(false);
    
    // 测试无锁队列
    run_benchmark(true);
    
    return 0;
} 