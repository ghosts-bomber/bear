import logging
import datetime
import sys
from cyber_record.record import Record
from PyQt5.QtWidgets import QWidget,QPushButton,QHBoxLayout,QVBoxLayout,QMainWindow
from PyQt5.QtCore import Qt, pyqtSignal
from check_item_table import CheckItemTable
from channels_view_widget import ChannelsViewWidget

class RecordViewWidget(QWidget):
    parse_record_signal = pyqtSignal()
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.init_ui()
        self.parse_record_signal.connect(self.parse_record_info)
        self.check_table.check_change.connect(self.process_record_channel)

    def init_ui(self):
        hLayout = QHBoxLayout()
        hLayout.setContentsMargins(0,0,0,0)
        self.check_table = CheckItemTable(self) 
        self.channels_view_widget = ChannelsViewWidget(self)
        hLayout.addWidget(self.check_table)
        hLayout.addWidget(self.channels_view_widget)
        hLayout.setContentsMargins(0,0,0,0)
        hLayout.setStretch(0,2)
        hLayout.setStretch(1,8)
        self.setLayout(hLayout)

    def open_record(self,record_path:str)->bool:
        try:
            self.record = Record(record_path)
            self.parse_record_signal.emit() 
        except Exception as e:
            logging.debug(f"open record fail,path:{record_path} error:{e}")
            return False
        return True
    
    def parse_record_info(self)->None:
        start_time = self.record.get_start_time()
        end_time = self.record.get_end_time()
        i=0
        for channel in self.record.get_channel_cache():
            # channel.message_type
            # channel.message_number
            self.check_table.InsertItem(i,channel.name,channel.name)

    def process_record_channel(self,channel_name:str,checked:bool)->None:
        logging.info(f"process channel: {channel_name} checked:{checked}")
        if checked:
            text_data = ''
            for topic,message,t in self.record.read_messages(topics=channel_name):
                if topic == channel_name:
                    ts = t/1e9
                    dt = datetime.datetime.fromtimestamp(ts)
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S:%f")
                    # msg = 'receive time: '+formatted_time+'\n'+str(message)
                    text_data = text_data+"receive time:{}\n{}".format(formatted_time,message)
            self.channels_view_widget.add_channel_view(channel_name,text_data)
        else:
            self.channels_view_widget.del_channel_view(channel_name)

    
