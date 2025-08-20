#!/usr/bin/env bash
set -euo pipefail

# 统一构建脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="${BUILD_DIR:-$PROJECT_ROOT/build}"

# 默认配置
BUILD_TYPE="${BUILD_TYPE:-Release}"
BUILD_TESTS="${BUILD_TESTS:-ON}"
BUILD_BENCHMARKS="${BUILD_BENCHMARKS:-ON}"
BUILD_EXAMPLES="${BUILD_EXAMPLES:-ON}"
ENABLE_COVERAGE="${ENABLE_COVERAGE:-OFF}"
PARALLEL_JOBS="${PARALLEL_JOBS:-$(nproc 2>/dev/null || echo 4)}"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --debug)
            BUILD_TYPE="Debug"
            shift
            ;;
        --release)
            BUILD_TYPE="Release"
            shift
            ;;
        --no-tests)
            BUILD_TESTS="OFF"
            shift
            ;;
        --no-benchmarks)
            BUILD_BENCHMARKS="OFF"
            shift
            ;;
        --no-examples)
            BUILD_EXAMPLES="OFF"
            shift
            ;;
        --coverage)
            ENABLE_COVERAGE="ON"
            shift
            ;;
        --clean)
            echo "清理构建目录..."
            rm -rf "$BUILD_DIR"
            shift
            ;;
        --help|-h)
            echo "用法: $0 [选项]"
            echo "选项:"
            echo "  --debug          Debug构建"
            echo "  --release        Release构建（默认）"
            echo "  --no-tests       不构建测试"
            echo "  --no-benchmarks  不构建基准测试"
            echo "  --no-examples    不构建示例"
            echo "  --coverage       启用代码覆盖率"
            echo "  --clean          清理构建目录"
            echo "  --help|-h        显示帮助"
            echo
            echo "环境变量:"
            echo "  BUILD_DIR        构建目录（默认: $PROJECT_ROOT/build）"
            echo "  PARALLEL_JOBS    并行编译作业数（默认: $(nproc 2>/dev/null || echo 4)）"
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            echo "使用 --help 查看帮助"
            exit 1
            ;;
    esac
done

echo "=== 构建配置 ==="
echo "项目根目录: $PROJECT_ROOT"
echo "构建目录: $BUILD_DIR"
echo "构建类型: $BUILD_TYPE"
echo "构建测试: $BUILD_TESTS"
echo "构建基准: $BUILD_BENCHMARKS"
echo "构建示例: $BUILD_EXAMPLES"
echo "启用覆盖率: $ENABLE_COVERAGE"
echo "并行作业: $PARALLEL_JOBS"
echo

# 创建构建目录
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# 配置项目
echo "=== 配置项目 ==="
cmake \
    -DCMAKE_BUILD_TYPE="$BUILD_TYPE" \
    -DBUILD_TESTS="$BUILD_TESTS" \
    -DBUILD_BENCHMARKS="$BUILD_BENCHMARKS" \
    -DBUILD_EXAMPLES="$BUILD_EXAMPLES" \
    -DENABLE_COVERAGE="$ENABLE_COVERAGE" \
    "$PROJECT_ROOT"

# 构建项目
echo
echo "=== 构建项目 ==="
cmake --build . --parallel "$PARALLEL_JOBS"

echo
echo "=== 构建完成 ==="
echo "可执行文件位置:"

if [ "$BUILD_BENCHMARKS" = "ON" ] && [ -f "benchmarks/queue_benchmark" ]; then
    echo "  基准测试: $BUILD_DIR/benchmarks/queue_benchmark"
fi

if [ "$BUILD_TESTS" = "ON" ]; then
    if [ -f "tests/unit/unit_tests" ]; then
        echo "  单元测试: $BUILD_DIR/tests/unit/unit_tests"
    fi
    if [ -f "tests/integration/integration_tests" ]; then
        echo "  集成测试: $BUILD_DIR/tests/integration/integration_tests"
    fi
fi

echo
echo "下一步:"
echo "  运行测试: $SCRIPT_DIR/run_tests.sh"
echo "  运行基准: $SCRIPT_DIR/run_benchmarks.sh"
