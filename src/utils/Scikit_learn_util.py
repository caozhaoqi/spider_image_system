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
# from skimage.measure import compare_ssim as ssim


# scikit-image

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

    psnr = cv2.PSNR(image1_gray, image2_gray)
    print("峰值信噪比（PSNR）:", psnr)

    # 计算NCC
    ncc = cv2.NCC(image1_gray, image2_gray)
    print("归一化交叉相关（NCC）:", ncc)

@logger.catch
def compare_image_similarity(source_path, compare_path):
    """
    比较两个图片的相似度
    @:param image1_path

    """
    # 打开图片并转换为灰度图像
    img1 = Image.open(source_path).convert('L')
    img2 = Image.open(compare_path).convert('L')

    # 将图片转换为NumPy数组
    img1 = np.array(img1)
    img2 = np.array(img2)

    # 计算两个图片的差异度
    diff = np.abs(img1 - img2)
    similarity = 1 - np.mean(diff)

    return similarity


@logger.catch
def simular_images_compare(self, data_path):
    """

    :param self:
    :param data_path:
    :return:
    """
    images_list = find_images(data_path)
    i = 0
    # percent_process = 0
    for image in images_list:
        j = 0
        i += 1
        for image_2 in images_list:
            # analysis_two_picture(image, image_2)
            j += 1
            if i == j:
                continue
            ret = compare_image_similarity(image, image_2)
            if str(ret) == '1.0':
                logger.info(f"image 1 path {image}, image 2 path: {image_2} image path md5 simular. cur "
                            f"process {i * j}, count: {len(images_list) ** 2}")
                # logger.info(ret)
            percent_process = (i * j) / (len(images_list) ** 2) * 100
            if percent_process // 10:
                logger.info(f"cur process {i * j}, count: {len(images_list) ** 2}, cur process: {percent_process}%")
    return True


import os
import hashlib


def get_md5(file_path):
    """计算文件的MD5值"""
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            md5_hash.update(data)
    return md5_hash.hexdigest()


def compare_images(folder_path):
    """
    比较指定文件夹中的图片MD5值
    """
    same_md5_count = 0
    different_md5_count = 0
    total_count = 0

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.jpg', '.png', '.jpeg')):  # 根据需要调整文件扩展名
                file_path = os.path.join(root, file)
                total_count += 1
                file_md5 = get_md5(file_path)
                same_md5_count += 1 if file_md5 == get_md5(os.path.join(root, file)) else 0  # 如果是相同文件，只计算一次
                different_md5_count += 1 if file_md5 != get_md5(os.path.join(root, file)) else 0  # 如果是不同文件，只计算一次

    print(f"相同MD5值的图片数量：{same_md5_count}")
    print(f"不同MD5值的图片数量：{different_md5_count}")
    print(f"总图片数量：{total_count}")
    if same_md5_count > 0:
        print(f"相同的MD5值概率为：{same_md5_count / total_count}")
    if different_md5_count > 0:
        print(f"不同的MD5值概率为：{different_md5_count / total_count}")


# 测试样例


if __name__ == '__main__':
    compare_images(r'C:\Users\Administrator\PycharmProjects\spider_image_system\src\gui\data')

    pass
    # simular_images_compare(self=None)
