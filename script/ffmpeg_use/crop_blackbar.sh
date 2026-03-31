#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# crop_blackbar.sh — 批量裁剪会议截图黑边
# ============================================================

IMAGE="zsj439453290/alpine-node-ffmpeg:macos-arm64"
PROJECT="$(cd "$(dirname "$0")" && pwd)"

# ------------------------------------------------------------
# 1. Docker 环境检查
# ------------------------------------------------------------

# 1.1 检查 docker 命令是否可用
if ! command -v docker &>/dev/null; then
  echo "错误：未找到 docker 命令，请先安装 Docker。" >&2
  exit 1
fi

# 1.2 检查 Docker 服务是否运行
if ! docker info &>/dev/null; then
  echo "错误：Docker 服务未运行，请先启动 Docker。" >&2
  exit 1
fi

# 1.3 检查镜像是否已拉取，若不存在则自动 pull
if ! docker image inspect "${IMAGE}" &>/dev/null; then
  echo "镜像 ${IMAGE} 不存在，正在拉取..."
  docker pull "${IMAGE}"
fi

# ------------------------------------------------------------
# 2. 输出目录初始化与输入校验
# ------------------------------------------------------------

# 2.1 检查并创建 output/ 目录
if [ ! -d "${PROJECT}/output" ]; then
  echo "output/ 目录不存在，正在创建..."
  mkdir -p "${PROJECT}/output"
fi

# 2.2 确保 output/ 目录可写
if [ ! -w "${PROJECT}/output" ]; then
  echo "错误：output/ 目录不可写，请检查权限。" >&2
  exit 1
fi

# 2.3 检查 data/ 下是否存在 JPG 文件（不区分大小写）
shopt -s nullglob
jpg_files=("${PROJECT}/data"/*.jpg "${PROJECT}/data"/*.JPG)
shopt -u nullglob

if [ ${#jpg_files[@]} -eq 0 ]; then
  echo "错误：data/ 目录下未找到任何 JPG 文件，请确认输入文件已就位。" >&2
  exit 1
fi

# ------------------------------------------------------------
# 3. 单张图片方向探测（容器内 ffprobe）
# ------------------------------------------------------------

# 返回 "portrait" 或 "landscape"
detect_orientation() {
  local filename="$1"
  local dimensions

  dimensions=$(docker run --rm \
    -v "${PROJECT}/data:/work/data:ro" \
    "${IMAGE}" \
    ffprobe -v error -select_streams v:0 \
      -show_entries stream=width,height \
      -of csv=p=0 "/work/data/${filename}")

  local width height
  IFS=',' read -r width height <<< "${dimensions}"

  if [ "${height}" -gt "${width}" ]; then
    echo "portrait"
  else
    echo "landscape"
  fi
}

# ------------------------------------------------------------
# 4. 单张图片裁剪（容器内 ffmpeg）
# ------------------------------------------------------------

# 返回 0 表示成功，非零表示失败（不退出整个脚本）
crop_image() {
  local filename="$1"
  local orientation crop_params

  orientation=$(detect_orientation "${filename}")

  if [ "${orientation}" = "portrait" ]; then
    crop_params="crop=1260:720:0:640"
  else
    crop_params="crop=2334:1260:227:0"
  fi

  if docker run --rm \
    -v "${PROJECT}/data:/work/data:ro" \
    -v "${PROJECT}/output:/work/output" \
    -w /work \
    "${IMAGE}" \
    ffmpeg -hide_banner -y \
      -i "/work/data/${filename}" \
      -vf "${crop_params}" \
      -frames:v 1 -q:v 2 -update 1 \
      "/work/output/${filename}"; then
    return 0
  else
    echo "错误：裁剪失败 [${filename}]，方向=${orientation}，crop=${crop_params}" >&2
    return 1
  fi
}

# ------------------------------------------------------------
# 5. 主循环：遍历、进度输出与结果汇总
# ------------------------------------------------------------

jpg_files=()
while IFS= read -r line; do
  jpg_files+=("$line")
done < <(find "${PROJECT}/data" -maxdepth 1 -iname "*.jpg" | sort)
total=${#jpg_files[@]}

if [ "${total}" -eq 0 ]; then
  echo "错误：data/ 目录下未找到任何 JPG 文件。" >&2
  exit 1
fi

success=0
fail=0
current=0

for filepath in "${jpg_files[@]}"; do
  filename=$(basename "${filepath}")
  current=$((current + 1))
  echo "[${current}/${total}] 正在处理: ${filename}"

  if crop_image "${filename}"; then
    success=$((success + 1))
  else
    fail=$((fail + 1))
  fi
done

echo ""
echo "处理完成：成功 ${success} 张，失败 ${fail} 张"

if [ "${fail}" -gt 0 ]; then
  exit 1
fi
