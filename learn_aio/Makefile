# AIO基准测试工具 - Makefile
# 提供便捷的构建目标，包括各种sanitizer模式

.PHONY: all clean help release debug asan tsan ubsan msan test-all

# 默认目标
all: release

# 帮助信息
help:
	@echo "AIO基准测试工具 - 构建目标"
	@echo ""
	@echo "基本构建:"
	@echo "  make release    - Release构建 (默认)"
	@echo "  make debug      - Debug构建"
	@echo ""
	@echo "Sanitizer构建:"
	@echo "  make asan       - AddressSanitizer (内存错误检测)"
	@echo "  make tsan       - ThreadSanitizer (数据竞争检测)"
	@echo "  make ubsan      - UndefinedBehaviorSanitizer (未定义行为检测)"
	@echo "  make msan       - MemorySanitizer (未初始化内存检测)"
	@echo ""
	@echo "测试和清理:"
	@echo "  make test-all   - 构建并测试所有sanitizer版本"
	@echo "  make clean      - 清理所有构建目录"
	@echo ""
	@echo "示例:"
	@echo "  make asan       # 构建AddressSanitizer版本"
	@echo "  make test-all   # 测试所有版本"

# Release构建
release:
	@echo "构建Release版本..."
	@./build_with_sanitizer.sh release

# Debug构建
debug:
	@echo "构建Debug版本..."
	@./build_with_sanitizer.sh debug

# AddressSanitizer构建
asan:
	@echo "构建AddressSanitizer版本..."
	@./build_with_sanitizer.sh asan

# ThreadSanitizer构建
tsan:
	@echo "构建ThreadSanitizer版本..."
	@./build_with_sanitizer.sh tsan

# UndefinedBehaviorSanitizer构建
ubsan:
	@echo "构建UndefinedBehaviorSanitizer版本..."
	@./build_with_sanitizer.sh ubsan

# MemorySanitizer构建
msan:
	@echo "构建MemorySanitizer版本..."
	@./build_with_sanitizer.sh msan

# 测试所有版本
test-all:
	@echo "构建并测试所有sanitizer版本..."
	@echo ""
	@echo "=== 测试Release版本 ==="
	@./build_with_sanitizer.sh --clean release --test
	@echo ""
	@echo "=== 测试AddressSanitizer版本 ==="
	@./build_with_sanitizer.sh asan --test
	@echo ""
	@echo "=== 测试ThreadSanitizer版本 ==="
	@./build_with_sanitizer.sh tsan --test
	@echo ""
	@echo "=== 测试UndefinedBehaviorSanitizer版本 ==="
	@./build_with_sanitizer.sh ubsan --test
	@echo ""
	@echo "=== 所有测试完成 ==="

# 清理构建目录
clean:
	@echo "清理所有构建目录..."
	@./build_with_sanitizer.sh --clean
	@echo "清理完成"

# 快速测试 - 只测试最常用的sanitizer
quick-test:
	@echo "快速测试常用sanitizer版本..."
	@echo ""
	@echo "=== 测试AddressSanitizer版本 ==="
	@./build_with_sanitizer.sh asan --test
	@echo ""
	@echo "=== 测试ThreadSanitizer版本 ==="
	@./build_with_sanitizer.sh tsan --test
	@echo ""
	@echo "=== 快速测试完成 ==="

# 安装依赖
install-deps:
	@echo "安装构建依赖..."
	@if command -v apt-get >/dev/null 2>&1; then \
		sudo apt-get update && \
		sudo apt-get install -y libaio-dev liburing-dev cmake build-essential; \
	elif command -v dnf >/dev/null 2>&1; then \
		sudo dnf install -y libaio-devel liburing-devel cmake gcc-c++ make; \
	elif command -v yum >/dev/null 2>&1; then \
		sudo yum install -y libaio-devel liburing-devel cmake gcc-c++ make; \
	else \
		echo "错误: 无法识别的包管理器，请手动安装依赖"; \
		exit 1; \
	fi
	@echo "依赖安装完成" 