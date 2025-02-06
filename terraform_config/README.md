# Terraform腾讯云ECS开发环境快速搭建

本项目使用 Terraform 管理腾讯云基础设施配置

## 功能

* 通过cpu/内存筛选指定可用区下最低价格的竞价实例并部署
* 增加一个instance查询时的架构选项, 如果没有设置时, 自动按照最低价的来


## 目录结构

```
.
├── environments/          # 环境特定配置
│   ├── dev/              # 开发环境
│   ├── staging/          # 预发环境
│   └── prod/             # 生产环境
├── modules/              # 可重用的基础设施模块
│   ├── network/          # 网络相关配置
│   └── compute/          # 计算资源相关配置
└── global/              # 全局配置
    └── provider.tf      # 提供商配置
```

## 使用方法

1. 初始化项目（以开发环境为例）：
```bash
cd environments/dev
# 修改terraform.tfvars中的变量

terraform init
```

2. 查看变更计划：
```bash
terraform plan
```

3. 应用变更：
```bash
terraform apply
```

## 模块说明

### 网络模块 (modules/network)
- VPC 配置
- 可用区查询
- 子网配置

### 计算模块 (modules/compute)
- CVM 实例配置
- 安全组配置

## 环境配置

每个环境目录（dev/staging/prod）包含：
- `main.tf`: 主配置文件
- `variables.tf`: 变量定义
- `terraform.tfvars`: 环境特定的变量值（需要手动创建）

## 注意事项

1. 敏感信息（如密钥）不要提交到版本控制
2. 每个环境使用独立的状态文件
3. 在应用更改前务必先查看计划（terraform plan）

# 环境

参照[tencentcloudstack/terraform\-provider\-tencentcloud: Terraform Tencent Cloud Provider](https://github.com/tencentcloudstack/terraform-provider-tencentcloud), 进行腾讯云插件安装

```
brew tap hashicorp/tap
brew install terraform

mkdir -p $GOPATH/src/github.com/tencentcloudstack
cd $GOPATH/src/github.com/tencentcloudstack
git clone https://github.com/tencentcloudstack/terraform-provider-tencentcloud.git
cd terraform-provider-tencentcloud
go build .

cd terraform_config
source .env

terraform init
terraform plan
terraform apply
terraform destroy
```
# 使用自定义修改后的provider

[Sean10/terraform\-provider\-tencentcloud at SPOTPAID](https://github.com/Sean10/terraform-provider-tencentcloud/tree/SPOTPAID)

``` bash
Users=$(whoami)
cd /Users/${Users}/Code/
git clone https://github.com/Sean10/terraform-provider-tencentcloud.git
cd terraform-provider-tencentcloud
go build .

vim ~/.terraformrc
```

添加下述内容

```
provider_installation {
  dev_overrides {
    "registry.terraform.io/tencentcloudstack/tencentcloud" = "/Users/${Users}/Code/terraform-provider-tencentcloud"
  }
  # 对于其他源保持默认安装方式
  direct {}
}

```

# TODO

- [ ] 如何才能在创建后自动设置免密? 并联动触发ansible等步骤?
    目前初步看, 最好是让terraform完成免密后, 后续动作由独立的ansible进行
    其次, 有些需固化的内容则持久化成镜像, 后续直接启动.
- [ ] 把terraform和ansible, ssh等联动模块都装上
- [ ] 如何将terraform.tfstate进行持久化保存?
- [ ] 如何在创建前, 通过查询价格寻找可用区? 毕竟有的0.4, 有的0.01
    DescribeInstancesSellTypeByFilter 这个API疑似可以起到效果, 但是没有封装terraform
        主要参考[云服务器 获取可用区机型配置信息\-实例相关接口\-API 中心\-腾讯云](https://cloud.tencent.com/document/api/213/17378)这里的接口输出, 在provider的sdk输出中进行封装调用
        成功使用UnitPriceDiscount查到了价格
    使用腾讯云控制台的竞价实例价格查询功能。
    如果您需要在 Terraform 中自动化这个过程，您可以：
    创建一个自定义的数据源
    使用 local-exec provisioner 调用腾讯云 CLI 来获取价格信息
    使用外部数据源（external data source）来集成您自己的脚本

    但是竞价实例价格,好像本身是运行时变化, 即后续涨价完全有可能. 直到超出预算, 这个可能可以配置告警?
- [ ] 持久化存储, 用什么比较好? 腾讯云30g/月, cos也要4元+, 实际闲置时间比较久.
    * CFS的按量付费, 可能对于短期比较省事?
* [ ] 需要清理多余的安装providerd呃动作.
* 根据输入的os_name, 自动查询其中的镜像, 从available_images.json中选择更详细的os名字更新到筛选列表中
* 增加单独的检测竞价实例状态脚本, 每分钟检测, 一旦检测到即将释放, 主动触发打包压缩, 上传cos.