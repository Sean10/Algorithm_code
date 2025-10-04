#!/bin/bash

# =============================================================================
# Git 仓库迁移脚本测试工具
# 功能：创建测试环境并验证 migrate_git_repo_to_subdir.sh 的功能
# =============================================================================

set -e

# --- 颜色输出 ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- 测试目录配置 ---
TEST_BASE_DIR=$(mktemp -d -t git_migrate_test_XXXXXX)
SOURCE_REPO="$TEST_BASE_DIR/source-repo"
TARGET_REPO="$TEST_BASE_DIR/target-repo"
TARGET_SUBDIR="migrated/source-project"

# --- 脚本路径 ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATE_SCRIPT="$SCRIPT_DIR/migrate_git_repo_to_subdir.sh"

echo "=========================================="
echo "Git 迁移脚本单元测试"
echo "=========================================="
echo "测试目录: $TEST_BASE_DIR"
echo "迁移脚本: $MIGRATE_SCRIPT"
echo "=========================================="
echo ""

# --- 清理函数 ---
cleanup() {
    echo ""
    echo -e "${YELLOW}清理测试环境...${NC}"
    if [ -d "$TEST_BASE_DIR" ]; then
        rm -rf "$TEST_BASE_DIR"
        echo -e "${GREEN}✓ 测试目录已删除${NC}"
    fi
}

# 注册清理函数
trap cleanup EXIT

# --- 检查迁移脚本是否存在 ---
if [ ! -f "$MIGRATE_SCRIPT" ]; then
    echo -e "${RED}错误: 未找到迁移脚本 $MIGRATE_SCRIPT${NC}"
    exit 1
fi

# 赋予执行权限
chmod +x "$MIGRATE_SCRIPT"

# =============================================================================
# 测试准备：创建源仓库
# =============================================================================
echo -e "${BLUE}[测试 1/4] 创建源仓库...${NC}"

mkdir -p "$SOURCE_REPO"
cd "$SOURCE_REPO"
git init
git config user.name "Test User"
git config user.email "test@example.com"

# 创建一些文件和目录结构
mkdir -p src/utils
mkdir -p docs
mkdir -p tests

cat > README.md << 'EOF'
# 源项目

这是一个测试项目，用于验证 Git 仓库迁移功能。
EOF

cat > src/main.py << 'EOF'
#!/usr/bin/env python3
"""主程序入口"""

def main():
    print("Hello from source repo!")

if __name__ == "__main__":
    main()
EOF

cat > src/utils/helper.py << 'EOF'
"""工具函数模块"""

def helper_function():
    return "This is a helper function"
EOF

cat > docs/guide.md << 'EOF'
# 使用指南

这是使用指南文档。
EOF

cat > tests/test_main.py << 'EOF'
"""单元测试"""

def test_main():
    assert True
EOF

# 第一次提交
git add .
git commit -m "Initial commit: project structure"

echo -e "${GREEN}✓ 创建了初始提交${NC}"

# 修改一些文件，创建更多历史
echo "" >> README.md
echo "## 更新日志" >> README.md
echo "- 2025-10-04: 添加了更多功能" >> README.md
git add README.md
git commit -m "docs: update README with changelog"

cat > src/config.py << 'EOF'
"""配置模块"""

CONFIG = {
    "version": "1.0.0",
    "debug": False
}
EOF

git add src/config.py
git commit -m "feat: add configuration module"

# 修改 main.py
cat > src/main.py << 'EOF'
#!/usr/bin/env python3
"""主程序入口"""

from config import CONFIG

def main():
    print(f"Hello from source repo! Version: {CONFIG['version']}")

if __name__ == "__main__":
    main()
EOF

git add src/main.py
git commit -m "feat: integrate config module in main"

# 添加 .gitignore
cat > .gitignore << 'EOF'
*.pyc
__pycache__/
.DS_Store
EOF

git add .gitignore
git commit -m "chore: add .gitignore"

SOURCE_COMMIT_COUNT=$(git log --oneline | wc -l | tr -d ' ')
echo -e "${GREEN}✓ 源仓库创建完成，共 $SOURCE_COMMIT_COUNT 次提交${NC}"

# 显示源仓库结构
echo ""
echo "源仓库文件结构:"
tree -L 2 2>/dev/null || find . -maxdepth 2 -type f | grep -v "\.git" | sort

# =============================================================================
# 测试准备：创建目标仓库
# =============================================================================
echo ""
echo -e "${BLUE}[测试 2/4] 创建目标仓库...${NC}"

mkdir -p "$TARGET_REPO"
cd "$TARGET_REPO"
git init
git config user.name "Test User"
git config user.email "test@example.com"

# 创建目标仓库的初始结构
mkdir -p projects
mkdir -p shared

cat > README.md << 'EOF'
# 目标 Monorepo

这是一个大型项目，包含多个子项目。
EOF

cat > shared/common.py << 'EOF'
"""共享工具模块"""

def common_function():
    return "Common utility"
EOF

git add .
git commit -m "Initial monorepo structure"

# 添加更多提交
mkdir -p projects/existing-project
echo "# 现有项目" > projects/existing-project/README.md
git add projects/existing-project
git commit -m "feat: add existing project"

TARGET_COMMIT_COUNT=$(git log --oneline | wc -l | tr -d ' ')
echo -e "${GREEN}✓ 目标仓库创建完成，共 $TARGET_COMMIT_COUNT 次提交${NC}"

