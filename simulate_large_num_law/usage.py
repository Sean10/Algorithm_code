# # 系统思考：均匀与非均匀哈希分布对得盘率的影响分析

# ## 问题分析
# 1. 核心目标：验证均匀哈希与非均匀哈希在得盘率上的差异
# 2. 关键指标：可成功写入的对象数占总对象数的比例
# 3. 技术路径：通过模拟哈希分布，统计不同情况下的得盘率


import numpy as np
import hashlib
import matplotlib.pyplot as plt

def rjenkins_hash(key):
    # Jenkins one-at-a-time hash算法实现
    hash_val = 0
    for char in key:
        hash_val += ord(char)
        hash_val += (hash_val << 10)
        hash_val ^= (hash_val >> 6)
    hash_val += (hash_val << 3)
    hash_val ^= (hash_val >> 11)
    hash_val += (hash_val << 15)
    return hash_val

def simulate_disk_utilization(num_objects, num_buckets, hash_func):
    # 模拟对象分布
    objects = [f"object_{i}" for i in range(num_objects)]
    bucket_counts = np.zeros(num_buckets)
    
    # 计算哈希分布
    for obj in objects:
        hash_val = hash_func(obj)
        bucket = hash_val % num_buckets
        bucket_counts[bucket] += 1
    
    # 计算得盘率
    avg_load = num_objects / num_buckets
    overflow = np.sum(bucket_counts[bucket_counts > avg_load] - avg_load)
    disk_utilization = (num_objects - overflow) / num_objects
    
    return disk_utilization

# 参数设置
num_objects = 100000
num_buckets = 100

# 均匀哈希模拟
uniform_hash = lambda x: int(hashlib.md5(x.encode()).hexdigest(), 16)
uniform_util = simulate_disk_utilization(num_objects, num_buckets, uniform_hash)

# 非均匀哈希模拟
non_uniform_hash = rjenkins_hash
non_uniform_util = simulate_disk_utilization(num_objects, num_buckets, non_uniform_hash)

print(f"均匀哈希得盘率: {uniform_util:.4f}")
print(f"非均匀哈希得盘率: {non_uniform_util:.4f}")


# ## 实现验证
# 1. 均匀哈希使用MD5算法，确保分布均匀性
# 2. 非均匀哈希采用Jenkins算法，模拟实际场景中的哈希碰撞
# 3. 通过统计超过平均负载的桶数量，计算得盘率损失

# ## 结果分析
# - 均匀哈希得盘率应接近100%
# - 非均匀哈希得盘率会有所下降，具体数值取决于哈希算法的分布特性
# - 通过调整对象数量和桶数量，可以观察得盘率的变化趋势

def plot_distribution_comparison(num_objects, num_buckets, uniform_hash, non_uniform_hash):
    # 生成对象列表
    objects = [f"object_{i}" for i in range(num_objects)]

    # 计算两种哈希分布
    uniform_counts = np.zeros(num_buckets)
    non_uniform_counts = np.zeros(num_buckets)

    for obj in objects:
        # 均匀哈希
        uniform_val = uniform_hash(obj)
        uniform_bucket = uniform_val % num_buckets
        uniform_counts[uniform_bucket] += 1

        # 非均匀哈希
        non_uniform_val = non_uniform_hash(obj)
        non_uniform_bucket = non_uniform_val % num_buckets
        non_uniform_counts[non_uniform_bucket] += 1

    # 绘制柱状图
    plt.figure(figsize=(12, 6))

    # 均匀哈希分布
    plt.subplot(1, 2, 1)
    plt.bar(range(num_buckets), uniform_counts, color='blue')
    plt.title('Uniform Hash Distribution')
    plt.xlabel('Bucket Index')
    plt.ylabel('Object Count')
    plt.axhline(y=num_objects/num_buckets, color='red', linestyle='--', label='Average Load')

    # 非均匀哈希分布
    plt.subplot(1, 2, 2)
    plt.bar(range(num_buckets), non_uniform_counts, color='green')
    plt.title('Non-Uniform Hash Distribution')
    plt.xlabel('Bucket Index')
    plt.ylabel('Object Count')
    plt.axhline(y=num_objects/num_buckets, color='red', linestyle='--', label='Average Load')

    plt.tight_layout()
    plt.savefig('hash_distribution.png')
    # plt.show()

# 调用绘图函数
plot_distribution_comparison(num_objects, num_buckets, uniform_hash, non_uniform_hash)

def simulate_multiple_runs(num_runs, num_objects_list, num_buckets, uniform_hash, non_uniform_hash):
    # 存储多次运行结果
    uniform_results = []
    non_uniform_results = []

    for num_objects in num_objects_list:
        uniform_utils = []
        non_uniform_utils = []

        for _ in range(num_runs):
            # 均匀哈希模拟
            uniform_util = simulate_disk_utilization(num_objects, num_buckets, uniform_hash)
            uniform_utils.append(uniform_util)

            # 非均匀哈希模拟
            non_uniform_util = simulate_disk_utilization(num_objects, num_buckets, non_uniform_hash)
            non_uniform_utils.append(non_uniform_util)

        # 计算平均值
        uniform_results.append(np.mean(uniform_utils))
        non_uniform_results.append(np.mean(non_uniform_utils))

    return uniform_results, non_uniform_results

def plot_convergence(num_objects_list, uniform_results, non_uniform_results):
    plt.figure(figsize=(10, 6))

    # 绘制均匀哈希收敛曲线
    plt.plot(num_objects_list, uniform_results, 'b-', label='Uniform Hash')

    # 绘制非均匀哈希收敛曲线
    plt.plot(num_objects_list, non_uniform_results, 'g-', label='Non-Uniform Hash')

    plt.title('Disk Utilization Convergence under Law of Large Numbers')
    plt.xlabel('Number of Objects')
    plt.ylabel('Average Disk Utilization')
    plt.legend()
    plt.grid(True)
    # plt.show()
    plt.savefig('convergence.png')

# 参数设置
num_runs = 1  # 每组数据运行次数
num_objects_list = [1000, 10000, 100000]  # 不同规模的对象数量
num_buckets = 100

# 运行模拟
uniform_results, non_uniform_results = simulate_multiple_runs(
    num_runs, num_objects_list, num_buckets, uniform_hash, non_uniform_hash
)

# 绘制收敛图
plot_convergence(num_objects_list, uniform_results, non_uniform_results)
