from abc import abstractmethod
import typing
from Result import IResult
from text_data import TextData

class IPlugin:
    def __init__(self) -> None:
        pass
    @abstractmethod
    def GetPluginInfo(self)->str:
        return ''

    @abstractmethod
    def Process(self,text_data:TextData)->typing.List['IResult']:
        return []

