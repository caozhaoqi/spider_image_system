import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import QVBoxLayout, QTextEdit, QLabel, QDialog
from PyQt5.QtCore import QTimer, QFile, QTextStream, Qt
from loguru import logger

from run import constants
from utils.log_monitor import find_latest_log_file

LOG_FILE_PATTERN = 'sis_v*.log'
LOG_DIR = Path(constants.basic_path) / "log_dir"


class LogDisplayDialog(QDialog):
    """Real-time log viewer dialog"""

    def __init__(self):
        super().__init__()
        self.log_file_name_label = None
        self.timer = None
        self.log_text_edit = None
        self.init_ui()
        self.setup_timer()

    @logger.catch
    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle('Log Viewer')
        self.resize(800, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add file name label
        self.log_file_name_label = QLabel()
        layout.addWidget(self.log_file_name_label)

        # Add scrollable text area
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        layout.addWidget(self.log_text_edit)

    @logger.catch
    def setup_timer(self):
        """Set up timer for periodic log updates"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_log)
        self.timer.start(2500)

    @logger.catch
    def update_log(self):
        """Update log content"""
        if not constants.log_check_visible:
            return

        log_file_path = find_latest_log_file(LOG_FILE_PATTERN, str(LOG_DIR))
        self.log_file_name_label.setText(log_file_path)

        log_file = QFile(log_file_path)
        if not log_file.exists():
            self.log_text_edit.append("Log file does not exist")
            return

        if log_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(log_file)
            stream.setCodec('UTF-8')
            content = stream.readAll()
            self.log_text_edit.append(content)
            log_file.close()

    @logger.catch
    def scroll_to_bottom(self):
        """Scroll text edit to bottom"""
        cursor = self.log_text_edit.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text_edit.setTextCursor(cursor)

    @logger.catch
    def stop_timer(self):
        """Stop the update timer"""
        self.timer.stop()
        logger.debug("Log viewer timer stopped")
        constants.log_check_visible = False

    @logger.catch
    def closeEvent(self, event):
        """Handle dialog close event"""
        logger.debug('Log viewer dialog closing')
        constants.log_check_visible = False
        self.stop_timer()
        super().closeEvent(event)


@logger.catch
def show_log_output_method():
    """Show the log viewer dialog"""
    if not constants.log_check_visible:
        dialog = LogDisplayDialog()
        dialog.showMaximized()
        dialog.setWindowFlag(Qt.WindowMinMaxButtonsHint)
        constants.log_check_visible = True
        logger.info("Log viewer shown")
        dialog.exec_()
    else:
        logger.warning("Log viewer already shown")
