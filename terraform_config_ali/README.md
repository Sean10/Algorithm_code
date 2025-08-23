# Terraform阿里云ECS开发环境快速搭建

本项目使用 Terraform 管理阿里云基础设施配置

## 功能

* 创建本地nvme盘的实例
* 创建RDMA实例



# 环境


``` bash
brew tap hashicorp/tap
brew install terraform



cd terraform_config_ali
source .env

terraform init

# 申请本地nvme设备
bash -x deploy.sh local_nvme
# 申请多台RDMA网卡的设备
# bash -x deploy.sh RDMA


# 清理
bash -x cleanup.sh local_nvme
# bash -x cleanup.sh RDMA

```

# 待办
* 默认没返回价格, 得单独查询, 疑似和腾讯云一样? terraform的provider中没有默认输出.