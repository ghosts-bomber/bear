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
        return 'cpu使用率'

    def Process(self,text_data)->typing.List['IResult']:
        results:typing.List['IResult'] = []
        item = TextResult()
        item.SetResult('cpu使用率绘图')
        results.append(item)
        results = results + self.get_common_result('行驶中触发升降级','cpu使用率异常')

        start_time="00:00:00"
        end_time="23:59:59"
        start_int=self.ConvertStrToTime(start_time)
        end_int=self.ConvertStrToTime(end_time)


        cpu_usage = [[] for i in range(12)]
        time = []

        end_times = []
        print(start_int)
        print(end_int)

        need_end=True
        for line in text_data.get_lines():
            if 'cpu 0' in line:
                tp = line.split()[1].split("][")[0].split(".")[0]
                tim = self.ConvertStrToTime(tp)
                if tim < start_int or tim > end_int:
                    need_end=False
                    continue
                need_end=True
                time.append(self.ConvertStrToTime(tp))
            if 'and system' in line and need_end:
                cpu_id = int(line.split()[2])
                usage = float(line.split()[6].split("and")[0][:-1])
                cpu_usage[cpu_id].append(usage * 100)
                
        CPUPeakTime = [[] for i in range(12)]
        CPUPeakValue = [[] for i in range(12)]
        logging.info(len(cpu_usage[1]))
        logging.info(len(time))
        for i in range(12):
            for j in range(1, len(cpu_usage[i]) - 1):
                if cpu_usage[i][j] > 90 and \
                    cpu_usage[i][j-1] < cpu_usage[i][j] and \
                        cpu_usage[i][j] >= cpu_usage[i][j+1] and \
                        j < len(time):
                    CPUPeakTime[i].append(time[j])
                    CPUPeakValue[i].append(cpu_usage[i][j])

        cpufig = plt.figure(figsize=(12, 36))
        cpufig_xtick_list = list(range(time[0], time[-1], max(1, (time[-1] - time[0]) // 30)))
        for i in range(len(cpu_usage)):
            subfig = cpufig.add_subplot(12, 1, i + 1)
            subfig.plot(time,
                        cpu_usage[i],
                        linewidth=1,
                        marker='o',
                        markersize=1.5,
                        linestyle='solid',
                        color='g')
            subfig.axhline(y=100, c='r', linewidth=1)
            subfig.set_title(f'--- CPU{i} ---')
            subfig.set_ylabel('percentage')
            subfig.set_xticks(cpufig_xtick_list)
            subfig.set_xticklabels(
                [f'{self.ConvertTimeToStr(t)}' for t in cpufig_xtick_list],
                rotation='vertical')
            subfig.scatter(CPUPeakTime[i], CPUPeakValue[i], c='r', marker='o', s=2)
            subfig.set_yticks(np.arange(0, 110, 10))
            for x, y in zip(CPUPeakTime[i], CPUPeakValue[i]):
                    subfig.annotate(f'{self.ConvertTimeToStr(x)}',
                                    xy=(x, y),
                                    xytext=(0, 10),
                                    textcoords='offset points',
                                    ha='center',
                                    va='top')
                
        cpufig.tight_layout()
        cpufig.savefig('./tmp/CPU-Usage.png', dpi=300)
        plt.close(cpufig)
        # cpufig.savefig('CPU-Usage.png', dpi=300)
        results.append(ImageResult(self.figure_to_qimage(cpufig)))
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

