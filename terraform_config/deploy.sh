#!/bin/bash

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 环境变量
ENV=${1:-dev}
TERRAFORM_DIR="environments/${ENV}"
ANSIBLE_DIR="ansible"
INVENTORY_FILE="inventory.json"
SSH_CONFIG_FILE="$HOME/.ssh/config"
BACKUP_FILE="$HOME/.ssh/config.bak"

# 检查必要工具
check_requirements() {
    echo "检查必要工具..."
    command -v terraform >/dev/null 2>&1 || { echo "需要 terraform 但未安装"; exit 1; }
    command -v ansible-playbook >/dev/null 2>&1 || { echo "需要 ansible-playbook 但未安装"; exit 1; }
    command -v jq >/dev/null 2>&1 || { echo "需要 jq 但未安装"; exit 1; }
}

# 检查SSH密钥
check_ssh_key() {
    local key_file="$HOME/.ssh/sean10_tencent"
    if [ ! -f "$key_file" ]; then
        echo "SSH密钥文件不存在: $key_file"
        exit 1
    fi
}

# 备份SSH配置
backup_ssh_config() {
    if [ -f "${SSH_CONFIG_FILE}" ] && [ ! -f "${BACKUP_FILE}" ]; then
        cp "${SSH_CONFIG_FILE}" "${BACKUP_FILE}"
        echo "已备份SSH配置到 ${BACKUP_FILE}"
    fi
}

# 创建资源
create_infrastructure() {
    echo -e "${GREEN}开始创建基础设施...${NC}"
    cd "${TERRAFORM_DIR}"
    # terraform init
    terraform apply -auto-approve
    
    # 导出Ansible清单
    terraform output -json ansible_inventory > "../../${INVENTORY_FILE}"
    
    # terraform output -json ssh_key_info | jq -r '. | ssh_key_private_key' >> ~/.ssh/tmp_ssh_private_key
    # 更新SSH配置
    backup_ssh_config
    {
        echo -e "\n# Terraform managed: ${ENV} environment"

        terraform output -json ssh_config | jq -r '. | "Host \(.host)\n  HostName \(.hostname)\n  User \(.user)\n  IdentityFile \(.identity_file)\n"'
    } >> "${SSH_CONFIG_FILE}"
    
    cd ../..
}

# 等待SSH可用
wait_for_ssh() {
    echo "等待SSH服务就绪..."
    HOST=$(jq -r '.all.hosts.tenos.ansible_host' "${INVENTORY_FILE}")
    USER=$(jq -r '.all.hosts.tenos.ansible_user' "${INVENTORY_FILE}")
    PASSWORD=$(jq -r '.all.vars.ansible_ssh_pass' "${INVENTORY_FILE}")
    
    for i in {1..30}; do
        if sshpass -p "${PASSWORD}" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 "${USER}@${HOST}" 'exit' 2>/dev/null; then
            echo "SSH连接已就绪"
            return 0
        fi
        echo "等待SSH服务... ${i}/30"
        sleep 10
    done
    
    echo "SSH服务未就绪，退出"
    exit 1
}

# 运行Ansible配置
run_ansible() {
    echo -e "${GREEN}开始配置服务器...${NC}"
    cd "${ANSIBLE_DIR}"
    tar czf /tmp/extra_mnt.tar.gz -C ../extra_mnt .
    ansible-playbook -i "${INVENTORY_FILE}" site.yml
    rm -f /tmp/extra_mnt.tar.gz
    cd ..
}

# 主流程
main() {
    check_requirements
    check_ssh_key
    create_infrastructure
    wait_for_ssh
    run_ansible
    echo -e "${GREEN}部署完成${NC}"
}

main 