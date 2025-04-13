
output "instance" {
    value = data.alicloud_instance_types.cheapest.instance_types.0
}

output "alicloud_images" {
    value = data.alicloud_images.default.images
}

output "ansible_inventory" {
  description = "Ansible 清单信息（JSON格式）"
  value = {
    all = {
      hosts = {
        "tenos" = {
          ansible_host = alicloud_instance.instance.0.public_ip
          ansible_user = "root"  # 基于Ubuntu镜像
          private_ip   = alicloud_instance.instance.0.private_ip
        #   zone        = alicloud_instance.instance.0.zone
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
    hostname     = alicloud_instance.instance.0.public_ip
    user         = "root"  # 基于Ubuntu镜像
    identity_file = "~/.ssh/sean10_tencent"
    password = var.password
  }
}
