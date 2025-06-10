#!/bin/bash
#
# 使用 perf 对指定的 benchmark 程序进行性能分析
#
# 使用方法:
# 1. 确保在 build 目录下
# 2. bash ../benchmark/scripts/run_perf_analysis.sh <benchmark_executable> [benchmark_args...]
#
# 示例:
# bash ../benchmark/scripts/run_perf_analysis.sh ./benchmark/benchmark_cpu_intensive

set -e # 如果任何命令失败，则立即退出

# --- 参数与环境检查 ---

# 检查 perf 是否安装
if ! command -v perf &> /dev/null; then
    echo "错误: perf 命令未找到。"
    echo "请安装 perf (通常在 'linux-tools-common' 或类似包中)。"
    exit 1
fi

# 检查是否在 build 目录
if [ ! -f "CMakeCache.txt" ]; then
    echo "错误: 请在 'build' 目录下运行此脚本。"
    exit 1
fi

# 检查 benchmark 可执行文件参数
if [ -z "$1" ]; then
    echo "错误: 请提供一个 benchmark 可执行文件作为参数。"
    echo "例如: bash ../benchmark/scripts/run_perf_analysis.sh ./benchmark/benchmark_cpu_intensive"
    exit 1
fi

BENCH_EXECUTABLE=$1
shift # 移除第一个参数，剩下的是 benchmark 的参数
BENCH_ARGS="$@"

if [ ! -f "$BENCH_EXECUTABLE" ] || [ ! -x "$BENCH_EXECUTABLE" ]; then
    echo "错误: benchmark 文件 '$BENCH_EXECUTABLE' 不存在或不可执行。"
    exit 1
fi

# --- Perf 配置 ---

# 定义要采集的性能事件
# 注意：'cycles' 事件可能在某些虚拟机或容器环境中不可用。
# 如果遇到 "not supported" 错误, 请尝试移除 'cycles'。
PERF_EVENTS="cycles,instructions,cache-references,cache-misses,branch-instructions,branch-misses"

# 创建输出目录
PERF_DIR="perf_results"
mkdir -p "$PERF_DIR"

# 获取 benchmark 的基本名称用于命名输出文件
BENCH_NAME=$(basename "$BENCH_EXECUTABLE")
PERF_DATA_FILE="${PERF_DIR}/${BENCH_NAME}_$(date +"%Y%m%d_%H%M%S").data"

echo "================================================="
echo "        开始对 benchmark 进行 perf 分析"
echo "================================================="
echo "分析目标:    $BENCH_EXECUTABLE"
echo "Perf 事件:    $PERF_EVENTS"
echo "Perf 输出文件: $PERF_DATA_FILE"
echo "-------------------------------------------------"

# --- 执行 Perf ---

echo "正在运行 'perf record'..."
echo "注意: 程序将在 perf 下正常运行，这可能会花费一些时间。"

# 使用 perf record 运行 benchmark
# -e: 指定事件
# -g: 开启调用图 (call-graph) 记录 (方便回溯函数调用栈)
# -o: 指定输出文件
# --: 分隔 perf 参数和要执行的命令
perf record -e "$PERF_EVENTS" -g -o "$PERF_DATA_FILE" -- "$BENCH_EXECUTABLE" $BENCH_ARGS

echo "-------------------------------------------------"
echo "         Perf record 完成"
echo "================================================="
echo
echo "分析步骤:"
echo "1. Perf 数据已成功采集到: $PERF_DATA_FILE"
echo "2. 使用 'perf report' 来交互式地分析结果:"
echo "   perf report -i $PERF_DATA_FILE"
echo
echo "3. 或者使用 'perf annotate' 查看特定函数的热点代码:"
echo "   perf annotate -i $PERF_DATA_FILE <symbol_name>"
echo
echo "提示: 由于您当前的环境可能不支持 'cycles' 事件，"
echo "如果脚本失败，请编辑此脚本，从 PERF_EVENTS 变量中移除 'cycles'。" 