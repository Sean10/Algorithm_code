# 安装
``` bash
docker build --network=host -t centos-base-ceph .

docker build --network=host -t centos-ceph-clion -f Dockerfile_clion .

docker run --name ssh_centos --privileged=true --cap-add sys_ptrace -p127.0.0.1:2222:22 -it -v /Users/sean10/Code/ceph/master/ceph:/ceph  centos-ceph-clion /bin/bash
```

# 将容器作为镜像
``` bash
docker commit -m "add sshd" [containerid] [new_imagename]

docker commit a80121793748 sean10/centos_ceph_clion
docker push sean10/centos_ceph_clion
docker run --name centos_ceph_clion --privileged=true --cap-add sys_ptrace -p127.0.0.1:2222:22 -it -v /Users/sean10/Code/ceph/master/ceph:/ceph  sean10/centos_ceph_clion /bin/bash

# sean用户的默认密码 Fighton

docker commit 62aa128c8711 sean10/centos_ceph_clion:v1.0 
# 这个版本是刚刚clion index完的版本, 东西都存在了/home/sean/ceph里
这个镜像里已经enable了sshd, 且改成了我自己的sshd配置方式
用下面这个运行就可以了
docker run --name centos_ceph_clion --privileged=true --cap-add sys_ptrace -p127.0.0.1:2222:22 -it sean10/centos_ceph_clion:v1.0  /usr/sbin/init


```

## 运行
``` bash
docker run --name test_centos --privileged=true --cap-add sys_ptrace -p127.0.0.1:2222:22 -it -v /Users/sean10/Code/ceph/master/ceph:/ceph  centos-base-ceph:latest /bin/bash


# Build and run:
#   docker build -t clion/centos7-cpp-env:0.1 -f Dockerfile.centos7-cpp-env .
#   docker run -d --cap-add sys_ptrace -p127.0.0.1:2222:22 clion/centos7-cpp-env:0.1
#   ssh-keygen -f "$HOME/.ssh/known_hosts" -R "[localhost]:2222"
#
# stop:
#   docker stop clion_remote_env
# 
# ssh credentials (test user):
#   user@password 
```

# 和clion联调
[Using Docker with CLion \| The CLion Blog](https://blog.jetbrains.com/clion/2020/01/using-docker-with-clion/)

主要就是参照上面这篇博客操作即可.


# 存在的问题
## 不存在systemd进程,无法启动
``` bash
[root@a80121793748 /]# systemctl
Failed to get D-Bus connection: Operation not permitted
```

