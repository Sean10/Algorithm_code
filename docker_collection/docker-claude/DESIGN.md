# Claude Code Docker沙箱环境设计文档

## 项目概述

本项目将Claude Code容器化运行，实现`--dangerously-skip-permissions`的免确认权限沙盒模式，支持在不同技术栈的项目中使用。

## 核心设计决策

### 1. 启动时rsync复制机制
- **实现方式**: `entrypoint.sh` 启动脚本在容器启动时执行
- **挂载方式**: 主机目录只读挂载 (`ro`)，复制到容器内可写位置
- **路径映射**:
  - `${HOME}/.claude` → `/host-claude:ro` → 复制到 `/home/node/.claude`
  - `${HOME}/.agents` → `/host-agents:ro` → 复制到 `/home/node/.agents`
  - `${HOME}/.ssh` → `/host-ssh:ro` → 复制到 `/home/node/.ssh`
- **排除项**: `projects/`、`*.log`、`*.tmp`、`node_modules/`、`.cache/`
- **优势**: 避免直接挂载导致的权限问题，支持容器内修改后重启恢复

### 2. dangerously-skip-permissions集成策略
- **实现方式**: 通过 shell 别名实现
- **方法**: `alias claude="claude --dangerously-skip-permissions"`
- **位置**: 自动添加到 `~/.zshrc` 和 `~/.bashrc`
- **优势**: 用户无需每次手动添加参数，确保始终使用免确认模式

### 3. 工作空间挂载
- **挂载路径**: `.` → `/workspace:cached`
- **访问模式**: 双向读写，cached模式提升性能
- **适用场景**: 支持容器内外的文件编辑和版本控制

### 4. 命令历史持久化
- **挂载方式**: 命名卷 `claude-bash-history` 挂载到 `/commandhistory`
- **用途**: 持久化 shell 命令历史

## 配置文件说明

### Dockerfile
- **基础镜像**: `node:22-alpine`（Alpine Linux，更轻量）
- **Claude Code版本**: 固定为 `2.1.17`（确保稳定性）
- **主要组件**:
  - 基础开发工具: git, python3, make, g++, nano
  - 网络工具: iptables, ipset
  - Git增强: git-delta 0.18.2 用于代码审查
  - Shell环境: zsh-in-docker 自动配置
  - Claude Code: 全局安装 @anthropic-ai/claude-code@2.1.17
- **用户**: 创建 node 用户 (uid 1000)，配置 sudo NOPASSWD

### docker-compose.yml
- **无头模式**: `stdin_open: true, tty: true`
- **权限配置**: `NET_ADMIN, NET_RAW` 支持网络管理
- **环境变量**:
  - `NODE_OPTIONS=--max-old-space-size=4096`
  - `CLAUDE_CONFIG_DIR=/home/node/.claude`
  - `POWERLEVEL9K_DISABLE_GITSTATUS=true`
  - `DEVCONTAINER=true`
- **挂载配置**:
  - 工作区: `.:/workspace:rw`
  - 命令历史: `claude-bash-history:/commandhistory`
  - 主机配置: `${HOME}/.claude:/host-claude:ro`
  - 主机agents: `${HOME}/.agents:/host-agents:ro`
  - 主机SSH: `${HOME}/.ssh:/host-ssh:ro`
- **健康检查**: 配置容器健康状态监控

### devcontainer.json
- **VS Code集成**: 预置Claude Code扩展
- **挂载配置**: 绑定挂载 `.claude` 目录
- **初始化命令**: 自动创建claude别名
- **终端配置**: 默认使用zsh shell

### entrypoint.sh
启动脚本执行流程：
1. 复制 `.claude` 核心配置（排除临时文件）
2. 复制 custom agents
3. 复制 SSH 密钥并设置权限
4. 设置文件 owner 为 node 用户
5. 创建 `claude` 命令别名
6. 执行传入的命令（默认 `zsh`）

## 使用场景

### 1. Headless服务器自动化开发
```bash
docker-compose up -d
docker-compose exec claude-code zsh
```

### 2. VS Code远程开发
```bash
# 使用VS Code打开项目，选择"在容器中重新打开"
# VS Code自动检测devcontainer.json并启动容器
```

### 3. 手动启动
```bash
# 构建镜像
docker-compose build

# 启动容器
docker-compose up

# 访问容器
docker-compose exec claude-code zsh
```

## 优势特性

1. **真正免确认**: `--dangerously-skip-permissions`自动生效
2. **配置无缝继承**: 主机claude配置、skills、API等完全保留
3. **工作空间隔离**: 项目文件与claude配置完全分离
4. **灵活扩展**: 支持不同技术栈的定制化需求
5. **开发友好**: 同时支持CLI和IDE两种开发模式
6. **SSH支持**: 自动复制SSH密钥，支持Git操作
7. **历史持久化**: 命令历史保存在命名卷中

## 安全考虑

1. **配置隔离**: 主机配置只读挂载，容器内可写副本
2. **权限控制**: 使用非root用户运行claude
3. **数据隔离**: workspace目录独立挂载，避免泄露
4. **密钥安全**: SSH密钥复制后设置正确权限(600/644)

## 技术选型说明

### 为什么使用Alpine镜像？
- 镜像更小（约200MB vs 1GB+）
- 启动更快
- 资源占用更少

### 为什么固定Claude Code版本？
- 确保稳定性，避免自动更新导致不兼容
- 便于复现和调试

### 为什么用rsync而非直接挂载？
- 避免权限冲突（主机UID可能与容器内不匹配）
- 支持容器内修改后不影响主机
- 可以精确排除不需要的文件

## 后续优化方向

1. **多技术栈支持**: 基于当前Dockerfile复制修改为Python/Go等变体
2. **配置模板**: 提供常用项目类型的配置模板
3. **CI/CD集成**: 支持GitHub Actions/GitLab CI自动部署
4. **多用户支持**: 考虑支持不同UID的用户
