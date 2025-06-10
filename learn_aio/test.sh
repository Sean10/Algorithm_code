#!/bin/bash

# AIO基准测试工具 - 测试脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    print_info "检查系统依赖..."
    
    # 检查编译器
    if ! command -v g++ &> /dev/null; then
        print_error "g++ 编译器未找到"
        exit 1
    fi
    
    # 检查libaio
    if ! ldconfig -p | grep -q libaio; then
        print_error "libaio 库未找到，请安装 libaio-dev"
        exit 1
    fi
    
    print_info "依赖检查通过"
}

# 编译程序
build_program() {
    print_info "编译程序..."
    
    if [ -f "CMakeLists.txt" ]; then
        # 使用CMake编译
        mkdir -p build
        cd build
        cmake .. || { print_error "CMake配置失败"; exit 1; }
        make -j$(nproc) || { print_error "编译失败"; exit 1; }
        cd ..
        BINARY="build/aio_bench"
    elif [ -f "Makefile" ]; then
        # 使用Makefile编译
        make clean
        make -j$(nproc) || { print_error "编译失败"; exit 1; }
        BINARY="aio_bench"
    else
        print_error "未找到构建文件 (CMakeLists.txt 或 Makefile)"
        exit 1
    fi
    
    print_info "编译完成: $BINARY"
}

# 运行基本测试
run_basic_tests() {
    print_info "运行基本功能测试..."
    
    # 测试帮助信息
    print_info "测试帮助信息..."
    $BINARY --help || { print_error "帮助信息测试失败"; exit 1; }
    
    # 创建测试文件
    TEST_FILE="test_file.dat"
    TEST_SIZE="100M"
    
    print_info "创建测试文件: $TEST_FILE ($TEST_SIZE)"
    
    # 短时间随机读写测试
    print_info "随机读写测试 (5秒)..."
    $BINARY -f $TEST_FILE -s $TEST_SIZE -p rand_rw -r 5 -q 8 -t 1 || {
        print_error "随机读写测试失败"
        cleanup_test_files
        exit 1
    }
    
    # 顺序读测试
    print_info "顺序读测试 (3秒)..."
    $BINARY -f $TEST_FILE -p seq_read -r 3 -q 4 -t 1 || {
        print_error "顺序读测试失败"
        cleanup_test_files
        exit 1
    }
    
    # 数据验证测试
    print_info "数据验证测试 (3秒)..."
    $BINARY -f $TEST_FILE -p rand_rw -r 3 -q 4 -t 1 -v || {
        print_error "数据验证测试失败"
        cleanup_test_files
        exit 1
    }
    
    print_info "基本功能测试通过"
}

# 运行性能测试
run_performance_tests() {
    print_info "运行性能测试..."
    
    TEST_FILE="perf_test.dat"
    TEST_SIZE="500M"
    
    # 4K随机读测试
    print_info "4K随机读性能测试..."
    $BINARY -f $TEST_FILE -s $TEST_SIZE -p rand_read -b 4096 -q 32 -t 2 -r 10 -V
    
    # 64K顺序写测试  
    print_info "64K顺序写性能测试..."
    $BINARY -f $TEST_FILE -s $TEST_SIZE -p seq_write -b 65536 -q 16 -t 1 -r 10 -V
    
    # 混合读写测试
    print_info "混合读写性能测试..."
    $BINARY -f $TEST_FILE -s $TEST_SIZE -p rand_rw -b 8192 -q 16 -t 2 -r 10 -V
    
    print_info "性能测试完成"
}

# 运行输出格式测试
run_output_tests() {
    print_info "测试输出格式..."
    
    TEST_FILE="output_test.dat"
    TEST_SIZE="50M"
    
    # JSON输出测试
    print_info "JSON格式输出测试..."
    $BINARY -f $TEST_FILE -s $TEST_SIZE -p rand_read -r 3 -o json > /tmp/aio_test.json
    if ! python3 -m json.tool /tmp/aio_test.json > /dev/null 2>&1; then
        print_warn "JSON格式验证失败 (可能python3未安装)"
    else
        print_info "JSON格式输出正确"
    fi
    
    # CSV输出测试
    print_info "CSV格式输出测试..."
    $BINARY -f $TEST_FILE -s $TEST_SIZE -p rand_write -r 3 -o csv > /tmp/aio_test.csv
    if [ $(wc -l < /tmp/aio_test.csv) -ge 2 ]; then
        print_info "CSV格式输出正确"
    else
        print_warn "CSV输出可能有问题"
    fi
    
    # 清理临时文件
    rm -f /tmp/aio_test.json /tmp/aio_test.csv
}

# 清理测试文件
cleanup_test_files() {
    print_info "清理测试文件..."
    rm -f test_file.dat perf_test.dat output_test.dat
}

# 主函数
main() {
    echo "AIO基准测试工具 - 自动测试脚本"
    echo "=================================="
    
    # 检查是否以root运行（可选）
    if [ "$EUID" -eq 0 ]; then
        print_warn "以root权限运行测试"
    fi
    
    # 执行测试步骤
    check_dependencies
    build_program
    
    # 检查二进制文件是否存在
    if [ ! -f "$BINARY" ]; then
        print_error "编译后的二进制文件不存在: $BINARY"
        exit 1
    fi
    
    run_basic_tests
    run_output_tests
    run_performance_tests
    
    cleanup_test_files
    
    print_info "所有测试完成！"
    echo
    echo "程序已就绪，可以使用以下命令运行："
    echo "  $BINARY -f <测试文件> [选项]"
    echo
    echo "查看帮助信息："
    echo "  $BINARY --help"
}

# 信号处理
trap cleanup_test_files EXIT

# 运行主函数
main "$@" 