variable "availability_zone" {
  default = "ap-shanghai-5"
}

data "tencentcloud_images" "images" {
  image_type       = ["PUBLIC_IMAGE"]
  image_name_regex = "OpenCloudOS Server"
}

data "tencentcloud_instance_types" "types" {
  filter {
    name   = "instance-family"
    values = ["S1", "S2", "S3", "S4", "S5", "S6", "SA2", "SA3"]
  }

  cpu_core_count   = 2
  exclude_sold_out = true
}

// create vpc
resource "tencentcloud_vpc" "vpc" {
  cidr_block = "10.0.0.0/16"
  name       = "vpc"
}

// create subnet
resource "tencentcloud_subnet" "subnet" {
  vpc_id            = tencentcloud_vpc.vpc.id
  availability_zone = var.availability_zone
  name              = "subnet"
  cidr_block        = "10.0.1.0/24"
}

// create CVM instance
resource "tencentcloud_instance" "cvm" {
  instance_name     = "tf-example"
  instance_charge_type = "SPOTPAID"
  spot_instance_type = "ONE-TIME"
  spot_max_price = 0.06
  availability_zone = var.availability_zone
  image_id          = data.tencentcloud_images.images.images.0.image_id
  instance_type     = data.tencentcloud_instance_types.types.instance_types.0.instance_type
  system_disk_type  = "CLOUD_PREMIUM"
  system_disk_size  = 50
  hostname          = "sean10"
  project_id        = 0
  vpc_id            = tencentcloud_vpc.vpc.id
  subnet_id         = tencentcloud_subnet.subnet.id

  data_disks {
    data_disk_type = "CLOUD_PREMIUM"
    data_disk_size = 50
    encrypt        = false
  }

  tags = {
    tagKey = "tagValue"
  }
}