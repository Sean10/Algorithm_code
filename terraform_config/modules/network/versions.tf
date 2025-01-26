terraform {
  required_providers {
    tencentcloud = {
      source = "tencentcloudstack/tencentcloud"
      version = ">= 1.81.0"
      configuration_aliases = [ tencentcloud ]
    }
  }
} 