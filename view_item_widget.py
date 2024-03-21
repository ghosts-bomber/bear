from PyQt5.QtWidgets import QWidget,QPushButton,QHBoxLayout,QVBoxLayout,QTextEdit,QLabel
from PyQt5.QtGui import QTextCursor,QTextBlock,QCursor
from large_text_edit import LargeTextEdit
from text_data import TextData
import logging
class ViewItemWidget(QWidget): 
    def __init__(self, channel_name:str,text_data:str,parent=None) -> None: 
        super().__init__(parent) 
        self.channel_name = channel_name 
        self.text_data = TextData(text_data)
        self.init_ui()

    def init_ui(self)->None: 
        self.label = QLabel(self.channel_name,self)
        self.text_edit = LargeTextEdit(self.text_data,self)
        vLayout = QVBoxLayout()
        vLayout.setContentsMargins(0,0,0,0)
        vLayout.addWidget(self.label)
        vLayout.addWidget(self.text_edit)
        self.setLayout(vLayout)

'''
    def get_end_cursor(self)->int:
        self.text_edit.textCursor().movePosition(QTextCursor.MoveOperation.End)
        return self.get_current_cursor()

    def get_current_cursor(self)->int:
        return self.text_edit.textCursor().position()

    def get_current_contain_lines(self)->int:
        text_edit_height = self.text_edit.height()
        average_line_height = self.text_edit.fontMetrics().height()
        num_lines = text_edit_height // average_line_height
        return num_lines

    def scroll_changed(self):
        scroll_bar = self.text_edit.verticalScrollBar()
        max_value = scroll_bar.maximum()
        logging.debug(f"scroll bar maximum:{max_value}")
        current_value = scroll_bar.value()
        contain_line_num = self.get_current_contain_lines()
        self.text_edit.setText("")
        if contain_line_num > len(self.plain_text_lines):
            for line in self.plain_text_lines:
                self.text_edit.append(line)
        elif current_value+contain_line_num > len(self.plain_text_lines):
            for line in self.plain_text_lines[-contain_line_num:]:
                self.text_edit.append(line)
        else:
            for line in self.plain_text_lines[current_value:current_value+contain_line_num]:
                self.text_edit.append(line)
'''


