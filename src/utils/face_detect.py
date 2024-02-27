import cv2 as cv
from loguru import logger


@logger.catch
def face_detect(image_path):
    """
    使用OpenCV进行人脸和眼睛检测。

    :param image_path: 图像文件的路径。
    :return: None
    """
    try:
        # 加载分类器
        face_cascade = cv.CascadeClassifier('./xml_data/haarcascade_frontalface_default.xml')
        eye_cascade = cv.CascadeClassifier('./xml_data/haarcascade_eye.xml')

        # 读取图像
        img = cv.imread(image_path)
        if img is None:
            logger.error(f"Error: Unable to load image at {image_path}")
            return

        # 转换为灰度图像
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # 检测人脸
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        if len(faces) == 0:
            logger.warning("No faces detected.")
        for (x, y, w, h) in faces:
            cv.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]

            # 在人脸区域内检测眼睛
            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                cv.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

        # 显示结果
        # cv.imshow("Face Detection", img)
        cv.waitKey(0)
        cv.destroyAllWindows()

    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == '__main__':
    # 调用 show_detection() 函数标示检测到的人脸
    face_detect(r"C:\Users\Administrator\PycharmProjects\spider_image_system\src\run\data\img_url\hei1ta3_img_result"
                r"\images\115425528_p0_master1200.jpg")
