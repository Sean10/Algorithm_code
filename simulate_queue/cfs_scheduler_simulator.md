# cfs_scheduler_simulator.py

## 功能
cfs_scheduler_simulator.py 实现了一个简化版的完全公平调度器（CFS）模拟，模拟Linux内核的CFS调度算法。

## 设计
1. 定义 `Process` 类表示进程
2. 定义 `CFSScheduler` 类实现CFS调度逻辑
3. 实现 `generate_processes` 函数生成随机进程
4. 实现 `run_simulation` 函数执行单次模拟
5. 在主程序中设置参数并运行模拟

## 实现
- `Process` 类：包含进程ID、到达时间、执行时间和虚拟运行时间等属性
- `CFSScheduler` 类：使用最小堆实现就绪队列，根据虚拟运行时间调度进程
- `generate_processes` 函数：随机生成指定数量的进程
- `run_simulation` 函数：运行CFS调度模拟并返回平均周转时间和等待时间
- 主程序：设置模拟参数并运行模拟，输出结果

## 待办
1. 实现更复杂的CFS特性，如组调度、睡眠进程处理等
2. 添加其他调度算法以进行比较，如O(1)调度器、MLFQ等
3. 实现多核CPU调度支持
4. 添加进程优先级和nice值的影响
5. 实现可视化界面，展示调度过程和性能指标
6. 添加更多性能指标，如响应时间、吞吐量等
7. 实现长时间运行的进程和短时间运行的进程混合场景的模拟
