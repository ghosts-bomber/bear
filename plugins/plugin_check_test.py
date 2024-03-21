from IPlugin import IPlugin
from Result import IResult, TextResult
import typing
import logging

class CheckTest(IPlugin):
    def __init__(self) -> None:
        pass

    def GetPluginInfo(self) -> str:
        return 'test'

    def Process(self,text_data)->typing.List['IResult']:
        results:typing.List['IResult'] = []
        item = TextResult()
        item.SetResult('test msg')
        detail_result = TextResult()
        detail_result.SetResult('detail result')
        results.append(item)
        results.append(detail_result)
        print('++++++++++++++ test ++++++++++++++++++++++') 
        return results

