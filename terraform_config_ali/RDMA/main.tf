
# 使用数据源查询可用区信息，通过指定的实例类型、资源创建类型（如VSwitch）以及磁盘种类来过滤结果
# data "alicloud_zones" "default" {
#   available_instance_type     = var.instance_type
#   available_resource_creation = "VSwitch"
#   available_disk_category     = "cloud_essd"
# }

# Declare the data source
data "alicloud_instance_types" "cheapest" {
  availability_zone    = var.availability_zone
  instance_charge_type = "PostPaid"
  spot_strategy      = "SpotWithPriceLimit"
  instance_type_family = var.instance_type_family
  cpu_core_count       = var.cpu_core_count == 0 ? 2 : var.cpu_core_count
#   memory_size          = var.memory_size == 0 ? 4096 : var.memory_size
  # 不是所有都有price, 所以没法排序
  sorted_by = "CPU"

  output_file = "instance_types.json"
}

data "alicloud_images" "default" {
  name_regex  = var.os_name
  most_recent = true
  owners      = "system"
}

resource "alicloud_vpc" "vpc" {
  vpc_name   = "vpc-test_1"
  cidr_block = var.vpc_cidr_block
}

# 创建安全组，名称包含随机整数以保证唯一性，并关联至上述VPC
resource "alicloud_security_group" "group" {
  security_group_name = "test_1" # 替换了这里的字段名
  vpc_id              = alicloud_vpc.vpc.id
}

# 创建一条允许所有TCP流量进入的安全组规则，与之前创建的安全组关联
resource "alicloud_security_group_rule" "allow_all_tcp" {
  type              = "ingress"
  ip_protocol       = "tcp"
  nic_type          = "intranet"
  policy            = "accept"
  port_range        = "1/65535"
  priority          = 1
  security_group_id = alicloud_security_group.group.id
  cidr_ip           = "0.0.0.0/0"
}

# 创建VSwitch，名称中包含随机整数以确保唯一性，并与VPC、可用区关联
resource "alicloud_vswitch" "vswitch" {
  vpc_id       = alicloud_vpc.vpc.id
  cidr_block   = var.vsw_cidr_block
  zone_id      = var.availability_zone
  vswitch_name = "vswitch-test-1"
}

# 创建ECS实例，设置多个参数如可用区、安全组、实例类型等，并使用随机整数保证实例名称的唯一性
resource "alicloud_instance" "instance" {
  count = var.instance_count
  spot_price_limit = var.spot_max_price
  availability_zone          = var.availability_zone
  security_groups            = [alicloud_security_group.group.id]
  instance_type              = data.alicloud_instance_types.cheapest.instance_types.0.id
  system_disk_category       = "cloud_essd"
  system_disk_name           = "test_foo_system_disk_${count.index}"
  system_disk_description    = "test_foo_system_disk_description"
  system_disk_size           = var.system_disk_size
  image_id                   = data.alicloud_images.default.images.0.id
  instance_name              = "test_ecs_${count.index}"
  vswitch_id                 = alicloud_vswitch.vswitch.id
  # 设置按需收费, CDT
  internet_charge_type       = "PayByTraffic"
  internet_max_bandwidth_out = 5
  network_interface_traffic_mode = "HighPerformance"
  password                   = var.password # 用户根据自己实际情况设置

  data_disks {
    name        = "disk2"
    size        = var.cloud_disk_size
    category    = "cloud_essd"
    description = "disk2"
  }
}