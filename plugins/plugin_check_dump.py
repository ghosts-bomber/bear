
from IPlugin import IPlugin
from Result import IResult, TextResult,TextWithNumResult
import typing
import logging
class CheckDump(IPlugin):
    def __init__(self) -> None:
        pass

    def GetPluginInfo(self) -> str:
        return 'trace日志堆栈检查'

    def Process(self,text_data)->typing.List['IResult']:
        results:typing.List['IResult'] = []
        item = TextResult()
        item.SetResult('trace日志堆栈检查')
        results.append(item)
        results = results + self.get_common_result('ad灯不亮 / 行驶中调STBY模块','{}模块崩溃')
        for i,line in enumerate(text_data.get_lines()):
            if line.find('Stack Info')!=-1 or line.find('stack dump')!=-1:
                results.append(TextWithNumResult(i+1,line))
                
        return results


