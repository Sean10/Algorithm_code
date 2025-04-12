# 输出实例基本信息
output "instance" {
  description = "实例基本信息"
  value = {
    id           = tencentcloud_instance.cvm.id
    name         = tencentcloud_instance.cvm.instance_name
    private_ip   = tencentcloud_instance.cvm.private_ip
    public_ip    = tencentcloud_instance.cvm.public_ip
    type         = tencentcloud_instance.cvm.instance_type
    zone         = tencentcloud_instance.cvm.availability_zone
  }
}

# 输出安全组信息
output "security_group" {
  description = "安全组信息"
  value = {
    id   = tencentcloud_security_group.default.id
    name = tencentcloud_security_group.default.name
  }
}

# 实例网络信息
output "instance_info" {
  description = "实例详细信息"
  value = {
    instance_name = tencentcloud_instance.cvm.instance_name
    private_ip    = tencentcloud_instance.cvm.private_ip
    public_ip     = tencentcloud_instance.cvm.public_ip
    vpc_id        = tencentcloud_instance.cvm.vpc_id
    subnet_id     = tencentcloud_instance.cvm.subnet_id
  }
}

# 安全组信息
output "security_group_info" {
  description = "安全组信息"
  value = {
    security_group_id = tencentcloud_security_group.default.id
    security_group_name = tencentcloud_security_group.default.name
  }
}

# output "ssh_key_info" {
#   description = "SSH密钥信息"
#   value = {
#     ssh_key_id = tencentcloud_ssm_ssh_key_pair_secret.example.id
#     ssh_key_name = tencentcloud_ssm_ssh_key_pair_secret.example.ssh_key_name
#     ssh_key_private_key = data.tencentcloud_ssm_ssh_key_pair_value.created_ssh_key.private_key
#   }
# }