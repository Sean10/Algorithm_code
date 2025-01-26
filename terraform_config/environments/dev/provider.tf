# 默认provider配置
provider "tencentcloud" {
  region = var.region
}

# 为不同区域创建provider配置
provider "tencentcloud" {
  alias  = "shanghai"
  region = "ap-shanghai"
}

provider "tencentcloud" {
  alias  = "guangzhou"
  region = "ap-guangzhou"
}

provider "tencentcloud" {
  alias  = "beijing"
  region = "ap-beijing"
}