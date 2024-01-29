from loguru import logger

from gui import constants


@logger.catch
def spider_btn_control(btn):
    """
    下载按钮控制
    :param btn:
    :return:
    """
    if btn.isEnabled():  # Check if the button is in "normal" state
        btn.setText("停止抓取")
        btn.setEnabled(False)  # Disable the button
        logger.warning("stop spider.")
        # Set your constant or variable accordingly
        constants.stop_spider_url_flag = True
    else:  # Button is currently disabled (or "stop" state)
        btn.setText("开始抓取")
        btn.setEnabled(True)  # Enable the button
        logger.info("spider url.")
        # Reset your constant or variable accordingly
        constants.stop_spider_url_flag = False


@logger.catch
def tk_upload_btn_control(btn):
    """
    上传按钮控制
    :param btn:
    :return:
    """
    if btn["state"] == "normal":
        btn["state"] = "disabled"
        btn["text"] = "正在上传中"
        logger.warning("uploading file , please wait ... ")

    else:
        btn["state"] = "normal"
        btn["text"] = "点击开始上传"
        logger.info("upload finished .")

