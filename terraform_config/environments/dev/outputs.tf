# 输出所有实例信息（JSON格式）
output "ansible_inventory" {
  description = "Ansible 清单信息（JSON格式）"
  value = {
    all = {
      hosts = {
        "tenos" = {
          ansible_host = module.compute.instance.public_ip
          ansible_user = "root"  # 基于Ubuntu镜像
          private_ip   = module.compute.instance.private_ip
          environment  = var.environment
          zone        = module.compute.instance.zone
        }
      }
      vars = {
        ansible_ssh_common_args = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
        # ansible_ssh_private_key_file = "~/.ssh/tmp_ssh_private_key"
        ansible_ssh_pass = var.password
      }
    }
  }
}

# 输出SSH配置信息
output "ssh_config" {
  description = "SSH 配置信息"
  value = {
    host         = "tenos"
    hostname     = module.compute.instance.public_ip
    user         = "root"  # 基于Ubuntu镜像
    identity_file = "~/.ssh/sean10_tencent"
    password = var.password
  }
} 