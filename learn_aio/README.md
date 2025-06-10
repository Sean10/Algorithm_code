# AIO 基准测试工具

一个基于 Linux AIO (libaio) 的高性能IO基准测试工具，类似于 fio，专门用于测试块设备和文件的随机/顺序读写性能。

## 功能特性

### 核心功能
- **多种异步IO引擎**: 支持 Linux AIO (libaio) 和 io_uring 两种高性能异步IO引擎
- **Direct IO**: 支持 O_DIRECT 绕过系统缓存，直接访问存储设备
- **多种IO模式**: 支持随机读、随机写、随机读写、顺序读、顺序写
- **多线程支持**: 支持多线程并发测试，自动设置CPU亲和性
- **灵活配置**: 支持自定义块大小、队列深度、运行时间等参数

### 性能特性
- **内存池管理**: 高效的对齐内存分配和重用
- **批量IO处理**: 支持批量提交和完成处理
- **零拷贝设计**: 最小化数据拷贝开销
- **轮询模式**: 支持低延迟轮询模式

### 统计和监控
- **实时统计**: IOPS、带宽、延迟统计
- **延迟分布**: P95、P99 延迟统计
- **多种输出格式**: 支持文本、JSON、CSV 格式输出
- **数据验证**: 可选的数据正确性验证

## 系统要求

- Linux 内核 2.6+ (支持 AIO)
- Linux 内核 5.1+ (支持 io_uring，可选)
- libaio 库
- liburing 库 (使用 io_uring 时需要)
- C++17 编译器 (GCC 7+ 或 Clang 5+)
- CMake 3.10+

## 安装依赖

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install libaio-dev liburing-dev cmake build-essential
```

### CentOS/RHEL/openEuler
```bash
sudo yum install libaio-devel liburing-devel cmake gcc-c++ make
# 或者对于较新版本
sudo dnf install libaio-devel liburing-devel cmake gcc-c++ make
```

## 项目结构

```
learn_aio/
├── src/                    # 源代码目录
│   ├── main.cpp           # 主程序入口
│   ├── config.h/cpp       # 配置管理
│   ├── aio_engine.h/cpp   # libaio引擎实现
│   ├── uring_engine.h/cpp # io_uring引擎实现
│   ├── io_engine.h        # 通用IO引擎接口
│   ├── benchmark.h/cpp    # 基准测试控制
│   ├── stats.h/cpp        # 统计收集
│   ├── utils.h/cpp        # 工具函数
│   └── nanobench_impl.cpp # nanobench库实现
├── include/               # 第三方库头文件
│   └── nanobench.h        # nanobench性能分析库
├── tools/                 # 工具程序目录
│   ├── CMakeLists.txt     # 工具程序独立构建文件
│   ├── README.md          # 工具程序说明文档
│   └── test_nanobench.cpp # nanobench环境检测工具
├── CMakeLists.txt         # 主项目CMake构建文件
├── test.sh               # 自动化测试脚本
├── README.md             # 项目说明
└── DESIGN.md             # 技术设计文档
```

## 编译

### 主程序编译
```bash
# 克隆代码
git clone <repository-url>
cd learn_aio

# 创建构建目录
mkdir build
cd build

# 配置和编译
cmake ..
make -j$(nproc)

# 安装（可选）
sudo make install
```

### Sanitizer构建
```bash
# 使用Makefile快速构建
make help          # 查看所有构建选项
make asan          # AddressSanitizer版本
make tsan          # ThreadSanitizer版本
make ubsan         # UndefinedBehaviorSanitizer版本

# 使用构建脚本
./build_with_sanitizer.sh asan --test    # 构建并测试
./build_with_sanitizer.sh --help         # 查看帮助

# 快速测试所有sanitizer
make quick-test
```

### 工具程序编译
```bash
# 编译tools目录中的工具程序
cd tools
mkdir build
cd build
cmake ..
make

# 运行环境检测工具
./test_nanobench
```

## 使用方法

### 基本用法

```bash
# 测试文件的随机读写性能（默认参数）
./aio_bench -f test.dat

# 测试块设备的随机读性能
./aio_bench -f /dev/nvme0n1 -p rand_read -q 64 -t 4 -r 60

