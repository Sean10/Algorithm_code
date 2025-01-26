terraform {
  required_version = ">= 1.0.0"
  
  required_providers {
    tencentcloud = {
      source = "tencentcloudstack/tencentcloud"
      version = ">= 1.81.0"
    }
  }
  
  backend "local" {
    path = "terraform.tfstate"
  }
}

locals {
  # 如果指定了region，就使用指定的region，否则使用优先级列表中的第一个可用region
  selected_region = var.region != "" ? var.region : var.region_priority[0]
  
  # 定义支持的区域列表
  supported_regions = toset([
    "ap-shanghai",
    "ap-guangzhou",
    "ap-beijing"
  ])

  # 验证选择的region是否在支持列表中
  validate_region = (
    contains(local.supported_regions, local.selected_region) 
    ? local.selected_region 
    : file("ERROR: Selected region ${local.selected_region} is not supported. Supported regions are: ${join(", ", local.supported_regions)}")
  )
}

module "network" {
  source = "../../modules/network"

  providers = {
    tencentcloud = tencentcloud.shanghai
  }

  environment      = var.environment
  region          = local.selected_region
  availability_zone = var.availability_zone

  vpc_cidr    = "10.0.0.0/16"
  subnet_cidr = "10.0.1.0/24"
}

module "compute" {
  source = "../../modules/compute"

  providers = {
    tencentcloud = tencentcloud.shanghai
  }

  environment      = var.environment
  region          = local.selected_region
  availability_zone = var.availability_zone
  vpc_id          = module.network.vpc_id
  subnet_id       = module.network.subnet_info.subnet_id
  instance_name   = "${var.environment}-cvm"

  cpu_core_count      = var.cpu_cores
  memory_size         = var.memory_size
  instance_charge_type = var.instance_charge_type
  spot_max_price      = var.spot_max_price
  system_disk_size    = var.system_disk_size
} 