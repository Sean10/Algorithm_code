#!/bin/bash

echo "=== AIO引擎性能对比测试 ==="
echo "测试文件: test_file.dat (500MB)"
echo "测试参数: 随机读写, 队列深度32, 2线程, 10秒"
echo

# 确保测试文件存在
if [ ! -f "build/test_file.dat" ]; then
    echo "创建测试文件..."
    dd if=/dev/zero of=build/test_file.dat bs=1M count=500 > /dev/null 2>&1
fi

echo "1. 测试 libaio 引擎:"
echo "-------------------"
cd build && ./aio_bench -f test_file.dat -e libaio -p rand_rw -q 32 -t 2 -r 10 -o text 2>/dev/null | grep -E "(平均 IOPS|平均带宽|平均延迟|P95延迟|P99延迟)"

echo
echo "2. 测试 io_uring 引擎:"
echo "---------------------"
./aio_bench -f test_file.dat -e io_uring -p rand_rw -q 32 -t 2 -r 10 -o text 2>/dev/null | grep -E "(平均 IOPS|平均带宽|平均延迟|P95延迟|P99延迟)"

echo
echo "=== 对比完成 ==="
echo "注意: 性能结果可能因系统配置、存储设备和当前负载而有所不同" 