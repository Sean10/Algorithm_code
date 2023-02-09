#!/bin/python3
#
# 用于清理掉keepalived.conf配置中残留的配置
#
import re

with open("keepalived.conf", "r") as f:
        content = f.read()


result = re.sub(r"vrrp_instance VI_CEPH[^}]+}[^}]+}[^}]+}[^}]+}",  '', content)
result = re.sub(r"vrrp_script check_ceph[^}]+}",  '', result)
result = re.sub(r",?VI_CEPH,?", "", result)

with open('new.conf', "w") as f:
        f.write(result)
