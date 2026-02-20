#!/usr/bin/env python3
"""
递归遍历目录下的 HTML 和 PDF 文件，使用 markitdown docker 转换为 Markdown。
支持并发处理。
支持提取 base64 图片到独立文件。
"""

import argparse
import base64
import hashlib
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


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


def convert_file(file_path: Path, docker_image: str, extract_images: bool) -> tuple[str, bool, str]:
    """转换单个文件，返回 (文件名, 是否成功, 消息)"""
    md_path = file_path.with_suffix('.md')

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
            return (str(file_path), True, msg)
        else:
            error_msg = result.stderr.decode('utf-8', errors='replace')
            return (str(file_path), False, f"失败: {error_msg[:200]}")

    except Exception as e:
        return (str(file_path), False, f"异常: {str(e)}")


def find_files(directory: Path, extensions: list[str]) -> list[Path]:
    """递归查找指定扩展名的文件"""
    files = []
    for ext in extensions:
        files.extend(directory.rglob(f'*{ext}'))
    return sorted(files)


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

    args = parser.parse_args()

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
    print("-" * 50)

    files = find_files(directory, args.extensions)

    if not files:
        print("未找到匹配的文件")
        sys.exit(0)

    print(f"找到 {len(files)} 个文件\n")

    success_count = 0
    fail_count = 0

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = {
            executor.submit(convert_file, f, args.image, extract_images): f
            for f in files
        }

        for future in as_completed(futures):
            file_path, success, message = future.result()

            if success:
                success_count += 1
                if args.verbose:
                    print(f"[OK] {message}")
            else:
                fail_count += 1
                print(f"[FAIL] {file_path}: {message}")

    print("-" * 50)
    print(f"完成: 成功 {success_count}, 失败 {fail_count}")

    if fail_count > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
