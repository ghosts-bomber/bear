from PyQt5.QtWidgets import QWidget,QPushButton,QHBoxLayout,QVBoxLayout,QSplitter
from PyQt5.QtCore import Qt
from view_item_widget import ViewItemWidget
class ChannelsViewWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.init_ui()
        self.channel_view_dict = {}

    def init_ui(self):
        self.hLayout = QHBoxLayout()
        self.setLayout(self.hLayout)
        self.splitter = QSplitter(self)
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.hLayout.addWidget(self.splitter)
    def add_channel_view(self,channel_name:str,text_data:str)->None:
        if channel_name not in self.channel_view_dict:
            self.channel_view_dict[channel_name] = ViewItemWidget(channel_name,text_data,self)
            # self.hLayout.addWidget(self.channel_view_dict[channel_name])
            self.splitter.addWidget(self.channel_view_dict[channel_name])

    def del_channel_view(self,channel_name:str)->None:
        if channel_name in self.channel_view_dict:
            # self.splitter.removeWidget(self.channel_view_dict[channel_name])
            self.channel_view_dict.pop(channel_name).close()

    def add_data_to_channel_view(self,channel_name:str,data:str,time:float)->bool:
        if channel_name in self.channel_view_dict:
            self.channel_view_dict[channel_name].add_data(data,time)
            return True
        return False

