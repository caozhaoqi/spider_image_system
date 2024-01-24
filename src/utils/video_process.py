import requests
from bs4 import BeautifulSoup
import pytube
from loguru import logger

from utils.VideoPlayerThread import VideoPlayerThread


def search_videos(keywords):
    """

    :param keywords:
    :return:
    """
    # 发送HTTP请求获取网页内容
    url = f"https://www.baidu.com/search?q={keywords}"  # 替换为实际的搜索页面URL
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 解析HTML代码，查找视频链接
    video_containers = soup.find_all('div', class_='video-container')  # 根据实际页面结构修改查找方式
    video_links_list = []
    for container in video_containers:
        video_link = container.find('a')['href']  # 获取视频链接
        video_links_list.append(video_link)

    return video_links_list


def download_video(video_link, output_paths):
    """

    :param video_link:
    :param output_paths:
    :return:
    """
    # 创建YouTube对象并下载视频
    yt = pytube.YouTube(video_link)
    highest_res = yt.streams.get_highest_resolution()
    highest_res.download(output_paths)


import cv2


# def pause_resume(self):
#     """
#
#     :return:
#     """
#     if self.position % fps == 0:  # 如果是整帧数，则暂停视频
#         if self.speed == 1.0:  # 如果是正常速度，则暂停视频
#             self.update_status.emit('Paused')
#             cap.release()
#             cv2.destroyAllWindows()
#     else:  # 否则快进到下一帧并继续播放视频
#         self.position += 1
#         self.update_progress.emit(int(self.position / fps * 100))  # 更新进度条位置s
#     pass


@logger.catch
def load_and_play_video(video_file):
    """

    :param video_file:
    :return:
    """
    video_player_thread = VideoPlayerThread(video_file)
    # video_file
    video_player_thread.start()
    video_player_thread.run()


# return true


if __name__ == '__main__':
    keyword = 'your keyword'  # 替换为实际的关键词
    video_links = search_videos(keyword)
    for link in video_links:
        output_path = f"videos/{link.split('/')[-1]}"  # 根据实际需求修改输出路径和文件名格式
        download_video(link, output_path)
