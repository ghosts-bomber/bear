from IPlugin import IPlugin
from Result import IResult, TextResult,TextWithNumResult
import typing
import logging

class CheckWheel(IPlugin):
    def __init__(self) -> None:
        pass

    def GetPluginInfo(self) -> str:
        return '左右轮速异常检测'

    def Process(self,text_data)->typing.List['IResult']:
        results:typing.List['IResult'] = []
        item = TextResult()
        item.SetResult('定位左右轮速异常检测')
        results.append(item)
        for i,line in enumerate(text_data.get_lines()):
            if line.find('wheel speed lf:')!=-1 or line.find('PilotErrorLevel: 2')!=-1 or line.find('fl_valid or fr_valid is invalid')!=-1:
                results.append(TextWithNumResult(i,line))
        return results


