# 生产者-消费者队列：从基础到高级的学习之旅

[![构建状态](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![测试覆盖率](https://img.shields.io/badge/coverage-90%25-green.svg)]()
[![许可证](https://img.shields.io/badge/license-MIT-blue.svg)]()

本项目是一个系统化的生产者-消费者模式学习项目，涵盖从基础的互斥锁队列到高级无锁数据结构的完整实现和性能分析。

## 🎯 项目目标

- **学习**: 系统掌握无锁编程的核心概念和实现技术
- **实践**: 通过完整的代码实现加深理解
- **对比**: 通过性能基准测试直观感受不同实现的差异
- **应用**: 通过 gRPC 服务化展示实际应用场景

## 📚 学习路径

项目按照循序渐进的学习路径组织，每个阶段都有对应的实现、测试和文档：

### 阶段一：基础概念 📖
- **位置**: `src/stage1_basics/`
- **内容**: 互斥锁队列的经典实现
- **重点**: 理解线程安全、条件变量、RAII
- **文件**: `mutex_queue.hpp`

### 阶段二：SPSC 无锁队列 🚀
- **位置**: `src/stage2_spsc/`
- **内容**: 单生产者单消费者无锁环形缓冲区
- **重点**: 内存序、acquire-release 语义、缓存行对齐
- **文件**: `spsc_ring_buffer.hpp`

### 阶段三：MPMC 无锁队列 🔥
- **位置**: `src/stage3_mpmc/`
- **内容**: Michael-Scott 队列算法、ABA 问题
- **重点**: CAS 操作、标记指针、内存回收
- **状态**: 🚧 待实现

### 阶段四：安全内存回收 ⚡
- **位置**: `src/stage4_smr/`
- **内容**: 险象指针、基于纪元的回收
- **重点**: 内存安全、性能权衡
- **状态**: 🚧 待实现

### 阶段五：性能优化 💎
- **位置**: `src/stage5_optimization/`
- **内容**: 伪共享、缓存行对齐、NUMA 优化
- **重点**: 硬件感知的优化技术
- **状态**: 🚧 待实现

### 阶段六：服务化应用 🌐
- **位置**: `grpc_service/`
- **内容**: gRPC 服务封装、多语言客户端
- **重点**: 系统集成、跨语言互操作

## 🛠️ 快速开始

### 环境要求

- C++17 兼容编译器 (GCC 7+ / Clang 5+)
- CMake 3.10+
- Boost 库
- Google Test (可选，用于测试)

### 一键构建

```bash
# 克隆项目
git clone <repository-url>
cd simulate_producer_consumer

# 构建所有组件
./scripts/build.sh

# 运行测试
./scripts/run_tests.sh

# 运行基准测试
./scripts/run_benchmarks.sh
```

### 分步构建

```bash
# 只构建基准测试
./scripts/build.sh --no-tests --no-examples

# Debug 构建
./scripts/build.sh --debug

# 启用代码覆盖率
./scripts/build.sh --coverage
```

## 🧪 测试系统

项目采用多层次的测试策略：

### 单元测试
```bash
# 运行所有单元测试
./scripts/run_tests.sh --unit

# 详细输出
./scripts/run_tests.sh --unit --verbose
```

### 集成测试
```bash
# 运行集成测试
./scripts/run_tests.sh --integration
```

### 性能基准
```bash
# 完整基准测试
./scripts/run_benchmarks.sh

# 自定义参数
QUEUE_SIZES="1024 4096" CONSUMERS="2 4 8" ./scripts/run_benchmarks.sh
```

## 📊 性能结果

基于 OpenEuler 系统的典型性能数据：

| 指标 | 互斥锁队列 | SPSC 无锁队列 | Boost 无锁队列 |
|------|------------|---------------|----------------|
| 平均延迟 | ~2.6 μs | ~0.33 μs | ~0.33 μs |
| 最大延迟 | ~220 μs | ~9 μs | ~9 μs |
| 吞吐量 | ~1.5M ops/s | ~12M ops/s | ~12M ops/s |
| 公平性 | ✅ 优秀 | ⚠️ 有限 | ⚠️ 有限 |

*注：实际性能取决于硬件配置、负载模式和编译优化级别*

## 📁 项目结构

```
simulate_producer_consumer/
├── src/                    # 核心实现
│   ├── stage1_basics/      # 阶段一：基础概念
│   ├── stage2_spsc/        # 阶段二：SPSC 队列
│   ├── stage3_mpmc/        # 阶段三：MPMC 队列
│   ├── stage4_smr/         # 阶段四：内存回收
│   └── stage5_optimization/# 阶段五：性能优化
├── benchmarks/             # 性能基准测试
├── tests/                  # 单元和集成测试
├── examples/               # 示例程序
├── grpc_service/           # gRPC 服务化
├── scripts/                # 构建和测试脚本
├── results/                # 测试和基准结果
└── docs/                   # 文档
```

## 🎮 示例程序

### 基础使用示例
```bash
# 运行基础示例
./build/examples/basic_usage/simple_producer_consumer
```

### 基准测试示例
```bash
# 运行基准测试
./build/benchmarks/queue_benchmark --help

# 自定义参数
./build/benchmarks/queue_benchmark \
  --queue-size 8192 \
  --test-count 1000 \
  --consumers 4 \
  --csv-summary results/my_test.csv
```

## 📖 学习资源

- **`guide.md`**: 详细的学习指南和理论基础
- **测试代码**: 最佳的使用示例和边界情况处理
- **基准代码**: 性能测试的实现细节
- **学术论文**: Michael & Scott 算法、Hazard Pointers 等


## 📋 待办事项

- [ ] 实现 Michael-Scott MPMC 队列
- [ ] 添加 Hazard Pointers 内存回收
- [ ] 实现 Epoch-Based 回收机制
- [ ] 添加 NUMA 感知优化
- [ ] 完善 gRPC 服务实现
- [ ] 添加更多性能分析工具
