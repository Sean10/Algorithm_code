# 查询CVM产品可用区
data "tencentcloud_availability_zones_by_product" "cvm_zones" {
  product = "cvm"
}

# 查询VPC产品可用区
data "tencentcloud_availability_zones_by_product" "vpc_zones" {
  product = "vpc"
}

# 输出CVM可用区信息
output "cvm_zones" {
  value = data.tencentcloud_availability_zones_by_product.cvm_zones.zones
}

# 输出CVM可用区名称列表
output "cvm_zone_names" {
  value = data.tencentcloud_availability_zones_by_product.cvm_zones.zones[*].name
}

# 输出VPC可用区信息
output "vpc_zones" {
  value = data.tencentcloud_availability_zones_by_product.vpc_zones.zones
}

# 输出VPC可用区名称列表
output "vpc_zone_names" {
  value = data.tencentcloud_availability_zones_by_product.vpc_zones.zones[*].name
} 