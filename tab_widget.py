from PyQt5.QtWidgets import QStackedWidget,QWidget,QVBoxLayout
from PyQt5.QtCore import Qt,pyqtSignal
from qfluentwidgets import TabBar,TabCloseButtonDisplayMode

class TabWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.tab_num = 0
        self.init_ui()
        self.tab_bar.setMovable(True)
        self.tab_bar.setScrollable(True)
        self.tab_bar.setTabShadowEnabled(True)
        self.tab_bar.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.ON_HOVER)

    def init_ui(self):
        self.main_v_layout = QVBoxLayout(self)
        self.tab_bar = TabBar(self)
        self.stack_widget = QStackedWidget(self)

        self.main_v_layout.setContentsMargins(0,0,0,0)
        self.main_v_layout.setSpacing(0)
        self.main_v_layout.addWidget(self.tab_bar)
        self.main_v_layout.addWidget(self.stack_widget)

    def get_tab_key(self)->str:
        key = 'tab_widget'+str(self.tab_num)
        self.tab_num = self.tab_num +1
        return key


