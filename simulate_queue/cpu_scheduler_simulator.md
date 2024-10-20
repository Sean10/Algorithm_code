# cpu_scheduler_simulator.py

## 功能
cpu_scheduler_simulator.py 模拟多进程在单CPU上的调度，计算CPU利用率和执行效率。

- 模拟多个进程在单CPU上的执行
- 实现简化版的CFS（完全公平调度器）
- 考虑上下文切换时间
- 计算CPU利用率和执行效率

## 设计
1. 定义 `Process` 类表示进程
2. 定义 `CPUScheduler` 类模拟CPU调度器
3. 实现 `generate_processes` 函数生成随机进程
4. 实现 `simulate_cpu_scheduling` 函数执行单次模拟
5. 在主程序中多次运行模拟并计算平均值

## 实现


``` mermaid
classDiagram
    class Process {
        +int pid
        +int arrival_time
        +int execution_time
        +int remaining_time
        +int completion_time
        +int waiting_time
        +execute(time_slice)
    }

    class CPUScheduler {
        +List processes
        +int context_switch_time
        +int current_time
        +int total_execution_time
        +int total_waiting_time
        +run(time_slice)
        +get_average_turnaround_time()
        +get_average_waiting_time()
        +get_cpu_utilization()
        +get_throughput()
    }

    class generate_processes {
        <<function>>
    }

    class simulate_cpu_scheduling {
        <<function>>
    }

    Process --o CPUScheduler : contains
    generate_processes ..> Process : creates
    simulate_cpu_scheduling ..> generate_processes : uses
    simulate_cpu_scheduling ..> CPUScheduler : uses
    CPUScheduler --> Process : manages
```


- `Process` 类：包含进程ID、到达时间、执行时间等属性
- `CPUScheduler` 类：管理进程执行和上下文切换，计算性能指标
- `generate_processes` 函数：随机生成指定数量的进程
- `simulate_cpu_scheduling` 函数：运行单次CPU调度模拟
- 主程序：设置模拟参数，多次运行模拟并计算平均性能指标

## 待办
1. 实现更多调度算法，如优先级调度、多级反馈队列等
2. 添加多CPU支持
3. 考虑I/O操作对调度的影响
4. 实现可视化界面，展示调度过程
5. 添加更详细的性能指标分析
