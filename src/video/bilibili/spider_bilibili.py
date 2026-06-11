# -*- coding: utf-8 -*-
"""
B站角色视频搜索 & 下载程序
搜索 阿罗娜 / 普拉娜 (碧蓝档案) 相关视频，并支持下载
"""

import requests
import json
import time
import os
import re
import subprocess
import sys
from datetime import datetime

# ============ 配置 ============
# 从浏览器获取Cookie填入下方，否则可能触发反爬
COOKIE = "buvid3=6592C030-4422-EFA9-878C-1B9F8DA8E2FE24234infoc; b_nut=1770088324; _uuid=110D87B91-BE610-DF65-14F2-CD8D9C5E810F327582infoc; buvid_fp=5e11f8781deaa20bf08b0e0ed525df9c; home_feed_column=5; buvid4=5A077B87-08C4-AF75-F8A2-DD05C689CEFA29972-026020311-BChkT12H7lVdA/OGjQ8Xwg%3D%3D; CURRENT_QUALITY=0; rpdid=|(JmYkJ~|Rk0J'u~~||))JRm; CURRENT_FNVAL=4048; csrf_state=0780ea7a8f6c19e229d468abc8172833; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3ODE0MTk0NjEsImlhdCI6MTc4MTE2MDIwMSwicGx0IjotMX0.wR3-7zvPvwU_pdOOSXeU6J6mKLaXkD0iJn8xQayXZyY; bili_ticket_expires=1781419401; SESSDATA=8cf9937b%2C1796712261%2C8d198%2A62CjDRUOnJZxbVXwkmifx4PXTQXjNs0rZ_mzNasWF8t2vfTNYdvLbCWExdfD_Ed0g6uPwSVlJkYm9JZlFnNWpIaEdWWnNTU1JFSU1HYUd6bDM4NFA2c2lYMlp1RG5kYllfVFhRLXd5QS1LOFU4c3VkOGlXVWVtTEFIcFhrS1hqMnNRdWQ5Vkk1cHZRIIEC; bili_jct=ad256a4f079dd62fa7606d13c1ec7800; DedeUserID=335112696; DedeUserID__ckMd5=e388e55bd03d61df; sid=hawf8oqs; theme-tip-show=SHOWED; browser_resolution=1470-150; b_lsid=3CCA64D9_19EB56CEA54"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
    "Origin": "https://www.bilibili.com",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

if COOKIE:
    HEADERS["Cookie"] = COOKIE

SEARCH_API = "https://api.bilibili.com/x/web-interface/search/type"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(OUTPUT_DIR, "downloads")
COOKIE_FILE = os.path.join(OUTPUT_DIR, "bilibili_cookies.txt")
# ==============================


def search_videos(keyword, page=1, pagesize=30):
    """搜索B站视频"""
    params = {
        "search_type": "video",
        "keyword": keyword,
        "page": page,
        "pagesize": pagesize,
    }
    try:
        resp = requests.get(SEARCH_API, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            print(f"  API返回错误: code={data.get('code')}, message={data.get('message')}")
            return []
        result = data.get("data", {})
        return result.get("result", [])
    except requests.exceptions.HTTPError as e:
        if "412" in str(e):
            print(f"  触发反爬(412)，请配置Cookie后再试")
        else:
            print(f"  HTTP错误: {e}")
        return []
    except Exception as e:
        print(f"  请求失败: {e}")
        return []


def search_videos_fallback(keyword, page=1):
    """备用方案: HTML页面解析"""
    url = "https://search.bilibili.com/all"
    params = {"keyword": keyword, "page": page}
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        html = resp.text
        match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
        if not match:
            return []
        state = json.loads(match.group(1))
        videos = state.get("videoData", {}).get("result", [])
        if not videos:
            for key in ["result", "items", "videos"]:
                v = state.get(key, [])
                if v:
                    videos = v
                    break
        return videos
    except Exception:
        return []


def format_number(num):
    """格式化数字显示"""
    if num is None:
        return "0"
    try:
        num = int(num)
        if num >= 10000:
            return f"{num / 10000:.1f}万"
        return str(num)
    except (ValueError, TypeError):
        return str(num)


def print_videos(videos, keyword):
    """打印视频列表（带序号）"""
    if not videos:
        print(f"  未找到相关视频\n")
        return []

    print(f"  共找到 {len(videos)} 个视频:\n")
    for i, v in enumerate(videos, 1):
        title = v.get("title", "").replace("<em class=\"keyword\">", "").replace("</em>", "")
        bvid = v.get("bvid", "N/A")
        play = format_number(v.get("play") or v.get("play_count") or v.get("playCount"))
        danmaku = format_number(v.get("danmaku") or v.get("video_review") or 0)
        author = v.get("author", v.get("up", {}).get("name", "未知"))
        duration = v.get("duration", 0)
        try:
            minutes, seconds = divmod(int(duration), 60)
            duration_str = f"{minutes}:{seconds:02d}"
        except (ValueError, TypeError):
            duration_str = str(duration)

        print(f"  [{i:>2}] {title}")
        print(f"       BV: {bvid}  |  UP: {author}  |  播放: {play}  |  {duration_str}")
    print()

    return videos


def download_video(url, output_dir, index=1, total=1):
    """使用 yt-dlp 下载单个B站视频"""
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n  ⬇️  正在下载 [{index}/{total}]: {url}")
    print(f"      保存到: {output_dir}\n")

    # 构建命令
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "-o", os.path.join(output_dir, "%(title)s.%(ext)s"),
        "--no-playlist",
    ]

    # 如果Cookie文件存在则使用
    if os.path.exists(COOKIE_FILE):
        cmd += ["--cookies", COOKIE_FILE]

    cmd.append(url)

    try:
        result = subprocess.run(cmd, check=True)
        print(f"  ✅ 下载完成: {url}\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ 下载失败: {e}\n")
        return False
    except FileNotFoundError:
        print(f"  ❌ 未找到 yt-dlp，请运行: pip3 install yt-dlp\n")
        return False


