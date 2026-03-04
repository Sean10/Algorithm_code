#pragma once

#include <atomic>
#include <memory>
#include <cstdint>
#include <immintrin.h>  // 用于预取指令
#include <thread>

// NUMA 支持（可选）
#ifdef HAS_NUMA
#include <numa.h>
#endif

namespace stage5 {

/**
 * Stage5: 高性能优化技术
 * 
 * 这个模块展示了无锁编程中的各种高级性能优化技术：
 * 1. 缓存行对齐 (Cache Line Alignment)
 * 2. 伪共享避免 (False Sharing Avoidance) 
 * 3. 内存预取 (Prefetching)
 * 4. NUMA 感知优化 (NUMA-aware Optimization)
 * 5. 内存序优化 (Memory Ordering Optimization)
 * 6. CPU 缓存友好的数据布局
 */

// 获取缓存行大小的辅助函数
constexpr size_t get_cache_line_size() {
    // 大多数现代 x86 CPU 的缓存行大小是 64 字节
    return 64;
}

/**
 * 缓存行对齐的原子变量包装器
 * 确保每个变量独占一个缓存行，避免伪共享
 */
template<typename T>
struct alignas(get_cache_line_size()) CacheAligned {
    std::atomic<T> value;
    
    CacheAligned() : value{} {}
    CacheAligned(T initial) : value(initial) {}
    
    // 禁止拷贝，避免意外的非对齐拷贝
    CacheAligned(const CacheAligned&) = delete;
    CacheAligned& operator=(const CacheAligned&) = delete;
    
    T load(std::memory_order order = std::memory_order_seq_cst) const {
        return value.load(order);
    }
    
    void store(T desired, std::memory_order order = std::memory_order_seq_cst) {
        value.store(desired, order);
    }
    
    bool compare_exchange_weak(T& expected, T desired,
                              std::memory_order success = std::memory_order_seq_cst,
                              std::memory_order failure = std::memory_order_seq_cst) {
        return value.compare_exchange_weak(expected, desired, success, failure);
    }
};

/**
 * NUMA 感知的内存分配器
 * 当 NUMA 库不可用时，回退到标准内存分配
 */
template<typename T>
class NumaAllocator {
private:
    int numa_node_;
    bool numa_available_;

public:
    using value_type = T;

    explicit NumaAllocator(int node = -1) : numa_node_(node), numa_available_(false) {
#ifdef HAS_NUMA
        numa_available_ = (numa_available() >= 0);
        if (numa_node_ == -1 && numa_available_) {
            // 自动检测当前 CPU 的 NUMA 节点
            numa_node_ = numa_node_of_cpu(sched_getcpu());
        }
#else
        numa_available_ = false;
        (void)node;  // 避免未使用警告
#endif
    }

    template<typename U>
    NumaAllocator(const NumaAllocator<U>& other) : numa_node_(other.numa_node_), numa_available_(other.numa_available_) {}

    T* allocate(size_t n) {
#ifdef HAS_NUMA
        if (numa_available_) {
            // 在指定 NUMA 节点上分配内存
            void* ptr = numa_alloc_onnode(n * sizeof(T), numa_node_);
            if (!ptr) {
                throw std::bad_alloc();
            }
            return static_cast<T*>(ptr);
        }
#endif
        // NUMA 不可用，使用标准分配
        return static_cast<T*>(std::aligned_alloc(get_cache_line_size(),
                                                     n * sizeof(T)));
    }

    void deallocate(T* ptr, size_t n) {
#ifdef HAS_NUMA
        if (numa_available_) {
            numa_free(ptr, n * sizeof(T));
            return;
        }
#endif
        std::free(ptr);
    }

    template<typename U>
    bool operator==(const NumaAllocator<U>& other) const {
        return numa_node_ == other.numa_node_;
    }

    template<typename U>
    bool operator!=(const NumaAllocator<U>& other) const {
        return !(*this == other);
    }

    int numa_node() const { return numa_node_; }
};

/**
 * CPU 缓存友好的循环缓冲区
 * 使用多种优化技术：
 * 1. 缓存行对齐
 * 2. 预取指令
 * 3. 内存序优化
 * 4. 避免伪共享
 */
template<typename T, size_t Capacity>
class OptimizedRingBuffer {
private:
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be power of 2");
    static constexpr size_t MASK = Capacity - 1;
    static constexpr size_t CACHE_LINE_SIZE = get_cache_line_size();
    
