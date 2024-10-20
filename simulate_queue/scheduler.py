"""
scheduling_algorithm.py 

FCFS
SJF
RR
CFS

"""

import random
import heapq
from dataclasses import dataclass, field
from typing import List
import math
from tabulate import tabulate

@dataclass(order=True)
class Process:
    pid: int = field(compare=False)
    arrival_time: int
    burst_time: int
    priority: int = field(compare=False)
    remaining_time: int = field(compare=False, default=0)
    start_time: int = field(compare=False, default=0)
    finish_time: int = field(compare=False, default=0)
    waiting_time: int = field(compare=False, default=0)
    turnaround_time: int = field(compare=False, default=0)

class Scheduler:
    def __init__(self, processes):
        self.processes = processes
        self.current_time = 0
        self.completed_processes = []
        
    def run(self):
        raise NotImplementedError
        
    def calculate_metrics(self):
        total_waiting_time = sum(p.waiting_time for p in self.completed_processes)
        total_turnaround_time = sum(p.turnaround_time for p in self.completed_processes)
        avg_waiting_time = total_waiting_time / len(self.completed_processes)
        avg_turnaround_time = total_turnaround_time / len(self.completed_processes)
        return avg_waiting_time, avg_turnaround_time

class FCFSScheduler(Scheduler):
    def run(self):
        ready_queue = sorted(self.processes, key=lambda p: p.arrival_time)
        
        while ready_queue:
            process = ready_queue.pop(0)
            if self.current_time < process.arrival_time:
                self.current_time = process.arrival_time
            
            process.start_time = self.current_time
            process.finish_time = self.current_time + process.burst_time
            process.waiting_time = process.start_time - process.arrival_time
            process.turnaround_time = process.finish_time - process.arrival_time
            
            self.current_time = process.finish_time
            self.completed_processes.append(process)

class SJFScheduler(Scheduler):
    def run(self):
        ready_queue = []
        remaining_processes = sorted(self.processes, key=lambda p: p.arrival_time)
        
        while remaining_processes or ready_queue:
            while remaining_processes and remaining_processes[0].arrival_time <= self.current_time:
                heapq.heappush(ready_queue, (remaining_processes[0].burst_time, remaining_processes[0]))
                remaining_processes.pop(0)
            
            if not ready_queue:
                self.current_time = remaining_processes[0].arrival_time
                continue
            
            _, process = heapq.heappop(ready_queue)
            process.start_time = self.current_time
            process.finish_time = self.current_time + process.burst_time
            process.waiting_time = process.start_time - process.arrival_time
            process.turnaround_time = process.finish_time - process.arrival_time
            
            self.current_time = process.finish_time
            self.completed_processes.append(process)

class RoundRobinScheduler(Scheduler):
    def __init__(self, processes, time_quantum):
        super().__init__(processes)
        self.time_quantum = time_quantum
        
    def run(self):
        ready_queue = []
        remaining_processes = sorted(self.processes, key=lambda p: p.arrival_time)
        
        while remaining_processes or ready_queue:
            while remaining_processes and remaining_processes[0].arrival_time <= self.current_time:
                process = remaining_processes.pop(0)
                process.remaining_time = process.burst_time
                ready_queue.append(process)
            
            if not ready_queue:
                self.current_time = remaining_processes[0].arrival_time
                continue
            
            process = ready_queue.pop(0)
            if process.start_time == 0:
                process.start_time = self.current_time
            
            execution_time = min(self.time_quantum, process.remaining_time)
            self.current_time += execution_time
            process.remaining_time -= execution_time
            
            if process.remaining_time == 0:
                process.finish_time = self.current_time
                process.turnaround_time = process.finish_time - process.arrival_time
                process.waiting_time = process.turnaround_time - process.burst_time
                self.completed_processes.append(process)
            else:
                while remaining_processes and remaining_processes[0].arrival_time <= self.current_time:
                    ready_queue.append(remaining_processes.pop(0))
                ready_queue.append(process)

