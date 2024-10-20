import random

class Car:
    def __init__(self, position, speed, acceleration):
        self.position = position
        self.speed = speed
        self.acceleration = acceleration

    def update(self, dt):
        self.speed += self.acceleration * dt
        self.speed = max(0, min(self.speed, 100))  # 限制速度在0-30之间
        self.position += self.speed * dt

class Road:
    def __init__(self, length, min_distance):
        self.length = length
        self.min_distance = min_distance
        self.cars = []

    def add_car(self, car):
        if not self.cars:
            self.cars.append(car)
            return True
        
        # 检查与其他车的距离
        for other_car in self.cars:
            if abs(car.position - other_car.position) < self.min_distance:
                return False
        
        self.cars.append(car)
        return True

    def update(self, dt):
        for car in self.cars:
            car.update(dt)
            # 确保车辆不会离开公路
            car.position = car.position % self.length
        self.cars.sort(key=lambda x: x.position)

def simulate_road(road_length, min_distance, max_cars, simulation_time, dt):
    road = Road(road_length, min_distance)
    
    for _ in range(max_cars):
        attempts = 0
        while attempts < 10:  # 尝试10次添加车辆
            new_car = Car(
                position=random.uniform(0, road_length),
                speed=random.uniform(20, 30),
                acceleration=random.uniform(-1, 1)
            )
            if road.add_car(new_car):
                break
            attempts += 1

    for _ in range(int(simulation_time / dt)):
        road.update(dt)

    return len(road.cars)

# 模拟参数
road_length = 1000  # 公路长度（米）
min_distance = 20   # 车辆之间的最小距离（米）
max_cars = 100      # 尝试添加的最大车辆数
simulation_time = 60  # 模拟时间（秒）
dt = 0.1            # 时间步长（秒）

# 运行多次模拟并计算平均值
num_simulations = 10
total_cars = 0
for _ in range(num_simulations):
    car_count = simulate_road(road_length, min_distance, max_cars, simulation_time, dt)
    total_cars += car_count

average_cars = total_cars / num_simulations
print(f"平均公路可容纳的车辆数量: {average_cars:.2f}")
