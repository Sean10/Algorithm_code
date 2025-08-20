#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
BUILD_DIR="$ROOT_DIR/build"

# 参数矩阵（可按需调整或从环境变量覆盖）
QUEUE_SIZES=(${QUEUE_SIZES:-4096 65536})
TEST_COUNTS=(${TEST_COUNTS:-1000})
CONSUMERS=(${CONSUMERS:-2 4 8})
TIMEOUT=${TIMEOUT:-15}

RUN_ID=$(date +%Y%m%d_%H%M%S)
OUT_DIR="$ROOT_DIR/results/$RUN_ID"
mkdir -p "$OUT_DIR"

echo "结果目录: $OUT_DIR"

# 记录环境信息
{
  echo "===== uname -a ====="; uname -a
  echo
  echo "===== lscpu ====="; (command -v lscpu >/dev/null && lscpu) || echo "lscpu not available"
  echo
  echo "===== /proc/cpuinfo (first 100 lines) ====="; head -n 100 /proc/cpuinfo || true
  echo
  echo "===== free -h ====="; (command -v free >/dev/null && free -h) || echo "free not available"
} > "$OUT_DIR/env.txt" 2>&1 || true

# 构建（如果需要）
if [ ! -f "$BUILD_DIR/benchmarks/queue_benchmark" ]; then
    echo "基准程序不存在，正在构建..."
    "$ROOT_DIR/scripts/build.sh" --no-tests --no-examples >/dev/null
fi

CSV_LATENCY="$OUT_DIR/latency.csv"
CSV_SUMMARY="$OUT_DIR/summary.csv"

# 执行参数矩阵
for qs in "${QUEUE_SIZES[@]}"; do
  for tc in "${TEST_COUNTS[@]}"; do
    for c in "${CONSUMERS[@]}"; do
      echo "运行: queue_size=$qs, test_count=$tc, consumers=$c"
      "$BUILD_DIR/benchmarks/queue_benchmark" \
        --queue-size "$qs" \
        --test-count "$tc" \
        --consumers "$c" \
        --timeout "$TIMEOUT" \
        --csv-latency "$CSV_LATENCY" \
        --csv-summary "$CSV_SUMMARY" | sed 's/^/  /'
    done
  done
done

echo
echo "汇总文件: $CSV_SUMMARY"
echo "延迟文件: $CSV_LATENCY"
echo
echo "summary.csv 预览:"
tail -n 10 "$CSV_SUMMARY" || true


