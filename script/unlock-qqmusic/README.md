

# 使用方式


## 方案1(仅限windows)
使用frida 注入dll解密, qqmusic_decrypt等等就是这个方案

## 方案2(仅限2023年及以前的qq音乐版本, 最后没屏蔽成功强制升级的弹窗)
7.9.1 mac版本
链接: https://pan.baidu.com/s/1H31TWrToAo6ZBzg5foFc6w  密码: vqve

``` bash

docker run --name unlock-music -d -p 18180:80 bananice1999/unlock-music:20241122
```

浏览器打开 http://localhost:18180  ,选中自动保存到指定目录, 然后 批量上传指定目录mgg文件即可
