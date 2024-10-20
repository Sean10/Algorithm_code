# rr_scheduler_simulator.py

## 功能
rr_scheduler_simulator.py 实现了一个轮转（Round Robin，RR）调度器的模拟，并与完全公平调度器（CFS）进行对比，以体现CFS调度器的价值。

## 设计
1. 定义 `Process` 类表示进程
2. 定义 `RRScheduler` 类实现轮转调度逻辑
3. 实现 `generate_processes` 函数生成随机进程
4. 实现 `run_simulation` 函数执行单次模拟
5. 在主程序中运行RR和CFS两种调度器的模拟，并比较结果

## 实现
- `Process` 类：包含进程ID、到达时间、执行时间等属性
- `RRScheduler` 类：使用双端队列实现就绪队列，根据固定的时间片轮流执行进程
- `generate_processes` 函数：随机生成指定数量的进程
- `run_simulation` 函数：运行调度模拟并返回平均周转时间和等待时间
- 主程序：设置模拟参数，运行RR和CFS两种调度器的模拟，输出并比较结果

## 待办
1. 添加不同类型的进程（如CPU密集型和I/O密集型）到模拟中
2. 实现更多的性能指标，如响应时间、公平性指数等
3. 可视化调度过程，直观展示两种调度器的差异
4. 添加长时间运行的后台进程和短暂的交互式进程的混合工作负载
5. 实现进程优先级，观察不同调度器如何处理不同优先级的进程
6. 添加多核CPU支持，比较在多核环境下两种调度器的表现
7. 实现自适应时间片大小的改进版RR调度器，与基本RR和CFS进行对比
8. 添加吞吐量、CPU利用率等更多系统级性能指标
9. 实现不同负载情况下的自动化测试和性能报告生成
10. 考虑实现其他调度算法（如MLFQ、SJF等）进行更全面的比较