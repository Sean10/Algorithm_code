# 会议截图去黑边批量裁剪

批量裁剪手机会议截图中的黑边，通过 Docker 容器内的 ffmpeg 处理，宿主机无需安装 ffmpeg。

## 背景

手机截屏的会议投屏画面上下（竖屏）或左右（横屏）存在大量黑边，且顶部状态栏含有时间、信号、电量等有色内容，无法用自动黑边检测准确识别。本脚本采用固化裁剪参数方案，按图片方向直接套用对应参数批量处理。

## 前置要求

- macOS（arm64）
- Docker 已安装并运行
- `data/` 目录下放置待处理的 JPG 截图

## 目录结构

```
.
├── crop_blackbar.sh   # 批量裁剪脚本
├── data/              # 输入：原始截图（JPG）
└── output/            # 输出：裁剪后图片（自动创建）
```

## 使用方法

```bash
chmod +x crop_blackbar.sh
./crop_blackbar.sh
```

脚本会自动：
1. 检查 Docker 环境，镜像不存在时自动拉取
2. 创建 `output/` 目录
3. 对每张图片用容器内 ffprobe 判断方向，再用 ffmpeg 裁剪
4. 输出处理进度和最终成功/失败统计

## 裁剪参数

| 方向 | 判断条件 | crop 参数 | 输出尺寸 |
|------|----------|-----------|----------|
| 竖屏 portrait | height > width | `crop=1260:720:0:640` | 1260×720 |
| 横屏 landscape | width ≥ height | `crop=2334:1260:227:0` | 2334×1260 |

## Docker 镜像

`zsj439453290/alpine-node-ffmpeg:macos-arm64`

所有 ffmpeg / ffprobe 命令均在容器内执行，通过卷挂载读写 `data/` 和 `output/`。
