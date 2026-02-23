#!/usr/bin/env python3
"""
递归遍历目录下的 HTML 和 PDF 文件，使用 markitdown docker 转换为 Markdown。
支持并发处理。
支持提取 base64 图片到独立文件。
"""

import argparse
import base64
import hashlib
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from pyzotero import Zotero
    PYZOTERO_AVAILABLE = True
except ImportError:
    PYZOTERO_AVAILABLE = False


def extract_and_save_images(md_path: Path, content: str) -> tuple[str, int]:
    """
    从 markdown 内容中提取 base64 图片并保存到独立文件。
    使用 discussion #269 中的方案。
    """
    media_dir = md_path.parent / md_path.stem  # 例如: 6epHYEsnEkw.md -> 6epHYEsnEkw/
    media_dir.mkdir(exist_ok=True)

    count = 0

    # 匹配 base64 图片的正则 (来自 discussion #269)
    base64_pattern = r'data:image/([a-zA-Z0-9]+);base64,([a-zA-Z0-9+/]+={0,2})'

    def replace_match(match):
        nonlocal count
        image_format = match.group(1)  # png, jpeg, gif 等
        base64_data = match.group(2)    # base64 编码的数据

        # 生成文件名
        ext = f'.{image_format}'
        name_hash = hashlib.md5(base64_data[:100].encode()).hexdigest()[:8]
        filename = f"{name_hash}_{count}{ext}"
        filepath = media_dir / filename

        try:
            # 解码并保存图片
            image_data = base64.b64decode(base64_data)
            filepath.write_bytes(image_data)

            count += 1
            # 返回本地相对路径引用
            return f'{md_path.stem}/{filename}'
        except Exception as e:
            print(f"  [警告] 保存图片失败: {filename}, {e}")
            return match.group(0)  # 保留原始内容

    # 替换所有 data:image/xxx;base64,xxx 模式
    new_content = re.sub(base64_pattern, replace_match, content)

    return new_content, count


def convert_file(file_path: Path, docker_image: str, extract_images: bool) -> tuple[str, bool, str, Path, str]:
    """转换单个文件，返回 (文件名, 是否成功, 消息, md_path, parent_key)"""
    md_path = file_path.with_suffix('.md')
    parent_key = file_path.parent.name  # Zotero 条目 key (目录名)

    try:
        with open(file_path, 'rb') as f:
            result = subprocess.run(
                ['docker', 'run', '--rm', '-i', docker_image, '--keep-data-uris'],
                stdin=f,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False
            )

        if result.returncode == 0:
            content = result.stdout.decode('utf-8', errors='replace')

            # 提取并保存图片
            image_count = 0
            if extract_images:
                content, image_count = extract_and_save_images(md_path, content)

            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)

            msg = f"成功 -> {md_path}"
            if image_count > 0:
                msg += f" (含 {image_count} 个图片)"
            return (str(file_path), True, msg, md_path, parent_key)
        else:
            error_msg = result.stderr.decode('utf-8', errors='replace')
            return (str(file_path), False, f"失败: {error_msg[:200]}", md_path, parent_key)

    except Exception as e:
        return (str(file_path), False, f"异常: {str(e)}", md_path, parent_key)


def find_files(directory: Path, extensions: list[tuple[Path, str]]):
    """递归查找指定扩展名的文件，返回 (file_path, parent_key) 列表"""
    files = []
    for ext in extensions:
        for file_path in directory.rglob(f'*{ext}'):
            parent_key = file_path.parent.name
            files.append((file_path, parent_key))
    return sorted(files, key=lambda x: x[0])


def get_zotero_item_info(item_key: str) -> dict | None:
    """获取 Zotero 条目信息，返回 (title, parent_key, is_attachment)"""
    if not PYZOTERO_AVAILABLE:
        return None
    try:
        # 本地模式用于读取
        zot = Zotero(0, 'user', None, local=True)
        item = zot.item(item_key)
        if not item:
            return None
        data = item.get('data', {})
        item_type = data.get('itemType', '')
        is_attachment = item_type in ('attachment', 'snapshot', 'note')

        # 如果是附件，获取父条目
        parent_key = data.get('parentItem', '')

        title = data.get('title', '')
        if not title:
            title = data.get('filename', '')

        return {
            'title': title,
            'parent_key': parent_key,
            'is_attachment': is_attachment,
            'item_type': item_type,
            'data': data
        }
    except Exception:
        pass
    return None


