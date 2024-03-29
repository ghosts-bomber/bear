from re import search
from PyQt5.QtWidgets import QPushButton, QScroller, QWidget,QHBoxLayout,QVBoxLayout,QTextEdit,QLabel,QScrollBar,QAbstractSlider,QShortcut,QLineEdit,QDialog,QMenu,QAction,QFileDialog
from PyQt5.QtGui import QTextCharFormat, QTextCursor,QTextBlock,QCursor, QTextOption,QFontMetrics,QKeySequence,QColor
from PyQt5.QtCore import Qt,pyqtSignal
import logging
from text_data import TextData
from plugin_menu import PluginMenu
from qfluentwidgets import RoundMenu,Action,MenuAnimationType

class SearchWidget(QWidget):
    sig_search= pyqtSignal()
    jump_line = pyqtSignal(int)
    show_search = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.init_ui()
        self.search_edit.returnPressed.connect(self.send_search_sig)
        self.down_btn.clicked.connect(self.down_btn_clicked)
        self.up_btn.clicked.connect(self.up_btn_clicked)
        self.show_all_search_btn.clicked.connect(self.show_all_search_btn_clicked)
        self.search_lines = []
        self.current_num = 0
        
    def init_ui(self):
        self.search_edit = QLineEdit(self)
        self.search_label = QLabel(self)
        self.up_btn = QPushButton("↑",self)
        self.down_btn = QPushButton("↓",self)
        self.show_all_search_btn = QPushButton("all",self)
        self.h_layout = QHBoxLayout(self)
        
        self.h_layout.addStretch()
        self.h_layout.addWidget(self.search_edit)
        self.h_layout.addWidget(self.search_label)
        self.h_layout.addWidget(self.up_btn)
        self.h_layout.addWidget(self.down_btn)
        self.h_layout.addWidget(self.show_all_search_btn)
        self.h_layout.setContentsMargins(0,0,0,0)

    def set_search_focus(self):
        self.search_edit.setFocus()

    def hide(self):
        self.search_edit.clear()
        self.search_lines.clear()
        self.current_num = 0
        super().hide()

    def clear(self):
        self.search_edit.clear()

    def set_search_text(self,text):
        self.search_edit.setText(text)

    def get_search_text(self):
        return self.search_edit.text()
    def get_search_result_lines(self):
        return self.search_lines
    def send_search_sig(self):
        self.sig_search.emit()

    def set_search_result_info(self,search_lines,current_num):
        self.search_lines = search_lines
        self.current_num = current_num
        self.update_search_label()

    def update_search_label(self):
        self.search_label.setText("{}/{}".format(self.current_num,len(self.search_lines)))
        
    def down_btn_clicked(self):
        if self.current_num<len(self.search_lines):
            self.current_num = self.current_num+1
        else:
            self.current_num = 1
        self.jump_line.emit(self.search_lines[self.current_num-1])  
        self.update_search_label()

    def up_btn_clicked(self):
        if self.current_num > 1:
            self.current_num = self.current_num - 1
        else:
            self.current_num = len(self.search_lines)
        self.jump_line.emit(self.search_lines[self.current_num-1])  
        self.update_search_label()

    def show_all_search_btn_clicked(self):
        self.show_search.emit()