def interactive_download(all_videos, character_name):
    """交互式选择下载"""
    if not all_videos:
        return

    print(f"\n{'='*60}")
    print(f"  {character_name} - 共 {len(all_videos)} 个视频")
    print(f"{'='*60}")

    vids = print_videos(all_videos, character_name)
    if not vids:
        return

    print(f"  选项:")
    print(f"    [1-{len(vids)}] 输入序号下载单个视频")
    print(f"    [a] 下载全部 {len(vids)} 个视频")
    print(f"    [q] 跳过，不下载")

    choice = input(f"\n  请输入: ").strip().lower()
    if choice == "q" or not choice:
        return
    elif choice == "a":
        _batch_download(vids, character_name)
    else:
        parts = [p.strip() for p in choice.replace("，", ",").split(",")]
        indices = []
        for p in parts:
            if p.isdigit():
                idx = int(p)
                if 1 <= idx <= len(vids):
                    indices.append(idx)
        if indices:
            _batch_download([vids[i - 1] for i in indices], character_name)


def _batch_download(videos, character_name):
    """批量下载视频"""
    if not videos:
        return

    # 创建角色专属下载目录
    safe_name = re.sub(r'[\\/:*?"<>|+]', '_', character_name)
    char_dir = os.path.join(DOWNLOAD_DIR, safe_name)
    total = len(videos)

    print(f"\n  {'='*60}")
    print(f"  开始下载 {total} 个视频到: {char_dir}")
    print(f"  {'='*60}\n")

    for i, v in enumerate(videos, 1):
        bvid = v.get("bvid")
        if not bvid:
            continue
        url = f"https://www.bilibili.com/video/{bvid}"
        download_video(url, char_dir, i, total)
        time.sleep(1)  # 避免请求过快

    print(f"  {'='*60}")
    print(f"  全部下载完成！文件保存在: {char_dir}")
    print(f"  {'='*60}\n")


def main():
    characters = [
        {"name": "阿罗娜", "keyword": "阿罗娜 碧蓝档案"},
        {"name": "普拉娜", "keyword": "普拉娜 碧蓝档案"},
        {"name": "阿罗娜+普拉娜", "keyword": "阿罗娜 普拉娜"},
    ]

    all_results = {}
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n{'='*60}")
    print(f"  B站角色视频搜索 & 下载")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    for char in characters:
        print(f"▸ 搜索: {char['name']} (关键词: {char['keyword']})")
        time.sleep(1.5)

        videos = search_videos(char["keyword"])
        if not videos:
            print(f"  尝试备用解析方案...")
            videos = search_videos_fallback(char["keyword"])

        print_videos(videos, char["name"])

        all_results[char["name"]] = {
            "keyword": char["keyword"],
            "count": len(videos),
            "videos": [
                {
                    "title": v.get("title", "").replace("<em class=\"keyword\">", "").replace("</em>", ""),
                    "bvid": v.get("bvid"),
                    "author": v.get("author", v.get("up", {}).get("name")),
                    "play": v.get("play") or v.get("play_count"),
                    "danmaku": v.get("danmaku") or v.get("video_review"),
                    "duration": v.get("duration"),
                    "url": f"https://www.bilibili.com/video/{v.get('bvid')}",
                }
                for v in videos
            ],
        }

    # 保存搜索结果
    result_file = save_to_json(all_results, f"bilibili_角色视频_{timestamp}.json")
    print(f"  搜索结果已保存: {result_file}\n")

    # ========== 下载环节 ==========
    print(f"{'='*60}")
    print(f"  下载管理")
    print(f"{'='*60}\n")

    for char in characters:
        videos = all_results.get(char["name"], {}).get("videos", [])
        if videos:
            interactive_download(videos, char["name"])

    print(f"  ✨ 全部完成!")


def save_to_json(data, filename):
    """保存结果到JSON文件"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filepath


if __name__ == "__main__":
    main()