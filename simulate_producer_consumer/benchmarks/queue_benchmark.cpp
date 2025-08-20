#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>
#include <atomic>
#include <sys/time.h>
#include <boost/lockfree/queue.hpp>
#include <errno.h>
#include "tools/csv_writer.hpp"

#define SPIN_YIELD_COUNT 32

// 互斥锁队列（动态容量）
typedef struct {
    int64_t* data;
    int head;
    int tail;
    int count;
    int capacity;
    pthread_mutex_t mutex;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} MutexQueue;

// Boost无锁队列包装
class LockFreeQueue {
private:
    boost::lockfree::queue<int64_t> queue;
public:
    explicit LockFreeQueue(size_t capacity) : queue(capacity) {}
    
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
    int max_tests;
};

// 初始化互斥锁队列
void mutex_queue_init(MutexQueue* q, int capacity) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->capacity = capacity;
    q->data = new int64_t[capacity];
    pthread_mutexattr_t attr;
    pthread_mutexattr_init(&attr);
    pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_ERRORCHECK);
    pthread_mutex_init(&q->mutex, &attr);
    pthread_mutexattr_destroy(&attr);
    pthread_cond_init(&q->not_empty, NULL);
    pthread_cond_init(&q->not_full, NULL);
}

void mutex_queue_destroy(MutexQueue* q) {
    pthread_mutex_destroy(&q->mutex);
    pthread_cond_destroy(&q->not_empty);
    pthread_cond_destroy(&q->not_full);
    delete[] q->data;
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

    while (q->count == q->capacity) {
        ret = pthread_cond_timedwait(&q->not_full, &q->mutex, &ts);
        if (ret == ETIMEDOUT) {
            pthread_mutex_unlock(&q->mutex);
            return -1;
        }
    }
    
    q->data[q->tail] = value;
    q->tail = (q->tail + 1) % q->capacity;
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
    q->head = (q->head + 1) % q->capacity;
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
        while (completed_tests < thread_arg->max_tests && failed_pops < max_failed_pops) {
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
        while (completed_tests < thread_arg->max_tests && failed_pops < max_failed_pops) {
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

using bench_tools::append_latency_csv;
using bench_tools::append_summary_csv;

void run_benchmark(bool use_lockfree,
                   int queue_size,
                   int test_count,
                   int consumer_count,
                   int timeout_seconds,
                   const char* csv_latency_path,
                   const char* csv_summary_path) {
    const char* queue_type = use_lockfree ? "无锁队列" : "互斥锁队列";
    printf("\n测试 %s:\n", queue_type);
    
    void* queue;
    if (use_lockfree) {
        queue = new LockFreeQueue(queue_size);
    } else {
        queue = new MutexQueue();
        mutex_queue_init((MutexQueue*)queue, queue_size);
    }
    
    // 为每个消费者分配延迟数组
    double** all_latencies = new double*[consumer_count];
    for (int i = 0; i < consumer_count; i++) {
        all_latencies[i] = new double[test_count];
        // 初始化为-1表示未完成的测试
        for (int j = 0; j < test_count; j++) {
            all_latencies[i][j] = -1;
        }
    }
    
    // 启动消费者线程
    pthread_t* consumers = new pthread_t[consumer_count];
    ThreadArg* thread_args = new ThreadArg[consumer_count];
    std::atomic<int> completed_count(0);
    std::atomic<bool> should_stop(false);
    
    // 启动生产者线程
    pthread_t producer_thread;
    ThreadArg producer_arg;
    producer_arg.queue = queue;
    producer_arg.is_lockfree = use_lockfree;
    producer_arg.should_stop = &should_stop;
    producer_arg.max_tests = 0; // 未使用
    pthread_create(&producer_thread, NULL, producer, &producer_arg);
    
    for (int i = 0; i < consumer_count; i++) {
        thread_args[i].queue = queue;
        thread_args[i].thread_id = i;
        thread_args[i].latencies = all_latencies[i];
        thread_args[i].completed_count = &completed_count;
        thread_args[i].should_stop = &should_stop;
        thread_args[i].is_lockfree = use_lockfree;
        thread_args[i].max_tests = test_count;
        pthread_create(&consumers[i], NULL, consumer, &thread_args[i]);
    }
    
    // 等待所有消费者完成或超时
    struct timeval start_time, current_time;
    gettimeofday(&start_time, NULL);
    
    while (completed_count.load() < consumer_count) {
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
    for (int i = 0; i < consumer_count; i++) {
        pthread_join(consumers[i], NULL);
    }
    
    // 计算统计信息
    double total_latency = 0;
    double min_latency = 1e9;
    double max_latency = 0;
    int total_samples = 0;
    
    for (int i = 0; i < consumer_count; i++) {
        for (int j = 0; j < test_count; j++) {
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
        printf("线程数: %d\n", consumer_count);
        printf("每线程测试次数: %d\n", test_count);
        printf("成功完成的样本数: %d\n", total_samples);
        printf("平均延迟: %.2f 微秒\n", avg_latency);
        printf("最小延迟: %.2f 微秒\n", min_latency);
        printf("最大延迟: %.2f 微秒\n", max_latency);
        printf("理论每秒处理能力: %.2f\n", (1000000.0 / avg_latency * consumer_count));
        // 附加写入CSV
        append_latency_csv(csv_latency_path, use_lockfree ? "lockfree" : "mutex",
                           consumer_count, test_count, all_latencies);
        append_summary_csv(csv_summary_path, use_lockfree ? "lockfree" : "mutex",
                           queue_size, test_count, consumer_count, timeout_seconds,
                           total_samples, avg_latency, min_latency, max_latency);
    } else {
        printf("没有成功完成的测试样本\n");
    }
    
    // 清理资源
    for (int i = 0; i < consumer_count; i++) {
        delete[] all_latencies[i];
    }
    delete[] all_latencies;
    delete[] consumers;
    delete[] thread_args;
    
    if (use_lockfree) {
        delete static_cast<LockFreeQueue*>(queue);
    } else {
        MutexQueue* mq = static_cast<MutexQueue*>(queue);
        mutex_queue_destroy(mq);
        delete mq;
    }
}

static void print_usage(const char* prog) {
    printf("用法: %s [--queue-size N] [--test-count N] [--consumers N] [--timeout N] [--csv-latency PATH] [--csv-summary PATH]\n", prog);
    printf("默认: queue-size=65536, test-count=1000, consumers=8, timeout=15秒\n");
}

int main(int argc, char** argv) {
    int queue_size = 65536;
    int test_count = 1000;
    int consumer_count = 8;
    int timeout_seconds = 15;
    const char* csv_latency_path = NULL;
    const char* csv_summary_path = NULL;

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--queue-size") == 0 && i + 1 < argc) {
            queue_size = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--test-count") == 0 && i + 1 < argc) {
            test_count = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--consumers") == 0 && i + 1 < argc) {
            consumer_count = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--timeout") == 0 && i + 1 < argc) {
            timeout_seconds = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--csv-latency") == 0 && i + 1 < argc) {
            csv_latency_path = argv[++i];
        } else if (strcmp(argv[i], "--csv-summary") == 0 && i + 1 < argc) {
            csv_summary_path = argv[++i];
        } else if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            print_usage(argv[0]);
            return 0;
        } else {
            print_usage(argv[0]);
            return 1;
        }
    }

    // 测试互斥锁队列
    run_benchmark(false, queue_size, test_count, consumer_count, timeout_seconds,
                  csv_latency_path, csv_summary_path);
    
    // 测试无锁队列
    run_benchmark(true, queue_size, test_count, consumer_count, timeout_seconds,
                  csv_latency_path, csv_summary_path);
    
    return 0;
}