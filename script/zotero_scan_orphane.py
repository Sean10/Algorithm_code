#!/usr/bin/python
# https://forums.zotero.org/discussion/comment/215096/#Comment_215096
import sqlite3
import os

def get_dir_size(path):
    """计算目录及其所有子文件的总大小(字节)"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except Exception as e:
        print(f"计算大小时出错: {path}, 错误: {e}")
    return total_size

def format_size(size_bytes):
    """将字节数格式化为可读的大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

# Update this to match your data directory
zoterostorage = "/Users/sean10/Zotero"

zoterostoragefiles = zoterostorage +  "/storage"
dbh = sqlite3.connect(zoterostorage + "/zotero.sqlite")

# Query all attachments
c = dbh.cursor()

c.execute("SELECT key FROM items")

# Fetching all dirs as a set
files = set(os.listdir(zoterostoragefiles))

for key in c.fetchall():
    if key[0] in files:
        files.remove(key[0])

# Loop over the orphan files and calculate total size
print("=" * 60)
print("孤儿目录列表:")
print("=" * 60)

total_size = 0
orphan_details = []

for orphan in sorted(files):
    orphan_path = os.path.join(zoterostoragefiles, orphan)
    if os.path.exists(orphan_path):
        if os.path.isdir(orphan_path):
            size = get_dir_size(orphan_path)
        else:
            size = os.path.getsize(orphan_path)
        total_size += size
        orphan_details.append((orphan, size))

# 打印每个孤儿对象的详细信息
for orphan, size in orphan_details:
    print(f"{orphan}: {format_size(size)}")

print("=" * 60)
print(f"孤儿对象总数: {len(orphan_details)}")
print(f"孤儿对象总大小: {format_size(total_size)} ({total_size:,} 字节)")
print("=" * 60)
