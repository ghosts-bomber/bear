from PyQt5.QtWidgets import QMessageBox,QWidget,QPushButton,QHBoxLayout,QVBoxLayout,QFileDialog,QStackedWidget
import logging
from ndp_data import NDPApi
from ndp_login_widget import NDPLoginWidget
from ndp_tap_widget import NDPTapWidget
class NDPMainWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.init_ui()
        self.ndp_login_widget.sig_login_success.connect(self.login_success)

    def init_ui(self):
        self.h_layout = QHBoxLayout(self)
        self.stacked_widget = QStackedWidget(self)
        self.ndp_login_widget = NDPLoginWidget(self)

        self.h_layout.setSpacing(0)
        self.h_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.h_layout)
        self.h_layout.addWidget(self.stacked_widget)
        
        self.stacked_widget.addWidget(self.ndp_login_widget)
        self.stacked_widget.setCurrentWidget(self.ndp_login_widget)

    def login_success(self):
        logging.info('login success')
        self.ndp_tap_widget = NDPTapWidget(self)
        self.stacked_widget.addWidget(self.ndp_tap_widget)
        self.stacked_widget.setCurrentWidget(self.ndp_tap_widget)


