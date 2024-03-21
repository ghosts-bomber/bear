from PyQt5.QtWidgets import QCheckBox,QStyledItemDelegate,QWidget,QStyleOptionButton,QStyleOptionViewItem,QStyle,QApplication
from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import Qt,QRect,QPoint,QEvent
import typing

def CheckBoxRect(styleOptions:QStyleOptionViewItem)->QRect:
    checkSyle = QStyleOptionButton()
    checkBoxRect = QApplication.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator,checkSyle)
    checkBoxPoint = QPoint(int(styleOptions.rect.x()+styleOptions.rect.width()/2-checkBoxRect.width()/2),
                           int(styleOptions.rect.y()+styleOptions.rect.height()/2-checkBoxRect.height()/2))
    return QRect(checkBoxPoint,checkBoxRect.size())


class CheckBoxDeledate(QStyledItemDelegate):
    def __init__(self, col:int,parent=None) -> None:
        super().__init__(parent)
        self.col = col
        '''
    def createEditor(self, parent: QWidget, option, index: QtCore.QModelIndex) -> QWidget:
        checkbox = QCheckBox(parent)
        return checkbox
    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex) -> None:
        value = index.model().data(index,Qt.ItemDataRole.UserRole)
        editor.setChecked(value)

    def setModelData(self, editor: QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
        if editor.isChecked():
            model.setData(index,True,Qt.ItemDataRole.UserRole)
        else:
            model.setData(index,False,Qt.ItemDataRole.UserRole)

    def updateEditorGeometry(self, editor: QWidget, option, index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)
        '''
    def paint(self, painter: QtGui.QPainter, option, index: QtCore.QModelIndex) -> None:
        bChecked = index.model().data(index,Qt.ItemDataRole.UserRole)
        if index.column()==self.col:
            checkboxStyle = QStyleOptionButton()
            checkboxStyle.state|= QStyle.StateFlag.State_Enabled
            if bChecked:
                checkboxStyle.state|=QStyle.StateFlag.State_On
            else:
                checkboxStyle.state|=QStyle.StateFlag.State_Off
            checkboxStyle.rect = CheckBoxRect(option)
            QApplication.style().drawControl(QStyle.ControlElement.CE_CheckBox,checkboxStyle,painter)
        else:
            return super().paint(painter,option,index)

    def editorEvent(self, event: QtCore.QEvent, model: QtCore.QAbstractItemModel, option, index: QtCore.QModelIndex) -> bool:
        if index.column()==self.col:
            if event.type()==QEvent.Type.MouseButtonPress and CheckBoxRect(option).contains(event.pos()):
                data = model.data(index,Qt.ItemDataRole.UserRole)
                model.setData(index,~data,Qt.ItemDataRole.UserRole)
                # if data:
                #     model.setData(index,False,Qt.ItemDataRole.UserRole)
                # else:
                #     model.setData(index,True,Qt.ItemDataRole.UserRole)
                # 
        return super().editorEvent(event, model, option, index)
