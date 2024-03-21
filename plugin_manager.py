import json
import logging
import os
import importlib.util
from abc import abstractmethod
import collections
from singleton import singleton
from IPlugin import IPlugin
class BaseManager(object):
    def __init__(self)->None:
        pass
    @abstractmethod
    def GetPlugin(self,name):
        pass
    @abstractmethod
    def GetAllPlugin(self):
        pass
@singleton
class PluginManager(BaseManager):
    def __init__(self) -> None:
        super().__init__()
        self.plugin_dir = 'plugins'
        self.plugins = {}
        self._loadPlugin()

    def GetPlugin(self, name):
        if name not in self.plugins:
            logging.warning(f"{name} don't exit")
            return None
        return self.plugins.get(name)

    def GetAllPlugin(self):
        return self.plugins
    
    def _loadPlugin(self):
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py'):
                plugin_path = os.path.join(self.plugin_dir, filename)
                plugin_name = os.path.splitext(filename)[0]

                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                plugin_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(plugin_module)
                print(plugin_module)
                for name in dir(plugin_module):
                    obj = getattr(plugin_module, name)
                    if type(obj)==type and issubclass(obj, IPlugin) and obj != IPlugin:
                        self.plugins[plugin_name] = obj()
                        logging.info(f"load plugin {plugin_name},plugin info {self.plugins[plugin_name].GetPluginInfo()}")


if __name__ == "__main__":
    plugin_manager = PluginManager()
