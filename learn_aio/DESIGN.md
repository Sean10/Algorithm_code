# AIO 基准测试工具 - 技术设计文档

## 系统架构

### 整体架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   main.cpp      │    │   config.h      │    │   utils.h       │
│   程序入口       │    │   配置管理       │    │   工具函数       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
               ┌─────────────────────────────────┐
               │         benchmark.h             │
               │        基准测试控制器            │
               └─────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   aio_engine.h  │    │    stats.h      │    │   worker        │
│   AIO引擎核心    │    │   性能统计       │    │   工作线程       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
┌─────────────────┐
│   Linux AIO     │
│   (libaio)      │
└─────────────────┘
```

### 核心组件

#### 1. Config (配置管理)
- **职责**: 命令行参数解析、配置验证、默认值管理
- **特性**: 
  - 完整的命令行选项支持
  - 智能默认值
  - 参数验证和错误提示
  - 多种输出格式配置

#### 2. AIOEngine (AIO引擎)
- **职责**: Linux AIO的封装和管理
- **特性**:
  - 异步IO上下文管理
  - 内存池管理（对齐内存分配）
  - IO请求的生命周期管理
  - 批量提交和完成处理

#### 3. StatsCollector (统计收集器)
- **职责**: 性能指标收集和报告生成
- **特性**:
  - 实时IOPS/带宽/延迟统计
  - 延迟分布计算（P95, P99）
  - 多格式输出支持
  - 线程安全的统计数据

#### 4. Benchmark (基准测试控制器)
- **职责**: 测试流程控制和线程管理
- **特性**:
  - 多线程工作调度
  - 信号处理和优雅停止
  - 进度监控和报告
  - CPU亲和性设置

## Linux AIO 实现细节

### AIO 上下文管理

```cpp
// AIO上下文初始化
io_context_t ctx = 0;
int ret = io_setup(queue_depth, &ctx);

// AIO上下文清理
io_destroy(ctx);
```

### IO 请求生命周期

1. **请求准备**
   ```cpp
   struct iocb cb;
   memset(&cb, 0, sizeof(cb));
   cb.aio_fildes = fd;
   cb.aio_lio_opcode = IO_CMD_PREAD; // 或 IO_CMD_PWRITE
   cb.aio_buf = (uint64_t)buffer;
   cb.aio_nbytes = size;
   cb.aio_offset = offset;
   cb.aio_data = user_data;
   ```

2. **请求提交**
   ```cpp
   struct iocb* cbs[] = {&cb};
   int ret = io_submit(ctx, 1, cbs);
   ```

3. **完成等待**
   ```cpp
   struct io_event events[max_events];
   int num = io_getevents(ctx, min_nr, max_nr, events, timeout);
   ```

4. **结果处理**
   ```cpp
   for (int i = 0; i < num; i++) {
       struct io_event* event = &events[i];
       // event->res 包含实际传输的字节数
       // event->data 包含用户数据
   }
   ```

### 内存管理策略

#### 对齐内存分配
```cpp
void* aligned_alloc(size_t size, size_t alignment = 4096) {
    void* ptr = nullptr;
    if (posix_memalign(&ptr, alignment, size) != 0) {
        return nullptr;
    }
    return ptr;
}
```

**为什么需要内存对齐？**
- Direct IO要求缓冲区地址按页大小(4096字节)对齐
- 提高DMA传输效率
- 避免跨页访问导致的性能损失

#### 内存池设计
- 预分配 `queue_depth * 2` 个缓冲区
- 使用轮询分配策略减少锁竞争
- 自动内存对齐和生命周期管理

### Direct IO 特性

#### 启用Direct IO
```cpp
int flags = O_RDWR | O_DIRECT;
int fd = open(filename.c_str(), flags);
```

#### Direct IO优势
- 绕过系统缓存，直接访问存储设备
- 减少内存拷贝开销
- 更准确的性能测试结果
- 适合大文件和高性能存储测试

#### Direct IO限制
- 缓冲区必须内存对齐（通常4K）
- 读写大小必须是块大小的倍数
- 偏移量必须对齐
- 某些文件系统可能不支持

## 性能优化设计

### 1. 零拷贝架构
- 使用Direct IO避免内核缓冲
- 预分配对齐内存池
- 避免不必要的内存拷贝

### 2. 批量处理
```cpp
// 批量提交IO请求
std::vector<struct iocb*> cbs;
for (int i = 0; i < batch_size; i++) {
    cbs.push_back(&requests[i].cb);
}
io_submit(ctx, cbs.size(), cbs.data());
```

### 3. 轮询优化
```cpp
// 轮询模式 - 零超时
struct timespec timeout = {0, 0};
int num = io_getevents(ctx, 0, max_events, events, &timeout);