# 显示目标仓库结构
echo ""
echo "目标仓库文件结构（迁移前）:"
tree -L 2 2>/dev/null || find . -maxdepth 2 -type f | grep -v "\.git" | sort

# =============================================================================
# 执行迁移测试
# =============================================================================
echo ""
echo -e "${BLUE}[测试 3/4] 执行迁移脚本...${NC}"
echo "=========================================="

# 运行迁移脚本
SOURCE_REPO_PATH="$SOURCE_REPO" \
TARGET_REPO_PATH="$TARGET_REPO" \
TARGET_SUBDIR="$TARGET_SUBDIR" \
SOURCE_BRANCH="main" \
TARGET_BRANCH="main" \
"$MIGRATE_SCRIPT"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 迁移脚本执行失败${NC}"
    exit 1
fi

echo "=========================================="

# =============================================================================
# 验证结果
# =============================================================================
echo ""
echo -e "${BLUE}[测试 4/4] 验证迁移结果...${NC}"

cd "$TARGET_REPO"

# 测试 1: 检查子目录是否存在
echo -n "检查目标子目录是否存在... "
if [ -d "$TARGET_SUBDIR" ]; then
    echo -e "${GREEN}✓ 通过${NC}"
else
    echo -e "${RED}✗ 失败${NC}"
    exit 1
fi

# 测试 2: 检查文件是否都迁移过来
echo -n "检查 README.md 是否存在... "
if [ -f "$TARGET_SUBDIR/README.md" ]; then
    echo -e "${GREEN}✓ 通过${NC}"
else
    echo -e "${RED}✗ 失败${NC}"
    exit 1
fi

echo -n "检查 src/main.py 是否存在... "
if [ -f "$TARGET_SUBDIR/src/main.py" ]; then
    echo -e "${GREEN}✓ 通过${NC}"
else
    echo -e "${RED}✗ 失败${NC}"
    exit 1
fi

echo -n "检查 src/config.py 是否存在... "
if [ -f "$TARGET_SUBDIR/src/config.py" ]; then
    echo -e "${GREEN}✓ 通过${NC}"
else
    echo -e "${RED}✗ 失败${NC}"
    exit 1
fi

echo -n "检查 .gitignore 是否存在... "
if [ -f "$TARGET_SUBDIR/.gitignore" ]; then
    echo -e "${GREEN}✓ 通过${NC}"
else
    echo -e "${RED}✗ 失败${NC}"
    exit 1
fi

# 测试 3: 检查文件内容
echo -n "验证文件内容完整性... "
if grep -q "源项目" "$TARGET_SUBDIR/README.md"; then
    echo -e "${GREEN}✓ 通过${NC}"
else
    echo -e "${RED}✗ 失败${NC}"
    exit 1
fi

# 测试 4: 检查历史记录
echo -n "检查历史记录是否保留... "
MIGRATED_COMMIT_COUNT=$(git log --oneline -- "$TARGET_SUBDIR" | wc -l | tr -d ' ')
if [ "$MIGRATED_COMMIT_COUNT" -ge "$SOURCE_COMMIT_COUNT" ]; then
    echo -e "${GREEN}✓ 通过 (保留了 $MIGRATED_COMMIT_COUNT 条记录，源仓库 $SOURCE_COMMIT_COUNT 条)${NC}"
else
    echo -e "${RED}✗ 失败 (仅保留了 $MIGRATED_COMMIT_COUNT 条记录，源仓库有 $SOURCE_COMMIT_COUNT 条)${NC}"
    exit 1
fi

# 测试 5: 检查特定提交信息是否保留
echo -n "检查提交信息是否保留... "
if git log --oneline -- "$TARGET_SUBDIR" | grep -q "Initial commit"; then
    echo -e "${GREEN}✓ 通过${NC}"
else
    echo -e "${RED}✗ 失败${NC}"
    exit 1
fi

# 测试 6: 检查原有文件是否保留
echo -n "检查目标仓库原有文件是否保留... "
if [ -f "shared/common.py" ] && [ -d "projects/existing-project" ]; then
    echo -e "${GREEN}✓ 通过${NC}"
else
    echo -e "${RED}✗ 失败${NC}"
    exit 1
fi

# 测试 7: 验证目录结构
echo ""
echo "目标仓库文件结构（迁移后）:"
tree -L 3 2>/dev/null || find . -maxdepth 3 -type f | grep -v "\.git" | sort

# 测试 8: 显示合并后的历史
echo ""
echo "合并后的提交历史（最近 10 条）:"
git log --oneline --graph -10

echo ""
echo "迁移子目录的提交历史:"
git log --oneline -- "$TARGET_SUBDIR" | head -n 10

# =============================================================================
# 测试总结
# =============================================================================
echo ""
echo "=========================================="
echo -e "${GREEN}所有测试通过！${NC}"
echo "=========================================="
echo "测试统计:"
echo "  源仓库提交数:   $SOURCE_COMMIT_COUNT"
echo "  目标仓库原有提交: $TARGET_COMMIT_COUNT"
echo "  迁移后保留历史:  $MIGRATED_COMMIT_COUNT"
echo "  迁移文件数:     $(find "$TARGET_SUBDIR" -type f | wc -l | tr -d ' ')"
echo ""
echo "测试环境位置: $TEST_BASE_DIR"
echo "你可以手动检查测试结果:"
echo "  cd $TARGET_REPO"
echo "  git log --graph --oneline"
echo ""
echo "按回车键清理测试环境，或按 Ctrl+C 保留测试环境..."
read -r

echo -e "${GREEN}测试完成！${NC}"

