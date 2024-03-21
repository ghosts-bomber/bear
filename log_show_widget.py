from PyQt5.QtWidgets import QMessageBox, QStackedWidget, QTextEdit,QWidget,QPushButton,QHBoxLayout,QVBoxLayout,QFileDialog,QSplitter
from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtGui import QColor,QTextOption
from qfluentwidgets import TabBar,TabCloseButtonDisplayMode
from text_data import TextData
from large_text_edit import LargeTextEdit
import os
from tab_widget import TabWidget
from Result import ResultType

class LogTextProcessWidget(QWidget):
    def __init__(self, text_data,parent=None) -> None:
        super().__init__(parent)
        self.init_ui()
        self.large_text_edit = LargeTextEdit(text_data,self)
        self.splitter.addWidget(self.large_text_edit)
        self.plugin_result_view = QTextEdit(self)
        self.splitter.addWidget(self.plugin_result_view)

        self.plugin_result_view.setReadOnly(True)
        self.plugin_result_view.setWordWrapMode(QTextOption.NoWrap)
        self.plugin_result_view.hide()

        self.large_text_edit.sig_plugin_results.connect(self.show_result)

    def init_ui(self):
        self.main_h_layout = QHBoxLayout(self)
        self.main_h_layout.setContentsMargins(0,0,0,0)
        self.splitter = QSplitter(self)
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.main_h_layout.addWidget(self.splitter)

    def show_result(self,results):
        self.plugin_result_view.show()
        for item in results:
            if item.GetResultType() == ResultType.TEXT:
                self.plugin_result_view.append(item.GetResult())
        
        self.plugin_result_view.append('\n\n')


 

class LogShowWidget(TabWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def open_log(self,file_path):
        with open(file_path,'r') as file:
            # TODO don't read all to ram
            data = file.read()
            text_data = TextData(data)
            log_text_widget = LogTextProcessWidget(text_data,self)
            self.stack_widget.addWidget(log_text_widget)
            key = self.get_tab_key()
            file_name = os.path.basename(file_path)
            self.tab_bar.addTab(routeKey=key,
                                    text=file_name,
                                    onClick=lambda:self.stack_widget.setCurrentWidget(log_text_widget)
                                    )
            self.tab_bar.setCurrentTab(key)
            self.tab_bar.currentTab().setToolTip(file_name)
            self.stack_widget.setCurrentWidget(log_text_widget)


