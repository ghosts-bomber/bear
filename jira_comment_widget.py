from jira_api import JiraApi
import base64
import time
import logging
from tools import Tools
from PyQt5.QtWidgets import QMessageBox,QApplication, QTextEdit,QWidget,QPushButton,QHBoxLayout,QVBoxLayout,QFileDialog,QSplitter,QDialog
from PyQt5.QtCore import Qt,pyqtSignal,QEvent,QMimeData,QFile, QIODevice, QByteArray,QBuffer,QFileInfo,QUrl,QIODevice
from PyQt5.QtGui import QImage, QImageReader, QTextDocumentFragment
from qfluentwidgets import InfoBar,InfoBarPosition,PushButton
class TextEdit(QTextEdit):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
    def canInsertFromMimeData(self, source: QMimeData) -> bool:
        return source.hasImage() or source.hasUrls() or \
               super(TextEdit, self).canInsertFromMimeData(source)

    def insertFromMimeData(self, source:QMimeData) -> None:
        if source.hasImage():
            self.insert_image(source.imageData())
        elif source.hasUrls():
            for url in source.urls():
                file_info = QFileInfo(url.toLocalFile())
                ext = file_info.suffix().lower()
                if ext in QImageReader.supportedImageFormats():
                    self.insert_image(QImage(file_info.filePath()), ext)
                else:
                    self.insert_file(url)
        else:
            super(TextEdit, self).insertFromMimeData(source)

    def insert_image(self, image: QImage, fmt: str = "png"):
        data = QByteArray()
        buffer = QBuffer(data)
        image.save(buffer, fmt)
        base64_data = str(data.toBase64())[2:-1]
        data = f'<img src="data:image/{fmt};base64,{base64_data}" />'
        fragment = QTextDocumentFragment.fromHtml(data)
        self.textCursor().insertFragment(fragment)

    def insert_file(self, url: QUrl):
        """插入文件"""
        file = None
        # noinspection PyBroadException
        try:
            file = QFile(url.toLocalFile())
            if not file.open(QIODevice.ReadOnly or QIODevice.Text):
                return
            file_data = file.readAll()
            # noinspection PyBroadException
            try:
                self.textCursor().insertHtml(str(file_data, encoding="utf8"))
            except Exception:
                self.textCursor().insertHtml(str(file_data))
        except Exception:
            if file:
                file.close()

class JiraCommentWidget(QWidget):
    def __init__(self, aip:str,parent=None) -> None:
        super().__init__(parent)
        self.init_ui()
        self.jira_api = JiraApi()
        self.aip = aip
        self.issue = self.jira_api.get_issue(self.aip)
        self.commit_btn.clicked.connect(self.commit_btn_clicked)
        self.commit_and_open_jira_btn.clicked.connect(self.commit_and_open_jira_btn_clicked)

    def init_ui(self):
        main_v_layout = QVBoxLayout(self)
        main_v_layout.setContentsMargins(0,0,0,0)

        self.commment_edit = TextEdit(self)
        btn_widget = QWidget(self)
        main_v_layout.addWidget(self.commment_edit)
        main_v_layout.addWidget(btn_widget)
        
        btn_h_layout = QHBoxLayout(btn_widget)
        btn_h_layout.setSpacing(0)
        btn_h_layout.setContentsMargins(0,0,0,0)
        self.commit_btn = PushButton('提交评论',self)
        self.commit_and_open_jira_btn = PushButton('提交并跳转jira',self)
        self.commit_btn.setFixedWidth(120)
        self.commit_and_open_jira_btn.setFixedWidth(120)
        btn_h_layout.addStretch()
        btn_h_layout.addWidget(self.commit_btn)
        btn_h_layout.addStretch()
        btn_h_layout.addWidget(self.commit_and_open_jira_btn)
        btn_h_layout.addStretch()
    
    def add_comment(self,comment:str):
        self.commment_edit.append(comment)

    def gen_jira_comment(self):
        markdown_content = self.commment_edit.toMarkdown()
        result = ''
        i = 0
        for line in markdown_content.split('\n'):
            if line.startswith('![image](data:image/png;base64,'):
                base64_data = line.split(",")[1][:-1]
                decoded_data = base64.b64decode(base64_data)
                attachment_name= f'{i}.png'
                i = i+1
                self.jira_api.add_issue_attachment_use_bytes(self.issue,decoded_data,attachment_name) 
                result = result+'\n'+self.jira_api.get_image_attachment_comment(attachment_name)+'\n'
            elif line!='':
                result = result + line +'\n'
        return result

    def commit_btn_clicked(self):
        self.commit_comment_to_jira()
        InfoBar.info(
            title='info',
            content="评论已提交",
            orient=Qt.Horizontal,
            isClosable=False,   # disable close button
            position=InfoBarPosition.BOTTOM_LEFT,
            duration=2000,
            parent=self
        ) 

    def commit_and_open_jira_btn_clicked(self):
        self.commit_comment_to_jira()
        Tools.open_file_use_system_default(Tools.get_jira_visit_link(self.aip))

    def commit_comment_to_jira(self):
        comment = self.gen_jira_comment()
        logging.info(f'add comment:{comment}')
        # wait jira system process attachment
        time.sleep(2)
        self.jira_api.add_issue_comment(self.issue,comment)


