FROM node:22-alpine

# Install system dependencies required for Claude Code
RUN apk add --no-cache \
    git \
    openssh-client \
    curl \
    bash \
    python3 \
    make \
    g++ \
    tzdata \
    nano \
    jq \
    && rm -rf /var/cache/apk/*

# Install Claude Code CLI globally using npm
RUN npm install -g @anthropic-ai/claude-code@latest

# Set working directory
WORKDIR /workspace

# Create necessary directories with proper permissions
RUN mkdir -p /home/node/.claude && \
    chmod 755 /home/node/.claude && \
    mkdir -p /home/node/.ssh && \
    chmod 700 /home/node/.ssh

# Configure git for proper operation
RUN git config --global user.email "claude@docker.local" && \
    git config --global user.name "Claude Code"

# Set default shell to zsh
ENV SHELL=/bin/zsh

# Volume mounts for persistent data
VOLUME ["/home/node/.claude", "/workspace", "/home/node/.ssh"]

# Environment variables
ENV NODE_ENV=production
ENV CLAUDE_CONFIG_DIR=/home/node/.claude
ENV TZ=Asia/Shanghai
ENV EDITOR=nano
ENV VISUAL=nano

# Labels for metadata
LABEL maintainer="claude-code-docker-setup"
LABEL description="Claude Code CLI with all dependencies and nano editor"
LABEL version="1.1.0"
LABEL source="built from @anthropic-ai/claude-code npm package"
LABEL features="nano-editor, timezone-fix, git-config, claude-code"
