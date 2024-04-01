import matplotlib.pyplot as plt
# import matplotlib
from .PublicLib import *

# matplotlib.use('agg')


def AnalyseGnss(lines: list, targetDir: str, beg: int, end: int):
    text_results = []
    plt_results = []

    time = list(range(beg, end + 1, 1))
    gnssLostFrame = [0] * len(time)
    gnssLatency = [0] * len(time)
    gnssLatencySum = 0.0
    gnssLatencyCnt = 0

    imuLatency = [0] * len(time)
    imuLatencySum = 0.0
    imuLatencyCnt = 0
    for line in lines:
        fields = line.split(' ')
        logTimeStr = fields[1][:8]
        tp = ConvertStrToTime(logTimeStr)
        index = tp - beg
        if 'imu time diff warning' in line:
            imuLatency[index] += 1
            imuLatencyCnt += 1
            imuLatencySum += float(fields[-1])
        elif 'lost frame' in line:
            gnssLostFrame[index] += 1
        elif 'not synchronized' in line:
            gnssLatency[index] += 1
            gnssLatencySum += float(fields[-1])
            gnssLatencyCnt += 1
        else:
            pass

    result = ''
    result += f'Satelite data lost percentage:            '+ \
        f'{round(100*sum(gnssLostFrame)/(15*len(gnssLostFrame)),2)}%\n'

    result += f'Satelite latency out of bound percentage: '+ \
        f'{round(100*sum(gnssLatency)/(15*len(gnssLatency)),2)}%\n'

    result += f'Satelite latency average when out of bound: ' + \
        f'{round(1000*gnssLatencySum/gnssLatencyCnt) if gnssLatencyCnt > 0 else 0}ms\n'

    result += f'IMU latency out of bound percentage:      '+ \
        f'{round(100*sum(imuLatency)/len(100*(imuLatency)),2)}%\n'

    result += f'IMU latency average when out of bound: ' + \
        f'{round(1000*imuLatencySum/imuLatencyCnt) if imuLatencyCnt > 0 else 0}ms\n'

    with open(f'{targetDir}/GnssFrameLostAndLag.txt', 'w+') as f:
        f.write(result)
    text_results.append(result)

    fig = plt.figure(figsize=(12, 12))
    time_xtick_list = list(
        range(time[0], time[-1], max(1, (time[-1] - time[0]) // 30)))
    gnssLostFrameFig = fig.add_subplot(3, 1, 1)
    gnssLostFrameFig.plot(time,
                          gnssLostFrame,
                          marker='o',
                          markersize=1.5,
                          linestyle='solid',
                          linewidth=1)
    gnssLostFrameFig.grid(which='major',
                          axis='both',
                          linestyle='--',
                          linewidth=0.5)
    gnssLostFrameFig.set_title(
        f'gnss frame lost {ConvertTimeToStr(beg)} ~ {ConvertTimeToStr(end)}')
    gnssLostFrameFig.set_ylabel('lost frames per second')
    gnssLostFrameFig.set_xticks(time_xtick_list)
    gnssLostFrameFig.set_xticklabels(
        [f'{ConvertTimeToStr(t)}' for t in time_xtick_list],
        rotation='vertical')

    gnssLatencyFig = fig.add_subplot(3, 1, 2)
    gnssLatencyFig.plot(time,
                        gnssLatency,
                        marker='x',
                        markersize=1.5,
                        linestyle='solid',
                        linewidth=1)
    gnssLatencyFig.grid(which='major',
                        axis='both',
                        linestyle='--',
                        linewidth=0.5)
    gnssLatencyFig.set_title(
        f'gnss latency count {ConvertTimeToStr(beg)} ~ {ConvertTimeToStr(end)}'
    )
    gnssLatencyFig.set_ylabel('latency out of bound per second')
    gnssLatencyFig.set_xticks(time_xtick_list)
    gnssLatencyFig.set_xticklabels(
        [f'{ConvertTimeToStr(t)}' for t in time_xtick_list],
        rotation='vertical')

    imuLatencyFig = fig.add_subplot(3, 1, 3)
    imuLatencyFig.plot(time,
                       imuLatency,
                       marker='x',
                       markersize=1.5,
                       linestyle='solid',
                       linewidth=1)
    imuLatencyFig.grid(which='major',
                       axis='both',
                       linestyle='--',
                       linewidth=0.5)
    imuLatencyFig.set_title(
        f'imu latency {ConvertTimeToStr(beg)} ~ {ConvertTimeToStr(end)}')
    imuLatencyFig.set_ylabel('latency out of bound per second')
    imuLatencyFig.set_xticks(time_xtick_list)
    imuLatencyFig.set_xticklabels(
        [f'{ConvertTimeToStr(t)}' for t in time_xtick_list],
        rotation='vertical')

    fig.tight_layout()
    fig.savefig(f'{targetDir}/GnssAndImuLatencyLostFrame.png', dpi=300)
    plt_results.append(fig)
    return text_results,plt_results
