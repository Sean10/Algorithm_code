FROM node:22-alpine

ARG GIT_DELTA_VERSION=0.18.2

# Install system dependencies required for Claude Code
RUN apk add --no-cache \
    git \
    openssh-client \
    curl \
    bash \
    zsh \
    python3 \
    make \
    g++ \
    tzdata \
    nano \
    jq \
    fzf \
    iptables \
    ipset \
    wget \
    sudo \
    && rm -rf /var/cache/apk/*

# Install git-delta for code review (use portable binary for Alpine)
RUN wget -q "https://github.com/dandavison/delta/releases/latest/download/delta-${GIT_DELTA_VERSION}-x86_64-unknown-linux-musl.tar.gz" && \
    tar -xzf "delta-${GIT_DELTA_VERSION}-x86_64-unknown-linux-musl.tar.gz" && \
    mv delta-0.18.2-x86_64-unknown-linux-musl/delta /usr/local/bin/ && \
    chmod +x /usr/local/bin/delta && \
    rm "delta-${GIT_DELTA_VERSION}-x86_64-unknown-linux-musl.tar.gz"

# Create node group and user (node:alpine already has node user, check and use it)
RUN (id node 2>/dev/null || (addgroup -g 1000 node && adduser -u 1000 -G node -s /bin/zsh -D node))

# Install Claude Code CLI globally using npm
RUN npm install -g @anthropic-ai/claude-code@2.1.17

# Set working directory
WORKDIR /workspace

# Create necessary directories with proper permissions
RUN chown -R node:node /home/node && \
    mkdir -p /home/node/.claude && \
    mkdir -p /home/node/.ssh && \
    chmod 755 /home/node/.claude && \
    chmod 700 /home/node/.ssh

# Configure git for proper operation
RUN git config --global user.email "claude@docker.local" && \
    git config --global user.name "Claude Code" && \
    git config --global delta.navigation true && \
    git config --global delta.features sidebar

# Install zsh-in-docker for automatic zsh configuration
ARG ZSH_IN_DOCKER_VERSION=1.2.0
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/romkatv/zsh-in-docker/${ZSH_IN_DOCKER_VERSION}/zsh-in-docker.sh)" -- \
    --skip-chsh \
    --skip-oh-my-zsh \
    --plugins git docker docker-compose

# Switch to node user for subsequent commands
USER node

# Set default shell to zsh
ENV SHELL=/bin/zsh

# Volume mounts for persistent data
VOLUME ["/home/node/.claude", "/workspace", "/home/node/.ssh"]

# Environment variables
ENV NODE_ENV=production
ENV CLAUDE_CONFIG_DIR=/home/node/.claude
ENV TZ=Asia/Shanghai

# Labels for metadata
LABEL maintainer="claude-code-docker-setup"
LABEL description="Claude Code CLI with all dependencies and zsh-in-docker"
LABEL version="1.2.0"
LABEL source="built from @anthropic-ai/claude-code npm package"
LABEL features="zsh-in-docker, git-delta, fzf, gh, iptables, nano-editor, timezone-fix, git-config, claude-code"
