#!/bin/bash

# 运行所有benchmark并将结果保存到文件中
# 这个脚本应该在build目录下运行

# 检查是否在build目录
if [ ! -f "CMakeCache.txt" ]; then
    echo "错误：请在build目录下运行此脚本"
    exit 1
fi

echo "================================================="
echo "        开始运行线程池基准测试套件"
echo "================================================="

# 创建存放结果的目录
RESULTS_DIR="benchmark_results"
mkdir -p $RESULTS_DIR

# 获取当前日期和时间戳
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 定义输出格式
BENCH_FORMAT="--benchmark_format=json"

# --- 运行各个benchmark ---

echo -e "\n[1/3] 正在运行CPU密集型任务测试..."
./benchmark/benchmark_cpu_intensive $BENCH_FORMAT > $RESULTS_DIR/cpu_intensive_${TIMESTAMP}.json
echo "CPU密集型测试完成，结果已保存。"

echo -e "\n[2/3] 正在运行IO密集型任务测试..."
./benchmark/benchmark_io_intensive $BENCH_FORMAT > $RESULTS_DIR/io_intensive_${TIMESTAMP}.json
echo "IO密集型测试完成，结果已保存。"

echo -e "\n[3/3] 正在运行线程池实现对比测试..."
./benchmark/benchmark_threadpool_comparison $BENCH_FORMAT > $RESULTS_DIR/threadpool_comparison_${TIMESTAMP}.json
echo "线程池对比测试完成，结果已保存。"

echo -e "\n[4/4] 正在运行优化前后对比测试..."
./benchmark/benchmark_optimization_comparison $BENCH_FORMAT > $RESULTS_DIR/optimization_comparison_${TIMESTAMP}.json
echo "优化前后对比测试完成，结果已保存。"

echo -e "\n[5/5] 正在运行内存分配性能对比测试..."
# 运行默认分配器的版本
./benchmark/benchmark_memory_allocation $BENCH_FORMAT > $RESULTS_DIR/memory_comparison_default_${TIMESTAMP}.json
echo "默认分配器测试完成。"

# 检查tcmalloc版本是否存在且可执行
TCMALLOC_BENCH="./benchmark/benchmark_memory_allocation_tcmalloc"
if [ -f "$TCMALLOC_BENCH" ] && [ -x "$TCMALLOC_BENCH" ]; then
    echo "正在运行tcmalloc优化版本测试..."
    $TCMALLOC_BENCH $BENCH_FORMAT > $RESULTS_DIR/memory_comparison_tcmalloc_${TIMESTAMP}.json
    echo "tcmalloc版本测试完成。"
else
    echo "未找到tcmalloc优化版本，跳过测试。"
fi

echo "================================================="
echo "        所有基准测试运行完毕！"
echo "================================================="
echo "结果文件保存在目录: $RESULTS_DIR"
echo "现在你可以使用 analyze_results.py 脚本来分析这些JSON文件。"
echo "例如: python3 ../benchmark/scripts/analyze_results.py $RESULTS_DIR/cpu_intensive_${TIMESTAMP}.json" 