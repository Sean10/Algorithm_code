import random
import math

class Process:
    def __init__(self, pid, arrival_time, execution_time):
        self.pid = pid
        self.arrival_time = arrival_time
        self.execution_time = execution_time
        self.remaining_time = execution_time
        self.completion_time = 0
        self.waiting_time = 0

    def execute(self, time_slice):
        executed_time = min(self.remaining_time, time_slice)
        self.remaining_time -= executed_time
        return executed_time

class CPUScheduler:
    def __init__(self, processes, context_switch_time):
        self.processes = processes
        self.context_switch_time = context_switch_time
        self.current_time = 0
        self.total_execution_time = 0
        self.total_waiting_time = 0

    def run(self, time_slice):
        queue = sorted(self.processes, key=lambda p: p.arrival_time)
        completed_processes = []

        while queue or completed_processes:
            if not queue:
                next_arrival = min((p for p in completed_processes if p.arrival_time > self.current_time), key=lambda p: p.arrival_time, default=None)
                if next_arrival is None:
                    break
                self.current_time = next_arrival.arrival_time
                queue = [p for p in completed_processes if p.arrival_time <= self.current_time]
                completed_processes = [p for p in completed_processes if p.arrival_time > self.current_time]
                queue.sort(key=lambda p: p.remaining_time)  # Shortest Remaining Time First

            process = queue.pop(0)
            
            # 等待时间
            if self.current_time > process.arrival_time:
                process.waiting_time += self.current_time - max(process.arrival_time, self.current_time - time_slice)

            # 上下文切换
            if self.current_time > 0:
                self.current_time += self.context_switch_time

            # 执行进程
            executed_time = process.execute(time_slice)
            self.current_time += executed_time
            self.total_execution_time += executed_time

            if process.remaining_time > 0:
                queue.append(process)
            else:
                process.completion_time = self.current_time
                completed_processes.append(process)

        self.processes = completed_processes

    def get_average_turnaround_time(self):
        return sum(p.completion_time - p.arrival_time for p in self.processes) / len(self.processes)

    def get_average_waiting_time(self):
        return sum(p.waiting_time for p in self.processes) / len(self.processes)

    def get_cpu_utilization(self):
        return self.total_execution_time / self.current_time if self.current_time > 0 else 0

    def get_throughput(self):
        return len(self.processes) / (self.current_time / 1000) if self.current_time > 0 else 0  # 假设时间单位是毫秒

def generate_processes(num_processes, arrival_rate, min_execution_time, max_execution_time):
    processes = []
    current_time = 0
    for i in range(num_processes):
        arrival_time = current_time + int(random.expovariate(1/arrival_rate))
        execution_time = random.randint(min_execution_time, max_execution_time)
        processes.append(Process(i, arrival_time, execution_time))
        current_time = arrival_time
    return processes

def simulate_cpu_scheduling(num_processes, arrival_rate, min_execution_time, max_execution_time, context_switch_time, time_slice):
    processes = generate_processes(num_processes, arrival_rate, min_execution_time, max_execution_time)
    scheduler = CPUScheduler(processes, context_switch_time)
    scheduler.run(time_slice)
    
    return (
        scheduler.get_average_turnaround_time(),
        scheduler.get_average_waiting_time(),
        scheduler.get_cpu_utilization(),
        scheduler.get_throughput()
    )

# 模拟参数
num_processes_list = [1, 5, 6, 10, 20, 30, 40, 50]
arrival_rate = 1  # 平均每10ms到达一个新进程
min_execution_time = 5
max_execution_time = 5
context_switch_time = 0.05
time_slice = 1
num_simulations = 10

for num_processes in num_processes_list:
    total_turnaround_time = 0
    total_waiting_time = 0
    total_cpu_utilization = 0
    total_throughput = 0
    
    for _ in range(num_simulations):
        turnaround_time, waiting_time, cpu_utilization, throughput = simulate_cpu_scheduling(
            num_processes, arrival_rate, min_execution_time, max_execution_time, context_switch_time, time_slice
        )
        total_turnaround_time += turnaround_time
        total_waiting_time += waiting_time
        total_cpu_utilization += cpu_utilization
        total_throughput += throughput
    
    avg_turnaround_time = total_turnaround_time / num_simulations
    avg_waiting_time = total_waiting_time / num_simulations
    avg_cpu_utilization = total_cpu_utilization / num_simulations
    avg_throughput = total_throughput / num_simulations
    
    print(f"进程数: {num_processes}")
    print(f"平均周转时间: {avg_turnaround_time:.2f}ms")
    print(f"平均等待时间: {avg_waiting_time:.2f}ms")
    print(f"平均CPU利用率: {avg_cpu_utilization:.2%}")
    print(f"平均吞吐量: {avg_throughput:.2f}进程/秒")
    print()