class CFSScheduler(Scheduler):
    def __init__(self, processes):
        super().__init__(processes)
        self.time_slice = 10  # 增加基本时间片
        self.min_granularity = 2  # 增加最小调度粒度

    def run(self):
        ready_queue = []
        remaining_processes = sorted(self.processes, key=lambda p: p.arrival_time)
        vruntime = {}  # 用于跟踪每个进程的虚拟运行时间

        while remaining_processes or ready_queue:
            while remaining_processes and remaining_processes[0].arrival_time <= self.current_time:
                process = remaining_processes.pop(0)
                process.remaining_time = process.burst_time
                vruntime[process.pid] = 0
                ready_queue.append(process)

            if not ready_queue:
                self.current_time = remaining_processes[0].arrival_time
                continue

            process = min(ready_queue, key=lambda p: vruntime[p.pid])
            
            if process.start_time == 0:
                process.start_time = self.current_time

            time_slice = max(self.min_granularity, 
                             min(self.time_slice, process.remaining_time))
            
            self.current_time += time_slice
            process.remaining_time -= time_slice

            priority = max(1, process.priority)  # 将优先级限制在最小1
            vruntime[process.pid] += time_slice * (1024 / priority)

            if process.remaining_time <= 0:
                process.finish_time = self.current_time
                process.turnaround_time = process.finish_time - process.arrival_time
                process.waiting_time = process.turnaround_time - process.burst_time
                self.completed_processes.append(process)
                ready_queue.remove(process)
            else:
                ready_queue.append(ready_queue.pop(0))

def generate_processes(num_processes):
    processes = []
    for i in range(num_processes):
        arrival_time = random.randint(0, 100)
        burst_time = random.randint(1, 30)
        priority = random.randint(1, 5)
        processes.append(Process(i, arrival_time, burst_time, priority))
    return processes

def run_simulation(scheduler_class, processes, **kwargs):
    scheduler = scheduler_class(processes, **kwargs)
    scheduler.run()
    avg_waiting_time, avg_turnaround_time = scheduler.calculate_metrics()
    return avg_waiting_time, avg_turnaround_time

def generate_fcfs_favorable_processes(num_processes):
    processes = []
    for i in range(num_processes):
        arrival_time = i * 10  # 进程间隔更大,减少重叠
        burst_time = random.randint(5, 15)  # 突发时间差异不大
        processes.append(Process(i, arrival_time, burst_time, 1))
    return processes

def generate_sjf_favorable_processes(num_processes):
    processes = []
    for i in range(num_processes):
        arrival_time = 0  # 所有进程同时到达
        burst_time = random.randint(1, 50)  # 突发时间差异很大
        processes.append(Process(i, arrival_time, burst_time, 1))
    return processes

def generate_rr_favorable_processes(num_processes):
    processes = []
    for i in range(num_processes):
        arrival_time = i * 2  # 进程逐步到达
        if i % 3 == 0:
            burst_time = random.randint(1, 5)  # 短进程
        else:
            burst_time = random.randint(15, 25)  # 长进程
        processes.append(Process(i, arrival_time, burst_time, 1))
    return processes

def generate_cfs_favorable_processes(num_processes):
    processes = []
    for i in range(num_processes):
        arrival_time = i * 5  # 进程逐步到达,间隔更大
        if i % 4 == 0:
            burst_time = random.randint(1, 5)  # 短进程
            priority = 3  # 高优先级
        elif i % 4 == 1:
            burst_time = random.randint(5, 10)  # 中短进程
            priority = 2  # 中高优先级
        elif i % 4 == 2:
            burst_time = random.randint(10, 20)  # 中长进程
            priority = 2  # 中低优先级
        else:
            burst_time = random.randint(20, 30)  # 长进程
            priority = 1  # 低优先级
        processes.append(Process(i, arrival_time, burst_time, priority))
    
    # 添加一些同时到达的进程,以测试CFS对同时到达进程的处理
    for i in range(4):
        arrival_time = num_processes * 5  # 在其他进程之后同时到达
        burst_time = random.randint(5, 25)
        priority = random.randint(1, 3)
        processes.append(Process(num_processes + i, arrival_time, burst_time, priority))
    
    return processes

if __name__ == "__main__":
    num_processes = 15  # 增加进程数以更好地展示差异
    time_quantum = 4

    cases = ["FCFS", "SJF", "RR", "CFS"]
    schedulers = [FCFSScheduler, SJFScheduler, RoundRobinScheduler, CFSScheduler]
    generate_functions = [
        generate_fcfs_favorable_processes,
        generate_sjf_favorable_processes,
        generate_rr_favorable_processes,
        generate_cfs_favorable_processes
    ]

    results = []

    for case, generate_func in zip(cases, generate_functions):
        processes = generate_func(num_processes)
        case_results = []
        for scheduler in schedulers:
            if scheduler == RoundRobinScheduler:
                awt, att = run_simulation(scheduler, processes, time_quantum=time_quantum)
            else:
                awt, att = run_simulation(scheduler, processes)
            case_results.append([case, scheduler.__name__.replace("Scheduler", ""), f"{awt:.2f}", f"{att:.2f}"])
        results.extend(case_results)

    headers = ["Case", "Scheduler", "Avg Waiting Time", "Avg Turnaround Time"]
    print(tabulate(results, headers=headers, tablefmt="pipe"))
