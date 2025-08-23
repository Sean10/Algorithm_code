# 查询可用的系统镜像
data "tencentcloud_images" "selected" {
  image_type = ["PUBLIC_IMAGE"]
  os_name    = var.os_name

  result_output_file = "available_images.json"  # 输出查询结果便于调试
}

# 定义本地变量
locals {
  # 根据CPU和内存要求，选择价格最低的实例类型
  selected_instance_type = try(
    data.tencentcloud_instance_types.selected.instance_types[0].instance_type,
    "SA2.SMALL1" # 默认实例类型，仅作为后备选项
  )

  # 选择匹配的系统镜像
  selected_image_id = try(
    data.tencentcloud_images.selected.images[0].image_id,
    var.image_id # 使用默认镜像作为后备选项
  )
}

# 查询可用的实例类型
data "tencentcloud_instance_types" "selected" {
  cpu_core_count = var.cpu_core_count
  memory_size    = var.memory_size
  # availability_zone = var.availability_zone

  filter {
    name   = "instance-charge-type"
    values = ["SPOTPAID"]
  }
  exclude_sold_out = true

  result_output_file = "instance_types.json"  # 输出查询结果便于调试
}

# 创建安全组
resource "tencentcloud_security_group" "default" {
  name        = "${var.environment}-security-group"
  description = "Default security group for ${var.environment}"
}

# 配置安全组规则集
resource "tencentcloud_security_group_rule_set" "default" {
  security_group_id = tencentcloud_security_group.default.id

  # 入站规则
  ingress {
    action      = "ACCEPT"
    cidr_block  = "0.0.0.0/0"
    protocol    = "TCP"
    port        = "22"
    description = "允许SSH访问"
  }

  ingress {
    action      = "ACCEPT"
    cidr_block  = "0.0.0.0/0"
    protocol    = "TCP"
    port        = "80,443"
    description = "允许HTTP/HTTPS访问"
  }

  # 出站规则
  egress {
    action      = "ACCEPT"
    cidr_block  = "0.0.0.0/0"
    protocol    = "ALL"
    port        = "ALL"
    description = "允许所有出站流量"
  }
}

# 创建 CVM 实例
resource "tencentcloud_instance" "cvm" {
  instance_name    = var.instance_name
  availability_zone = var.availability_zone
  image_id         = local.selected_image_id
  instance_type    = local.selected_instance_type
  system_disk_type = var.system_disk_type
  system_disk_size = var.system_disk_size


  password = var.password
  # key_ids = [tencentcloud_ssm_ssh_key_pair_secret.example.id]
  vpc_id                     = var.vpc_id
  subnet_id                  = var.subnet_id
  instance_charge_type       = var.instance_charge_type
  internet_charge_type       = "TRAFFIC_POSTPAID_BY_HOUR"
  internet_max_bandwidth_out = 100
  allocate_public_ip        = true


  orderly_security_groups = [
    tencentcloud_security_group.default.id
  ]

  spot_instance_type = var.instance_charge_type == "SPOTPAID" ? "ONE-TIME" : null
  spot_max_price    = var.instance_charge_type == "SPOTPAID" ? var.spot_max_price : null

  tags = {
    environment = var.environment
  }
}


resource "tencentcloud_cbs_storage" "my_storage" {
  storage_type      = "CLOUD_HSSD"
  storage_name      = "${var.environment}-storage"
  storage_size      = var.data_disk_size
  availability_zone = var.availability_zone
  project_id        = 0
  encrypt           = false

  tags = {
    test = "tf"
  }
}

resource "tencentcloud_cbs_storage_attachment" "my_attachment" {
  storage_id  = tencentcloud_cbs_storage.my_storage.id
  instance_id = tencentcloud_instance.cvm.id
}


# resource "tencentcloud_kms_key" "example" {
#   alias                = "${var.environment}-kms-key"
#   description          = "example of kms key"
#   key_rotation_enabled = false
#   is_enabled           = true

#   tags = {
#     createdBy = "terraform"
#   }
# }

# resource "tencentcloud_ssm_ssh_key_pair_secret" "example" {
#   secret_name   = "${var.environment}-ssh-key"
#   project_id    = 0
#   description   = "desc."
#   kms_key_id    = tencentcloud_kms_key.example.id
#   ssh_key_name  = "${var.environment}-ssh"
#   status        = "Enabled"
#   clean_ssh_key = true

#   tags = {
#     createdBy = "terraform"
#   }
# }

# data "tencentcloud_ssm_ssh_key_pair_value" "created_ssh_key" {
#   secret_name = "${var.environment}-ssh-key"
#   ssh_key_id  = tencentcloud_ssm_ssh_key_pair_secret.example.id
# }