# 测试大文件的顺序写性能
./aio_bench -f bigfile.dat -s 10G -p seq_write -b 1M -d
```

### 命令行参数

| 参数 | 长选项 | 说明 | 默认值 |
|------|--------|------|--------|
| `-f` | `--file` | 测试文件或块设备路径 (必需) | 无 |
| `-s` | `--size` | 文件大小 | 1GB |
| `-b` | `--block-size` | IO块大小 | 4096 |
| `-p` | `--pattern` | IO模式 | rand_rw |
| `-q` | `--queue-depth` | 队列深度 | 32 |
| `-t` | `--threads` | 线程数 | 1 |
| `-r` | `--runtime` | 运行时间(秒) | 30 |
| `-d` | `--direct` | 使用Direct IO | 启用 |
| `-v` | `--verify` | 验证数据正确性 | 禁用 |
| `-V` | `--verbose` | 详细输出 | 禁用 |
| `-B` | `--batch-size` | 批量提交大小 | 16 |
| `-P` | `--polling` | 使用轮询模式 | 禁用 |
| `-o` | `--output-format` | 输出格式 | text |
| `-e` | `--engine-type` | IO引擎类型 | libaio |
| `-M` | `--perf-benchmark` | 启用性能分析模式 | 禁用 |

### IO模式说明

| 模式 | 说明 |
|------|------|
| `rand_read` | 随机读 |
| `rand_write` | 随机写 |
| `rand_rw` | 随机读写混合 |
| `seq_read` | 顺序读 |
| `seq_write` | 顺序写 |

### IO引擎类型说明

| 引擎 | 说明 | 内核要求 |
|------|------|----------|
| `libaio` | Linux AIO (默认) | 2.6+ |
| `io_uring` | 新一代异步IO接口 | 5.1+ |

### 输出格式

#### 文本格式（默认）
```
=== 配置信息 ===
文件/设备: /dev/nvme0n1
文件大小: 1073741824 字节
块大小: 4096 字节
IO模式: 随机读写
队列深度: 32
线程数: 4
运行时间: 30 秒
...

=== 最终统计报告 ===
总运行时间: 30.12 秒
总操作数: 45678
平均 IOPS: 1516.23
平均带宽: 5.93 MB/s
平均延迟: 84.5 μs
P95延迟: 156.7 μs
P99延迟: 234.1 μs
```

#### JSON格式
```bash
./aio_bench -f test.dat -o json
```

#### CSV格式
```bash
./aio_bench -f test.dat -o csv
```

## 使用示例

### 1. NVMe SSD 性能测试
```bash
# 4K随机读测试，高队列深度
./aio_bench -f /dev/nvme0n1 -p rand_read -b 4k -q 128 -t 8 -r 60

# 4K随机写测试
./aio_bench -f /dev/nvme0n1 -p rand_write -b 4k -q 32 -t 4 -r 30

# 混合读写测试
./aio_bench -f /dev/nvme0n1 -p rand_rw -b 4k -q 64 -t 4 -r 60
```

### 2. 大块顺序IO测试
```bash
# 1M顺序读测试
./aio_bench -f /dev/nvme0n1 -p seq_read -b 1M -q 16 -t 2 -r 30

# 1M顺序写测试
./aio_bench -f /dev/nvme0n1 -p seq_write -b 1M -q 8 -t 1 -r 30
```

### 3. 文件系统性能测试
```bash
# 创建测试文件并测试
./aio_bench -f /mnt/test/large.dat -s 10G -p rand_rw -b 64k -q 32 -t 4 -r 120

# 数据验证测试
./aio_bench -f test.dat -s 1G -p rand_rw -v -V -r 60
```

### 4. 延迟敏感测试
```bash
# 低队列深度延迟测试
./aio_bench -f /dev/nvme0n1 -p rand_read -b 4k -q 1 -t 1 -r 30 -V

# 轮询模式低延迟测试
./aio_bench -f /dev/nvme0n1 -p rand_read -b 4k -q 8 -P -r 30
```

### 5. IO引擎对比测试
```bash
# 使用libaio引擎测试
./aio_bench -f test.dat -e libaio -p rand_rw -q 32 -t 2 -r 10

