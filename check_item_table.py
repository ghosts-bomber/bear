from PyQt5.QtWidgets import QTableView
from PyQt5.QtCore import Qt,QModelIndex,pyqtSignal
from PyQt5.QtGui import QStandardItemModel,QStandardItem
import typing
import logging
from checkbox_delegate import CheckBoxDeledate
ID_COL = 0
CHECK_COL = 1
CHANNEL_NAME_COL = 2

class CheckItemTable(QTableView):
    check_change = pyqtSignal(str,bool)
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.dataModel = QStandardItemModel()
        self.dataModel.setColumnCount(3)
        self.setModel(self.dataModel)
        self.dataModel.setHeaderData(ID_COL,Qt.Orientation.Horizontal,'')
        self.dataModel.setHeaderData(CHECK_COL,Qt.Orientation.Horizontal,'check')
        self.dataModel.setHeaderData(CHANNEL_NAME_COL,Qt.Orientation.Horizontal,'channel name')
        self.hideColumn(ID_COL)
        self.horizontalHeader().setStretchLastSection(True)
        self.checkboxDelegate = CheckBoxDeledate(CHECK_COL,self)
        self.setItemDelegateForColumn(CHECK_COL,self.checkboxDelegate)
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        # self.setDragEnabled(True)
        # self.setDragDropMode(QTableView.DragDropMode.InternalMove)
        # self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        # self.setAcceptDrops(True)
        # self.setDropIndicatorShown(True)
        # self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.dataModel.dataChanged.connect(self.process_data_changed)


    def InsertItem(self,row:int,id:str,channel_name:str)->None:
        self.dataModel.insertRow(row)
        idIndex = self.dataModel.index(row,ID_COL)
        self.dataModel.setData(idIndex,id,Qt.ItemDataRole.UserRole)
        infoIndex = self.dataModel.index(row,CHANNEL_NAME_COL)
        self.dataModel.setData(infoIndex,channel_name,Qt.ItemDataRole.DisplayRole)
        self.dataModel.setData(infoIndex,channel_name,Qt.ItemDataRole.ToolTipRole)
        checkIndex = self.dataModel.index(row,CHECK_COL)
        self.dataModel.setData(checkIndex,False,Qt.ItemDataRole.UserRole)

    def AppendItem(self,id:str,itemInfo:str)->None:
        self.InsertItem(self.dataModel.rowCount(),id,itemInfo)

    def GetCheckItems(self)->typing.List['int']:
        checkItems = []
        for i in range(0,self.dataModel.rowCount()):
            index = self.dataModel.index(i,CHECK_COL)
            if self.dataModel.data(index,Qt.ItemDataRole.UserRole):
                idIndex = self.dataModel.index(i,ID_COL)
                checkItems.append(self.dataModel.data(idIndex,Qt.ItemDataRole.UserRole))
        return checkItems

    def process_data_changed(self,top_left:QModelIndex,bottom_right:QModelIndex,list)->None:
        logging.debug("item changed")
        if top_left.isValid():
            if top_left.column()==CHECK_COL:
                checked:bool = self.dataModel.data(top_left,Qt.ItemDataRole.UserRole)
                channel_name:str = self.dataModel.data(self.dataModel.index(top_left.row(),CHANNEL_NAME_COL),Qt.ItemDataRole.DisplayRole)
                logging.info(f"{channel_name} is {checked}")
                self.check_change.emit(channel_name,checked)



