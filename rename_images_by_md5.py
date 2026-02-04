#!/usr/bin/env python3
"""
将图片文件重命名为基于内容的 MD5 值
"""
import hashlib
import os
import shutil
from pathlib import Path


def get_image_md5(file_path):
    """计算图片内容的 MD5"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def rename_images_by_md5(source_dir, output_dir):
    """
    将图片重命名为 MD5 并复制到新文件夹
    :param source_dir: 源图片目录
    :param output_dir: 输出目录
    """
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 支持的图片扩展名
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'}
    
    # 统计
    total = 0
    processed = 0
    skipped = 0
    
    print(f"源目录: {source_path}")
    print(f"输出目录: {output_path}")
    print("-" * 60)
    
    # 遍历所有文件
    for file_path in source_path.rglob('*'):
        if not file_path.is_file():
            continue
            
        total += 1
        ext = file_path.suffix.lower()
        
        # 只处理图片文件
        if ext not in image_extensions:
            continue
        
        try:
            # 计算 MD5
            md5_hash = get_image_md5(file_path)
            
            # 保持相对路径结构
            relative_path = file_path.relative_to(source_path)
            relative_dir = relative_path.parent
            
            # 新文件名
            new_name = f"{md5_hash}{ext}"
            new_dir = output_path / relative_dir
            new_path = new_dir / new_name
            
            # 创建目标子目录
            new_dir.mkdir(parents=True, exist_ok=True)
            
            # 如果目标文件已存在（相同内容），跳过
            if new_path.exists():
                print(f"跳过（已存在）: {relative_path} -> {relative_dir / new_name}")
                skipped += 1
            else:
                # 复制文件
                shutil.copy2(file_path, new_path)
                print(f"处理: {relative_path} -> {relative_dir / new_name}")
                processed += 1
                
        except Exception as e:
            print(f"错误: {file_path} - {e}")
    
    print("-" * 60)
    print(f"总文件数: {total}")
    print(f"已处理: {processed}")
    print(f"已跳过: {skipped}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python rename_images_by_md5.py <源目录> <输出目录>")
        print("示例: python rename_images_by_md5.py ./ydnote/assets_ori ./ydnote/assets_md5")
        sys.exit(1)
    
    source_directory = sys.argv[1]
    output_directory = sys.argv[2]
    
    if not os.path.exists(source_directory):
        print(f"错误: 源目录不存在: {source_directory}")
        sys.exit(1)
    
    rename_images_by_md5(source_directory, output_directory)


