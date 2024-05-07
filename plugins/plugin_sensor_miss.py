from IPlugin import IPlugin
from Result import IResult, TextResult,TextWithNumResult
import typing
import logging
class SensorMiss(IPlugin):
    def __init__(self) -> None:
        pass

    def GetPluginInfo(self) -> str:
        return '传感器数据丢失'

    def Process(self,text_data)->typing.List['IResult']:
        results:typing.List['IResult'] = []
        item = TextResult()
        item.SetResult('传感器数据检测')
        results.append(item)
        results = results + self.get_common_result('传感器数据异常','')
        for i,line in enumerate(text_data.get_lines()):
            if line.find('Failed to get sensor data')!=-1 or line.find('Pointcloud miss in detection at')!=-1:
                results.append(TextWithNumResult(i+1,line))
                
        return results


