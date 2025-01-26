# 查询CVM产品可用区
data "tencentcloud_availability_zones_by_product" "cvm_zones" {
  product = "cvm"
}

# 查询VPC产品可用区
data "tencentcloud_availability_zones_by_product" "vpc_zones" {
  product = "vpc"
}

locals {
  # 如果没有指定可用区，则使用第一个可用的区域
  selected_zone = var.availability_zone != null ? var.availability_zone : data.tencentcloud_availability_zones_by_product.vpc_zones.zones[0].name
}

# VPC 配置
resource "tencentcloud_vpc" "main" {
  name         = "${var.environment}-vpc"
  cidr_block   = var.vpc_cidr
  is_multicast = false

  tags = {
    environment = var.environment
  }
}

# 子网配置
resource "tencentcloud_subnet" "main" {
  name              = "${var.environment}-subnet"
  vpc_id            = tencentcloud_vpc.main.id
  cidr_block        = var.subnet_cidr
  availability_zone = local.selected_zone
  is_multicast      = false

  tags = {
    environment = var.environment
  }
} 