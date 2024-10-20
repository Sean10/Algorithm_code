import random
import math
from tabulate import tabulate

class Customer:
    def __init__(self, arrival_time):
        self.arrival_time = arrival_time
        self.service_start_time = 0
        self.departure_time = 0

class MM1Queue:
    def __init__(self, arrival_rate, service_rate):
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.queue = []
        self.current_time = 0
        self.server_busy = False
        self.completed_customers = []

    def generate_interarrival_time(self):
        return random.expovariate(self.arrival_rate)

    def generate_service_time(self):
        return random.expovariate(self.service_rate)

    def simulate(self, simulation_time):
        next_arrival_time = self.generate_interarrival_time()
        next_departure_time = float('inf')

        while self.current_time < simulation_time:
            if next_arrival_time < next_departure_time:
                self.current_time = next_arrival_time
                customer = Customer(self.current_time)
                self.queue.append(customer)
                next_arrival_time = self.current_time + self.generate_interarrival_time()

                if not self.server_busy:
                    self.server_busy = True
                    customer.service_start_time = self.current_time
                    service_time = self.generate_service_time()
                    next_departure_time = self.current_time + service_time
            else:
                self.current_time = next_departure_time
                departing_customer = self.queue.pop(0)
                departing_customer.departure_time = self.current_time
                self.completed_customers.append(departing_customer)

                if self.queue:
                    next_customer = self.queue[0]
                    next_customer.service_start_time = self.current_time
                    service_time = self.generate_service_time()
                    next_departure_time = self.current_time + service_time
                else:
                    self.server_busy = False
                    next_departure_time = float('inf')

    def get_average_waiting_time(self):
        total_waiting_time = sum(c.service_start_time - c.arrival_time for c in self.completed_customers)
        return total_waiting_time / len(self.completed_customers)

    def get_average_system_time(self):
        total_system_time = sum(c.departure_time - c.arrival_time for c in self.completed_customers)
        return total_system_time / len(self.completed_customers)

    def get_server_utilization(self):
        total_service_time = sum(c.departure_time - c.service_start_time for c in self.completed_customers)
        return total_service_time / self.current_time

def run_simulation(arrival_rate, service_rate, simulation_time, num_simulations):
    total_waiting_time = 0
    total_system_time = 0
    total_server_utilization = 0

    for _ in range(num_simulations):
        queue = MM1Queue(arrival_rate, service_rate)
        queue.simulate(simulation_time)
        total_waiting_time += queue.get_average_waiting_time()
        total_system_time += queue.get_average_system_time()
        total_server_utilization += queue.get_server_utilization()

    avg_waiting_time = total_waiting_time / num_simulations
    avg_system_time = total_system_time / num_simulations
    avg_server_utilization = total_server_utilization / num_simulations

    # 理论值计算
    rho = arrival_rate / service_rate
    theoretical_waiting_time = rho / (service_rate * (1 - rho))
    theoretical_system_time = 1 / (service_rate * (1 - rho))

    return {
        "到达率": arrival_rate,
        "服务率": service_rate,
        "模拟平均等待时间": avg_waiting_time,
        "模拟平均系统时间": avg_system_time,
        "模拟服务器利用率": avg_server_utilization,
        "理论平均等待时间": theoretical_waiting_time,
        "理论平均系统时间": theoretical_system_time,
        "理论服务器利用率": rho
    }

def main():
    simulation_time = 1000  # 模拟时间
    num_simulations = 100  # 每组参数的模拟次数

    # 定义多组输入参数
    input_params = [
        (0.5, 1.0),  # (到达率, 服务率)
        (0.7, 1.0),
        (0.9, 1.0),
        (0.5, 1.2),
        (0.5, 0.8)
    ]

    results = []
    for arrival_rate, service_rate in input_params:
        result = run_simulation(arrival_rate, service_rate, simulation_time, num_simulations)
        results.append(result)

    # 使用 tabulate 库来格式化输出表格
    headers = list(results[0].keys())
    table_data = [[result[key] for key in headers] for result in results]
    
    print(tabulate(table_data, headers=headers, floatfmt=".4f", tablefmt="grid"))

if __name__ == "__main__":
    main()
