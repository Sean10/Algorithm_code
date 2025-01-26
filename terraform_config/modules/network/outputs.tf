# VPC 网络信息
output "vpc_info" {
  description = "VPC 信息"
  value = {
    vpc_id      = tencentcloud_vpc.main.id
    vpc_cidr    = tencentcloud_vpc.main.cidr_block
    vpc_name    = tencentcloud_vpc.main.name
  }
}

# 子网信息
output "subnet_info" {
  description = "子网信息"
  value = {
    subnet_id   = tencentcloud_subnet.main.id
    subnet_cidr = tencentcloud_subnet.main.cidr_block
    subnet_name = tencentcloud_subnet.main.name
  }
}

# 输出CVM可用区信息
output "cvm_zones" {
  description = "CVM 可用区列表"
  value = data.tencentcloud_availability_zones_by_product.cvm_zones.zones
}

# 输出VPC可用区信息
output "vpc_zones" {
  description = "VPC 可用区列表"
  value = data.tencentcloud_availability_zones_by_product.vpc_zones.zones
}

# 输出VPC ID
output "vpc_id" {
  value = tencentcloud_vpc.main.id
}

# 输出VPC CIDR
output "vpc_cidr" {
  value = tencentcloud_vpc.main.cidr_block
} 