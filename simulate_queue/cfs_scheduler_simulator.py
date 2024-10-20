import random
from collections import deque
import heapq

class Process:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.start_time = None
        self.finish_time = None
        self.vruntime = 0

    def __lt__(self, other):
        return self.vruntime < other.vruntime

    def __eq__(self, other):
        return self.vruntime == other.vruntime

class CFSScheduler:
    def __init__(self, time_slice=1):
        self.ready_queue = []
        self.current_time = 0
        self.time_slice = time_slice
        self.completed_processes = []

    def add_process(self, process):
        heapq.heappush(self.ready_queue, process)

    def run(self, simulation_time):
        while self.current_time < simulation_time and self.ready_queue:
            process = heapq.heappop(self.ready_queue)
            
            if process.start_time is None:
                process.start_time = self.current_time

            execution_time = min(self.time_slice, process.remaining_time)
            self.current_time += execution_time
            process.remaining_time -= execution_time

            # Update vruntime
            process.vruntime += execution_time * (1024 / process.burst_time)

            if process.remaining_time > 0:
                heapq.heappush(self.ready_queue, process)
            else:
                process.finish_time = self.current_time
                self.completed_processes.append(process)

    def get_average_turnaround_time(self):
        return sum(p.finish_time - p.arrival_time for p in self.completed_processes) / len(self.completed_processes)

    def get_average_waiting_time(self):
        return sum(p.start_time - p.arrival_time for p in self.completed_processes) / len(self.completed_processes)

def generate_processes(num_processes, max_arrival_time, min_burst_time, max_burst_time):
    processes = []
    for i in range(num_processes):
        arrival_time = random.randint(0, max_arrival_time)
        burst_time = random.randint(min_burst_time, max_burst_time)
        processes.append(Process(i, arrival_time, burst_time))
    return sorted(processes, key=lambda p: p.arrival_time)

def run_simulation(num_processes, max_arrival_time, min_burst_time, max_burst_time, simulation_time):
    processes = generate_processes(num_processes, max_arrival_time, min_burst_time, max_burst_time)
    scheduler = CFSScheduler()

    for process in processes:
        scheduler.add_process(process)

    scheduler.run(simulation_time)

    avg_turnaround_time = scheduler.get_average_turnaround_time()
    avg_waiting_time = scheduler.get_average_waiting_time()

    return avg_turnaround_time, avg_waiting_time

def main():
    num_processes = 10
    max_arrival_time = 10
    min_burst_time = 1
    max_burst_time = 10
    simulation_time = 100

    avg_turnaround_time, avg_waiting_time = run_simulation(
        num_processes, max_arrival_time, min_burst_time, max_burst_time, simulation_time
    )

    print(f"平均周转时间: {avg_turnaround_time:.2f}")
    print(f"平均等待时间: {avg_waiting_time:.2f}")

if __name__ == "__main__":
    main()
