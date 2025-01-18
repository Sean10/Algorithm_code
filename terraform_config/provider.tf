terraform {
  required_providers {
    tencentcloud = {
      source = "tencentcloudstack/tencentcloud"
      # 通过version指定版本；若不指定，默认为最新版本
      # version = ">=1.81.60"
    }
  }
}

provider "tencentcloud" {
  region = "ap-shanghai"
  # AKSK已通过插件设置，无需在这里配置
}