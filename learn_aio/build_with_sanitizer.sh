#!/bin/bash

# AIO基准测试工具 - Sanitizer构建脚本
# 用于快速构建带有不同sanitizer的版本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印帮助信息
print_help() {
    echo "用法: $0 [选项] [sanitizer类型]"
    echo
    echo "Sanitizer类型:"
    echo "  asan     - AddressSanitizer (检测内存错误、缓冲区溢出等)"
    echo "  tsan     - ThreadSanitizer (检测数据竞争)"
    echo "  ubsan    - UndefinedBehaviorSanitizer (检测未定义行为)"
    echo "  msan     - MemorySanitizer (检测未初始化内存读取)"
    echo "  debug    - Debug构建 (无sanitizer)"
    echo "  release  - Release构建 (默认)"
    echo
    echo "选项:"
    echo "  -c, --clean    清理构建目录"
    echo "  -t, --test     构建后运行快速测试"
    echo "  -h, --help     显示此帮助信息"
    echo
    echo "示例:"
    echo "  $0 asan              # 构建AddressSanitizer版本"
    echo "  $0 tsan --test       # 构建ThreadSanitizer版本并测试"
    echo "  $0 --clean release   # 清理后构建Release版本"
}

# 打印彩色消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 清理构建目录
clean_build() {
    print_message $YELLOW "清理构建目录..."
    rm -rf build_*
    print_message $GREEN "清理完成"
}

# 构建项目
build_project() {
    local sanitizer=$1
    local build_dir="build_${sanitizer}"
    local cmake_args=""
    
    print_message $BLUE "开始构建 ${sanitizer} 版本..."
    
    # 设置CMake参数
    case $sanitizer in
        "asan")
            cmake_args="-DCMAKE_BUILD_TYPE=Debug -DENABLE_ASAN=ON"
            ;;
        "tsan")
            cmake_args="-DCMAKE_BUILD_TYPE=Debug -DENABLE_TSAN=ON"
            ;;
        "ubsan")
            cmake_args="-DCMAKE_BUILD_TYPE=Debug -DENABLE_UBSAN=ON"
            ;;
        "msan")
            cmake_args="-DCMAKE_BUILD_TYPE=Debug -DENABLE_MSAN=ON"
            ;;
        "debug")
            cmake_args="-DCMAKE_BUILD_TYPE=Debug"
            ;;
        "release")
            cmake_args="-DCMAKE_BUILD_TYPE=Release"
            ;;
        *)
            print_message $RED "错误: 未知的sanitizer类型: $sanitizer"
            print_help
            exit 1
            ;;
    esac
    
    # 创建构建目录
    mkdir -p "$build_dir"
    cd "$build_dir"
    
    # 配置和构建
    print_message $YELLOW "配置项目..."
    cmake $cmake_args "$PROJECT_ROOT"
    
    print_message $YELLOW "编译项目..."
    make -j$(nproc)
    
    print_message $GREEN "构建完成: $build_dir/aio_bench"
    
    # 显示二进制文件信息
    echo
    print_message $BLUE "二进制文件信息:"
    ls -lh aio_bench
    file aio_bench
    
    cd "$PROJECT_ROOT"
}

# 运行快速测试
run_test() {
    local sanitizer=$1
    local build_dir="build_${sanitizer}"
    local binary="$build_dir/aio_bench"
    
    if [ ! -f "$binary" ]; then
        print_message $RED "错误: 找不到可执行文件 $binary"
        return 1
    fi
    
    print_message $BLUE "运行快速测试..."
    
    # 创建小测试文件
    dd if=/dev/zero of="$build_dir/test_small.dat" bs=1M count=10 2>/dev/null
    
    # 设置sanitizer环境变量
    export ASAN_OPTIONS="abort_on_error=1:fast_unwind_on_malloc=0"
    export TSAN_OPTIONS="abort_on_error=1"
    export UBSAN_OPTIONS="abort_on_error=1"
    export MSAN_OPTIONS="abort_on_error=1"
    
    # 运行测试
    cd "$build_dir"
    
    echo "测试帮助信息..."
    timeout 5 ./aio_bench --help > /dev/null
    
    echo "测试libaio引擎..."
    timeout 10 ./aio_bench -f test_small.dat -e libaio -r 3 -q 8 > /dev/null
    
    echo "测试io_uring引擎..."
    timeout 10 ./aio_bench -f test_small.dat -e io_uring -r 3 -q 8 > /dev/null
    
    cd "$PROJECT_ROOT"
    
    print_message $GREEN "测试完成，未发现错误"
}

# 主函数
main() {
    local sanitizer="release"
    local clean=false
    local test=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -c|--clean)
                clean=true
                shift
                ;;
            -t|--test)
                test=true
                shift
                ;;
            -h|--help)
                print_help
                exit 0
                ;;
            asan|tsan|ubsan|msan|debug|release)
                sanitizer=$1
                shift
                ;;
            *)
                print_message $RED "错误: 未知参数 $1"
                print_help
                exit 1
                ;;
        esac
    done
    
    # 检查编译器支持
    if ! command -v gcc &> /dev/null && ! command -v clang &> /dev/null; then
        print_message $RED "错误: 未找到GCC或Clang编译器"
        exit 1
    fi
    
    # 显示配置信息
    print_message $BLUE "=== AIO基准测试工具 - Sanitizer构建 ==="
    echo "Sanitizer类型: $sanitizer"
    echo "清理构建: $clean"
    echo "运行测试: $test"
    echo
    
    # 清理构建目录
    if [ "$clean" = true ]; then
        clean_build
    fi
    
    # 构建项目
    build_project "$sanitizer"
    
    # 运行测试
    if [ "$test" = true ]; then
        echo
        run_test "$sanitizer"
    fi
    
    echo
    print_message $GREEN "=== 构建完成 ==="
    print_message $YELLOW "可执行文件位置: build_${sanitizer}/aio_bench"
    
    # 显示使用建议
    case $sanitizer in
        "asan")
            echo
            print_message $BLUE "AddressSanitizer使用建议:"
            echo "- 设置环境变量: export ASAN_OPTIONS=\"abort_on_error=1:fast_unwind_on_malloc=0\""
            echo "- 运行时会检测内存错误、缓冲区溢出、使用后释放等问题"
            ;;
        "tsan")
            echo
            print_message $BLUE "ThreadSanitizer使用建议:"
            echo "- 设置环境变量: export TSAN_OPTIONS=\"abort_on_error=1\""
            echo "- 运行时会检测数据竞争和线程安全问题"
            ;;
        "ubsan")
            echo
            print_message $BLUE "UndefinedBehaviorSanitizer使用建议:"
            echo "- 设置环境变量: export UBSAN_OPTIONS=\"abort_on_error=1\""
            echo "- 运行时会检测未定义行为，如整数溢出、空指针解引用等"
            ;;
        "msan")
            echo
            print_message $BLUE "MemorySanitizer使用建议:"
            echo "- 设置环境变量: export MSAN_OPTIONS=\"abort_on_error=1\""
            echo "- 运行时会检测未初始化内存的读取"
            echo "- 注意: 需要用MSan重新编译所有依赖库"
            ;;
    esac
}

# 运行主函数
main "$@" 