def get_collection_path(zot, collection_key: str) -> str:
    """获取 collection 的完整路径"""
    try:
        collection = zot.collection(collection_key)
        if not collection:
            return ""
        data = collection.get('data', {})
        name = data.get('name', '')
        # 尝试获取父 collection
        parent = data.get('parent', '')
        if parent:
            parent_path = get_collection_path(zot, parent)
            if parent_path:
                return f"{parent_path}/{name}"
        return name
    except Exception:
        return ""


def delete_original_attachment(zot, item_key: str, file_path: str, item_version: int) -> tuple[bool, str]:
    """删除原始 html 条目和磁盘文件"""
    file_deleted = False
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            file_deleted = True
    except Exception as e:
        print(f"  [调试] 删除文件失败: {e}")

    # pyzotero 的 @backoff_check 装饰器: 成功返回 True, 失败抛异常
    try:
        zot.delete_item({"key": item_key, "version": item_version})
        msg = f"已删除条目 {item_key}"
        if file_deleted:
            msg += " 和文件"
        return True, msg
    except Exception as e:
        print(f"  [调试] delete_item 异常: {type(e).__name__}: {e}")
        if file_deleted:
            return True, f"已删除文件，但 Zotero 条目删除失败: {e}"
        return False, f"删除失败: {e}"


