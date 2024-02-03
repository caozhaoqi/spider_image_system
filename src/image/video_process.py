import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os

import cv2
from loguru import logger

from run import constants
from run.constants import output_video_fps, output_video_height, output_video_width
from utils.time_utils import id_generate_time


@logger.catch
def generate_video_from_images(images_input_path, video_out_path):
    """
    generate video from images list
    :param images_input_path:
    :param video_out_path:
    :return:
    """
    image_paths = []
    for root, dirs, files in os.walk(images_input_path):
        for file in files:
            if "square" in file or "custom" in file or "error_images" in root or "small_images" in root \
                    or "gif_unzip" in root:
                logger.warning(f"skip file, because images error or small, name:{file}")
                continue
            elif file.endswith('.jpg') or file.endswith('.png'):  # 仅处理jpg和png图片文件
                image_paths.append(os.path.join(root, file))
    logger.debug(
        "scan image coule use image length: " + str(len(image_paths)) + ", scan dir: " + str(constants.data_path))
    if len(image_paths) <= 0:
        return False
    width = 0
    height = 0

    for image_path in image_paths:
        try:
            image = cv2.imread(image_path)
            if width == 0:
                width = image.shape[1]
            height = image.shape[0]
        except Exception as e:
            logger.error("error! detail: " + "file name or path: " + image_path + ", error detail: " + str(e))
            continue

        # 检查输出路径是否存在，如果不存在则创建目录
    if not os.path.exists(video_out_path):
        os.makedirs(video_out_path)

    fourcc = cv2.VideoWriter.fourcc(*'MJPG')
    # 创建VideoWriter对象
    video_name = video_out_path + id_generate_time() + "test.mp4"
    video = cv2.VideoWriter(video_name, fourcc, int(output_video_fps), (width, height))  # 设置视频帧率、输出视频大小
    if not video.isOpened():
        print("无法打开视频文件写入器")
        return False

    try:
        export_index = 0
        image_size_len = len(image_paths)
        for image_path in os.listdir(images_input_path):
            export_index += 1
            percent_cur = int((export_index / image_size_len) * 100)
            image = cv2.imread(os.path.join(images_input_path, image_path))
            if image is None:  # 增加对图像是否正确读取的检查
                logger.error("Image not loaded:" + image_path)
                continue
            resized_image = cv2.resize(image, (width, height))  # 将图像的宽度和高度设置为适合MPEG-4的尺寸
            if image is not None:
                video.write(resized_image)
            if percent_cur % 10 == 0:
                logger.info(f"export process to export_index / image_size_len: {export_index} / {image_size_len} * "
                            f"100%10: {percent_cur}%")
    finally:  # 确保视频资源被释放，无论是否有异常发生
        video.release()
    return video_name


@logger.catch
def convert_image(images_input_path, target_dir):
    """
    convert images to universal size
    :param images_input_path:
    :param target_dir:
    :return:
    """
    # 确保目标目录存在
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 遍历源目录中的所有文件
    image_paths = []
    for root, dirs, files in os.walk(images_input_path):
        for file in files:
            if "result" in file:
                continue
            elif file.endswith('.jpg') or file.endswith('.png'):  # 仅处理jpg和png图片文件
                image_paths.append(os.path.join(root, file))
                # 检查文件是否为图片
    if len(image_paths) == 0:
        logger.warning("convert image no image!")
        return False
    logger.debug("convert_image: scan result, need convert images count: " + str(len(image_paths)))
    for filename in image_paths:
        result = image_fill_black(target_dir, filename)
        if not result:
            continue
    return True


