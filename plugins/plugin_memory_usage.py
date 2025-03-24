from IPlugin import IPlugin
from Result import IResult, TextResult,ImageResult
import typing
import logging
from PyQt5.QtGui import QImage
import matplotlib.pyplot as plt
import numpy as np

class CpuUsage(IPlugin):
    def __init__(self) -> None:
        pass

    def GetPluginInfo(self) -> str:
        return '内存使用率'

    def Process(self,text_data)->typing.List['IResult']:
        results:typing.List['IResult'] = []
        item = TextResult()
        item.SetResult('内存使用率绘图')
        results.append(item)
        results = results + self.get_common_result('后台无网络','内存使用率异常')

        start_time="00:00:00"
        end_time="23:59:59"
        start_int=self.ConvertStrToTime(start_time)
        end_int=self.ConvertStrToTime(end_time)


        mem_usagee = [[] for i in range(1)]
        time = []

        end_times = []
        print(start_int)
        print(end_int)

        need_end=True
        for line in text_data.get_lines():
            if 'neodrive memory' in line:
                tp = line.split()[1].split("][")[0].split(".")[0]
                tim = self.ConvertStrToTime(tp)
                if tim < start_int or tim > end_int:
                    need_end=False
                    continue
                need_end=True
                time.append(self.ConvertStrToTime(tp))
                usage = float(line.split()[6])
                mem_usagee[0].append(usage * 1024)
                

        memfig = plt.figure(figsize=(10, 8))
        memfig_xtick_list = list(range(time[0], time[-1], max(1, (time[-1] - time[0]) // 30)))
        for i in range(len(mem_usagee)):
            subfig = memfig.add_subplot(len(mem_usagee), 1, i + 1)
            subfig.plot(time,
                        mem_usagee[i],
                        linewidth=1,
                        marker='o',
                        markersize=1.5,
                        linestyle='solid',
                        color='g')
            subfig.set_title(f'--- neodrive memory usage ---')
            subfig.set_ylabel('MB')
            subfig.set_xticks(memfig_xtick_list)
            subfig.set_xticklabels(
                [f'{self.ConvertTimeToStr(t)}' for t in memfig_xtick_list],
                rotation='vertical')
            subfig.set_yticks(np.arange(0, 25000, 1000))
                
        memfig.tight_layout()
        memfig.savefig('./tmp/memory-Usage.png', dpi=300)
        plt.close(memfig)
        # cpufig.savefig('CPU-Usage.png', dpi=300)
        results.append(ImageResult(self.figure_to_qimage(memfig)))
        return results

    def ConvertTimeToStr(self,time: int):
        hour = time // 3600
        time %= 3600
        minute = time // 60
        time %= 60
        return '%2s:%2s:%2s' % (str(hour).zfill(2), str(minute).zfill(2),
                                str(time).zfill(2))

    def ConvertStrToTime(self,timeStr: str):
        temp = timeStr.split(':')
        return int(temp[0]) * 3600 + int(temp[1]) * 60 + int(temp[2])
    
    def figure_to_qimage(self,figure):
        buffer = figure.canvas.buffer_rgba()
        width, height = figure.canvas.get_width_height()
        image = QImage(buffer, width, height, QImage.Format_ARGB32)
        return image

