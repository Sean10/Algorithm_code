#!/usr/bin/env bash
set -euo pipefail

# 测试运行脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="${BUILD_DIR:-$PROJECT_ROOT/build}"

# 解析命令行参数
UNIT_ONLY=false
INTEGRATION_ONLY=false
COVERAGE=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            UNIT_ONLY=true
            shift
            ;;
        --integration)
            INTEGRATION_ONLY=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "用法: $0 [选项]"
            echo "选项:"
            echo "  --unit           只运行单元测试"
            echo "  --integration    只运行集成测试"
            echo "  --coverage       生成代码覆盖率报告"
            echo "  --verbose|-v     详细输出"
            echo "  --help|-h        显示帮助"
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            echo "使用 --help 查看帮助"
            exit 1
            ;;
    esac
done

# 检查构建目录
if [ ! -d "$BUILD_DIR" ]; then
    echo "错误: 构建目录不存在: $BUILD_DIR"
    echo "请先运行: $SCRIPT_DIR/build.sh"
    exit 1
fi

# 创建测试结果目录
TEST_RESULTS_DIR="$PROJECT_ROOT/results/tests/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$TEST_RESULTS_DIR"

echo "=== 运行测试 ==="
echo "构建目录: $BUILD_DIR"
echo "结果目录: $TEST_RESULTS_DIR"
echo

cd "$BUILD_DIR"

# 运行单元测试
if [ "$INTEGRATION_ONLY" = false ]; then
    echo "=== 单元测试 ==="
    if [ -f "tests/unit/unit_tests" ]; then
        UNIT_CMD="./tests/unit/unit_tests"
        if [ "$VERBOSE" = true ]; then
            UNIT_CMD="$UNIT_CMD --gtest_print_time=1"
        fi
        UNIT_CMD="$UNIT_CMD --gtest_output=xml:$TEST_RESULTS_DIR/unit_tests.xml"
        
        echo "运行: $UNIT_CMD"
        if $UNIT_CMD | tee "$TEST_RESULTS_DIR/unit_tests.log"; then
            echo "✓ 单元测试通过"
        else
            echo "✗ 单元测试失败"
            exit 1
        fi
    else
        echo "警告: 单元测试可执行文件不存在"
    fi
    echo
fi

# 运行集成测试
if [ "$UNIT_ONLY" = false ]; then
    echo "=== 集成测试 ==="
    if [ -f "tests/integration/integration_tests" ]; then
        INTEGRATION_CMD="./tests/integration/integration_tests"
        if [ "$VERBOSE" = true ]; then
            INTEGRATION_CMD="$INTEGRATION_CMD --gtest_print_time=1"
        fi
        INTEGRATION_CMD="$INTEGRATION_CMD --gtest_output=xml:$TEST_RESULTS_DIR/integration_tests.xml"
        
        echo "运行: $INTEGRATION_CMD"
        if $INTEGRATION_CMD | tee "$TEST_RESULTS_DIR/integration_tests.log"; then
            echo "✓ 集成测试通过"
        else
            echo "✗ 集成测试失败"
            exit 1
        fi
    else
        echo "警告: 集成测试可执行文件不存在"
    fi
    echo
fi

# 运行CTest
echo "=== CTest ==="
if command -v ctest >/dev/null 2>&1; then
    CTEST_CMD="ctest --output-on-failure"
    if [ "$VERBOSE" = true ]; then
        CTEST_CMD="$CTEST_CMD --verbose"
    fi
    
    echo "运行: $CTEST_CMD"
    if $CTEST_CMD | tee "$TEST_RESULTS_DIR/ctest.log"; then
        echo "✓ CTest通过"
    else
        echo "✗ CTest失败"
        exit 1
    fi
else
    echo "CTest不可用"
fi
echo

# 生成代码覆盖率报告
if [ "$COVERAGE" = true ]; then
    echo "=== 代码覆盖率 ==="
    if command -v gcov >/dev/null 2>&1 && command -v lcov >/dev/null 2>&1; then
        echo "生成覆盖率报告..."
        lcov --capture --directory . --output-file "$TEST_RESULTS_DIR/coverage.info"
        lcov --remove "$TEST_RESULTS_DIR/coverage.info" '/usr/*' --output-file "$TEST_RESULTS_DIR/coverage_filtered.info"
        
        if command -v genhtml >/dev/null 2>&1; then
            genhtml "$TEST_RESULTS_DIR/coverage_filtered.info" --output-directory "$TEST_RESULTS_DIR/coverage_html"
            echo "HTML覆盖率报告: $TEST_RESULTS_DIR/coverage_html/index.html"
        fi
        
        # 显示覆盖率摘要
        lcov --summary "$TEST_RESULTS_DIR/coverage_filtered.info"
    else
        echo "警告: gcov 或 lcov 不可用，无法生成覆盖率报告"
        echo "安装方法: sudo apt-get install gcov lcov"
    fi
    echo
fi

echo "=== 测试完成 ==="
echo "所有测试通过! ✓"
echo "结果保存在: $TEST_RESULTS_DIR"

# 显示测试摘要
if [ -f "$TEST_RESULTS_DIR/unit_tests.log" ]; then
    echo
    echo "单元测试摘要:"
    grep -E "(RUN|OK|FAILED)" "$TEST_RESULTS_DIR/unit_tests.log" | tail -5 || true
fi

if [ -f "$TEST_RESULTS_DIR/integration_tests.log" ]; then
    echo
    echo "集成测试摘要:"
    grep -E "(RUN|OK|FAILED)" "$TEST_RESULTS_DIR/integration_tests.log" | tail -5 || true
fi
