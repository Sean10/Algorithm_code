# Claude Code Docker 沙箱环境

将 Claude Code CLI 容器化运行，实现 `--dangerously-skip-permissions` 免确认权限的沙盒模式。

## 核心特性

- **免确认权限**: 自动配置 `--dangerously-skip-permissions` 别名
- **配置继承**: 启动时 rsync 复制主机 `.claude`、`.agents`、`.ssh` 目录
- **工作空间隔离**: 挂载当前目录为 `/workspace`，项目文件与配置分离
- **双模式支持**: Headless CLI 模式 + VS Code 远程开发模式
- **历史持久化**: 命令历史存储在命名卷中

## 快速开始

### 环境要求

- Docker / Docker Compose

### 使用方式

**Headless 服务器模式:**

```bash
# 启动容器
docker compose up -d

# 进入容器
docker compose exec -it claude-code zsh

# 直接使用（已自动配置别名）
claude "Your task"


# 或者
docker compose exec claude-code claude --dangerously-skip-permissions
```

**VS Code 远程开发:**

1. 用 VS Code 打开项目
2. 按 `Cmd+Shift+P`，选择 "Dev Containers: Reopen in Container"

## 项目结构

| 文件 | 说明 |
|------|------|
| `Dockerfile` | 镜像构建，基于 `node:22-alpine` |
| `docker-compose.yml` | 容器编排配置 |
| `devcontainer.json` | VS Code Dev Container 配置 |
| `entrypoint.sh` | 启动脚本，复制主机配置到容器内 |

## 配置详情

### Dockerfile

- **基础镜像**: `node:22-alpine`
- **Claude Code**: 版本 `2.1.17`
- **开发工具**: git, zsh, python3, make, g++, nano, jq, fzf
- **网络工具**: iptables, ipset
- **Git 增强**: git-delta 0.18.2
- **Shell**: zsh + zsh-in-docker
- **用户**: node (uid 1000)

### docker-compose.yml

```yaml
services:
  claude-code:
    build: .
    image: claude-code-local:latest
    cap_add: [NET_ADMIN, NET_RAW]    # 权限配置
    environment:
      - NODE_OPTIONS=--max-old-space-size=4096
      - CLAUDE_CONFIG_DIR=/home/node/.claude
      - POWERLEVEL9K_DISABLE_GITSTATUS=true
      - DEVCONTAINER=true
    volumes:
      - .:/workspace:rw               # 工作区
      - claude-bash-history:/commandhistory  # 历史记录
      - ${HOME}/.claude:/host-claude:ro      # 主机配置（只读）
      - ${HOME}/.agents:/host-agents:ro      # 主机 agents
      - ${HOME}/.ssh:/host-ssh:ro            # SSH 密钥
```

## 启动机制

### 配置文件复制流程

`entrypoint.sh` 在容器启动时执行：

1. **复制 .claude 核心配置**
   - rsync 同步，排除 `projects/`、`*.log`、`*.tmp`、`node_modules/`、`.cache/`

2. **复制 custom agents**
   - 从 `~/.claude/agents` 和 `~/.agents` 复制到容器

3. **复制 SSH 密钥**
   - 自动复制 `id_*` 密钥、config、known_hosts
   - 设置正确权限 (600/644)

4. **设置权限**
   - 所有文件 owner 设为 node 用户

### 别名配置

自动在 `~/.zshrc` 和 `~/.bashrc` 中添加：

```bash
alias claude="claude --dangerously-skip-permissions"
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `TZ` | `Asia/Shanghai` | 时区 |
| `CLAUDE_CODE_VERSION` | `2.1.17` | Claude Code 版本 |
| `GIT_DELTA_VERSION` | `0.18.2` | git-delta 版本 |
| `ZSH_IN_DOCKER_VERSION` | `1.2.0` | zsh-in-docker 版本 |

## 扩展使用

### 多技术栈支持

基于 `node:22-alpine`，可根据需要修改 Dockerfile:

```dockerfile
# 基础镜像替换示例
FROM python:3.11-alpine
```

### CI/CD 集成

```yaml
- name: Run Claude Code
  run: |
    docker compose build
    docker compose run --rm claude-code claude "Your task"
```

## 注意事项

- 配置文件在容器启动时复制到容器内
- 主机文件变更需重启容器生效
- 使用非 root 用户 (node) 运行
- 命名卷 `claude-bash-history` 持久化命令历史
