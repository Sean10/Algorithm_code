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
注意这个过程中active_set的osd数量是不允许减少的, 因为这代表副本数, 不允许冗余降级
这个转换过程可以接受下述格式的命令
upmap 1.0 [0, 2, 1]  # 代表将1.0的active_set从[0, 1, 2]转换为[0, 2, 1], 直接填写最终结果即可



"""

import itertools
from pysat.formula import WCNF
from pysat.examples.rc2 import RC2
from collections import defaultdict

def calculate_balanced_pg_distribution(pg_distribution):
    osd_set = set()
    pg_count = len(pg_distribution)
    
    for osds in pg_distribution.values():
        osd_set.update(osds)
    
    osd_count = len(osd_set)
    
    # 创建WCNF
    wcnf = WCNF()
    
    # 创建变量
    var_map = {}
    for pg, osds in pg_distribution.items():
        replica_count = len(osds)
        for osd in osd_set:
            for pos in range(replica_count):
                var_map[(pg, osd, pos)] = len(var_map) + 1
    
    # 添加硬约束条件
    for pg, osds in pg_distribution.items():
        replica_count = len(osds)
        # 1. 每个PG必须保持原有的副本数量
        for pos in range(replica_count):
            wcnf.append([var_map[(pg, osd, pos)] for osd in osd_set])
        # 2. 每个位置只能有一个OSD
        for pos in range(replica_count):
            wcnf.extend([[-var_map[(pg, osd1, pos)], -var_map[(pg, osd2, pos)]] 
                         for osd1, osd2 in itertools.combinations(osd_set, 2)])
        # 3. 每个OSD在一个PG中只能出现一次
        for osd in osd_set:
            wcnf.extend([[-var_map[(pg, osd, pos1)], -var_map[(pg, osd, pos2)]] 
                         for pos1, pos2 in itertools.combinations(range(replica_count), 2)])
    
    # 添加软约束条件（优化目标）
    # 4. 每个OSD的PG总数应该尽可能接近平均值
    avg_pgs_per_osd = sum(len(osds) for osds in pg_distribution.values()) / osd_count
    for osd in osd_set:
        variables = [var_map[(pg, osd, pos)] for pg, osds in pg_distribution.items() for pos in range(len(osds))]
        for v in variables[:int(avg_pgs_per_osd)]:
            wcnf.append([v], weight=1)
        for v in variables[int(avg_pgs_per_osd):]:
            wcnf.append([-v], weight=1)
    
    # 5. 每个OSD的主PG数应该尽可能接近平均值
    avg_primary_pgs_per_osd = pg_count / osd_count
    for osd in osd_set:
        variables = [var_map[(pg, osd, 0)] for pg in pg_distribution]
        for v in variables[:int(avg_primary_pgs_per_osd)]:
            wcnf.append([v], weight=2)  # 给主PG分配更高的权重
        for v in variables[int(avg_primary_pgs_per_osd):]:
            wcnf.append([-v], weight=2)  # 给主PG分配更高的权重
    
    # 使用MaxSAT求解器
    with RC2(wcnf) as rc2:
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

