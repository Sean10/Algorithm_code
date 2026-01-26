# Claude Code Docker沙箱环境设计文档

## 项目概述

本项目将Claude Code容器化运行，实现`--dangerously-skip-permissions`的免确认权限沙盒模式，支持在不同技术栈的项目中使用。

## 核心设计决策

### 1. dangerously-skip-permissions集成策略
- **实现方式**: 在docker-compose.yml和devcontainer.json中预置CLI参数
- **方法**: 通过shell别名实现 `claude` → `claude --dangerously-skip-permissions`
- **优势**: 用户无需每次手动添加参数，确保始终使用免确认模式

### 2. 配置继承方案
- **挂载方式**: 直接读写挂载(`rw`)主机的`~/.claude`目录
- **路径映射**: `${HOME}/.claude` → `/home/node/.claude`
- **同步机制**: 容器内外实时双向同步，无需额外同步工具

### 3. 工作空间挂载
- **挂载路径**: `.` → `/workspace:cached`
- **访问模式**: 双向读写，cached模式提升性能
- **适用场景**: 支持容器内外的文件编辑和版本控制

## 配置文件说明

### Dockerfile
- **基础镜像**: `node:20`（保持简洁，支持Claude Code需求）
- **可变策略**: 后续可按需复制修改为其他技术栈变体
- **主要组件**:
  - 基础开发工具: git, zsh, fzf, gh等
  - 网络工具: iptables, ipset, dnsutils
  - Git增强: git-delta用于代码审查
  - Shell环境: zsh-in-docker自动配置
  - Claude Code: 全局安装，支持最新版本

### docker-compose.yml
- **无头模式**: `stdin_open: true, tty: true`
- **权限配置**: `NET_ADMIN, NET_RAW`支持防火墙脚本
- **环境变量**:
  - `NODE_OPTIONS=--max-old-space-size=4096`
  - `CLAUDE_CONFIG_DIR=/home/node/.claude`
  - `DEVCONTAINER=true`
- **启动命令**:
  - 初始化防火墙规则
  - 创建claude别名
  - 启动zsh shell
- **资源限制**:
  - CPU: 最大4核，保留1核
  - 内存: 最大8GB，保留2GB

### devcontainer.json
- **VS Code集成**: 预置Claude Code扩展
- **挂载配置**: 绑定挂载`.claude`目录，`delegated`一致性
- **初始化命令**: 自动创建claude别名
- **终端配置**: 默认使用zsh shell

## 使用场景

### 1. Headless服务器自动化开发
```bash
docker-compose up -d
docker-compose exec claude-code bash
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

## 安全考虑

1. **网络限制**: init-firewall.sh限制网络访问，仅允许必要服务
2. **权限控制**: 使用非root用户运行claude
3. **数据隔离**: workspace目录独立挂载，避免泄露

## 后续优化方向

1. **多技术栈支持**: 基于当前Dockerfile复制修改为Python/Go等变体
2. **配置模板**: 提供常用项目类型的配置模板
3. **CI/CD集成**: 支持GitHub Actions/GitLab CI自动部署
4. **持久化优化**: 考虑使用命名卷管理claude缓存
