from PyQt5.QtWidgets import QWidget,QPushButton,QHBoxLayout,QVBoxLayout,QFileDialog,QStackedWidget,QMessageBox
from PyQt5.QtCore import Qt,QUrl
from record_view_widget import RecordViewWidget
import logging
from tab_widget import TabWidget
from log_show_widget import LogShowWidget

class OpenBtnWidget(QWidget):
    def __init__(self, parent: None) -> None:
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_v_layout = QVBoxLayout(self)
        self.stack_widget = QStackedWidget(self)
        btn_widget = QWidget(self)
        btn_v_layout = QVBoxLayout(btn_widget)
        self.btn = QPushButton(self)

        main_v_layout.setContentsMargins(0,0,0,0)
        main_v_layout.setSpacing(0)
        main_v_layout.addWidget(self.stack_widget)

        btn_v_layout.setContentsMargins(0,0,0,0)
        btn_v_layout.setSpacing(0)
        btn_v_layout.addWidget(self.btn,0,Qt.AlignmentFlag.AlignCenter)
        self.stack_widget.addWidget(btn_widget)
        self.stack_widget.setCurrentWidget(btn_widget)

class OpenLogWidget(OpenBtnWidget):
    def __init__(self, parent: None) -> None:
        super().__init__(parent)
        self.btn.setText('open log')
        self.btn.clicked.connect(self.open_log_btn_clicked)

    def open_log_btn_clicked(self):
        log_path = QFileDialog.getOpenFileName(self)
        if len(log_path)==0 or len(log_path[0])==0:
            return
        logging.debug(f'get open file url:{log_path[0]}')
        self.log_show_widget = LogShowWidget(self)
        self.log_show_widget.open_log(log_path[0])
        self.stack_widget.addWidget(self.log_show_widget)
        self.stack_widget.setCurrentWidget(self.log_show_widget)

    
class OpenRecordWidget(OpenBtnWidget):
    def __init__(self, parent: None) -> None:
        super().__init__(parent)
        self.btn.setText('open record')
        self.btn.clicked.connect(self.open_record_btn_clicked)

    def open_record_btn_clicked(self):
        record_path = QFileDialog.getOpenFileName(self)
        if len(record_path)==0 or len(record_path[0])==0:
            return
        logging.debug(f'get open file url:{record_path[0]}')
        self.record_view_widget = RecordViewWidget(self)
        if self.record_view_widget.open_record(record_path[0]) == False:
            self.record_view_widget = None
            QMessageBox.warning(self,'','file is not record',)
            return
        self.stack_widget.addWidget(self.record_view_widget)
        self.stack_widget.setCurrentWidget(self.record_view_widget)

class LogTabWidget(TabWidget):
    def __init__(self, parent: None) -> None:
        super().__init__(parent)
        self.add_tab()
        self.tab_bar.tabAddRequested.connect(self.add_tab)

    def add_tab(self):
        open_log_widget = OpenLogWidget(self)
        self.stack_widget.addWidget(open_log_widget)
        key = self.get_tab_key()
        self.tab_bar.addTab(routeKey=key,
                            text='New tab',
                            onClick=lambda:self.stack_widget.setCurrentWidget(open_log_widget)
                            )
        self.key_widget[key] = open_log_widget
        self.tab_bar.setCurrentTab(key)
        self.stack_widget.setCurrentWidget(open_log_widget)

class RecordTabWidget(TabWidget):
    def __init__(self, parent: None) -> None:
        super().__init__(parent)
        self.add_tab()
        self.tab_bar.tabAddRequested.connect(self.add_tab)

    def add_tab(self):
        open_record_widget = OpenRecordWidget(self)
        self.stack_widget.addWidget(open_record_widget)
        key = self.get_tab_key()
        self.tab_bar.addTab(routeKey=key,
                            text='New tab',
                            onClick=lambda:self.stack_widget.setCurrentWidget(open_record_widget)
                            )
        self.key_widget[key] = open_record_widget
        self.tab_bar.setCurrentTab(key)
        self.stack_widget.setCurrentWidget(open_record_widget)