def migrate_attachments(args):
    """迁移模式：通过API列出条目，转换附件并创建linked_file"""
    if not PYZOTERO_AVAILABLE:
        print("错误: pyzotero 未安装，请运行: pip install pyzotero")
        sys.exit(1)

    if not args.zotero_api_key or not args.zotero_user_id:
        print("错误: 迁移模式需要 --zotero-api-key 和 --zotero-user-id 参数")
        print("       获取 API Key: https://www.zotero.org/settings/keys")
        print("       用户 ID 在: 编辑 > 首选项 > 同步")
        sys.exit(1)

    # 基础路径
    base_path = Path("/Users/sean10/Dropbox/workspace_ln/obsidian/zotero_collection")

    # 本地模式：快速读取所有条目信息
    print("从本地数据库获取所有条目...")
    zot_local = Zotero(0, 'user', None, local=True)
    all_items = zot_local.everything(zot_local.items())

    # 获取所有 collections 用于构建路径（本地）
    collections = zot_local.everything(zot_local.collections())
    collection_map = {}
    for col in collections:
        col_data = col.get('data', {})
        key = col_data.get('key', '')
        collection_map[key] = col_data

    # 过滤出包含 html/pdf 附件的条目
    attachments_to_migrate = []
    for item in all_items:
        data = item.get('data', {})
        item_type = data.get('itemType', '')
        content_type = data.get('contentType', '')
        link_mode = data.get('linkMode', '')

        # 只处理附件类型
        if item_type != 'attachment':
            continue

        # 检查是否为 html 或 pdf
        if content_type not in ('text/html', 'application/pdf'):
            continue

        # 获取父条目信息
        parent_key = data.get('parentItem', '')
        if not parent_key:
            continue

        # 获取父条目信息
        try:
            parent_item = zot_local.item(parent_key)
            if not parent_item:
                continue
            parent_data = parent_item.get('data', {})
            title = parent_data.get('title', 'untitled')
        except Exception:
            title = 'untitled'

        # 获取源文件路径
        # linked_file: path 是完整文件路径
        # imported_file/imported_url: 需要根据 collection 和 title 构建路径
        source_file_path = ""
        if link_mode == 'linked_file':
            source_file_path = data.get('path', '')
            # linked_file 的 path 可能是绝对路径或相对路径
            # 如果是相对路径，需要处理
            if source_file_path and not source_file_path.startswith('/'):
                # 相对路径，可能是 storage 路径，不适用新方案
                continue
        else:
            # imported_file/imported_url 模式，记录稍后构建路径
            source_file_path = None

        # 获取 collection 路径
        collections_data = parent_data.get('collections', [])
        collection_path = ""
        if collections_data:
            # 使用第一个 collection
            col_key = collections_data[0]
            col_data = collection_map.get(col_key, {})
            col_name = col_data.get('name', '')
            collection_path = col_name

        item_key = data.get('key', '')
        item_version = data.get('version', 0)
        attachments_to_migrate.append({
            'item_key': item_key,
            'item_version': item_version,
            'parent_key': parent_key,
            'title': title,
            'content_type': content_type,
            'collection_path': collection_path,
            'link_mode': link_mode,
            'source_path': source_file_path,  # linked_file 的路径，或 None 表示需要构建
            'data': data
        })

    # 处理重名情况：如果同一 stem 有多个文件，按类型添加后缀避免冲突
    # 先按 (collection_path, stem) 分组
    stem_groups = {}
    for att in attachments_to_migrate:
        # 先临时计算 stem
        if att['link_mode'] == 'linked_file' and att['source_path']:
            source_file = Path(att['source_path'])
        else:
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', att['title'])
            ext = '.html' if att['content_type'] == 'text/html' else '.pdf'
            source_file = Path(safe_title + ext)
        stem = source_file.stem
        key = (att['collection_path'], stem)
        if key not in stem_groups:
            stem_groups[key] = []
        stem_groups[key].append(att)

    # 为有多个文件的组分配后缀
    for key, atts in stem_groups.items():
        if len(atts) > 1:
            # 同一 stem 有多个文件，按类型分配后缀
            for i, att in enumerate(atts):
                if att['content_type'] == 'text/html':
                    att['_md_suffix'] = '_html'
                else:
                    att['_md_suffix'] = '_pdf'
        else:
            atts[0]['_md_suffix'] = ''

    print(f"找到 {len(attachments_to_migrate)} 个需要迁移的 html/pdf 附件")

    if not attachments_to_migrate:
        print("没有需要迁移的附件")
        return

    # 处理每个附件
    success_count = 0
    skip_count = 0
    fail_count = 0
    delete_count = 0
    delete_fail_count = 0

    # 初始化远程 API（用于创建 linked_file 和删除操作）
    zot_remote = Zotero(args.zotero_user_id, 'user', args.zotero_api_key)
    print("初始化远程 API 完成\n")

    for att in attachments_to_migrate:
        parent_key = att['parent_key']
        title = att['title']
        collection_path = att['collection_path']
        content_type = att['content_type']
        item_key = att['item_key']
        item_version = att.get('item_version', 0)
        link_mode = att['link_mode']
        source_path = att['source_path']

        # 获取源文件路径
        # linked_file: 直接使用 path 字段的路径
        # imported_file/imported_url: 根据 collection 和 title 构建
        if link_mode == 'linked_file' and source_path:
            source_file = Path(source_path)
            source_dir = source_file.parent
        else:
            if collection_path:
                source_dir = base_path / collection_path
            else:
                source_dir = base_path
            # 清理标题中的非法文件名字符
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
            ext = '.html' if content_type == 'text/html' else '.pdf'
            source_file = source_dir / f"{safe_title}{ext}"

        # 构建 md 文件路径（使用后缀避免重名冲突）
        md_suffix = att.get('_md_suffix', '')
        md_file = source_dir / f"{source_file.stem}{md_suffix}.md"

        print(f"\n[处理] {title}")
        print(f"  源文件: {source_file}")
        print(f"  MD 文件: {md_file}")

        # 检查源文件是否存在
        if not source_file.exists():
            print(f"  [跳过] 源文件不存在")
            skip_count += 1
            continue

        # 检查是否已存在 md linked_file（需单独请求 /children 接口，item 响应不含子项）
        try:
            children = zot_local.children(parent_key) or []

            # 查找是否已有 md linked_file
            has_md_linked = False
            for child in children:
                child_data = child.get('data', {})
                if child_data.get('itemType') == 'attachment':
                    child_link_mode = child_data.get('linkMode', '')
                    child_content_type = child_data.get('contentType', '')
                    child_path = child_data.get('path', '')
                    if child_link_mode == 'linked_file' and child_content_type == 'text/markdown':
                        if child_path.endswith('.md'):
                            has_md_linked = True
                            break
        except Exception as e:
            print(f"  [警告] 检查现有附件失败: {e}")
            has_md_linked = False

        if has_md_linked:
            print(f"  [跳过] 已存在 md linked_file")
            skip_count += 1
            continue

        # 转换文件
        if args.dry_run:
            print(f"  [DRY-RUN] 转换: {source_file} -> {md_file}")
            print(f"  [DRY-RUN] 创建 linked_file: {md_file}")
        else:
            # 使用现有的 convert_file 函数
            try:
                # 直接调用 markitdown
                with open(source_file, 'rb') as f:
                    result = subprocess.run(
                        ['docker', 'run', '--rm', '-i', args.image, '--keep-data-uris'],
                        stdin=f,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=False
                    )

                if result.returncode != 0:
                    error_msg = result.stderr.decode('utf-8', errors='replace')
                    print(f"  [失败] 转换失败: {error_msg[:200]}")
                    fail_count += 1
                    continue

                content = result.stdout.decode('utf-8', errors='replace')

                # 提取并保存图片
                image_count = 0
                if not args.no_extract_images:
                    content, image_count = extract_and_save_images(md_file, content)

                # 确保目录存在
                source_dir.mkdir(parents=True, exist_ok=True)

                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                msg = f"成功 -> {md_file}"
                if image_count > 0:
                    msg += f" (含 {image_count} 个图片)"
                print(f"  [OK] {msg}")
            except Exception as e:
                print(f"  [失败] 转换异常: {str(e)}")
                fail_count += 1
                continue

            # 创建 linked_file
            try:
                attachment_payload = {
                    'itemType': 'attachment',
                    'linkMode': 'linked_file',
                    'title': md_file.name,
                    'path': str(md_file),
                    'contentType': 'text/markdown',
                    'parentItem': parent_key
                }

                result = zot_remote.create_items([attachment_payload])
                if result and result.get('successful'):
                    print(f"  [OK] 已创建 linked_file")
                else:
                    print(f"  [失败] 创建 linked_file 失败: {result}")
                    fail_count += 1
                    continue
            except Exception as e:
                print(f"  [失败] 创建 linked_file 异常: {str(e)}")
                fail_count += 1
                continue

        success_count += 1

        # 删除原始 html 条目（可选）
        if args.delete_original and not args.dry_run:
            print(f"  [删除] 原始条目: {item_key}")
            delete_success, delete_msg = delete_original_attachment(zot_remote, item_key, str(source_file), item_version)
            if delete_success:
                print(f"  [OK] {delete_msg}")
                delete_count += 1
            else:
                print(f"  [失败] {delete_msg}")
                delete_fail_count += 1

    print("-" * 50)
    print(f"迁移完成:")
    print(f"  成功: {success_count}")
    print(f"  跳过: {skip_count}")
    print(f"  失败: {fail_count}")
    if args.delete_original:
        print(f"  删除: {delete_count}, 失败: {delete_fail_count}")


