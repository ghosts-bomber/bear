from PyQt5.QtWidgets import QMessageBox, QStackedWidget,QWidget,QPushButton,QHBoxLayout,QVBoxLayout,QFileDialog,QLineEdit
from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtGui import QColor
from ndp_show_widget import NDPShowWidget
from qfluentwidgets import TabBar,TabCloseButtonDisplayMode
from tab_widget import TabWidget
class NDPTapWidget(TabWidget):
    index = 0
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.tab_bar.setMovable(True)
        self.tab_bar.setScrollable(True)
        self.tab_bar.setTabMaximumWidth(120)
        self.tab_bar.setTabShadowEnabled(True)
        self.tab_bar.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.ON_HOVER)
        # self.tab_bar.setTabSelectedBackgroundColor(QColor(255, 255, 255, 125), QColor(255, 255, 255, 50))

        self.add_tab()
        self.tab_bar.tabAddRequested.connect(self.add_tab)

    def add_tab(self):
        ndp_show_widget = NDPShowWidget(self)
        self.stack_widget.addWidget(ndp_show_widget)
        key = self.get_tab_key()
        self.index = self.index + 1
        ndp_show_widget.setObjectName(key)
        ndp_show_widget.sig_aip_tab.connect(self.set_tab_title)
        self.tab_bar.addTab(routeKey=key,text='New tab',icon='',onClick=lambda:self.stack_widget.setCurrentWidget(ndp_show_widget))
        self.key_widget[key] = ndp_show_widget
        self.tab_bar.setCurrentTab(key)
        self.stack_widget.setCurrentWidget(ndp_show_widget)
    

    def set_tab_title(self,key,title):
       self.tab_bar.tab(key).setText(title)

