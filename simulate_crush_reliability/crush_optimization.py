#/bin/python3
"""

输入的pg分布如下, 其中active_set中是osd id, 第一个是primary osd, 其他是replica osd
pgid active_set
1.0 [0, 1, 2]
1.1 [1, 2, 0]
1.2 [2, 0, 1]
1.3 [0, 1, 2]

根据上述可计算得到
osd.id primary_pg_count replica_pg_count pg_count_sum 
0 2 2 4
1 1 3 4
2 1 3 4

由于每个pg实际上占用的空间是相近的, 所以最好是pg_count_sum相近, 且primary_pg_count和replica_pg_count尽可能相近. 这样得到的结果才是均衡的

比如上述结果是姑且算理想的. 

如果输入的pg分布如下, 则显然是不均衡的
pgid active_set
1.0 [0, 1, 2]
1.1 [0, 1, 2]
1.2 [0, 1, 2]
1.3 [0, 1, 2]


边界:
pgid可能会是上千个
active_set中的osd可能是几百个中选3个, 或选4个, 或选5个

要求使用pysat库计算crush map的期望均衡结果, 并能够根据输出的pgid->active_set结果, 计算出如何从原始的pgid->active_set结果, 转换到期望的pgid->active_set结果
这个转换过程可以接受下述格式的命令
upmap 1.0 [0, 2, 1]  # 代表将1.0的active_set从[0, 1, 2]转换为[0, 2, 1], 直接填写最终结果即可



"""

import itertools
from pysat.solvers import Glucose3
from pysat.formula import CNF
from collections import defaultdict

def calculate_balanced_pg_distribution(pg_distribution):
    osd_counts = defaultdict(lambda: {'primary': 0, 'replica': 0, 'total': 0})
    osd_set = set()
    pg_count = len(pg_distribution)
    
    for pg, osds in pg_distribution.items():
        osd_set.update(osds)
        osd_counts[osds[0]]['primary'] += 1
        for osd in osds[1:]:
            osd_counts[osd]['replica'] += 1
        for osd in osds:
            osd_counts[osd]['total'] += 1
    
    osd_count = len(osd_set)
    replica_count = len(next(iter(pg_distribution.values())))
    
    # 创建SAT求解器
    cnf = CNF()
    solver = Glucose3()
    
    # 创建变量
    var_map = {}
    for pg in pg_distribution:
        for osd in osd_set:
            for pos in range(replica_count):
                var_map[(pg, osd, pos)] = len(var_map) + 1
    
    # 添加硬约束条件
    # 1. 每个PG必须有指定数量的副本
    for pg in pg_distribution:
        cnf.append([var_map[(pg, osd, pos)] for osd in osd_set for pos in range(replica_count)])
        for pos in range(replica_count):
            cnf.extend([[-var_map[(pg, osd1, pos)], -var_map[(pg, osd2, pos)]] 
                        for osd1, osd2 in itertools.combinations(osd_set, 2)])
    
    # 添加软约束条件（优化目标）
    soft_clauses = []
    weights = []
    
    # 2. 每个OSD的PG总数应该尽可能接近平均值
    avg_pgs_per_osd = pg_count * replica_count // osd_count
    for osd in osd_set:
        variables = [var_map[(pg, osd, pos)] for pg in pg_distribution for pos in range(replica_count)]
        soft_clauses.extend([[v] for v in variables[:avg_pgs_per_osd]])
        soft_clauses.extend([[-v] for v in variables[avg_pgs_per_osd:]])
        weights.extend([1] * len(variables))
    
    # 3. 每个OSD的主PG数应该尽可能接近平均值
    avg_primary_pgs_per_osd = pg_count // osd_count
    for osd in osd_set:
        variables = [var_map[(pg, osd, 0)] for pg in pg_distribution]
        soft_clauses.extend([[v] for v in variables[:avg_primary_pgs_per_osd]])
        soft_clauses.extend([[-v] for v in variables[avg_primary_pgs_per_osd:]])
        weights.extend([2] * len(variables))  # 给主PG分配更高的权重
    
    # 使用MaxSAT求解器
    from pysat.examples.rc2 import RC2
    with RC2(cnf, solver='g3') as rc2:
        for clause, weight in zip(soft_clauses, weights):
            rc2.add_soft(clause, weight)
        
        model = rc2.compute()
        
        if model:
            new_distribution = defaultdict(list)
            for (pg, osd, pos), var in var_map.items():
                if model[var-1] > 0:
                    new_distribution[pg].append((osd, pos))
            
            for pg in new_distribution:
                new_distribution[pg] = [osd for osd, _ in sorted(new_distribution[pg], key=lambda x: x[1])]
            
            return dict(new_distribution)
    
    # 如果MaxSAT求解失败，返回原始分布
    return pg_distribution

def generate_upmap_commands(old_distribution, new_distribution):
    commands = []
    for pg in old_distribution:
        if old_distribution[pg] != new_distribution[pg]:
            commands.append(f"upmap {pg} {new_distribution[pg]}")
    return commands

# 示例使用
pg_distribution = {
    '1.0': [0, 1, 2],
    '1.1': [0, 1, 2],
    '1.2': [0, 1, 2],
    '1.3': [0, 1, 2]
}

balanced_distribution = calculate_balanced_pg_distribution(pg_distribution)
print("均衡后的PG分布:")
for pg, osds in balanced_distribution.items():
    print(f"{pg}: {osds}")

print("\nupmap命令:")
commands = generate_upmap_commands(pg_distribution, balanced_distribution)
for cmd in commands:
    print(cmd)

# 打印均衡后的OSD统计信息
osd_stats = defaultdict(lambda: {'primary': 0, 'replica': 0, 'total': 0})
for pg, osds in balanced_distribution.items():
    osd_stats[osds[0]]['primary'] += 1
    for osd in osds[1:]:
        osd_stats[osd]['replica'] += 1
    for osd in osds:
        osd_stats[osd]['total'] += 1

print("\nOSD统计信息:")
print("OSD ID  Primary PGs  Replica PGs  Total PGs")
for osd, stats in osd_stats.items():
    print(f"{osd:6d}  {stats['primary']:11d}  {stats['replica']:11d}  {stats['total']:9d}")

