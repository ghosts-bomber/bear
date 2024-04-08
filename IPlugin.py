from abc import abstractmethod
import typing
from Result import IResult,TextResult
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
    
    def get_common_result(self,problem='',reason='',resolution='')->typing.List['IResult']:
        results:typing.List['IResult'] = []
        results.append(TextResult(f'【问题现象】:{problem}')) 
        results.append(TextResult(f'【问题原因】:{reason}')) 
        results.append(TextResult(f'【解决方案】:{resolution}')) 
        results.append(TextResult(f'【解决版本】:')) 
        return results
