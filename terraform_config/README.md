

# 环境

参照[tencentcloudstack/terraform\-provider\-tencentcloud: Terraform Tencent Cloud Provider](https://github.com/tencentcloudstack/terraform-provider-tencentcloud), 进行腾讯云插件安装

```
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

# TODO

- [ ] 如何才能在创建后自动设置免密? 并联动触发ansible等步骤?
- [ ] 如何将terraform.tfstate进行持久化保存?
- [ ] 持久化存储, 用什么比较好? 腾讯云30g/月, cos也要4元+, 实际闲置时间比较久.
    * CFS的按量付费, 可能对于短期比较省事?