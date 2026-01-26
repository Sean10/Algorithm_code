# Claude Code Docker 沙箱环境

将 Claude Code CLI 容器化运行，实现 `--dangerously-skip-permissions` 免确认权限的沙盒模式。

## 核心特性

- **免确认权限**: 自动配置 `--dangerously-skip-permissions` 参数
- **配置继承**: 挂载主机 `~/.claude` 目录，保留 skills、API 配置
- **工作空间隔离**: 挂载当前目录为 `/workspace`，项目文件与配置分离
- **双模式支持**: Headless CLI 模式 + VS Code 远程开发模式
- **网络安全**: 内置防火墙脚本，限制仅允许必要网络访问

## 快速开始

### 环境要求

- Docker / Docker Compose
- VS Code (可选，用于远程开发)

### 使用方式

**Headless 服务器模式:**

```bash
# 启动容器
docker-compose up -d

# 进入容器
docker-compose exec -it claude-code zsh
```

**VS Code 远程开发:**

1. 用 VS Code 打开项目
2. 按 `Cmd+Shift+P`，选择 "Dev Containers: Reopen in Container"

## 项目结构

| 文件 | 说明 |
|------|------|
| `Dockerfile` | 基础镜像构建，基于 `node:20` |
| `docker-compose.yml` | 容器编排配置 |
| `devcontainer.json` | VS Code Dev Container 配置 |
| `init-firewall.sh` | 防火墙初始化脚本 |

## 配置详情

### Dockerfile

- **基础镜像**: `node:20`
- **开发工具**: git, zsh, fzf, gh, nano, vim
- **网络工具**: iptables, ipset, dnsutils, jq
- **Git 增强**: git-delta 0.18.2 (代码审查)
- **Shell**: zsh + oh-my-zsh

### docker-compose.yml

```yaml
services:
  claude-code:
    cap_add: [NET_ADMIN, NET_RAW]    # 防火墙权限
    environment:
      - NODE_OPTIONS=--max-old-space-size=4096
    volumes:
      - .:/workspace:rw               # 当前目录 -> 工作区
      - ${HOME}/.claude:/home/node/.claude:rw  # Claude 配置继承
    deploy:
      limits: cpus: '4.0', memory: 8G
      reservations: cpus: '1.0', memory: 2G
```



## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `TZ` | `America/Los_Angeles` | 时区 |
| `CLAUDE_CODE_VERSION` | `latest` | Claude Code 版本 |
| `GIT_DELTA_VERSION` | `0.18.2` | git-delta 版本 |
| `ZSH_IN_DOCKER_VERSION` | `1.2.0` | zsh-in-docker 版本 |

## 扩展使用

### 多技术栈支持

当前基于 `node:20`，可根据需要复制修改为 Python/Go 等技术栈变体:

```dockerfile
# 基础镜像替换示例
FROM python:3.11-slim
```

### CI/CD 集成

支持在 GitHub Actions/GitLab CI 中使用:

```yaml
- name: Run Claude Code
  run: |
    docker-compose build
    docker-compose run --rm claude-code claude "Your task"
```

## 注意事项

- 容器内外文件实时双向同步
- 使用非 root 用户 (node) 运行
- 建议定期清理未使用的 Docker 资源
