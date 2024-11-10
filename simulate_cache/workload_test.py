from cache_simulator import StorageLayer, LRUCache, WorkloadGenerator
from prettytable import PrettyTable

def test_workload(name: str, workload: WorkloadGenerator, cache_size: int, requests: int):
    # 模拟不同存储层
    memory = StorageLayer("Memory", access_time_us=0.1)
    ssd = StorageLayer("SSD", access_time_us=100)
    hdd = StorageLayer("HDD", access_time_us=10000)
    
    cache = LRUCache(cache_size, ssd)
    
    for _ in range(requests):
        key = workload.generate_request()
        cache.get(key)
    
    return {
        "workload": name,
        "cache_size": cache_size,
        "hit_rate": cache.hit_rate,
        "avg_latency": cache.avg_latency,
        "workload_hot_size": workload.hot_data_size
    }

def print_workload_info(workloads):
    """打印工作负载特征"""
    print("\n工作负载特征分析")
    table = PrettyTable()
    table.field_names = ["工作负载类型", "总数据量(MB)", "热点数据量(MB)", "热点访问比例(%)", "访问模式特征"]
    
    for name, wl in workloads.items():
        table.add_row([
            name,
            wl.total_data_size,
            wl.hot_data_size,
            f"{wl.hot_data_ratio*100:.0f}",
            "高频热点访问" if name == "OLTP" else "大范围扫描"
        ])
    print(table)

def main():
    # 工作负载定义
    workloads = {
        "OLTP": WorkloadGenerator(
            total_data_size=1000,    # 1GB
            hot_data_size=150,       # 150MB热点数据
            hot_data_ratio=0.8       # 80%的访问命中热点数据
        ),
        "OLAP": WorkloadGenerator(
            total_data_size=1000,    # 1GB
            hot_data_size=500,       # 500MB数据经常被访问
            hot_data_ratio=0.5       # 访问分布相对均匀
        )
    }
    
    # 打印工作负载特征
    print_workload_info(workloads)
    
    cache_sizes = [50, 150, 300]
    requests = 10000
    
    # 创建结果表格
    table = PrettyTable()
    table.field_names = ["工作负载", "缓存大小(MB)", "命中率(%)", "平均延迟(微秒)", "缓存效率"]
    
    # 收集所有结果
    results = []
    for cache_size in cache_sizes:
        results.append(test_workload("OLTP", workloads["OLTP"], cache_size, requests))
        results.append(test_workload("OLAP", workloads["OLAP"], cache_size, requests))
    
    # 添加结果到表格，并计算缓存效率
    for result in results:
        cache_efficiency = result['hit_rate'] / (result['cache_size'] / result['workload_hot_size']) \
            if result['workload'] == "OLTP" else \
            result['hit_rate'] / (result['cache_size'] / 500)  # OLAP使用500MB作为基准
            
        table.add_row([
            result["workload"],
            result["cache_size"],
            f"{result['hit_rate']*100:.2f}",
            f"{result['avg_latency']:.2f}",
            f"{cache_efficiency:.2f}"
        ])
    
    # 打印性能对比表格
    print("\n缓存性能对比分析")
    print(table)
    
    # 打印存储层延迟特征
    storage_table = PrettyTable()
    storage_table.field_names = ["存储层", "访问延迟"]
    storage_table.add_row(["内存", "0.1微秒"])
    storage_table.add_row(["SSD", "100微秒"])
    storage_table.add_row(["HDD", "10000微秒"])
    print("\n存储层特征")
    print(storage_table)
    
    # 打印分析结论
    print("\n性能分析：")
    oltp_results = [r for r in results if r["workload"] == "OLTP"]
    olap_results = [r for r in results if r["workload"] == "OLAP"]
    
    print(f"1. OLTP场景：")
    print(f"   - 最佳缓存命中率: {max(r['hit_rate']*100 for r in oltp_results):.2f}%")
    print(f"   - 最低平均延迟: {min(r['avg_latency'] for r in oltp_results):.2f}微秒")
    print(f"   - 热点数据比例: {workloads['OLTP'].hot_data_ratio*100:.0f}%")
    
    print(f"\n2. OLAP场景：")
    print(f"   - 最佳缓存命中率: {max(r['hit_rate']*100 for r in olap_results):.2f}%")
    print(f"   - 最低平均延迟: {min(r['avg_latency'] for r in olap_results):.2f}微秒")
    print(f"   - 热点数据比例: {workloads['OLAP'].hot_data_ratio*100:.0f}%")

if __name__ == "__main__":
    main()