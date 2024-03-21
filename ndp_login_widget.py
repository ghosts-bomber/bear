from PyQt5.QtWidgets import QCheckBox, QMessageBox,QWidget,QPushButton,QHBoxLayout,QVBoxLayout,QFileDialog,QLineEdit
from PyQt5.QtCore import Qt,pyqtSignal
from ndp_data import NDPApi
from config import Config
from qfluentwidgets import LineEdit,PrimaryPushButton,CheckBox,PasswordLineEdit
class NDPLoginWidget(QWidget):
    sig_login_success = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.init_ui()
        self.config = Config()
         
        self.user_name_edit.setText(self.config.get_login_user())
        if self.config.get_remember_pwd():
            self.passwd_edit.setText(self.config.get_login_pwd())
            self.remember_passwd.setChecked(True)
        else:
            self.auto_login.setEnabled(False)

        if self.config.get_auto_login():
            self.auto_login.setChecked(True)
        # TODO auto login

        self.login_btn.clicked.connect(self.login_btn_clicked)
        self.passwd_edit.returnPressed.connect(self.login_btn_clicked)
        self.remember_passwd.clicked.connect(self.remember_passwd_checked)
        self.auto_login.clicked.connect(self.auto_login_checked)

    def init_ui(self):
        self.user_name_edit = LineEdit(self)
        self.passwd_edit = PasswordLineEdit(self)
        self.login_btn = PrimaryPushButton('login',self)
        self.remember_passwd = CheckBox('remember password')
        self.auto_login = CheckBox('auto login')

        self.h_layout = QHBoxLayout(self)
        self.h_layout.setContentsMargins(0,0,0,0)
        self.h_layout.setSpacing(0)
        self.v_layout = QVBoxLayout()
        self.v_layout.setContentsMargins(0,0,0,0)
        self.v_layout.setSpacing(20)

        self.check_h_layout = QHBoxLayout()
        self.check_h_layout.setContentsMargins(0,0,0,0)

        self.v_layout.addStretch()
        self.v_layout.addWidget(self.user_name_edit)
        self.v_layout.addWidget(self.passwd_edit)
        self.check_h_layout.addWidget(self.remember_passwd)
        self.check_h_layout.addStretch()
        self.check_h_layout.addWidget(self.auto_login)
        self.v_layout.addLayout(self.check_h_layout)
        self.v_layout.addWidget(self.login_btn)
        self.v_layout.addStretch()

        self.h_layout.addStretch()
        self.h_layout.addLayout(self.v_layout)
        self.h_layout.addStretch()

        self.user_name_edit.setPlaceholderText('中台账号')
        self.user_name_edit.setClearButtonEnabled(True)
        self.passwd_edit.setPlaceholderText("••••••••••••")
        self.passwd_edit.setViewPasswordButtonVisible(True)
        self.passwd_edit.setClearButtonEnabled(True)

    def login_btn_clicked(self):
        user_name = self.user_name_edit.text()
        passwd = self.passwd_edit.text()
        if not user_name or not passwd:
            # TODO add tips
            return
        ndp_api = NDPApi()
        ret = ndp_api.login(user_name,passwd)
        if ret:
            if self.remember_passwd.isChecked():
                self.config.set_login_user(self.user_name_edit.text())
                self.config.set_login_pwd(self.passwd_edit.text())
            self.sig_login_success.emit()
        else:
            # TODO tips
            pass

    def remember_passwd_checked(self,checked):
        if checked:
            self.auto_login.setEnabled(True)
        else:
            self.auto_login.setChecked(False)
            self.auto_login.setEnabled(False)

    def auto_login_checked(self,checked):
        pass

