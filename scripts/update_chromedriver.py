#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromeDriver自动更新脚本
自动检测Chrome版本并下载匹配版本的ChromeDriver
"""

import os
import sys
import subprocess
import re
import zipfile
import shutil
from pathlib import Path


def get_chrome_version():
    """获取Chrome浏览器版本"""
    try:
        if sys.platform == "darwin":
            # macOS
            result = subprocess.run(
                ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
                capture_output=True, text=True
            )
            version_str = result.stdout.strip()
            # 提取版本号：Google Chrome 149.0.7827.103 -> 149.0.7827.103
            match = re.search(r'(\d+\.\d+\.\d+\.\d+)', version_str)
            if match:
                return match.group(1)
        else:
            # Linux/Windows
            result = subprocess.run(
                ["google-chrome", "--version"],
                capture_output=True, text=True
            )
            match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"获取Chrome版本失败: {e}")
    return None


def get_chromedriver_version():
    """获取当前ChromeDriver版本"""
    try:
        result = subprocess.run(
            ["chromedriver", "--version"],
            capture_output=True, text=True
        )
        # ChromeDriver 147.0.7727.117
        match = re.search(r'ChromeDriver\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"获取ChromeDriver版本失败: {e}")
    return None


def get_major_version(full_version):
    """获取主版本号"""
    if full_version:
        return full_version.split('.')[0]
    return None


def get_wdm_drivers_path():
    """获取webdriver-manager的驱动目录"""
    home = Path.home()
    return home / ".wdm" / "drivers" / "chromedriver"


def download_chromedriver(major_version, full_version):
    """下载匹配版本的ChromeDriver"""
    print(f"\n正在下载 ChromeDriver {full_version}...")

    # 确定平台
    if sys.platform == "darwin":
        if subprocess.run(["uname", "-m"], capture_output=True, text=True).stdout.strip() == "arm64":
            platform = "mac64"
            arch = "mac-arm64"
        else:
            platform = "mac64"
            arch = "mac64"
    elif sys.platform == "win32":
        platform = "win32"
        arch = "win32"
    else:
        platform = "linux64"
        arch = "linux64"

    # 下载URL（使用Chrome for Testing官方镜像）
    url = f"https://storage.googleapis.com/chrome-for-testing-public/{full_version}/{arch}/chromedriver-{arch}.zip"

    print(f"下载链接: {url}")

    # 创建临时目录
    temp_dir = Path("/tmp/chromedriver_update")
    temp_dir.mkdir(exist_ok=True)
    zip_path = temp_dir / f"chromedriver-{arch}.zip"

    try:
        # 下载
        subprocess.run(
            ["curl", "-L", "-o", str(zip_path), url],
            check=True
        )

        # 解压
        extract_dir = temp_dir / "extracted"
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # 找到chromedriver文件
        chromedriver_file = None
        for root, dirs, files in os.walk(extract_dir):
            if "chromedriver" in files and not files[0].endswith('.zip'):
                chromedriver_file = Path(root) / "chromedriver"
                break

        if not chromedriver_file:
            print("解压后未找到chromedriver文件")
            return False

        # 安装到webdriver-manager目录
        wdm_path = get_wdm_drivers_path() / platform / major_version / f"chromedriver-{arch}"
        wdm_path.parent.mkdir(parents=True, exist_ok=True)
        wdm_path.mkdir(exist_ok=True)

        dest_path = wdm_path / "chromedriver"
        shutil.copy2(chromedriver_file, dest_path)
        os.chmod(dest_path, 0o755)

        print(f"\n✅ ChromeDriver已安装到: {dest_path}")

        # 清理临时文件
        shutil.rmtree(temp_dir)

        return True

    except Exception as e:
        print(f"下载/安装ChromeDriver失败: {e}")
        if zip_path.exists():
            os.remove(zip_path)
        return False


def update_chromedriver():
    """更新ChromeDriver主函数"""
    print("=" * 60)
    print("ChromeDriver 自动更新工具")
    print("=" * 60)

    # 1. 检测Chrome版本
    chrome_version = get_chrome_version()
    if not chrome_version:
        print("❌ 无法获取Chrome版本，请确保已安装Google Chrome")
        return False

    chrome_major = get_major_version(chrome_version)
    print(f"\n📌 当前Chrome版本: {chrome_version} (主版本: {chrome_major})")

    # 2. 检测ChromeDriver版本
    chromedriver_version = get_chromedriver_version()
    if not chromedriver_version:
        print("\n⚠️  未检测到ChromeDriver，将进行安装")
        return download_chromedriver(chrome_major, chrome_version)

    chromedriver_major = get_major_version(chromedriver_version)
    print(f"📌 当前ChromeDriver版本: {chromedriver_version} (主版本: {chromedriver_major})")

    # 3. 检查是否需要更新
    if chrome_major == chromedriver_major:
        print(f"\n✅ Chrome ({chrome_version}) 和 ChromeDriver ({chromedriver_version}) 版本匹配，无需更新")
        return True

    print(f"\n⚠️  版本不匹配!")
    print(f"   Chrome需要主版本 {chrome_major}，但ChromeDriver是 {chromedriver_major}")
    print(f"\n正在更新ChromeDriver...")

    # 4. 下载并安装新版本
    success = download_chromedriver(chrome_major, chrome_version)

    if success:
        print("\n" + "=" * 60)
        print("✅ ChromeDriver更新成功!")
        print("=" * 60)
        print(f"\n请重启爬虫服务使新版本生效。")
        return True
    else:
        print("\n❌ ChromeDriver更新失败")
        return False


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        # 仅检查版本
        chrome_v = get_chrome_version()
        driver_v = get_chromedriver_version()
        print(f"Chrome: {chrome_v or '未安装'}")
        print(f"ChromeDriver: {driver_v or '未安装'}")
        if chrome_v and driver_v:
            if get_major_version(chrome_v) == get_major_version(driver_v):
                print("状态: ✅ 版本匹配")
            else:
                print("状态: ⚠️ 版本不匹配，需要更新")
    else:
        update_chromedriver()


if __name__ == "__main__":
    main()
