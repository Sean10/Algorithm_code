# 定义一个变量region，默认值为"cn-beijing"，用于指定阿里云区域
variable "region" {
  default = "cn-hangzhou"
}

variable "availability_zone" {
  default = "cn-hangzhou-i"
}

# 定义一个字符串类型的变量instance_type，默认值为"ecs.e-c1m1.large"，用于指定ECS实例类型
variable "instance_type_family" {
  type    = string
  default = "ecs.e-c1m1.large"
}

# 定义一个变量vpc_cidr_block，默认值为"172.16.0.0/16"，用于指定VPC的CIDR块
variable "vpc_cidr_block" {
  default = "172.16.0.0/16"
}

# 定义一个变量vsw_cidr_block，默认值为"172.16.0.0/24"，用于指定VSwitch的CIDR块
variable "vsw_cidr_block" {
  default = "172.16.0.0/24"
}

variable "os_name" {
  type    = string
  default = "Alibaba Cloud Linux 3.*64*"
}

variable "password" {
  type    = string
  default = "12345678"
}

variable "cpu_core_count" {
  type    = number
  default = 2
}

variable "memory_size" {
  type    = number
  default = 4096
}

variable "system_disk_size" {
  type    = number
  default = 40
}

variable "instance_count" {
  type    = number
  default = 1
}

variable "spot_max_price" {
  type    = number
  default = 0.2
}