# 使用io_uring引擎测试
./aio_bench -f test.dat -e io_uring -p rand_rw -q 32 -t 2 -r 10

# 运行对比脚本
./compare_engines.sh
```

### 6. 性能分析测试
```bash
# 启用nanobench性能分析
./aio_bench -f /dev/nvme0n1 -p rand_read -b 4k -q 32 -r 10 -M

# 检测nanobench环境支持
./tools/test_nanobench
```

## 性能调优建议

### 1. 系统配置
```bash
# 设置IO调度器（适用于SSD）
echo noop > /sys/block/nvme0n1/queue/scheduler

# 调整队列深度
echo 128 > /sys/block/nvme0n1/queue/nr_requests

# 禁用节能模式
echo performance > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### 2. 参数调优
- **队列深度**: SSD通常使用32-128，HDD使用8-32
- **线程数**: 不超过CPU核心数，通常为CPU核心数的50%-100%
- **块大小**: 随机IO使用4K-16K，顺序IO使用64K-1M
- **Direct IO**: 测试原始性能时务必启用

### 3. 监控指标
- **IOPS**: 关注随机IO性能
- **带宽**: 关注顺序IO性能  
- **延迟**: 关注响应时间，特别是P99延迟
- **CPU使用率**: 避免CPU成为瓶颈

## 与io_uring对比

本工具专门设计用于与io_uring性能对比：

| 特性 | libaio | io_uring |
|------|--------|----------|
| 内核版本 | 2.6+ | 5.1+ |
| API复杂度 | 中等 | 简单 |
| 性能 | 高 | 更高 |
| 功能 | 基础异步IO | 丰富的异步操作 |
| 兼容性 | 广泛 | 较新 |

## 调试和错误检测

### Sanitizer工具

项目支持多种sanitizer用于检测各类错误：

```bash
# 内存错误检测 (推荐日常使用)
make asan
cd build_asan
export ASAN_OPTIONS="abort_on_error=1:detect_leaks=1"
./aio_bench -f test.dat -e libaio -r 30

# 线程安全检测
make tsan  
cd build_tsan
export TSAN_OPTIONS="abort_on_error=1"
./aio_bench -f test.dat -e libaio -t 4 -r 30

# 未定义行为检测
make ubsan
cd build_ubsan
./aio_bench -f test.dat -e libaio -r 30
```

详细使用方法请参考 [SANITIZER_GUIDE.md](SANITIZER_GUIDE.md)

## 故障排除

### 常见问题

1. **权限错误**
   ```bash
   # 确保有读写权限
   sudo chmod 666 /dev/nvme0n1
   # 或以root运行
   sudo ./aio_bench -f /dev/nvme0n1
   ```

2. **内存不足**
   ```bash
   # 减少队列深度或线程数
   ./aio_bench -f test.dat -q 16 -t 2
   ```

3. **libaio未安装**
   ```bash
   # 安装libaio开发包
   sudo apt-get install libaio-dev
   ```

4. **Direct IO对齐错误**
   ```bash
   # 使用4K对齐的块大小
   ./aio_bench -f test.dat -b 4096
   ```

5. **Sanitizer相关问题**
   ```bash
   # 如果sanitizer版本运行太慢
   ./aio_bench -f test.dat -r 5 -q 8 -t 1
   
   # 查看详细错误信息
   export ASAN_OPTIONS="abort_on_error=0:halt_on_error=0"
   ```

## 开发和贡献

### 编译调试版本
```bash
mkdir debug
cd debug
cmake -DCMAKE_BUILD_TYPE=Debug ..
make -j$(nproc)
```

### 代码结构
```
src/
├── main.cpp           # 程序入口
├── config.{h,cpp}     # 配置管理
├── aio_engine.{h,cpp} # AIO引擎核心
├── benchmark.{h,cpp}  # 基准测试控制
├── stats.{h,cpp}      # 统计和报告
├── utils.{h,cpp}      # 工具函数
└── nanobench_impl.cpp # nanobench库实现

include/
└── nanobench.h        # nanobench性能分析库

tools/
├── CMakeLists.txt     # 工具程序构建配置
└── test_nanobench.cpp # nanobench环境检测工具
```

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 作者

开发用于异步IO性能测试和与io_uring技术对比研究。 