    // 数据缓冲区，缓存行对齐
    alignas(CACHE_LINE_SIZE) T buffer_[Capacity];
    
    // 生产者和消费者指针，分别放在不同的缓存行中避免伪共享
    alignas(CACHE_LINE_SIZE) CacheAligned<size_t> producer_pos_;
    alignas(CACHE_LINE_SIZE) CacheAligned<size_t> consumer_pos_;
    
    // 为了进一步优化，我们可能需要缓存生产者和消费者位置的本地拷贝
    alignas(CACHE_LINE_SIZE) mutable CacheAligned<size_t> cached_consumer_pos_;
    alignas(CACHE_LINE_SIZE) mutable CacheAligned<size_t> cached_producer_pos_;
    
    /**
     * 内存预取辅助函数
     */
    void prefetch_for_write(const void* addr) const {
#ifdef __builtin_prefetch
        __builtin_prefetch(addr, 1, 3);  // 预取到 L1 缓存，用于写入
#elif defined(_MSC_VER)
        _mm_prefetch(static_cast<const char*>(addr), _MM_HINT_T0);
#endif
    }
    
    void prefetch_for_read(const void* addr) const {
#ifdef __builtin_prefetch
        __builtin_prefetch(addr, 0, 3);  // 预取到 L1 缓存，用于读取
#elif defined(_MSC_VER)
        _mm_prefetch(static_cast<const char*>(addr), _MM_HINT_T0);
#endif
    }
    
    /**
     * 获取缓存的消费者位置，减少跨缓存行的内存访问
     */
    size_t get_cached_consumer_pos() const {
        size_t cached = cached_consumer_pos_.load(std::memory_order_relaxed);
        size_t actual = consumer_pos_.load(std::memory_order_acquire);
        
        if (cached != actual) {
            cached_consumer_pos_.store(actual, std::memory_order_relaxed);
            return actual;
        }
        return cached;
    }
    
    size_t get_cached_producer_pos() const {
        size_t cached = cached_producer_pos_.load(std::memory_order_relaxed);
        size_t actual = producer_pos_.load(std::memory_order_acquire);
        
        if (cached != actual) {
            cached_producer_pos_.store(actual, std::memory_order_relaxed);
            return actual;
        }
        return cached;
    }

public:
    OptimizedRingBuffer() 
        : producer_pos_(0), consumer_pos_(0)
        , cached_consumer_pos_(0), cached_producer_pos_(0) {}
    
    /**
     * 高度优化的入队操作
     */
    bool enqueue(const T& item) {
        size_t current_producer = producer_pos_.load(std::memory_order_relaxed);
        size_t next_producer = (current_producer + 1) & MASK;
        
        // 使用缓存的消费者位置减少内存访问
        if (next_producer == get_cached_consumer_pos()) {
            // 可能队列满，检查实际的消费者位置
            if (next_producer == consumer_pos_.load(std::memory_order_acquire)) {
                return false;  // 队列满
            }
        }
        
        // 预取下下个位置，为后续写入做准备
        size_t prefetch_pos = (next_producer + 1) & MASK;
        prefetch_for_write(&buffer_[prefetch_pos]);
        
        // 写入数据
        buffer_[current_producer] = item;
        
        // 使用 release 语义发布新位置，确保数据写入对消费者可见
        producer_pos_.store(next_producer, std::memory_order_release);
        
        return true;
    }
    
    /**
     * 高度优化的出队操作
     */
    bool dequeue(T& item) {
        size_t current_consumer = consumer_pos_.load(std::memory_order_relaxed);
        
        // 使用缓存的生产者位置减少内存访问
        if (current_consumer == get_cached_producer_pos()) {
            // 可能队列空，检查实际的生产者位置
            if (current_consumer == producer_pos_.load(std::memory_order_acquire)) {
                return false;  // 队列空
            }
        }
        
        // 预取下下个位置，为后续读取做准备
        size_t prefetch_pos = (current_consumer + 2) & MASK;
        prefetch_for_read(&buffer_[prefetch_pos]);
        
        // 读取数据
        item = buffer_[current_consumer];
        
        size_t next_consumer = (current_consumer + 1) & MASK;
        
        // 使用 release 语义发布新位置，确保空间释放对生产者可见
        consumer_pos_.store(next_consumer, std::memory_order_release);
        
        return true;
    }
    
