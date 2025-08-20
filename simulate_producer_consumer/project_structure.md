# 新项目架构设计

## 目录结构
```
simulate_producer_consumer/
├── README.md                          # 项目概述
├── guide.md                          # 学习指南
├── CMakeLists.txt                    # 顶层构建文件
│
├── src/                              # 核心实现
│   ├── stage1_basics/                # 阶段一：基础概念
│   │   ├── mutex_queue.hpp           # 互斥锁队列
│   │   └── lockfree_concepts.hpp     # 无锁基础概念
│   │
│   ├── stage2_spsc/                  # 阶段二：SPSC队列
│   │   ├── spsc_ring_buffer.hpp      # SPSC环形缓冲区
│   │   └── spsc_examples.cpp         # 使用示例
│   │
│   ├── stage3_mpmc/                  # 阶段三：MPMC队列
│   │   ├── michael_scott_queue.hpp   # Michael-Scott队列
│   │   └── aba_examples.cpp          # ABA问题示例
│   │
│   ├── stage4_smr/                   # 阶段四：安全内存回收
│   │   ├── hazard_pointers.hpp       # 险象指针
│   │   └── epoch_based_reclaim.hpp   # 基于纪元的回收
│   │
│   └── stage5_optimization/          # 阶段五：性能优化
│       ├── cache_aligned.hpp         # 缓存行对齐
│       └── false_sharing_demo.cpp    # 伪共享演示
│
├── benchmarks/                       # 性能基准测试
│   ├── CMakeLists.txt
│   ├── queue_benchmark.cpp           # 主基准程序
│   └── tools/
│       ├── csv_writer.hpp            # CSV输出工具
│       └── benchmark_utils.hpp       # 基准测试工具
│
├── tests/                            # 单元测试
│   ├── CMakeLists.txt
│   ├── unit/                         # 单元测试
│   │   ├── test_mutex_queue.cpp
│   │   ├── test_spsc_queue.cpp
│   │   ├── test_mpmc_queue.cpp
│   │   └── test_benchmark_tools.cpp
│   │
│   ├── integration/                  # 集成测试
│   │   ├── test_producer_consumer.cpp
│   │   └── test_stress.cpp
│   │
│   └── scripts/                      # 测试脚本
│       ├── run_unit_tests.sh
│       ├── run_integration_tests.sh
│       └── run_all_tests.sh
│
├── examples/                         # 示例代码
│   ├── basic_usage/
│   │   ├── simple_producer_consumer.cpp
│   │   └── multiple_queues_demo.cpp
│   │
│   └── advanced/
│       ├── memory_model_demo.cpp
│       └── performance_tuning.cpp
│
├── grpc_service/                     # 阶段六：gRPC服务化
│   ├── proto/
│   │   └── producer_consumer.proto
│   ├── server/
│   │   └── queue_service.py
│   ├── client/
│   │   ├── client.py
│   │   └── multi_client.py
│   └── requirements.txt
│
├── scripts/                          # 构建和测试脚本
│   ├── build.sh                      # 统一构建脚本
│   ├── run_benchmarks.sh             # 基准测试脚本
│   ├── run_tests.sh                  # 测试运行脚本
│   └── setup_dev_env.sh              # 开发环境设置
│
├── docs/                             # 文档
│   ├── api/                          # API文档
│   ├── design/                       # 设计文档
│   └── tutorials/                    # 教程
│
└── results/                          # 测试和基准结果
    └── [timestamp]/
        ├── env.txt
        ├── latency.csv
        └── summary.csv
```

## 构建系统
- 使用 CMake 的多目标构建
- 支持单独构建各个阶段的代码
- 集成 Google Test 框架
- 支持代码覆盖率检查

## 测试框架
- 单元测试：验证各个组件的正确性
- 集成测试：验证完整的生产者-消费者流程
- 压力测试：验证高并发场景下的稳定性
- 基准测试：性能对比分析

## 脚本化流程
- 一键构建：`scripts/build.sh`
- 一键测试：`scripts/run_tests.sh`
- 一键基准：`scripts/run_benchmarks.sh`
- CI/CD 支持
