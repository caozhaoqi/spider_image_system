import cv2
from loguru import logger
from sklearn.metrics import pairwise_distances

from utils.img_switch import find_images


@logger.catch
def analysis_two_picture(source_path, target_path):
    # 加载图片
    img1 = cv2.imread(source_path)
    img2 = cv2.imread(target_path)

    # 将图片转换为灰度图像
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # 提取SIFT特征点
    sift = cv2.SIFT.create()
    kp1, des1 = sift.detectAndCompute(gray1, None)
    kp2, des2 = sift.detectAndCompute(gray2, None)

    # 计算特征点匹配
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    # 去除误匹配点
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append([m])

    # 计算相似度矩阵
    X = np.array([kp1[m[0].queryIdx].pt for m in good]).reshape(-1, 1)
    Y = np.array([kp2[m[0].trainIdx].pt for m in good]).reshape(-1, 1)
    dist = pairwise_distances(X, Y)
    sim = 1 - dist / dist.max()

    # 返回相似概率
    sim_prob = sim.flatten() / sim.sum()
    logger.info('Similarity probability:' + str(sim_prob))


import numpy as np
from PIL import Image

"""
直方图
"""


@logger.catch
def calculate_histogram(image_path):
    # 打开图片并转换为RGB模式
    image = Image.open(image_path).convert('RGB')
    # 将图像转换为numpy数组
    pixels = np.array(image)
    # 计算直方图
    histogram = np.histogram2d(pixels[:, :, 0], pixels[:, :, 1], bins=64)[0]
    # 对直方图进行归一化
    histogram = histogram / np.sum(histogram)
    return histogram


@logger.catch
def compare_similarity(image1_path, image2_path):
    histogram1 = calculate_histogram(image1_path)
    histogram2 = calculate_histogram(image2_path)
    # 计算两个直方图的欧氏距离作为相似度指标
    similarity = 1 - np.linalg.norm(histogram1 - histogram2)
    return similarity


# 示例用法
from skimage.measure import compare_ssim as ssim


@logger.catch
def compare_picture(image_1_path, image_2_path):
    """

    :param image_1_path:
    :param image_2_path:
    :return:
    """
    # 读取两个图像文件
    image1 = cv2.imread(image_1_path)
    image2 = cv2.imread(image_2_path)

    # 将图像转换为灰度图像（如果需要）
    image1_gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    image2_gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # 计算结构相似度（SSIM）
    ssim_value = ssim(image1_gray, image2_gray, full=True)
    print("结构相似度（SSIM）:", ssim_value)


if __name__ == '__main__':
    images_list = find_images(r'C:\Users\Administrator\PycharmProjects\spider_image_system\src\gui\data')
    image1_path = r'C:\Users\Administrator\PycharmProjects\spider_image_system\src\gui\data\img_result' \
                  r'\result_85127787_p0_master1200.jpg'
    image2_path = r'C:\Users\Administrator\PycharmProjects\spider_image_system\src\gui\data\img_result' \
                  r'\result_85150285_p0_master1200.jpg'
    for image in images_list:
        for image_2 in images_list:
            # analysis_two_picture(image, image_2)
            compare_picture(image, image_2)
    # similarity = compare_similarity(image, image_2)
    # print(f"相似度: {similarity}")
