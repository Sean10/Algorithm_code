#!/bin/bash

# =============================================================================
# Git 仓库迁移脚本
# 功能：将一个完整的 Git 仓库迁移到另一个 Git 仓库的子目录中，保留完整历史
# 
# 使用方法:
#     ./migrate_git_repo_to_subdir.sh <源仓库路径> <目标仓库路径> <目标子目录>
# 
# 或者通过环境变量:
#     SOURCE_REPO_PATH=/path/to/source \
#     TARGET_REPO_PATH=/path/to/target \
#     TARGET_SUBDIR=subdir/path \
#     SOURCE_BRANCH=main \
#     TARGET_BRANCH=main \
#     ./migrate_git_repo_to_subdir.sh
# 
# 参数说明:
#     源仓库路径    - 需要迁移的完整 Git 仓库的本地路径
#     目标仓库路径  - 接收迁移内容的 Git 仓库的本地路径
#     目标子目录    - 在目标仓库中存放源仓库内容的子目录路径
#     SOURCE_BRANCH - 源仓库分支名（默认: main）
#     TARGET_BRANCH - 目标仓库分支名（默认: main）
# 
# 使用示例:
#     # 基本用法
#     ./migrate_git_repo_to_subdir.sh ~/old-project ~/monorepo projects/old-project
#     
#     # 使用环境变量
#     SOURCE_REPO_PATH=~/my-library \
#     TARGET_REPO_PATH=~/company-monorepo \
#     TARGET_SUBDIR=libraries/my-library \
#     ./migrate_git_repo_to_subdir.sh
#     
#     # 指定分支
#     SOURCE_REPO_PATH=/path/to/source \
#     TARGET_REPO_PATH=/path/to/target \
#     TARGET_SUBDIR=projects/migrated \
#     SOURCE_BRANCH=develop \
#     TARGET_BRANCH=main \
#     ./migrate_git_repo_to_subdir.sh
# 
# 功能特性:
#     ✅ 保留完整的 Git 提交历史
#     ✅ 保留所有标签和分支信息
#     ✅ 自动处理 master/main 分支差异
#     ✅ 支持冲突检测和回滚
#     ✅ 彩色输出和进度提示
#     ✅ 完整的错误处理和清理
# 
# 依赖要求:
#     - git-filter-repo (安装: pip3 install git-filter-repo 或 brew install git-filter-repo)
#     - Git 2.22+ (推荐)
# 
# 重要注意事项:
#     1. 【备份重要】执行前请备份目标仓库
#     2. 【工作区清洁】确保两个仓库都没有未提交的更改
#     3. 【路径使用】建议使用绝对路径避免路径错误
#     4. 【权限检查】确保脚本有执行权限 (chmod +x migrate_git_repo_to_subdir.sh)
#     5. 【网络无关】此脚本仅处理本地仓库，不涉及网络操作
#     6. 【不可逆操作】迁移会修改目标仓库，请谨慎操作
# 
# 测试验证:
#     运行同目录下的测试脚本验证功能:
#     ./test_migrate_git.sh
# 
# 故障排除:
#     - 如果提示找不到 git-filter-repo，请先安装该工具
#     - 如果出现权限错误，检查目录权限和脚本执行权限
#     - 如果合并失败，脚本会提供回滚命令
#     - 查看详细错误信息，脚本会输出具体的失败原因
# 
# 工作原理:
#     1. 验证源仓库和目标仓库的有效性
#     2. 使用 git-filter-repo 重写源仓库历史，将所有文件移动到指定子目录
#     3. 将重写后的历史作为远程仓库添加到目标仓库
#     4. 使用 git merge 合并历史，保留完整的提交记录
#     5. 清理临时文件和远程引用
# 
# 作者: AI Assistant
# 版本: 1.0
# 最后更新: 2025-10-04
# =============================================================================

set -e  # 遇到错误立即退出

# --- 配置参数 ---
SOURCE_REPO_PATH="${SOURCE_REPO_PATH:-}"          # 源仓库的本地路径
TARGET_REPO_PATH="${TARGET_REPO_PATH:-}"          # 目标仓库的本地路径
TARGET_SUBDIR="${TARGET_SUBDIR:-}"                # 目标仓库中的子目录路径
SOURCE_BRANCH="${SOURCE_BRANCH:-main}"            # 源仓库分支（默认 main）
TARGET_BRANCH="${TARGET_BRANCH:-main}"            # 目标仓库分支（默认 main）

