import requests
from bs4 import BeautifulSoup
import os


def get_pixiv_hot_images(limit, proxy):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/89.0.4389.82 Safari/537.36',
        'Referer': 'http://www.pixiv.net',
    }
    response = requests.get('http://www.pixiv.net/ranking.php', headers=headers, proxies=proxy)
    soup = BeautifulSoup(response.text, 'html.parser')
    hot_images = soup.select('img')[:limit]
    image_urls = [img['src'] for img in hot_images]
    return image_urls


def download_images(img_urls, output_dirs):
    """

    :param img_urls:
    :param output_dirs:
    :return:
    """
    for url in img_urls:
        filename = os.path.join(output_dirs, url.split('/')[-1])
        with requests.get(url, stream=True) as r:
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f"Downloaded: {filename}")


if __name__ == '__main__':
    output_dir = '../output'  # 保存下载图片的目录，可以自定义修改
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    proxy = {
        'http': 'http://192.168.199.26:8080',  # 替换为实际的代理服务器地址和端口
    }
    image_urls = get_pixiv_hot_images(10, proxy=proxy)
    download_images(image_urls, output_dir)
