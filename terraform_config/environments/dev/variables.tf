variable "region" {
  description = "腾讯云区域"
  type        = string
}

variable "environment" {
  description = "环境名称"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "VPC CIDR 块"
  type        = string
}

variable "subnet_cidr" {
  description = "子网 CIDR 块"
  type        = string
}

variable "cpu_cores" {
  description = "CPU核心数"
  type        = number
  default     = 1
}

variable "memory_size" {
  description = "内存大小(GB)"
  type        = number
  default     = 2
}

variable "instance_charge_type" {
  description = "实例计费类型"
  type        = string
}

variable "spot_max_price" {
  description = "竞价实例最高价格"
  type        = string
}

variable "system_disk_size" {
  description = "系统盘大小(GB)"
  type        = number
}

variable "region_priority" {
  description = "区域优先级列表"
  type        = list(string)
  default     = ["ap-shanghai", "ap-nanjing", "ap-hangzhou", "ap-guangzhou"]
}

variable "availability_zone" {
  description = "可用区"
  type        = string
  default     = null  # 设置为null，将根据region动态选择可用区
} 