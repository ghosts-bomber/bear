from PyQt5.QtWidgets import QLabel, QHeaderView,QStackedWidget, QTableView,QWidget,QHBoxLayout,QVBoxLayout,QGridLayout,QSplitter
from PyQt5.QtCore import QModelIndex, QUrl, Qt,pyqtSignal
from PyQt5.QtGui import QColor, QFont, QStandardItemModel,QStandardItem
from qfluentwidgets import SearchLineEdit,ComboBox,Flyout,InfoBarIcon,TableView,RoundMenu,Action,TabBar,TabCloseButtonDisplayMode,Pivot,HyperlinkLabel
from qfluentwidgets import FluentIcon as FIF
from cyber_record.record import logging
from ndp_data import NDPApi,AIPInfo
from config import Config
import tarfile
import os
import re
from datetime import datetime
from tools import Tools
from large_text_edit import LargeTextEdit
from text_data import TextData
from log_show_widget import LogShowWidget
from jira_comment_widget import JiraCommentWidget
class SearchAIPWidget(QWidget):
    sig_aip_info = pyqtSignal(AIPInfo,list,list)
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.init_ui()
        self.search_edit.searchSignal.connect(self.search_edit_enter)
        self.search_edit.returnPressed.connect(self.search_edit_enter)

    def init_ui(self):
        self.h_layout = QHBoxLayout(self)
        self.type_combox = ComboBox(self)
        self.type_combox.addItems(['AIP','GC','DC'])
        _label = QLabel('-',self)
        self.search_edit = SearchLineEdit(self)
        self.h_layout.setContentsMargins(0,0,0,0)
        self.h_layout.setSpacing(0)
        self.h_layout.addStretch()
        self.h_layout.addWidget(self.type_combox)
        self.h_layout.addWidget(_label)
        self.h_layout.addWidget(self.search_edit) 
        self.h_layout.addStretch()

    def set_focus(self):
        self.search_edit.setFocus()

    def search_edit_enter(self):
        aip = self.type_combox.currentText()+'-'+self.search_edit.text()
        s_type = self.type_combox.currentText()
        # if self.type_combox.currentText()=='GC':
        #     s_type = 'GC'
        if aip:
            ndp_api = NDPApi()
            aip_info= ndp_api.search_api(aip,s_type)
            if aip_info:
                log_list,record_list = ndp_api.aip_info(aip_info.aip_id)
                self.sig_aip_info.emit(aip_info,log_list,record_list)
                # TODO delete self
            else:
                logging.error("can't find {}".format(aip))
                Flyout.create(icon=InfoBarIcon.WARNING,
                              title='warning',
                              content=self.tr("can't find ")+aip,
                              target=self.search_edit,
                              parent= self
                              )

LOG_INFO_COL = 0
LOG_SIZE_COL = 1
LOG_OPERATOR_COL = 2

