# Sanitizer 使用指南

本文档介绍如何使用各种sanitizer来检测AIO基准测试工具中的内存错误、数据竞争等问题。

## 概述

Sanitizer是一系列编译时和运行时工具，用于检测程序中的各种错误：

- **AddressSanitizer (ASan)**: 检测内存错误
- **ThreadSanitizer (TSan)**: 检测数据竞争
- **UndefinedBehaviorSanitizer (UBSan)**: 检测未定义行为
- **MemorySanitizer (MSan)**: 检测未初始化内存读取

## 快速开始

### 使用Makefile构建

```bash
# 查看所有可用目标
make help

# 构建不同sanitizer版本
make asan      # AddressSanitizer
make tsan      # ThreadSanitizer
make ubsan     # UndefinedBehaviorSanitizer
make msan      # MemorySanitizer

# 快速测试常用sanitizer
make quick-test

# 测试所有sanitizer版本
make test-all
```

### 使用构建脚本

```bash
# 查看帮助
./build_with_sanitizer.sh --help

# 构建并测试AddressSanitizer版本
./build_with_sanitizer.sh asan --test

# 清理后构建Release版本
./build_with_sanitizer.sh --clean release
```

## 详细说明

### 1. AddressSanitizer (ASan)

**用途**: 检测内存错误，包括：
- 缓冲区溢出
- 使用后释放 (use-after-free)
- 重复释放 (double-free)
- 内存泄漏
- 栈溢出

**构建**:
```bash
make asan
# 或
./build_with_sanitizer.sh asan
```

**使用**:
```bash
# 设置环境变量
export ASAN_OPTIONS="abort_on_error=1:fast_unwind_on_malloc=0:detect_leaks=1"

# 运行测试
cd build_asan
./aio_bench -f test.dat -e libaio -r 10 -q 32
```

**常用环境变量**:
```bash
export ASAN_OPTIONS="
abort_on_error=1:
fast_unwind_on_malloc=0:
detect_leaks=1:
check_initialization_order=1:
strict_init_order=1
"
```

### 2. ThreadSanitizer (TSan)

**用途**: 检测多线程程序中的数据竞争和线程安全问题

**构建**:
```bash
make tsan
# 或
./build_with_sanitizer.sh tsan
```

**使用**:
```bash
# 设置环境变量
export TSAN_OPTIONS="abort_on_error=1:halt_on_error=1"

# 运行多线程测试
cd build_tsan
./aio_bench -f test.dat -e libaio -t 4 -r 10 -q 32
```

**常用环境变量**:
```bash
export TSAN_OPTIONS="
abort_on_error=1:
halt_on_error=1:
report_bugs=1:
report_thread_leaks=1
"
```

### 3. UndefinedBehaviorSanitizer (UBSan)

**用途**: 检测未定义行为，包括：
- 整数溢出
- 空指针解引用
- 数组越界
- 类型转换错误

**构建**:
```bash
make ubsan
# 或
./build_with_sanitizer.sh ubsan
```

**使用**:
```bash
# 设置环境变量
export UBSAN_OPTIONS="abort_on_error=1:print_stacktrace=1"

# 运行测试
cd build_ubsan
./aio_bench -f test.dat -e libaio -r 10 -q 32
```

### 4. MemorySanitizer (MSan)

**用途**: 检测未初始化内存的读取

**注意**: MSan要求所有依赖库都用MSan重新编译，使用较为复杂。

**构建**:
```bash
make msan
# 或
./build_with_sanitizer.sh msan
```

**使用**:
```bash
# 设置环境变量
export MSAN_OPTIONS="abort_on_error=1:print_stats=1"

# 运行测试
cd build_msan
./aio_bench -f test.dat -e libaio -r 10 -q 32
```

## 性能影响

不同sanitizer对性能的影响：

| Sanitizer | 内存开销 | 运行时开销 | 适用场景 |
|-----------|----------|------------|----------|
| ASan | 2-3x | 2x | 开发和测试 |
| TSan | 5-10x | 5-15x | 多线程调试 |
| UBSan | 最小 | 最小 | 持续集成 |
| MSan | 2-3x | 3x | 特殊调试 |

## 最佳实践

### 1. 开发阶段

```bash
# 日常开发使用ASan
make asan
cd build_asan
export ASAN_OPTIONS="abort_on_error=1:detect_leaks=1"
./aio_bench -f test.dat -e libaio -r 30
```

### 2. 多线程测试

```bash
# 专门测试线程安全
make tsan
cd build_tsan
export TSAN_OPTIONS="abort_on_error=1"
./aio_bench -f test.dat -e libaio -t 8 -r 60
```

### 3. 持续集成

```bash
# CI中使用UBSan，开销最小
make ubsan
cd build_ubsan
export UBSAN_OPTIONS="abort_on_error=1"
./aio_bench -f test.dat -e libaio -r 10
```

### 4. 全面检查

```bash
# 运行所有sanitizer测试
make test-all
```

## 常见问题排查

### 1. AddressSanitizer报错

**错误示例**:
```
ERROR: AddressSanitizer: heap-buffer-overflow
```

**排查步骤**:
1. 查看错误堆栈
2. 检查数组边界
3. 验证内存分配大小

### 2. ThreadSanitizer报错

**错误示例**:
```
WARNING: ThreadSanitizer: data race
```

**排查步骤**:
1. 检查共享变量访问
2. 添加适当的锁保护
3. 使用原子操作

### 3. 性能问题

如果sanitizer版本运行太慢：
1. 减少测试时间: `-r 5`
2. 降低队列深度: `-q 8`
3. 减少线程数: `-t 1`

## 环境变量参考

### AddressSanitizer
```bash
export ASAN_OPTIONS="
abort_on_error=1:
fast_unwind_on_malloc=0:
detect_leaks=1:
check_initialization_order=1:
strict_init_order=1:
detect_stack_use_after_return=1:
detect_invalid_pointer_pairs=1
"
```

### ThreadSanitizer
```bash
export TSAN_OPTIONS="
abort_on_error=1:
halt_on_error=1:
report_bugs=1:
report_thread_leaks=1:
report_destroy_locked=1:
report_signal_unsafe=1
"
```

### UndefinedBehaviorSanitizer
```bash
export UBSAN_OPTIONS="
abort_on_error=1:
print_stacktrace=1:
report_error_type=1:
silence_unsigned_overflow=0
"
```

### MemorySanitizer
```bash
export MSAN_OPTIONS="
abort_on_error=1:
print_stats=1:
halt_on_error=1:
msan_track_origins=2
"
```

## 集成到开发流程

### 1. 本地开发

```bash
# 开发时默认使用ASan
alias aio_debug='cd build_asan && export ASAN_OPTIONS="abort_on_error=1:detect_leaks=1" && ./aio_bench'
```

### 2. 代码提交前

```bash
# 提交前运行快速检查
make quick-test
```

### 3. CI/CD流水线

```bash
# 在CI中运行全面测试
make test-all
```

## 总结

Sanitizer是发现和修复程序错误的强大工具：

1. **开发阶段**: 主要使用AddressSanitizer
2. **多线程测试**: 使用ThreadSanitizer
3. **持续集成**: 使用UndefinedBehaviorSanitizer
4. **特殊调试**: 根据需要使用MemorySanitizer

通过合理使用这些工具，可以显著提高代码质量和程序稳定性。 