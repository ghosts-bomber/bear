import logging
import typing
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ndp_main_widget import NDPMainWidget
from qfluentwidgets import FluentWindow
from qfluentwidgets import FluentIcon as FIF
from open_widget import RecordTabWidget,LogTabWidget

class MainWindow(FluentWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.ndp_main_widget = NDPMainWidget(self)
        self.log_tab_widget = LogTabWidget(self)
        self.record_tab_widget = RecordTabWidget(self)
        self.ndp_main_widget.setObjectName('ndp_main_widget')
        self.log_tab_widget.setObjectName('log_tab_widget')
        self.record_tab_widget.setObjectName('record_tab_widget')

        self.init_navigation()
        self.init_window()
        
    def init_navigation(self):
        self.addSubInterface(self.ndp_main_widget,FIF.CALORIES,'AIP/GC')
        self.addSubInterface(self.log_tab_widget,FIF.DOCUMENT,'Open log')
        self.addSubInterface(self.record_tab_widget,FIF.VIDEO,'Open record')

    def init_window(self):
        # self.setWindowIcon(QIcon(''))
        self.resize(1400,1000)
        self.setWindowTitle('Bear')
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