// 阻塞模式 - 有超时
struct timespec timeout = {0, 1000000}; // 1ms
int num = io_getevents(ctx, 1, max_events, events, &timeout);
```

### 4. 多线程设计
- 每线程独立的AIO上下文
- 无锁的统计数据收集
- CPU亲和性绑定减少上下文切换

## 统计算法实现

### IOPS 计算
```cpp
double get_iops() const {
    double elapsed = get_elapsed_seconds();
    return static_cast<double>(total_operations) / elapsed;
}
```

### 带宽计算
```cpp
double get_bandwidth_mbps() const {
    double elapsed = get_elapsed_seconds();
    return (static_cast<double>(total_bytes) / (1024.0 * 1024.0)) / elapsed;
}
```

### 延迟百分位数计算
```cpp
uint64_t get_percentile_latency(double percentile) const {
    std::vector<uint64_t> sorted_latencies = latencies;
    std::sort(sorted_latencies.begin(), sorted_latencies.end());
    
    size_t index = static_cast<size_t>((percentile / 100.0) * 
                                      (sorted_latencies.size() - 1));
    return sorted_latencies[index];
}
```

## 随机数生成优化

### 线程本地随机数生成器
```cpp
thread_local std::mt19937 rng(std::random_device{}());

uint64_t generate_random_offset(uint64_t max_offset, uint32_t block_size) {
    std::uniform_int_distribution<uint64_t> dist(0, max_offset / block_size);
    return dist(rng) * block_size;
}
```

**优化考虑：**
- 避免全局锁竞争
- 每线程独立的随机状态
- 高质量的随机数算法

## 错误处理策略

### AIO错误处理
```cpp
int ret = io_submit(ctx, 1, cbs);
if (ret < 0) {
    // 处理提交错误
    handle_submit_error(-ret);
}

// 检查完成状态
if (event.res < 0) {
    // 处理IO错误
    handle_io_error(-event.res);
} else if (event.res != expected_size) {
    // 处理部分IO
    handle_partial_io(event.res, expected_size);
}
```

### 优雅停止机制
```cpp
// 信号处理
signal(SIGINT, signal_handler);

// 工作线程检查
while (!should_stop && !time_expired) {
    // 执行IO操作
}

// 等待所有IO完成
while (engine.get_pending_count() > 0) {
    engine.wait_for_completion(100);
}
```

## 与io_uring的对比设计

### 相同的测试接口
- 统一的配置参数
- 相同的统计指标
- 一致的输出格式
- 可比较的测试模式

### 差异化实现
| 特性 | libaio | io_uring |
|------|--------|----------|
| 系统调用 | io_setup/submit/getevents | io_uring_setup/enter |
| 队列模型 | 传统提交/完成队列 | 共享内存环形队列 |
| 批量操作 | 数组批量提交 | 环形队列批量 |
| 轮询支持 | 有限支持 | 原生轮询支持 |
| 内核版本 | 2.6+ | 5.1+ |

## 性能基准测试方法

### 测试矩阵
1. **IO模式**: 随机读、随机写、随机读写、顺序读、顺序写
2. **块大小**: 4K, 8K, 16K, 32K, 64K, 128K, 256K, 512K, 1M
3. **队列深度**: 1, 2, 4, 8, 16, 32, 64, 128, 256
4. **线程数**: 1, 2, 4, 8, 16

### 关键指标
- **IOPS**: 每秒IO操作数
- **带宽**: MB/s
- **延迟**: 平均延迟、P95延迟、P99延迟
- **CPU使用率**: 系统和用户CPU时间
- **错误率**: 失败的IO操作比例

### 测试环境要求
- 专用测试系统
- 禁用节能模式
- 固定CPU频率
- 隔离测试存储
- 清理系统缓存

## 代码质量保证

### 编译选项
```bash
CXXFLAGS = -std=c++17 -Wall -Wextra -O3 -g
```

### 内存检查
```bash
# 使用Valgrind检查内存泄漏
valgrind --leak-check=full ./aio_bench -f test.dat -r 10

# 使用AddressSanitizer
g++ -fsanitize=address -g -o aio_bench_debug src/*.cpp -laio
```

### 性能分析
```bash
# 使用perf分析热点
perf record -g ./aio_bench -f /dev/nvme0n1 -r 30
perf report

# CPU使用率分析
top -H -p $(pgrep aio_bench)
```

## 扩展性设计

### 插件化IO引擎
```cpp
class IOEngine {
public:
    virtual bool initialize() = 0;
    virtual bool submit_io(uint64_t offset, uint32_t size, bool is_read) = 0;
    virtual int wait_for_completion(int timeout_ms) = 0;
    virtual ~IOEngine() = default;
};

class AIOEngine : public IOEngine { ... };
class IOUringEngine : public IOEngine { ... };
```

### 配置驱动测试
```cpp
// 支持配置文件驱动的批量测试
struct TestCase {
    std::string name;
    IOPattern pattern;
    uint32_t block_size;
    uint32_t queue_depth;
    uint32_t num_threads;
    uint32_t runtime_seconds;
};
```

这个技术设计确保了工具的高性能、可扩展性和与io_uring的可比较性，为后续的性能对比研究提供了坚实的基础。 