class LargeTextEdit(QWidget):
    sig_plugin_results = pyqtSignal(list)
    def __init__(self, text_data,parent=None) -> None:
        super().__init__(parent)
        self.text_data = text_data
        self.init_ui()
        self.scroll_bar_value_change(0)
        self.scroll_bar.valueChanged.connect(self.scroll_bar_value_change)
        
        self.ctrl_f_shortcut = QShortcut(QKeySequence(Qt.Modifier.CTRL+Qt.Key.Key_F),self) 
        self.ctrl_f_shortcut.activated.connect(self.show_search_widget)
        self.ctrl_f_shortcut.setEnabled(False)
        self.search_widget.sig_search.connect(self.search_text)
        
        self.esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape),self)
        self.esc_shortcut.setEnabled(False)
        self.esc_shortcut.activated.connect(self.hide_search_widget)
        
        self.start = 0
        self.count = 0
        self.search_widget.jump_line.connect(self.jump_line)
        self.search_widget.show_search.connect(self.show_search_result_widget)
        self.setMouseTracking(True)
        # self.installEventFilter(self)

    def init_ui(self):
        self.line_number_edit = QTextEdit(self)
        self.main_edit = QTextEdit(self)
        self.scroll_bar = QScrollBar(self)
        # self.title = QLabel(self)
        self.search_widget = SearchWidget(self)

        main_layout = QVBoxLayout(self)
        text_edit_layout = QHBoxLayout()
        # main_layout.addWidget(self.title)
        main_layout.addWidget(self.search_widget)
        main_layout.addLayout(text_edit_layout)
        text_edit_layout.addWidget(self.line_number_edit)
        text_edit_layout.addWidget(self.main_edit)
        text_edit_layout.addWidget(self.scroll_bar)
        self.main_edit.verticalScrollBar().setDisabled(True)
        
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(0,0,0,0)
        text_edit_layout.setSpacing(0)
        text_edit_layout.setContentsMargins(0,0,0,0)
        
        self.search_widget.hide()
        self.main_edit.setWordWrapMode(QTextOption.NoWrap)
        self.main_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.main_edit.setReadOnly(True)
        self.line_number_edit.setWordWrapMode(QTextOption.NoWrap)
        self.line_number_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.line_number_edit.setReadOnly(True)
        self.resize_line_number_edit_width() 
        line_count = self.text_data.get_line_count()
        self.scroll_bar.setMinimum(0)
        self.scroll_bar.setMaximum(line_count)

        self.context_menu = RoundMenu(self.main_edit)
        # TODO move plugin menue class out
        self.plugin_menu = PluginMenu(self.main_edit)
        self.plugin_menu.sig_plugin_triggered.connect(self.plugin_process)
        self.context_menu.addMenu(self.plugin_menu.get_plugin_menu())
        export_action = Action("export",self.main_edit)
        self.context_menu.addAction(export_action)
        export_action.triggered.connect(self.export) 
        self.main_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.main_edit.customContextMenuRequested.connect(self.show_context_menu)


    def resize_line_number_edit_width(self):
        font = self.line_number_edit.font()
        font_metrics = QFontMetrics(font) 
        text_width = font_metrics.width(str(self.text_data.get_line_count()+10))+10
        self.line_number_edit.setMaximumWidth(text_width)
        self.line_number_edit.setMinimumWidth(text_width)
 
    def scroll_bar_value_change(self,value):
        self.count = self.get_container_count()
        count = self.count+100
        text = self.text_data.get_lines_combine(value,count)
        self.start = value
        self.main_edit.setText(text)
        line_num = ''
        for i in range(value,value+count):
            line_num = line_num+str(i+1)+'\n'
        self.line_number_edit.setText(line_num)
        self.clean_highlight()
        self.highlight_search()

    def wheelEvent(self,event):
        delta = event.angleDelta().y()
        if delta<0:
            self.scroll_bar.triggerAction(QAbstractSlider.SliderAction.SliderSingleStepAdd)
        else:
            self.scroll_bar.triggerAction(QAbstractSlider.SliderAction.SliderSingleStepSub)
        event.accept()

    def resizeEvent(self, event) -> None:
        self.scroll_bar_value_change(self.scroll_bar.value())
        return super().resizeEvent(event)

    def get_container_count(self):
        main_edit_font = self.main_edit.font()
        main_edit_size = self.main_edit.viewport().size()
        main_edit_font_metrics = QFontMetrics(main_edit_font)
        line_height = main_edit_font_metrics.lineSpacing()
        max_lines = main_edit_size.height() // line_height
        return max_lines 

    def show_search_widget(self):
        logging.info("show search")
        self.search_widget.show()
        if self.main_edit.textCursor().hasSelection():
            select_text = self.main_edit.textCursor().selectedText()
            self.search_widget.set_search_text(select_text)
        self.search_widget.set_search_focus()

    def hide_search_widget(self):
        self.search_widget.hide()
        self.search_widget.clear()
        self.clean_highlight()

    def clean_highlight(self):
        cursor = QTextCursor(self.main_edit.document())
        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.End,QTextCursor.KeepAnchor)
        format = QTextCharFormat()
        format.setBackground(QColor("white"))
        cursor.setCharFormat(format)

    def highlight_search(self):
        if not self.search_widget.isVisible():
            return 
        text = self.search_widget.get_search_text() 
        if text:
            cursor = QTextCursor(self.main_edit.document())
            format = QTextCharFormat()
            format.setBackground(QColor("yellow"))
            while not cursor.isNull() and not cursor.atEnd():
                cursor = self.main_edit.document().find(text,cursor)
                if not cursor.isNull():
                    cursor.mergeCharFormat(format)

    def search_text(self):
        self.clean_highlight() 
        text = self.search_widget.get_search_text()
        lines = self.text_data.search(text)
        if len(lines) <=0:
            return
        current_nu = -1
        b_jump = True
        for index,nu in enumerate(lines):
            current_nu = index
            if nu >= self.start and nu < self.start+self.count:
                b_jump = False
                break
            elif nu >= self.start+self.count:
                break
        if b_jump:
            self.scroll_bar.setValue(lines[current_nu])
        self.highlight_search()
        self.search_widget.set_search_result_info(lines,current_nu+1)

    def jump_line(self,line_number):
        if line_number >=self.start and line_number < self.start+self.count:
            return
        logging.info(f'line jump num:{line_number}')
        dst_number = line_number - self.count//2
        if dst_number<0:
            dst_number = 0
        self.scroll_bar.setValue(dst_number)
        self.highlight_line(line_number-dst_number)
    
    def highlight_line(self, line_number):
        block = self.main_edit.document().findBlockByLineNumber(line_number)

        highlight_format = QTextCharFormat()
        highlight_format.setBackground(Qt.yellow)

        cursor = self.main_edit.textCursor()
        cursor.setPosition(block.position())
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        cursor.mergeCharFormat(highlight_format)

    def show_search_result_widget(self):
        lines = self.search_widget.get_search_result_lines()
        search_result = self.text_data.combine_search_result(lines)
        dialog = QDialog(self)
        h_layout = QHBoxLayout(dialog)
        large_text_edit = LargeTextEdit(search_result)
        h_layout.addWidget(large_text_edit)
        dialog.show()

    def set_shortcut_enable(self,enable):
        self.esc_shortcut.setEnabled(enable)
        self.ctrl_f_shortcut.setEnabled(enable)

    def show_context_menu(self, pos):
        self.context_menu.exec_(self.main_edit.mapToGlobal(pos),aniType=MenuAnimationType.DROP_DOWN)
    
    def plugin_process(self,plugin_name):
        results = self.plugin_menu.plugin_process(plugin_name,self.text_data)
        self.sig_plugin_results.emit(results) 

    def export(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export File", "", "Text Files (*.txt)")
        if file_path:
            self.text_data.write_to_file(file_path)
    
    def enterEvent(self, event) -> None:
        self.set_shortcut_enable(True)
        return super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        self.set_shortcut_enable(False)
        return super().leaveEvent(event)

    # def eventFilter(self, source,event):
    #     if event.type()==event.FocusIn:
    #         self.ctrl_f_shortcut.setEnabled(True)
    #         logging.info("focusIn")
    #     elif event.type() == event.FocusOut:
    #         self.ctrl_f_shortcut.setEnabled(False)
    #         logging.info("focusOut")
    #     return super().eventFilter(source,event)    

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    text_data = TextData("1\n2\n3\n4\n5\n6\n7\n8\n")
    win = LargeTextEdit(text_data)
    win.show()
    sys.exit(app.exec_())