    /**
     * 批量操作，提高缓存利用率
     */
    size_t enqueue_batch(const T* items, size_t count) {
        size_t enqueued = 0;
        
        while (enqueued < count) {
            size_t current_producer = producer_pos_.load(std::memory_order_relaxed);
            size_t available_space = Capacity - 1 - 
                ((current_producer - get_cached_consumer_pos()) & MASK);
            
            if (available_space == 0) {
                // 重新检查实际的消费者位置
                available_space = Capacity - 1 - 
                    ((current_producer - consumer_pos_.load(std::memory_order_acquire)) & MASK);
                if (available_space == 0) {
                    break;  // 队列满
                }
            }
            
            size_t batch_size = std::min(count - enqueued, available_space);
            size_t wrap_point = Capacity - (current_producer & MASK);
            
            if (batch_size <= wrap_point) {
                // 不需要环绕，可以连续拷贝
                std::copy(items + enqueued, items + enqueued + batch_size,
                         &buffer_[current_producer & MASK]);
            } else {
                // 需要环绕拷贝
                std::copy(items + enqueued, items + enqueued + wrap_point,
                         &buffer_[current_producer & MASK]);
                std::copy(items + enqueued + wrap_point, 
                         items + enqueued + batch_size,
                         &buffer_[0]);
            }
            
            producer_pos_.store((current_producer + batch_size) & MASK, 
                              std::memory_order_release);
            enqueued += batch_size;
        }
        
        return enqueued;
    }
    
    size_t dequeue_batch(T* items, size_t count) {
        size_t dequeued = 0;
        
        while (dequeued < count) {
            size_t current_consumer = consumer_pos_.load(std::memory_order_relaxed);
            size_t available_items = 
                (get_cached_producer_pos() - current_consumer) & MASK;
            
            if (available_items == 0) {
                // 重新检查实际的生产者位置
                available_items = 
                    (producer_pos_.load(std::memory_order_acquire) - current_consumer) & MASK;
                if (available_items == 0) {
                    break;  // 队列空
                }
            }
            
            size_t batch_size = std::min(count - dequeued, available_items);
            size_t wrap_point = Capacity - (current_consumer & MASK);
            
            if (batch_size <= wrap_point) {
                // 不需要环绕，可以连续拷贝
                std::copy(&buffer_[current_consumer & MASK],
                         &buffer_[(current_consumer & MASK) + batch_size],
                         items + dequeued);
            } else {
                // 需要环绕拷贝
                std::copy(&buffer_[current_consumer & MASK],
                         &buffer_[Capacity],
                         items + dequeued);
                std::copy(&buffer_[0],
                         &buffer_[batch_size - wrap_point],
                         items + dequeued + wrap_point);
            }
            
            consumer_pos_.store((current_consumer + batch_size) & MASK,
                              std::memory_order_release);
            dequeued += batch_size;
        }
        
        return dequeued;
    }
    
    /**
     * 获取队列大小（近似值）
     */
    size_t size() const {
        size_t producer = producer_pos_.load(std::memory_order_acquire);
        size_t consumer = consumer_pos_.load(std::memory_order_acquire);
        return (producer - consumer) & MASK;
    }
    
    /**
     * 检查是否为空
     */
    bool empty() const {
        return producer_pos_.load(std::memory_order_acquire) == 
               consumer_pos_.load(std::memory_order_acquire);
    }
    
    /**
     * 获取容量
     */
    constexpr size_t capacity() const {
        return Capacity - 1;  // 实际可用容量比数组大小小 1
    }
    
    /**
     * 性能调优接口
     */
    void optimize_for_throughput() {
        // 预热缓存，提高后续操作的性能
        for (size_t i = 0; i < Capacity; ++i) {
            prefetch_for_write(&buffer_[i]);
        }
    }
    