def attach_to_zotero(md_path: Path, item_key: str, api_key: str, user_id: str) -> tuple[bool, str]:
    """将 MD 文件附加到 Zotero 条目（使用 linked_file 模式保持原路径）"""
    if not PYZOTERO_AVAILABLE:
        return False, "pyzotero 未安装，请运行: pip install pyzotero"

    if not api_key or not user_id:
        return False, "需要 --zotero-api-key 和 --zotero-user-id 参数来上传附件"

    try:
        # 使用 Web API 模式上传附件
        zot = Zotero(user_id, 'user', api_key)

        # 验证条目是否存在
        try:
            item = zot.item(item_key)
            if not item:
                return False, f"条目 {item_key} 不存在"
        except Exception as e:
            return False, f"无法访问条目 {item_key}: {e}"

        # 使用 linked_file 模式（保持原文件路径）
        attachment_payload = {
            'itemType': 'attachment',
            'linkMode': 'linked_file',
            'title': md_path.name,
            'path': str(md_path),
            'contentType': 'text/markdown',
            'parentItem': item_key
        }

        # 使用 create_items 创建附件
        try:
            result = zot.create_items([attachment_payload])
            if result and result.get('successful'):
                return True, f"已附加到 Zotero 条目 {item_key}"
            else:
                return False, f"附加失败: {result}"
        except Exception as e:
            return False, f"附加失败: {str(e)}"

    except Exception as e:
        return False, f"Zotero 连接错误: {str(e)}"


