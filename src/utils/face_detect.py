import cv2 as cv


def face_detect(image_path):
    """

    :param image_path:
    :return:
    """
    face_cascade = cv.CascadeClassifier('xml_data/haarcascade_frontalface_default.xml')
    eye_cascade = cv.CascadeClassifier('xml_data/haarcascade_eye.xml')
    img = cv.imread(image_path)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        cv.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex, ey, ew, eh) in eyes:
            cv.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
    cv.imshow(image_path, img)
    cv.waitKey(0)
    cv.destroyAllWindows()


if __name__ == '__main__':
    # 调用 show_detection() 函数标示检测到的人脸
    face_detect(r"C:\Users\Administrator\PycharmProjects\spider_image_system\src\run\data\a.jpg")
