
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from loguru import logger

from src.gui.about_dialog_ui import InformationDialog
from src.gui.dialog_ui import Dialog


@logger.catch
def edit_config_msg():
    """
    update ini config msg
    :return:
    """
    dialog = Dialog()
    logger.info("config msg dialog show visible.")
    dialog.exec_()
    # pass


@logger.catch
def visit_web():
    """
    visit
    :return:
    """
    QDesktopServices.openUrl(QUrl("https://caozhaoqi.github.io/"))
    logger.info("jump target help web url.")
    pass


@logger.catch
def about_message_lookup():
    """

    :return:
    """
    information_dialog = InformationDialog()
    information_dialog.exec_()
    logger.info("show sis tools basic info.")
    pass