@logger.catch
def image_fill_black(target_dir, image_path):
    """
    循环处理输入图像：如果输入尺寸大于输出尺寸则：缩小；如果输入尺寸小于输出尺寸，则用黑边填充。尺寸相等 输出图像
    :param target_dir:输出图像路径
    :param image_path:输入图像路径
    :return:是否转换成功
    """
    # Step 1： import opencv lib
    import cv2
    try:
        # Step 2: Define the target size
        target_size = (output_video_width, output_video_height)
        # 读取图片
        img = cv2.imread(image_path)
        # 检查图片尺寸
        height, width = img.shape[:2]
        border_width = 0
        border_height = 0
        grap_width = 0
        grap_height = 0
        while True:
            # 调整图片大小960x959 480 61
            # 如果图像尺寸大于目标尺寸，进行缩放
            if width < target_size[0] and height < target_size[1]:
                if width < target_size[0]:
                    border_width = abs(target_size[0] - width) // 2
                    grap_width = output_video_width - (border_width * 2) - width
                elif width == target_size[0]:
                    border_width = 0
                    grap_width = 0
                if height < target_size[1]:
                    # 计算黑边宽度 除2
                    border_height = abs(target_size[1] - height) // 2
                    # 计算少于目标宽度 目标高度值 ，
                    grap_height = output_video_height - (border_height * 2) - height
                elif height == target_size[1]:
                    border_height = 0
                    grap_height = 0
                border = border_width, border_height
                # 填充时自动补充至图像底边和右边 以确保输出图像等于目标尺寸 1920 1080
                img = cv2.copyMakeBorder(img, border[1], border[1] + grap_height, border[0], border[0] + grap_width,
                                         cv2.BORDER_CONSTANT, value=[0, 0, 0])
                out_height, out_width = img.shape[:2]
                if out_height == output_video_height and out_width == output_video_width:
                    break
                else:
                    continue
                # 如果图像尺寸大于目标尺寸，进行缩放
            elif width > target_size[0] or height > target_size[1]:
                img = cv2.resize(img, target_size, interpolation=cv2.INTER_LINEAR)
                out_height, out_width = img.shape[:2]
                if out_height == output_video_height and out_width == output_video_width:
                    break
                else:
                    continue
            else:
                logger.info(f"Image size matches the target size: {image_path}")
                break
        # Step 8: Display or save the resized image (optional)
        file_path, file_name = os.path.split(image_path)
        # 保存或显示结果
        cv2.imwrite(os.path.join(target_dir, "result_" + file_name), img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except AttributeError as uie:
        logger.error("error, AttributeError: 'NoneType' object has no attribute 'shape'! detail: " + str(uie) +
                     ", ""file_name or path: " + str(image_path))
        return False
    except Exception as e:
        logger.error("error, unknown error! detail: " + str(e) + ", file_name or path: " + str(image_path))
        return False
    return True


@logger.catch
def process_images_thread(self):
    """
    process image to video thread
    :param self:
    :return:
    """
    #  step 1> 处理不同尺寸照片，将其尺寸一直化
    result = convert_image(constants.data_path, constants.data_path + "/img_result")
    #  step 2> 根据处理后的图像，尝试生成视频
    if result:
        process_ret = generate_video_from_images(constants.data_path + "/img_result", constants.data_path + "/video/")
        if process_ret:
            logger.success("out video success! file_name: " + process_ret)
        constants.process_image_flag = False
        self.success_tips()


@logger.catch
def play_video_process(self):
    """
    播放视频进程
    :param self:
    :return:
    """
    try:
        if self.listWidget_4.selectedItems():
            selectedItem = self.listWidget_4.selectedItems()[0]
            selectedFilename = selectedItem.text()
            cap = cv2.VideoCapture(selectedFilename)
            # 创建窗口
            cv2.namedWindow('Video', cv2.WINDOW_NORMAL)

            # 初始化时间戳和播放速度
            last_time = 0
            play_speed = 1.0

            # 创建跟踪条
            # 第一个参数是跟踪条的名称，第二个参数是窗口的名称，第三个参数是跟踪条的默认位置（0-100），第四个参数是跟踪条的长度
            if cap.isOpened():
                while True:
                    ret, frame = cap.read()
                    if not ret:  # 视频结束或出错
                        break
                    cv2.imshow('Video: ' + selectedFilename, frame)
                    # position = cv2.getTrackbarPos('Position', 'Video')
                    # 获取当前时间戳
                    current_time = int(cap.get(cv2.CAP_PROP_POS_MSEC)) // 1000

                    # 处理暂停/继续播放
                    if cv2.waitKey(1) & 0xFF == ord('p'):  # 按p键暂停/继续播放
                        if current_time > last_time:  # 如果当前时间大于上次时间，说明视频在播放，暂停播放
                            cap.set(cv2.CAP_PROP_POS_FRAMES, last_time)
                            logger.info("p pause or play video up!")
                        else:  # 否则，恢复播放
                            cap.set(cv2.CAP_PROP_POS_FRAMES, current_time)
                            logger.info("p replay video up!")
                        last_time = current_time  # 更新上次时间

                    # 处理前进/后退
                    if cv2.waitKey(1) & 0xFF == ord('f'):  # 按f键快进
                        if current_time > last_time:  # 如果当前时间大于上次时间，说明视频在播放，快进到指定位置
                            cap.set(cv2.CAP_PROP_POS_MSEC, (last_time + 1000) * 1000)  # 快进10秒
                            logger.info("f video speed up!")
                        else:  # 否则，快退到指定位置
                            cap.set(cv2.CAP_PROP_POS_MSEC, last_time * 1000)  # 退后1秒
                            logger.info("f video speed down!")

                        last_time = current_time  # 更新上次时间

                    # 处理倍速播放
                    if cv2.waitKey(1) & 0xFF == ord('+'):  # 按+键增加播放速度
                        play_speed += 0.1
                        cap.set(cv2.CAP_PROP_SPEED, play_speed)  # 设置新的播放速度
                        logger.info("+ play video speed up!")
                    if cv2.waitKey(1) & 0xFF == ord('-'):  # 按-键减少播放速度
                        play_speed -= 0.1
                        logger.info("- play video speed down!")
                        if play_speed < 0:  # 防止速度过小导致播放出现问题
                            play_speed = 0.1
                            logger.info("- play video speed < min reset play_speed = 0.1!")
                        cap.set(cv2.CAP_PROP_SPEED, play_speed)  # 设置新的播放速度

                    # 在视频帧上显示当前播放位置和播放速度（可选）
                    cv2.putText(frame, f"Pos: {current_time}ms, Speed: {play_speed}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    if cv2.waitKey(1) & 0xFF == ord('q'):  # 按q退出播放
                        break
                cap.release()
                cv2.destroyAllWindows()
            else:
                logger.error("Error opening video file:", selectedFilename)
        else:
            logger.warning("Please select a video file.")
    except Exception as e:
        logger.error("error, detail: " + str(e))