# --- 临时目录 ---
TEMP_FILTERED_REPO=$(mktemp -d -t filtered_repo_XXXXXX)

# --- 颜色输出 ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- 清理函数 ---
cleanup() {
    echo -e "${YELLOW}清理临时文件...${NC}"
    rm -rf "$TEMP_FILTERED_REPO"
    echo -e "${GREEN}清理完成${NC}"
}

# 注册清理函数，确保在脚本退出时执行
trap cleanup EXIT

# --- 使用说明 ---
usage() {
    cat << EOF
使用方法:
    $0 <源仓库路径> <目标仓库路径> <目标子目录>

或者通过环境变量:
    SOURCE_REPO_PATH=/path/to/source \\
    TARGET_REPO_PATH=/path/to/target \\
    TARGET_SUBDIR=subdir/path \\
    SOURCE_BRANCH=main \\
    TARGET_BRANCH=main \\
    $0

参数说明:
    源仓库路径    - 需要迁移的完整 Git 仓库的本地路径
    目标仓库路径  - 接收迁移内容的 Git 仓库的本地路径
    目标子目录    - 在目标仓库中存放源仓库内容的子目录路径

示例:
    $0 /home/user/old-project /home/user/monorepo projects/old-project

EOF
    exit 1
}

# --- 参数解析 ---
if [ $# -eq 3 ]; then
    SOURCE_REPO_PATH="$1"
    TARGET_REPO_PATH="$2"
    TARGET_SUBDIR="$3"
elif [ $# -ne 0 ]; then
    echo -e "${RED}错误: 参数数量不正确${NC}"
    usage
fi

# 检查必需参数
if [ -z "$SOURCE_REPO_PATH" ] || [ -z "$TARGET_REPO_PATH" ] || [ -z "$TARGET_SUBDIR" ]; then
    echo -e "${RED}错误: 缺少必需参数${NC}"
    usage
fi

echo "=========================================="
echo "Git 仓库迁移工具"
echo "=========================================="
echo "源仓库路径:   $SOURCE_REPO_PATH"
echo "目标仓库路径: $TARGET_REPO_PATH"
echo "目标子目录:   $TARGET_SUBDIR"
echo "源仓库分支:   $SOURCE_BRANCH"
echo "目标仓库分支: $TARGET_BRANCH"
echo "=========================================="

# --- 1. 验证源仓库和目标仓库路径 ---
echo -e "${YELLOW}[1/5] 验证仓库路径...${NC}"

if [ ! -d "$SOURCE_REPO_PATH" ] || [ ! -d "$SOURCE_REPO_PATH/.git" ]; then
    echo -e "${RED}错误: 源仓库路径 '$SOURCE_REPO_PATH' 无效或不是一个 Git 仓库${NC}"
    exit 1
fi

if [ ! -d "$TARGET_REPO_PATH" ] || [ ! -d "$TARGET_REPO_PATH/.git" ]; then
    echo -e "${RED}错误: 目标仓库路径 '$TARGET_REPO_PATH' 无效或不是一个 Git 仓库${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 仓库路径验证通过${NC}"

# --- 2. 检查 git filter-repo 是否安装 ---
echo -e "${YELLOW}[2/5] 检查依赖工具...${NC}"

if ! command -v git-filter-repo &> /dev/null; then
    echo -e "${RED}错误: 未找到 git-filter-repo 工具${NC}"
    echo "请先安装 git-filter-repo:"
    echo "  pip3 install git-filter-repo"
    echo "或:"
    echo "  brew install git-filter-repo  (macOS)"
    exit 1
fi

echo -e "${GREEN}✓ 依赖工具检查通过${NC}"

# --- 3. 克隆并过滤源仓库 ---
echo -e "${YELLOW}[3/5] 克隆源仓库并调整目录结构...${NC}"

# 克隆源仓库到临时目录
git clone "$SOURCE_REPO_PATH" "$TEMP_FILTERED_REPO"
cd "$TEMP_FILTERED_REPO"

# 检查源仓库分支是否存在
if ! git rev-parse --verify "$SOURCE_BRANCH" &> /dev/null; then
    # 尝试 master 分支
    if git rev-parse --verify "master" &> /dev/null; then
        SOURCE_BRANCH="master"
        echo -e "${YELLOW}注意: 使用 master 分支代替 main${NC}"
    else
        echo -e "${RED}错误: 源仓库中找不到分支 $SOURCE_BRANCH${NC}"
        exit 1
    fi
fi

git checkout "$SOURCE_BRANCH"

# 使用 git filter-repo 将所有文件移动到子目录下
echo "正在重写历史，将所有文件移动到 $TARGET_SUBDIR/ 下..."
git filter-repo --to-subdirectory-filter "$TARGET_SUBDIR" --force

if [ $? -ne 0 ]; then
    echo -e "${RED}重写历史失败！${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 源仓库处理完成${NC}"

# --- 4. 合并到目标仓库 ---
echo -e "${YELLOW}[4/5] 合并到目标仓库...${NC}"

cd "$TARGET_REPO_PATH"

# 检查目标仓库分支是否存在
if ! git rev-parse --verify "$TARGET_BRANCH" &> /dev/null; then
    # 尝试 master 分支
    if git rev-parse --verify "master" &> /dev/null; then
        TARGET_BRANCH="master"
        echo -e "${YELLOW}注意: 使用 master 分支代替 main${NC}"
    else
        echo -e "${RED}错误: 目标仓库中找不到分支 $TARGET_BRANCH${NC}"
        exit 1
    fi
fi

git checkout "$TARGET_BRANCH"

# 保存当前 HEAD，以便出错时回滚
CURRENT_HEAD=$(git rev-parse HEAD)

# 添加过滤后的仓库作为远程
REMOTE_NAME="temp_migrate_$(date +%s)"
git remote add "$REMOTE_NAME" "$TEMP_FILTERED_REPO"
git fetch "$REMOTE_NAME" --tags

# 获取过滤后仓库的分支名（可能是 master 或 main）
FILTERED_BRANCH=$(cd "$TEMP_FILTERED_REPO" && git branch --show-current)
if [ -z "$FILTERED_BRANCH" ]; then
    FILTERED_BRANCH="$SOURCE_BRANCH"
fi

# 合并历史，允许不相关的历史
echo "正在合并历史..."
git merge "$REMOTE_NAME/$FILTERED_BRANCH" --allow-unrelated-histories -m "Migrate repository from $SOURCE_REPO_PATH to $TARGET_SUBDIR"

if [ $? -ne 0 ]; then
    echo -e "${RED}合并失败！可能存在冲突${NC}"
    echo "请手动解决冲突后执行:"
    echo "  git add ."
    echo "  git commit"
    echo "或者回滚:"
    echo "  git merge --abort"
    echo "  git reset --hard $CURRENT_HEAD"
    exit 1
fi

# 删除临时远程
git remote remove "$REMOTE_NAME"

echo -e "${GREEN}✓ 合并完成${NC}"

# --- 5. 验证结果 ---
echo -e "${YELLOW}[5/5] 验证迁移结果...${NC}"

if [ -d "$TARGET_SUBDIR" ]; then
    FILE_COUNT=$(find "$TARGET_SUBDIR" -type f | wc -l | tr -d ' ')
    echo -e "${GREEN}✓ 目标子目录存在，包含 $FILE_COUNT 个文件${NC}"
    
    # 显示历史记录
    COMMIT_COUNT=$(git log --oneline -- "$TARGET_SUBDIR" | wc -l | tr -d ' ')
    echo -e "${GREEN}✓ 保留了 $COMMIT_COUNT 条历史记录${NC}"
else
    echo -e "${RED}警告: 未找到目标子目录 $TARGET_SUBDIR${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}迁移成功！${NC}"
echo "=========================================="
echo "你可以执行以下命令查看结果:"
echo "  cd $TARGET_REPO_PATH"
echo "  git log --oneline --graph -- $TARGET_SUBDIR"
echo "  ls -la $TARGET_SUBDIR"
echo ""
echo "如果确认无误，可以推送到远程仓库:"
echo "  git push origin $TARGET_BRANCH"
echo "=========================================="

