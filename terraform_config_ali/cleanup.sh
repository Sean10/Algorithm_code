#!/bin/bash

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 环境变量
ENV=${1:-local_nvme}
TERRAFORM_DIR="${ENV}"
SSH_CONFIG_FILE="$HOME/.ssh/config"
BACKUP_FILE="$HOME/.ssh/config.bak"

# 清理SSH配置
cleanup_ssh_config() {
    echo -e "${GREEN}清理SSH配置...${NC}"
    
    # 如果存在备份文件，直接恢复
    if [ -f "${BACKUP_FILE}" ]; then
        cp "${BACKUP_FILE}" "${SSH_CONFIG_FILE}"
        rm "${BACKUP_FILE}"
        echo "已恢复SSH配置备份"
        return
    fi
    
    # 如果没有备份文件，手动删除相关配置
    if [ -f "${SSH_CONFIG_FILE}" ]; then
        # 删除Terraform管理的配置块
        sed -i.bak '/# Terraform managed: '"${ENV}"' environment/,+4d' "${SSH_CONFIG_FILE}"
        rm -f "${SSH_CONFIG_FILE}.bak"
        echo "已删除Terraform管理的SSH配置"
    fi
}

# 销毁云资源
destroy_infrastructure() {
    echo -e "${GREEN}开始销毁云资源...${NC}"
    cd "${TERRAFORM_DIR}"
    terraform destroy -auto-approve
    cd ../..
}

# 清理Ansible清单
cleanup_ansible() {
    echo -e "${GREEN}清理Ansible清单...${NC}"
    rm -f ansible/inventory.json
}

# 主流程
main() {
    echo -e "${GREEN}开始清理...${NC}"
    
    # 备份当前SSH配置
    if [ -f "${SSH_CONFIG_FILE}" ] && [ ! -f "${BACKUP_FILE}" ]; then
        cp "${SSH_CONFIG_FILE}" "${BACKUP_FILE}"
    fi
    
    # 执行清理
    cleanup_ssh_config
    destroy_infrastructure
    cleanup_ansible
    
    echo -e "${GREEN}清理完成${NC}"
}

main 