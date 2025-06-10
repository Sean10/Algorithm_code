# AIO基准测试工具集

这个目录包含用于环境检测和辅助功能的工具程序。

## 工具列表

### test_nanobench
用于检测系统是否支持nanobench的硬件性能计数器功能。

**功能：**
- 检测系统是否支持硬件性能计数器（CPU指令数、周期数、IPC等）
- 验证nanobench库的基本功能
- 提供性能计数器可用性的诊断信息

**编译：**
```bash
mkdir -p build
cd build
cmake ..
make
```

**运行：**
```bash
./test_nanobench
```

**预期输出：**
- 如果系统支持性能计数器，会显示详细的性能指标（ins/op, cyc/op, IPC等）
- 如果不支持，只会显示基本的时间测量（ns/op, op/s）

## 系统要求

- Linux系统
- 支持perf事件的内核
- 适当的权限设置（可能需要调整 `/proc/sys/kernel/perf_event_paranoid`）

## 故障排除

如果性能计数器不可用，可能的原因：
1. 虚拟机环境限制
2. 权限不足（尝试以root运行或调整perf_event_paranoid）
3. 硬件不支持
4. 内核配置问题

## 添加新工具

要添加新的工具程序：
1. 在此目录创建源文件
2. 在CMakeLists.txt中添加相应的add_executable
3. 更新此README.md文档 