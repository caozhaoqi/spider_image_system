#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量下载图片脚本
从指定URL列表文件中下载所有图片
"""

import os
import sys
import urllib.request
from pathlib import Path


def download_images(url_file_path, output_dir=None):
    """
    批量下载图片
    
    Args:
        url_file_path: URL列表文件路径
        output_dir: 输出目录，默认为当前目录下的images文件夹
    """
    url_file = Path(url_file_path)
    
    if not url_file.exists():
        print(f"❌ 文件不存在: {url_file_path}")
        return False
    
    # 设置输出目录
    if output_dir is None:
        output_dir = url_file.parent.parent / "downloaded_images" / url_file.stem
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 输出目录: {output_dir}")
    
    # 读取URL列表
    with open(url_file_path, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    total_urls = len(urls)
    print(f"\n📊 共发现 {total_urls} 个图片URL")
    
    success_count = 0
    fail_count = 0
    
    for i, url in enumerate(urls, 1):
        try:
            # 提取文件名
            filename = url.split('/')[-1]
            if not filename:
                filename = f"image_{i:04d}.webp"
            
            output_path = output_dir / filename
            
            # 检查文件是否已存在
            if output_path.exists():
                print(f"⚠️ [{i}/{total_urls}] 已存在，跳过: {filename}")
                success_count += 1
                continue
            
            # 下载图片
            urllib.request.urlretrieve(url, str(output_path))
            print(f"✅ [{i}/{total_urls}] 下载成功: {filename}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ [{i}/{total_urls}] 下载失败: {url}")
            print(f"   错误: {type(e).__name__}: {e}")
            fail_count += 1
    
    print(f"\n{'='*50}")
    print(f"📝 下载完成")
    print(f"   ✅ 成功: {success_count}")
    print(f"   ❌ 失败: {fail_count}")
    print(f"   📂 输出目录: {output_dir}")
    print(f"{'='*50}")
    
    return fail_count == 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python download_images.py <url_file_path> [output_dir]")
        sys.exit(1)
    
    url_file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    download_images(url_file_path, output_dir)