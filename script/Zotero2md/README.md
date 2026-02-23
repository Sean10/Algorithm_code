# Zotero2md

将 Zotero storage 目录下的 PDF/HTML 文件转换为 Markdown，并可选地附加到 Zotero 条目。

## 功能

- 将 PDF/HTML 文件转换为 Markdown
- 提取 Base64 图片为独立文件
- 支持并发处理
- 可将转换后的 MD 文件附加到对应的 Zotero 条目（使用 linked_file 模式）

## 安装

```bash
# 安装依赖
pip install pyzotero

# 确保 Docker 已安装并运行 markitdown 镜像
docker pull sean10/markitdown
```

## 使用方法

### 基本转换

```bash
# 转换当前目录
python3 convert.py

# 指定目录
python3 convert.py /path/to/storage

# 指定并发数
python3 convert.py /path/to/storage -c 5

# 指定文件扩展名
python3 convert.py /path/to/storage -e .pdf .html .docx
```

### Zotero 关联

首次使用需要配置 Zotero API：

1. **获取 API Key**: 访问 https://www.zotero.org/settings/keys/new
   - 创建新 Key，确保勾选 "Write" 权限

2. **获取用户 ID**: 在 Zotero 中 `编辑 > 首选项 > 同步` 查看

```bash
# Dry-run 测试（显示关联信息，不实际附加）
python3 convert.py /path/to/storage -z --dry-run \
  --zotero-api-key "YOUR_API_KEY" \
  --zotero-user-id "YOUR_USER_ID"

# 实际附加到 Zotero
python3 convert.py /path/to/storage -z \
  --zotero-api-key "YOUR_API_KEY" \
  --zotero-user-id "YOUR_USER_ID"
```

### 跳过转换，仅附加已存在的 MD 文件

如果已经转换过，需要重新附加到 Zotero：

```bash
# Dry-run 测试
python3 convert.py /path/to/storage --attach-only -z --dry-run \
  --zotero-api-key "YOUR_API_KEY" \
  --zotero-user-id "YOUR_USER_ID"

# 实际附加
python3 convert.py /path/to/storage --attach-only -z \
  --zotero-api-key "YOUR_API_KEY" \
  --zotero-user-id "YOUR_USER_ID"
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `directory` | 要遍历的目录 | 当前目录 |
| `-c, --concurrency` | 并发数 | 3 |
| `-i, --image` | Docker 镜像 | sean10/markitdown |
| `-e, --extensions` | 文件扩展名 | .html .pdf |
| `-v, --verbose` | 显示详细输出 | 关闭 |
| `--no-extract-images` | 不提取图片 | 开启 |
| `-z, --zotero` | 附加到 Zotero | 关闭 |
| `--attach-only` | 仅附加已存在的 MD 文件 | 关闭 |
| `--zotero-api-key` | Zotero API Key | - |
| `--zotero-user-id` | Zotero 用户 ID | - |
| `--dry-run` | 不实际执行，仅显示信息 | 关闭 |
| `-l, --limit` | 限制处理文件数量 | 不限制 |

## Zotero 本地模式说明

- 使用 `--dry-run` 时，会通过本地 API 读取条目标题（需要 Zotero 运行）
- 实际附加时使用 Web API，需要 API Key
- 附件使用 `linked_file` 模式，保持原文件路径不变

## 注意事项

- 确保 Zotero 已启动且已启用本地 API（设置 > 高级 > 允许其他应用程序与此计算机上的 Zotero 通信）
- linked_file 模式会在 Zotero 中创建一个指向原文件的链接，文件本身不移动
