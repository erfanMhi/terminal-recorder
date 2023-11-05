import sys
import threading
from datetime import datetime
from typing import Tuple
from pathlib import Path

from pynput import keyboard
from PyQt6.QtCore import Qt, QMetaObject, Q_ARG
# from PyQt6.QtCore import QMetaObject, QObject, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, 
    QTextEdit, QLabel, QSizePolicy)
from PyQt6.QtGui import QPalette, QColor, QTextCursor

from utils.utils import _get_active_app_name

TARGET_APP_NAME = "terminal"
RECORDED_FILE_FOLDER_NAME = "recorded_files"

TEXT_BOX_SPECIAL_KEYS = {
    keyboard.Key.space: ' ',
    keyboard.Key.enter: '\n',
    keyboard.Key.tab: '\t',
    keyboard.Key.backspace: '\b',
    keyboard.Key.delete: '\x7f',
}

SAVING_SPECIAL_KEYS = {
    keyboard.Key.space: ' ',
    keyboard.Key.enter: '\r',
    keyboard.Key.tab: '\t',
    keyboard.Key.esc: '\033',
    keyboard.Key.up: '\033[A',
    keyboard.Key.down: '\033[B',
    keyboard.Key.right: '\033[C',
    keyboard.Key.left: '\033[D',
    keyboard.Key.ctrl: '\033[E',
    keyboard.Key.shift: '\033[F',
    keyboard.Key.backspace: '\x7f',
    keyboard.Key.delete: '\x1b[3~',
    keyboard.Key.alt: '\033[G',
    keyboard.Key.caps_lock: '\033[H',
    keyboard.Key.f1: '\033[OP',
    keyboard.Key.f2: '\033[OQ',
    keyboard.Key.f3: '\033[OR',
    keyboard.Key.f4: '\033[OS',
    keyboard.Key.f5: '\033[15~',
    keyboard.Key.f6: '\033[17~',
    keyboard.Key.f7: '\033[18~',
    keyboard.Key.f8: '\033[19~',
    keyboard.Key.f9: '\033[20~',
    keyboard.Key.f10: '\033[21~',
    keyboard.Key.f11: '\033[23~',
    keyboard.Key.f12: '\033[24~',
}
    
class RecordStatusLabel(QLabel):

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAutoFillBackground(True)
        self.setPalette(QPalette(QColor("#E03C31")))
        self.setText("Record off")
    
    def set_record_on(self):
        self.setText("Record on")
        self.setPalette(QPalette(QColor("#46CB18")))

    def set_record_off(self):
        self.setText("Record off")
        self.setPalette(QPalette(QColor("#E03C31")))


class RecordTextBox(QTextEdit):
    
        def __init__(self):
            super().__init__()
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.setReadOnly(True)  # Disable the text box
            self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self._record_on = False

        # set a file name based on the date and time
        recorded_file_dir = Path(RECORDED_FILE_FOLDER_NAME)
        recorded_file_dir.mkdir(parents=True, exist_ok=True)
        self._file_name = recorded_file_dir / ('recorded_keys' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log")
        self._file_name.touch()

        # Set window title
        self.setWindowTitle("Terminal Recorder")

        # Set window dimensions
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a vertical layout for the central widget
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        ################## Create top Buttons ##################
        button_layout = QHBoxLayout()

        self.record_button = self._create_button("Record", self.handle_record_click)
        button_layout.addWidget(self.record_button)

        self.stop_button = self._create_button("Stop", self.handle_stop_click)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        ########################################################

        # Create a horizontal layout for the status label
        status_layout = QHBoxLayout()

        # Create a label to show the record status
        self.status_label = RecordStatusLabel()
        status_layout.addWidget(self.status_label)

        # Add the status layout to the vertical layout
        layout.addLayout(status_layout)

        self.text_box = RecordTextBox()
        layout.addWidget(self.text_box)

        self.listener_thread = threading.Thread(target=self.start_listener)
        self.listener_thread.start()

    def _create_button(self, text: str, handler: callable) -> QPushButton:
        button = QPushButton(text)
        button.clicked.connect(handler)
        return button

    def start_listener(self):
        with keyboard.Listener(on_press= self.on_key_press, on_release= self.on_key_release) as listener:
            listener.join()

    def handle_record_click(self):
        self._record_on = True
        self.status_label.set_record_on()
        self.record_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def handle_stop_click(self):
        self._record_on = False
        self.status_label.set_record_off()
        self.record_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def on_key_press(self, key: Tuple[keyboard.Key, str]):
        """Called when a key is pressed."""
        try:
            print('App name: ', _get_active_app_name().lower())
            if TARGET_APP_NAME in _get_active_app_name().lower() and self._record_on:
                print('pressed key: ', key)
                self.record_keys(key)

        except AttributeError:
            pass

    def record_keys(self, key: Tuple[keyboard.Key, str]):
        self._record_keys_in_text_box(key)
        self._record_keys_in_file(key)
        
    def _record_keys_in_file(self, key: Tuple[keyboard.Key, str]):
        with open(self._file_name, 'a') as f:
            if key in SAVING_SPECIAL_KEYS:
                key = SAVING_SPECIAL_KEYS[key]
            else:
                key = key.char
            f.write(key)
    
    def _record_keys_in_text_box(self, key: Tuple[keyboard.Key, str]):
        if key in TEXT_BOX_SPECIAL_KEYS:
            key = TEXT_BOX_SPECIAL_KEYS[key]
        else:
            key = key.char
        QMetaObject.invokeMethod(self.text_box, "insertPlainText", value0=Q_ARG(str, key))
        
    def on_key_release(self, key: Tuple[keyboard.Key, str]):
        """Called when a key is released."""
        pass
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())