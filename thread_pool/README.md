# C++17 线程池

这是一个现代C++17实现的工业级线程池库，提供高性能的任务调度和执行功能。

## TODO

* 支持线程超时

## 特性

- 基于C++17标准
- 支持异步任务提交和结果获取
- 自动线程管理
- 异常安全
- 优雅关闭机制
- 完整的单元测试覆盖
- 线程安全

## 要求

- C++17兼容的编译器
- CMake 3.14或更高版本
- （可选）Google Test用于运行测试

## 构建

```bash
mkdir build
cd build
cmake ..
make
```

## 运行测试

```bash
cd build
ctest
```

## 使用示例

```cpp
#include "thread_pool/thread_pool.hpp"

int main() {
    // 创建线程池
    tp::ThreadPool pool;  // 默认使用系统支持的线程数
    
    // 提交任务
    auto future = pool.submit([](int x) { return x * x; }, 42);
    
    // 获取结果
    int result = future.get();  // 结果将是1764
    
    return 0;
}
```

## API文档

### ThreadPool类

#### 构造函数
```cpp
explicit ThreadPool(size_t thread_count = std::thread::hardware_concurrency());
```

#### 提交任务
```cpp
template<typename F, typename... Args>
auto submit(F&& f, Args&&... args) -> std::future<typename std::invoke_result_t<F, Args...>>;
```

#### 其他方法
- `thread_count()`: 返回工作线程数量
- `queue_size()`: 返回当前等待队列中的任务数量

## 性能基准测试

本项目包含一套完整的基准测试，用于评估和比较不同线程池实现的性能。

### 运行基准测试

1.  **构建项目**:
    首先，按照上面的"构建"指南编译项目。请确保`THREAD_POOL_BUILD_BENCHMARK`选项为`ON`（默认开启）。

    ```bash
    mkdir build
    cd build
    cmake ..
    make -j$(nproc)
    ```

2.  **运行脚本**:
    所有基准测试可以通过一个脚本统一运行，该脚本必须在`build`目录下执行。

    ```bash
    # 确保当前位于 build 目录
    ../benchmark/scripts/run_all_benchmarks.sh
    ```
    此脚本会自动执行所有测试（CPU密集型、IO密集型、不同实现对比等），并将JSON格式的结果保存在`build/benchmark_results/`目录中。

### 分析测试结果

我们提供了一个Python脚本来解析和可视化基准测试的结果。

1.  **安装依赖**:
    分析脚本依赖于`pandas`和`matplotlib`。请使用你的系统包管理器安装它们。对于Debian/Ubuntu系统：
    ```bash
    sudo apt-get update
    sudo apt-get install -y python3-pandas python3-matplotlib
    ```

2.  **执行分析**:
    使用`analyze_results.py`脚本来处理生成的JSON文件。你需要将`[TIMESTAMP]`替换为实际结果文件的时间戳。

    ```bash
    # 位于build目录
    python3 ../benchmark/scripts/analyze_results.py benchmark_results/optimization_comparison_[TIMESTAMP].json
    ```
    脚本将会在终端打印数据摘要，并在`benchmark_results`目录下生成PNG格式的性能对比图。

### 性能结论：优化前后对比

基准测试`benchmark_optimization_comparison`对比了两种实现：
- **OriginalThreadPool**: 一个基础的单生产者/单消费者队列模型。
- **OptimizedThreadPool**: 采用工作窃取（Work-Stealing）策略的优化版本。

**分析摘要:**
- **吞吐量**: 在高并发（线程数超过CPU核心数）场景下，采用**工作窃取**策略的`OptimizedThreadPool`表现出更好的扩展性和更高的吞吐量。这是因为工作窃取机制允许空闲线程从其他线程的任务队列中获取工作，从而提高了整体的CPU利用率。
- **适用场景**: 对于需要处理大量并发短任务的应用，`OptimizedThreadPool`是更好的选择。

### 性能结论：内存分配器对比

除了线程池调度策略，内存分配器本身对性能也有巨大影响，尤其是在大量任务涉及频繁内存分配与释放的场景。我们对比了系统默认分配器（glibc malloc）和 Google 的 `tcmalloc`。

**分析摘要:**
- **性能表现**: 在内存分配密集型基准测试 (`benchmark_memory_allocation`) 中，链接了 `tcmalloc` 的版本在所有测试的线程数下都表现出更高的吞吐量和更低的执行时间。
- **原因分析**: `tcmalloc` 的核心优势在于其高效的线程本地缓存（Thread-Local Cache）。每个线程都有自己的内存池，用于处理小对象的分配，这极大地减少了多线程环境下对全局内存锁的竞争，从而降低了分配延迟，提升了整体性能。
- **结论**: 对于需要处理大量并发任务且任务内部涉及频繁小对象创建和销毁的应用，使用 `tcmalloc` 替代默认内存分配器是一个行之有效的性能优化手段。

## 使用 Perf 进行深度性能分析

除了运行常规的基准测试获取吞吐量数据外，本项目还提供了一个脚本，用于配合 Linux 下强大的性能分析工具 `perf`，对任意一个基准测试程序进行更底层的性能剖析。这可以帮助你获得CPU周期、指令数、缓存命中率、分支预测等硬件层面的详细数据，从而进行更精准的性能优化。

### 要求

- Linux环境
- 已安装 `perf` 工具 (通常包含在 `linux-tools-common`, `linux-tools-generic` 等包中)
- 当前用户有权限执行 `perf` (可能需要 `sudo` 或特定的 `kernel.perf_event_paranoid` sysctl 设置)

### 分析步骤

1.  **构建项目**:
    确保项目已成功编译，并且 benchmark 可执行文件已生成在 `build/benchmark/` 目录下。

2.  **运行分析脚本**:
    `run_perf_analysis.sh` 脚本必须在 `build` 目录下执行。它需要一个参数：你希望分析的 benchmark 程序的路径。

    ```bash
    # 位于 build 目录
    # 示例：分析 CPU 密集型任务
    bash ../benchmark/scripts/run_perf_analysis.sh ./benchmark/benchmark_cpu_intensive
    ```

    你也可以分析其他 benchmark，例如：
    ```bash
    # 分析优化后的线程池
    bash ../benchmark/scripts/run_perf_analysis.sh ./benchmark/benchmark_optimization_comparison
    ```

    脚本会自动调用 `perf record` 来记录性能事件，并将结果保存为一个 `.data` 文件，存放在 `build/perf_results/` 目录下。

    **注意**: 脚本默认采集 `cycles` (CPU周期) 事件。在某些虚拟化环境中，这个事件可能不被支持。如果脚本执行出错，请编辑 `benchmark/scripts/run_perf_analysis.sh` 文件，将 `PERF_EVENTS` 变量中的 `cycles` 移除。

3.  **生成性能报告**:
    当脚本运行完毕后，它会提示你如何使用 `perf report` 命令来查看分析结果。

    ```bash
    # 位于 build 目录
    perf report -i perf_results/benchmark_cpu_intensive_[TIMESTAMP].data
    ```

    `perf report` 会启动一个交互式界面，展示程序中各个函数和符号的性能开销（例如，CPU周期占比）。你可以深入挖掘热点函数，查看其汇编代码级别的性能数据。这对于定位CPU瓶颈、分析缓存未命中和分支预测错误等问题非常有用。