RECORD_URL_COL = 0
JIRA_KEY = 'jira'
class AIPInfoWidget(QWidget):
    log_widget_index = 0
    def __init__(self, aip:str,parent=None) -> None:
        super().__init__(parent)
        self.aip = aip
        self.init_ui()

        self.ndp_api = NDPApi()
        self.config = Config()

        self.log_model = QStandardItemModel()
        self.record_model = QStandardItemModel()
        self.log_table.setModel(self.log_model)
        self.record_table.setModel(self.record_model)

        self.log_model.setColumnCount(2)
        self.log_model.setHeaderData(LOG_INFO_COL,Qt.Orientation.Horizontal,'name')
        self.log_model.setHeaderData(LOG_SIZE_COL,Qt.Orientation.Horizontal,'size')
        # self.log_model.setHeaderData(LOG_OPERATOR_COL,Qt.Orientation.Horizontal,'operator')

        self.record_model.setColumnCount(1)
        self.record_model.setHeaderData(RECORD_URL_COL,Qt.Orientation.Horizontal,'url')

        self.log_table.horizontalHeader().setSectionResizeMode(LOG_INFO_COL,QHeaderView.ResizeMode.Stretch)
        self.log_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.log_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.log_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.log_table.customContextMenuRequested.connect(self.show_log_table_menu)
        self.log_table.setWordWrap(True)

        self.record_table.horizontalHeader().setSectionResizeMode(RECORD_URL_COL,QHeaderView.ResizeMode.Stretch)
        self.record_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.record_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.log_table.setWordWrap(True)

        self.log_show_widget.sig_select_content.connect(self.add_comment)
        self.log_table.doubleClicked.connect(self.log_table_double_clicked)
        self.record_table.doubleClicked.connect(self.record_table_double_clicked)

    def init_ui(self):
        self.h_layout = QHBoxLayout(self)
        self.v_layout = QVBoxLayout()
        self.aip_v_layout = QVBoxLayout()
        self.log_show_v_layout = QVBoxLayout()
        
        self.left_stack_widget = QStackedWidget(self)
        self.left_widget = QWidget(self)
        self.left_widget.setLayout(self.v_layout)
        self.pivot_widget = Pivot(self)
        self.v_layout.addWidget(self.left_stack_widget)
        self.v_layout.addWidget(self.pivot_widget)

        self.aip_widget = QWidget(self)
        self.jira_comment_widget = JiraCommentWidget(self.aip,self)
        self.left_stack_widget.addWidget(self.aip_widget)
        self.left_stack_widget.addWidget(self.jira_comment_widget)
        self.left_stack_widget.setCurrentWidget(self.aip_widget)

        self.splitter = QSplitter(self)
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
            
        aip_label_tip = QLabel('aip：',self)
        car_id_label_tip = QLabel('car id：',self)
        cyberrt_version_label_tip = QLabel('cyberrt version：',self)
        error_time_tip = QLabel('问题时间点：',self)
        error_info_tip = QLabel('故障描述：',self)
        dv_label_tip = QLabel('dv：',self)

        self.aip_hyperlink_label = HyperlinkLabel(
            text=self.aip,
            parent=self
        )

        self.car_id_label = QLabel(self)
        self.cyberrt_version_label = QLabel(self)
        self.error_time_label = QLabel(self)
        self.error_info_label = QLabel(self)
        self.dv_hyperlink_label = HyperlinkLabel(
            text='看dv，点我',
            parent=self
        )

        self.log_table = QTableView(self)
        self.record_table = QTableView(self)

        self.log_show_widget = LogShowWidget(self)

        self.box_layout = QGridLayout()
        self.box_layout.setContentsMargins(0,0,0,0)
        self.box_layout.addWidget(aip_label_tip,0,0)
        self.box_layout.addWidget(self.aip_hyperlink_label,0,1)
        self.box_layout.addWidget(car_id_label_tip,1,0)
        self.box_layout.addWidget(self.car_id_label,1,1)
        self.box_layout.addWidget(cyberrt_version_label_tip,2,0)
        self.box_layout.addWidget(self.cyberrt_version_label,2,1)
        self.box_layout.addWidget(error_time_tip,3,0)
        self.box_layout.addWidget(self.error_time_label,3,1)
        self.box_layout.addWidget(error_info_tip,4,0)
        self.box_layout.addWidget(self.error_info_label,4,1)
        self.box_layout.addWidget(dv_label_tip,5,0)
        self.box_layout.addWidget(self.dv_hyperlink_label,5,1)
       
    
        self.aip_widget.setLayout(self.aip_v_layout) 
        self.aip_v_layout.setContentsMargins(0,0,0,0)
        self.aip_v_layout.addLayout(self.box_layout)
        self.aip_v_layout.addWidget(self.log_table)
        self.aip_v_layout.addWidget(self.record_table)
        self.aip_v_layout.addStretch()
        

        self.h_layout.setContentsMargins(0,0,0,0)
        self.splitter.addWidget(self.left_widget)

        # self.h_splitter = QSplitter(self)
        # self.h_splitter.setOrientation(Qt.Orientation.Horizontal)
        # self.h_Layout.addWidget(self.splitter)
        
        # self.log_show_v_layout.setContentsMargins(0,0,0,0)
        # self.log_show_v_layout.setSpacing(0)
        # self.log_show_v_layout.addWidget(self.log_show_widget)

        self.splitter.addWidget(self.log_show_widget)
        self.h_layout.addWidget(self.splitter)
        self.splitter.setSizes([230,770])

        self.pivot_widget.addItem(
            routeKey='1',
            onClick=lambda:self.left_stack_widget.setCurrentWidget(self.aip_widget),
            text = 'info'
        )
        self.pivot_widget.addItem(
            routeKey=JIRA_KEY,
            onClick=lambda:self.left_stack_widget.setCurrentWidget(self.jira_comment_widget),
            text = 'comment'
        )
        self.pivot_widget.setCurrentItem('1')


    def set_aip_info(self,aip_info,log_list,record_list):
        # self.aip_label.setText(aip)
        self.aip_hyperlink_label.setUrl(QUrl(aip_info.jira_link))
        self.car_id_label.setText(aip_info.car_id)
        self.cyberrt_version_label.setText(aip_info.cyberrt_version)
        self.error_info_label.setText(aip_info.remark)
        self.error_time_label.setText(aip_info.datetime)
        self.dv_hyperlink_label.setUrl(QUrl(aip_info.dv_link))
    
        for i,iter in enumerate(log_list):
            log_info_item = QStandardItem(iter['name'])
            log_info_item.setData(iter['name'],Qt.ItemDataRole.ToolTipRole)
            log_info_item.setData(iter['objName'],Qt.ItemDataRole.UserRole)
            if self.check_log_container_error_time(aip_info.datetime,iter['name']):
                log_info_item.setData(QColor('red'),Qt.ItemDataRole.TextColorRole)
            self.log_model.setItem(i,LOG_INFO_COL,log_info_item)
            self.log_model.setItem(i,LOG_SIZE_COL,QStandardItem(str(iter['filesize'])))
            # self.log_model.setItem(i,LOG_OPERATOR_COL,QStandardItem())
    
        for i,iter in enumerate(record_list):
            self.record_model.setItem(i,RECORD_URL_COL,QStandardItem(iter))

        self.log_table.resizeRowsToContents()
        self.record_table.resizeRowsToContents()

    def get_log_file_from_index(self,index):
        log_info_index = self.log_model.index(index.row(),LOG_INFO_COL)
        log_name = self.log_model.data(log_info_index) 
        log_obj_name = self.log_model.data(log_info_index,Qt.ItemDataRole.UserRole) 
        log_size_index = self.log_model.index(index.row(),LOG_SIZE_COL)
        log_size = int(self.log_model.data(log_size_index))
        
        directory = self.config.get_tmp_dict()+'/'+self.aip
        Tools.create_directroy_if_not_exists(directory)
        local_path = directory+'/'+log_name
        if not os.path.exists(local_path) or os.path.getsize(local_path)!=log_size:
            url = self.ndp_api.get_file_download_url(log_obj_name)
            self.ndp_api.download_url(url,local_path)

        with tarfile.open(local_path,'r:gz') as tar:
            logging.info(f'extractall {local_path}')
            extracted_file_name = tar.getnames()[0].split("/")[-1]
            logging.info(f'extracted file name: {extracted_file_name}')
            tar.extractall(path=directory)
            extracted_file_path = directory+'/'+extracted_file_name
            return extracted_file_path
        return ''

    def log_table_double_clicked(self,index):
        extracted_file_path = self.get_log_file_from_index(index)
        self.open_log_use_text_edit(extracted_file_path)

    def open_log_use_system_default(self,index):
        extracted_file_path = self.get_log_file_from_index(index)
        Tools.open_file_use_system_default(extracted_file_path)

    def open_log_use_text_edit(self,file_path):
        self.log_show_widget.open_log(file_path)

    def record_table_double_clicked(self,index):
        pass

    def add_comment(self,content:str):
        self.jira_comment_widget.add_comment(content)
        self.left_stack_widget.setCurrentWidget(self.jira_comment_widget)
        self.pivot_widget.setCurrentItem(JIRA_KEY)

    def show_log_table_menu(self,pos):
        menu = RoundMenu(self.log_table) 
        open_action = Action(self.tr('Open'))
        open_system_defalue_action = Action(self.tr('Open with system default'))
        index = self.log_table.indexAt(pos)
        open_action.triggered.connect(lambda:self.log_table_double_clicked(index))
        open_system_defalue_action.triggered.connect(lambda:self.open_log_use_system_default(index))
        menu.addAction(open_action)
        menu.addAction(open_system_defalue_action)
        menu.exec(self.log_table.mapToGlobal(pos),ani=True)

    def check_log_container_error_time(self,error_time_str,log_name)->bool:
        match = re.search(r'(\d{8}-\d{6})_(\d{8}-\d{6})', log_name)
        if match:
            start_time_str = match.group(1)
            end_time_str = match.group(2)

            start_time = datetime.strptime(start_time_str, '%Y%m%d-%H%M%S')
            end_time = datetime.strptime(end_time_str, '%Y%m%d-%H%M%S') 
            
            error_time = datetime.strptime(error_time_str,'%Y-%m-%d %H:%M:%S')
            if start_time<=error_time and error_time<=end_time:
                return True
        return False
    def resizeEvent(self, event):
        self.log_table.resizeRowsToContents()
        # self.log_table.resizeColumnsToContents()
        self.record_table.resizeRowsToContents()
        # self.record_table.resizeColumnsToContents()
        return super().resizeEvent(event)


class NDPShowWidget(QWidget):
    sig_aip_tab = pyqtSignal(str,str)
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.init_ui()
        self.search_aip_widget.sig_aip_info.connect(self.aip_display)

    def init_ui(self):
        self.stack_widget = QStackedWidget(self)
        self.search_aip_widget = SearchAIPWidget(self)
        self.h_layout = QHBoxLayout(self)

        self.h_layout.setContentsMargins(0,0,0,0)
        self.h_layout.addWidget(self.stack_widget)
        
        self.stack_widget.addWidget(self.search_aip_widget)
        self.stack_widget.setCurrentWidget(self.search_aip_widget)
        self.search_aip_widget.set_focus()

    def aip_display(self,aip_info,log_list,record_list):
        self.aip_info_widget = AIPInfoWidget(aip_info.jira_issue_key,self)
        self.stack_widget.addWidget(self.aip_info_widget)
        self.stack_widget.setCurrentWidget(self.aip_info_widget)
        self.aip_info_widget.set_aip_info(aip_info,log_list,record_list)
        self.sig_aip_tab.emit(self.objectName(),aip_info.jira_issue_key)

