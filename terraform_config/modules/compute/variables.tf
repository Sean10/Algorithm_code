variable "environment" {
  description = "环境名称"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_id" {
  description = "子网 ID"
  type        = string
}

variable "availability_zone" {
  description = "可用区"
  type        = string
  default     = ""
}

variable "region" {
  description = "腾讯云地域"
  type        = string
  default     = ""  # 默认为空，将使用region_priority中的第一个地域
}

variable "instance_name" {
  description = "实例名称"
  type        = string
}

variable "cpu_core_count" {
  description = "需要的CPU核心数"
  type        = number
  default     = 1
}

variable "memory_size" {
  description = "需要的内存大小(GB)"
  type        = number
  default     = 2
}

variable "instance_type" {
  description = "实例类型，如果指定则使用指定类型，否则根据CPU和内存需求自动选择"
  type        = string
  default     = null
}

variable "os_name" {
  description = "操作系统名称，例如：centos、ubuntu等"
  type        = string
  default     = "ubuntu"
}

variable "image_id" {
  description = "镜像 ID"
  type        = string
  default     = "img-487zeit5" # Ubuntu 20.04
}

variable "password" {
  description = "密码"
  type        = string
}

variable "instance_charge_type" {
  description = "实例计费类型"
  type        = string
  default     = "SPOTPAID"  # 竞价付费
}

variable "spot_max_price" {
  description = "竞价实例最高价格"
  type        = string
  default     = "0.1"
}

variable "system_disk_type" {
  description = "系统盘类型"
  type        = string
  default     = "CLOUD_PREMIUM"
}

variable "system_disk_size" {
  description = "系统盘大小(GB)"
  type        = number
  default     = 40
}