def process_zotero_attachment(md_path: Path, parent_key: str, args) -> tuple[Path, bool, str]:
    """处理 Zotero 关联（线程安全）"""
    # 获取条目信息
    item_info = get_zotero_item_info(parent_key)

    if not item_info:
        return (md_path, False, f"无法获取条目 {parent_key} 信息，跳过")

    # 如果是附件，尝试获取父条目
    target_key = parent_key
    title_info = ""

    if item_info['is_attachment'] and item_info['parent_key']:
        # 获取父条目信息
        parent_info = get_zotero_item_info(item_info['parent_key'])
        if parent_info:
            target_key = item_info['parent_key']
            title_info = f" -> {parent_info['title']}"
        else:
            title_info = f" (附件父条目获取失败)"
    else:
        title_info = f" - {item_info['title']}"

    if args.dry_run:
        return (md_path, True, f"[DRY-RUN] {md_path.name} -> Zotero: {target_key}{title_info}")
    else:
        zotero_success, zotero_msg = attach_to_zotero(md_path, target_key, args.zotero_api_key, args.zotero_user_id)
        if zotero_success:
            return (md_path, True, f"{md_path.name} -> {target_key}{title_info}")
        else:
            return (md_path, False, zotero_msg)


def main():
    parser = argparse.ArgumentParser(
        description='使用 markitdown 将 HTML/PDF 转换为 Markdown'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='要遍历的目录 (默认: 当前目录)'
    )
    parser.add_argument(
        '-c', '--concurrency',
        type=int,
        default=3,
        help='并发数 (默认: 3)'
    )
    parser.add_argument(
        '-i', '--image',
        default='sean10/markitdown',
        help='Docker 镜像 (默认: sean10/markitdown)'
    )
    parser.add_argument(
        '-e', '--extensions',
        nargs='+',
        default=['.html', '.pdf'],
        help='要处理的文件扩展名 (默认: .html .pdf)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细输出'
    )
    parser.add_argument(
        '--extract-images',
        action='store_true',
        default=True,
        help='提取 base64 图片为独立文件 (默认: 开启)'
    )
    parser.add_argument(
        '--no-extract-images',
        action='store_true',
        help='不提取图片，保持 base64 格式'
    )
    parser.add_argument(
        '-z', '--zotero',
        action='store_true',
        help='将 MD 文件附加到 Zotero 条目 (需要 --zotero-api-key 和 --zotero-user-id)'
    )
    parser.add_argument(
        '--attach-only',
        action='store_true',
        help='仅附加已存在的 MD 文件，不进行转换'
    )
    parser.add_argument(
        '--zotero-api-key',
        default='',
        help='Zotero API Key (从 https://www.zotero.org/settings/keys 获取)'
    )
    parser.add_argument(
        '--zotero-user-id',
        default='',
        help='Zotero 用户 ID (在 Zotero 设置中查看)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='不实际附加到 Zotero，仅显示关联信息'
    )
    parser.add_argument(
        '-l', '--limit',
        type=int,
        default=0,
        help='限制处理的文件数量 (0=不限制)'
    )
    parser.add_argument(
        '--migrate',
        action='store_true',
        help='迁移模式：通过API列出条目，转换附件并创建linked_file'
    )
    parser.add_argument(
        '--delete-original',
        action='store_true',
        help='迁移时删除原始html条目和文件'
    )

    args = parser.parse_args()

    # 迁移模式：直接调用迁移函数并退出
    if args.migrate:
        migrate_attachments(args)
        sys.exit(0)

    directory = Path(args.directory).resolve()

    if not directory.exists():
        print(f"错误: 目录不存在: {directory}")
        sys.exit(1)

    if not directory.is_dir():
        print(f"错误: 不是有效目录: {directory}")
        sys.exit(1)

    print(f"扫描目录: {directory}")
    print(f"并发数: {args.concurrency}")
    print(f"Docker 镜像: {args.image}")
    print(f"扩展名: {args.extensions}")
    extract_images = not args.no_extract_images
    print(f"提取图片: {'是' if extract_images else '否'}")

    if args.zotero:
        if not PYZOTERO_AVAILABLE:
            print("错误: pyzotero 未安装，请运行: pip install pyzotero")
            sys.exit(1)
        if not args.dry_run and (not args.zotero_api_key or not args.zotero_user_id):
            print("错误: 上传附件需要 --zotero-api-key 和 --zotero-user-id 参数")
            print("       获取 API Key: https://www.zotero.org/settings/keys")
            print("       用户 ID 在: 编辑 > 首选项 > 同步")
            sys.exit(1)
        print(f"Zotero 关联: 开启 (dry-run: {args.dry_run})")
    print("-" * 50)

    # attach-only 模式：直接查找已存在的 MD 文件
    if args.attach_only:
        md_files = []
        for ext in ['.md']:
            for md_path in directory.rglob(f'*{ext}'):
                parent_key = md_path.parent.name
                md_files.append((md_path, parent_key))
        files = sorted(md_files, key=lambda x: x[0])
        print(f"找到 {len(files)} 个已存在的 MD 文件\n")
    else:
        files = find_files(directory, args.extensions)
        print(f"找到 {len(files)} 个文件\n")

    if not files:
        print("未找到匹配的文件")
        sys.exit(0)

    # 限制处理数量
    if args.limit > 0:
        files = files[:args.limit]
        print(f"限制处理: {args.limit} 个文件\n")

    success_count = 0
    fail_count = 0
    zotero_attached = 0
    zotero_failed = 0

    if args.attach_only:
        # attach-only 模式：直接附加到 Zotero
        for md_path, parent_key in files:
            print(f"  [ATTACH] {md_path.name}")

            if not args.zotero:
                continue

            # 获取条目信息
            item_info = get_zotero_item_info(parent_key)
            if not item_info:
                print(f"    无法获取条目 {parent_key} 信息，跳过")
                zotero_failed += 1
                continue

            # 如果是附件，尝试获取父条目
            target_key = parent_key
            title_info = ""

            if item_info['is_attachment'] and item_info['parent_key']:
                parent_info = get_zotero_item_info(item_info['parent_key'])
                if parent_info:
                    target_key = item_info['parent_key']
                    title_info = f" -> {parent_info['title']}"
                else:
                    title_info = f" (附件父条目获取失败)"
            else:
                title_info = f" - {item_info['title']}"

            if args.dry_run:
                print(f"    [DRY-RUN] {md_path.name} -> Zotero: {target_key}{title_info}")
                zotero_attached += 1
            else:
                zotero_success, zotero_msg = attach_to_zotero(md_path, target_key, args.zotero_api_key, args.zotero_user_id)
                if zotero_success:
                    print(f"    [ZOTERO] {md_path.name} -> {target_key}{title_info}")
                    zotero_attached += 1
                else:
                    print(f"    [ZOTERO] {zotero_msg}")
                    zotero_failed += 1

        print("-" * 50)
        print(f"完成: 附加 {zotero_attached}, 失败 {zotero_failed}")
        sys.exit(0)

    # 用于收集 Zotero 关联任务
    zotero_futures = []

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        # 提交转换任务
        futures = {
            executor.submit(convert_file, f[0], args.image, extract_images): f
            for f in files
        }

        for future in as_completed(futures):
            file_path, success, message, md_path, parent_key = future.result()

            if success:
                success_count += 1
                if args.verbose:
                    print(f"[OK] {message}")

                # Zotero 关联 - 提交到线程池并发执行
                if args.zotero and parent_key:
                    zotero_future = executor.submit(process_zotero_attachment, md_path, parent_key, args)
                    zotero_futures.append(zotero_future)
            else:
                fail_count += 1
                print(f"[FAIL] {file_path}: {message}")

    # 等待所有 Zotero 关联任务完成
    if zotero_futures:
        print("\n等待 Zotero 关联完成...")
        for future in as_completed(zotero_futures):
            md_path, zotero_success, msg = future.result()
            if zotero_success:
                print(f"  [ZOTERO] {msg}")
                zotero_attached += 1
            else:
                print(f"  [ZOTERO] {msg}")
                zotero_failed += 1

    print("-" * 50)
    print(f"完成: 成功 {success_count}, 失败 {fail_count}")

    if args.zotero:
        print(f"Zotero: 附加 {zotero_attached}, 失败 {zotero_failed}")

    if fail_count > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
