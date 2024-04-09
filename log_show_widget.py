from PyQt5.QtWidgets import QMessageBox,QApplication, QTextEdit,QWidget,QPushButton,QHBoxLayout,QVBoxLayout,QFileDialog,QSplitter,QDialog
from PyQt5.QtCore import Qt,pyqtSignal,QEvent,QMimeData,QFile, QIODevice, QByteArray,QBuffer,QFileInfo,QUrl,QIODevice
from PyQt5.QtGui import QTextCharFormat, QTextCursor,QTextBlock,QCursor, QTextOption,QFontMetrics,QKeySequence,QColor,QPixmap,QClipboard,QImage, QImageReader, QTextDocumentFragment
from qfluentwidgets import RoundMenu,Action
from text_data import TextData
from large_text_edit import LargeTextEdit
from qfluentwidgets import RoundMenu,Action,MenuAnimationType
import os
from tab_widget import TabWidget
from Result import ResultType
import logging

class ResultTextEdit(QTextEdit):
    sig_select_line = pyqtSignal(str)
    sig_jump_line = pyqtSignal(int)
    sig_select_content = pyqtSignal(str)
    def __init__(self, parent=None):
        super(ResultTextEdit, self).__init__(parent)
        self.context_menu = RoundMenu(self)
        # TODO move plugin menue class out
        add_comment_action = Action("add comment",self)
        self.context_menu.addAction(add_comment_action)
        add_comment_action.triggered.connect(self.add_select_to_comment) 
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.sig_select_line.connect(self.process_select_line_text)

    def process_select_line_text(self,text):
        parts = text.split(":*:")
        if len(parts) > 1:
            extracted_part = parts[0]
            print("Extracted:", extracted_part)
            # check is num
            if extracted_part.isdigit():
                num = int(extracted_part)
                logging.info(f'emit jump line num:{num}')
                self.sig_jump_line.emit(num)

    def add_select_to_comment(self):
        select_text = self.get_selected_text()
        self.sig_select_content.emit(select_text)
        # self.jira_comment_edit.show()
        # self.jira_comment_edit.add_comment(select_text)

    def get_selected_text(self):
        selected_text = self.textCursor().selection().toHtml()
        return selected_text
    
    def highlight_line(self, line_number):
        block = self.document().findBlockByLineNumber(line_number)

        highlight_format = QTextCharFormat()
        highlight_format.setBackground(Qt.yellow)

        cursor = self.textCursor()
        cursor.setPosition(block.position())
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        cursor.mergeCharFormat(highlight_format)

    def clean_highlight(self):
        cursor = QTextCursor(self.document())
        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.End,QTextCursor.KeepAnchor)
        format = QTextCharFormat()
        format.setBackground(QColor("white"))
        cursor.setCharFormat(format)

    def show_context_menu(self, pos):
        self.context_menu.exec_(self.mapToGlobal(pos),aniType=MenuAnimationType.DROP_DOWN)

    def mousePressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            cursor = self.cursorForPosition(event.pos())
            cursor.select(cursor.LineUnderCursor)
            block = cursor.block()
            line_number = block.blockNumber()
            text = block.text()
            logging.debug(f"select line text:{text}")
            self.clean_highlight()
            self.highlight_line(line_number)
            self.sig_select_line.emit(text)
        else:
            super(ResultTextEdit, self).mousePressEvent(event)

class LogTextProcessWidget(QWidget):
    sig_select_content = pyqtSignal(str)
    def __init__(self, text_data,parent=None) -> None:
        super().__init__(parent)
        self.init_ui()
        self.large_text_edit = LargeTextEdit(text_data,self)
        self.splitter.addWidget(self.large_text_edit)
        self.plugin_result_view = ResultTextEdit(self)
        self.splitter.addWidget(self.plugin_result_view)

        self.plugin_result_view.setReadOnly(True)
        self.plugin_result_view.setWordWrapMode(QTextOption.NoWrap)
        self.plugin_result_view.hide()
        self.plugin_result_view.sig_jump_line.connect(self.large_text_edit.jump_line)
        self.plugin_result_view.sig_select_content.connect(self.sig_select_content)

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
            if item.GetResultType() == ResultType.TEXT or item.GetResultType() == ResultType.TEXT_AND_NUM:
                self.plugin_result_view.append(item.GetResult())
            elif item.GetResultType() == ResultType.IMAGE:
                self.plugin_result_view.append('\n')
                self.insert_image(item.GetResult())
                # cursor = self.plugin_result_view.textCursor()
                # cursor.movePosition(QTextCursor.End)
                # cursor.insertImage(item.GetResult())
        self.plugin_result_view.append('\n\n')

    def insert_image(self, image: QImage, fmt: str = "png"):
        data = QByteArray()
        buffer = QBuffer(data)
        image.save(buffer, fmt)
        base64_data = str(data.toBase64())[2:-1]
        data = f'<img src="data:image/{fmt};base64,{base64_data}" />'
        fragment = QTextDocumentFragment.fromHtml(data)
        self.plugin_result_view.textCursor().insertFragment(fragment)


class LogShowWidget(TabWidget):
    sig_select_content = pyqtSignal(str)
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def open_log(self,file_path):
        with open(file_path,'r') as file:
            # TODO don't read all to ram
            data = file.read()
            text_data = TextData(data)
            log_text_widget = LogTextProcessWidget(text_data,self)
            log_text_widget.sig_select_content.connect(self.sig_select_content)
            self.stack_widget.addWidget(log_text_widget)
            key = self.get_tab_key()
            file_name = os.path.basename(file_path)
            self.tab_bar.addTab(routeKey=key,
                                    text=file_name,
                                    onClick=lambda:self.stack_widget.setCurrentWidget(log_text_widget)
                                    )
            self.key_widget[key] = log_text_widget
            self.tab_bar.setCurrentTab(key)
            self.tab_bar.currentTab().setToolTip(file_name)
            self.stack_widget.setCurrentWidget(log_text_widget)


