terraform {
  required_providers {
    aliyun = {
      source  = "aliyun/alicloud"
    #   version = "~> 1.246.0"
    }
  }
}

provider "alicloud" {
#   region     = var.region
#   access_key = var.access_key
#   secret_key = var.secret_key
}