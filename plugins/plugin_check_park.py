from IPlugin import IPlugin
from Result import IResult, TextResult,TextWithNumResult
import typing
import logging
class CheckPark(IPlugin):
    def __init__(self) -> None:
        pass

    def GetPluginInfo(self) -> str:
        return '升降级'

    def Process(self,text_data)->typing.List['IResult']:
        results:typing.List['IResult'] = []
        item = TextResult()
        item.SetResult('升降级检测')
        results.append(item)
        results = results + self.get_common_result('行驶中触发升降级','')
        for i,line in enumerate(text_data.get_lines()):
            if line.find('[reason:')!=-1 and line.find('[reason: ]')==-1:
                results.append(TextWithNumResult(i+1,line))
            elif line.find('monitor_message: msg:')!=-1 and line.find('[STAT_ABNORMAL]')!=-1:
                results.append(TextWithNumResult(i+1,line))
                
        return results


