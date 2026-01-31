#!/bin/zsh
# Entrypoint script for Claude Code Docker container
# 启动时复制宿主机配置到容器内

set -e

# 配置路径 - 挂载点
HOST_CLAUDE_DIR="${HOST_CLAUDE_DIR:-/host-claude}"
HOST_AGENTS_DIR="${HOST_AGENTS_DIR:-/host-claude/agents}"
HOST_CUSTOM_AGENTS_DIR="${HOST_CUSTOM_AGENTS_DIR:-/host-agents}"
HOST_SSH_DIR="${HOST_SSH_DIR:-/host-ssh}"

CONTAINER_CLAUDE_DIR="/home/node/.claude"
CONTAINER_AGENTS_DIR="/home/node/.claude/agents"
CONTAINER_CUSTOM_AGENTS_DIR="/home/node/.agents"
CONTAINER_SSH_DIR="/home/node/.ssh"

echo "=== Claude Code Container Startup ==="

# ========== 1. 复制 .claude 核心配置 ==========
echo ""
echo "[1/4] Copying Claude config..."

mkdir -p "$CONTAINER_CLAUDE_DIR"

if [ -d "$HOST_CLAUDE_DIR" ]; then
    rsync -av \
        --exclude='projects/' \
        --exclude='*.log' \
        --exclude='*.tmp' \
        --exclude='node_modules/' \
        --exclude='.cache/' \
        "$HOST_CLAUDE_DIR/" "$CONTAINER_CLAUDE_DIR/"
    echo "  - Claude config copied"
else
    echo "  - Warning: Host CLAUDE_DIR not found"
fi

# ========== 2. 复制 agents ==========
echo ""
echo "[2/4] Copying custom agents..."

mkdir -p "$CONTAINER_AGENTS_DIR"

if [ -d "$HOST_AGENTS_DIR" ]; then
    rsync -av "$HOST_AGENTS_DIR/" "$CONTAINER_AGENTS_DIR/"
    rsync -av "$HOST_CUSTOM_AGENTS_DIR/" "$CONTAINER_CUSTOM_AGENTS_DIR/"
    echo "  - Custom agents copied"
fi

# ========== 3. 复制 SSH 密钥 ==========
echo ""
echo "[3/4] Copying SSH keys..."

mkdir -p "$CONTAINER_SSH_DIR"
chmod 700 "$CONTAINER_SSH_DIR"

if [ -d "$HOST_SSH_DIR" ]; then
    for key in "$HOST_SSH_DIR"/id_*; do
        if [ -f "$key" ]; then
            cp "$key" "$CONTAINER_SSH_DIR/"
            chmod 600 "$CONTAINER_SSH_DIR/$(basename "$key")"
        fi
    done

    [ -f "$HOST_SSH_DIR/config" ] && cp "$HOST_SSH_DIR/config" "$CONTAINER_SSH_DIR/config" && chmod 600 "$CONTAINER_SSH_DIR/config"
    [ -f "$HOST_SSH_DIR/known_hosts" ] && cp "$HOST_SSH_DIR/known_hosts" "$CONTAINER_SSH_DIR/known_hosts" && chmod 644 "$CONTAINER_SSH_DIR/known_hosts"
    echo "  - SSH keys copied"
fi

# ========== 4. 设置权限 ==========
echo ""
echo "[4/4] Finalizing permissions..."

chown -R node:node "$CONTAINER_CLAUDE_DIR" "$CONTAINER_AGENTS_DIR" "$CONTAINER_SSH_DIR"

# 时区
ln -sf /usr/share/zoneinfo/${TZ:-Asia/Shanghai} /etc/localtime 2>/dev/null || true

echo "alias claude=\"claude --dangerously-skip-permissions\"" >> ~/.zshrc
echo "alias claude=\"claude --dangerously-skip-permissions\"" >> ~/.bashrc
alias claude="claude --dangerously-skip-permissions"

echo ""
echo "=== Startup Complete ==="
echo "User: $(whoami)"
echo "Workspace: /workspace"
echo ""

exec "$@"
