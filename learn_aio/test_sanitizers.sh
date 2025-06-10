#!/bin/bash

# 简单的sanitizer验证脚本

echo "=== Sanitizer功能验证 ==="
echo

# 检查构建目录
echo "1. 检查已构建的sanitizer版本:"
for dir in build_asan build_tsan build_ubsan build_msan; do
    if [ -d "$dir" ] && [ -f "$dir/aio_bench" ]; then
        echo "  ✅ $dir - $(ls -lh $dir/aio_bench | awk '{print $5}')"
    else
        echo "  ❌ $dir - 未构建"
    fi
done
echo

# 快速功能测试
echo "2. 快速功能测试:"

# 测试AddressSanitizer
if [ -f "build_asan/aio_bench" ]; then
    echo "  测试AddressSanitizer..."
    cd build_asan
    export ASAN_OPTIONS="abort_on_error=1:fast_unwind_on_malloc=0"
    dd if=/dev/zero of=test_quick.dat bs=1M count=5 > /dev/null 2>&1
    timeout 10 ./aio_bench -f test_quick.dat -e libaio -r 2 -q 4 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "    ✅ AddressSanitizer测试通过"
    else
        echo "    ❌ AddressSanitizer测试失败"
    fi
    cd ..
fi

# 测试ThreadSanitizer
if [ -f "build_tsan/aio_bench" ]; then
    echo "  测试ThreadSanitizer..."
    cd build_tsan
    export TSAN_OPTIONS="abort_on_error=1"
    dd if=/dev/zero of=test_quick.dat bs=1M count=5 > /dev/null 2>&1
    timeout 10 ./aio_bench -f test_quick.dat -e libaio -t 2 -r 2 -q 4 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "    ✅ ThreadSanitizer测试通过"
    else
        echo "    ❌ ThreadSanitizer测试失败"
    fi
    cd ..
fi

# 测试UBSan
if [ -f "build_ubsan/aio_bench" ]; then
    echo "  测试UndefinedBehaviorSanitizer..."
    cd build_ubsan
    export UBSAN_OPTIONS="abort_on_error=1"
    dd if=/dev/zero of=test_quick.dat bs=1M count=5 > /dev/null 2>&1
    timeout 10 ./aio_bench -f test_quick.dat -e libaio -r 2 -q 4 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "    ✅ UndefinedBehaviorSanitizer测试通过"
    else
        echo "    ❌ UndefinedBehaviorSanitizer测试失败"
    fi
    cd ..
fi

echo
echo "3. 使用建议:"
echo "  - 日常开发: make asan"
echo "  - 多线程调试: make tsan"
echo "  - 持续集成: make ubsan"
echo "  - 详细文档: 查看 SANITIZER_GUIDE.md"
echo
echo "=== 验证完成 ===" 