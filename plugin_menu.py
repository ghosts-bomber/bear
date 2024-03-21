from qfluentwidgets import RoundMenu,Action
from plugin_manager import PluginManager
from PyQt5.QtCore import QObject,pyqtSignal

class PluginMenu(QObject):
    sig_plugin_triggered = pyqtSignal(str)
    def __init__(self,parent:None) -> None:
        super().__init__(parent)
        self.menu = RoundMenu('plugins',parent)
        self.plugin_mananger = PluginManager()
        for name,plugin in self.plugin_mananger.GetAllPlugin().items():
            action = Action(plugin.GetPluginInfo()) 
            self.menu.addAction(action)
            action.triggered.connect(lambda enbale,plugin_name=name:self.action_triggered(plugin_name))

    def get_plugin_menu(self):
        return self.menu
    
    def action_triggered(self,plugin_name:str):
        self.sig_plugin_triggered.emit(plugin_name)

    def plugin_process(self,plugin_name,text_data):
        return self.plugin_mananger.GetPlugin(plugin_name).Process(text_data)