    void print_performance_stats() const {
        // 输出性能统计信息（调试用）
        printf("RingBuffer Performance Stats:\n");
        printf("- Capacity: %zu\n", Capacity);
        printf("- Cache line size: %zu\n", CACHE_LINE_SIZE);
        printf("- Producer position: %zu\n", producer_pos_.load(std::memory_order_relaxed));
        printf("- Consumer position: %zu\n", consumer_pos_.load(std::memory_order_relaxed));
        printf("- Current size: %zu\n", size());
    }
};

/**
 * 针对特定 CPU 架构优化的内存序
 * 在 x86 架构上，acquire-release 语义可以用更轻量的指令实现
 */
class ArchOptimizedMemoryOrder {
public:
#ifdef __x86_64__
    // x86 架构的内存模型比较强，可以使用更轻量的内存序
    static constexpr std::memory_order acquire = std::memory_order_acquire;
    static constexpr std::memory_order release = std::memory_order_release;
    static constexpr std::memory_order relaxed = std::memory_order_relaxed;
#elif defined(__aarch64__)
    // ARM 架构需要更严格的内存序
    static constexpr std::memory_order acquire = std::memory_order_acquire;
    static constexpr std::memory_order release = std::memory_order_release;
    static constexpr std::memory_order relaxed = std::memory_order_relaxed;
#else
    // 默认使用最安全的内存序
    static constexpr std::memory_order acquire = std::memory_order_seq_cst;
    static constexpr std::memory_order release = std::memory_order_seq_cst;
    static constexpr std::memory_order relaxed = std::memory_order_seq_cst;
#endif
};

/**
 * 性能基准测试和调优工具
 */
class PerformanceTuner {
private:
    static constexpr size_t WARMUP_ITERATIONS = 1000;
    static constexpr size_t BENCHMARK_ITERATIONS = 10000;
    
public:
    /**
     * 测量操作延迟
     */
    template<typename Func>
    static double measure_latency(Func&& func) {
        // 预热
        for (size_t i = 0; i < WARMUP_ITERATIONS; ++i) {
            func();
        }
        
        auto start = std::chrono::high_resolution_clock::now();
        
        for (size_t i = 0; i < BENCHMARK_ITERATIONS; ++i) {
            func();
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start);
        
        return static_cast<double>(duration.count()) / BENCHMARK_ITERATIONS;
    }
    
    /**
     * 测量吞吐量
     */
    template<typename Func>
    static double measure_throughput(Func&& func, size_t operations_per_call = 1) {
        auto start = std::chrono::high_resolution_clock::now();
        
        for (size_t i = 0; i < BENCHMARK_ITERATIONS; ++i) {
            func();
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        return (BENCHMARK_ITERATIONS * operations_per_call * 1000000.0) / duration.count();
    }
    
    /**
     * 检测和报告性能瓶颈
     */
    static void analyze_cache_performance() {
        printf("Cache Performance Analysis:\n");
        printf("- Cache line size: %zu bytes\n", get_cache_line_size());
        
        // 测试缓存命中率（简化版）
        constexpr size_t ARRAY_SIZE = 1024 * 1024;  // 1MB 数组
        auto* test_array = new int[ARRAY_SIZE];
        
        // 顺序访问（高缓存命中率）
        auto sequential_start = std::chrono::high_resolution_clock::now();
        volatile int sum = 0;
        for (size_t i = 0; i < ARRAY_SIZE; ++i) {
            sum += test_array[i];
        }
        auto sequential_end = std::chrono::high_resolution_clock::now();
        
        // 随机访问（低缓存命中率）
        auto random_start = std::chrono::high_resolution_clock::now();
        for (size_t i = 0; i < ARRAY_SIZE; ++i) {
            sum += test_array[rand() % ARRAY_SIZE];
        }
        auto random_end = std::chrono::high_resolution_clock::now();
        
        auto seq_duration = std::chrono::duration_cast<std::chrono::microseconds>(
            sequential_end - sequential_start);
        auto rand_duration = std::chrono::duration_cast<std::chrono::microseconds>(
            random_end - random_start);
        
        printf("- Sequential access: %ld μs\n", seq_duration.count());
        printf("- Random access: %ld μs\n", rand_duration.count());
        printf("- Cache miss penalty ratio: %.2f\n", 
               static_cast<double>(rand_duration.count()) / seq_duration.count());
        
        delete[] test_array;
    }
};

} // namespace stage5
