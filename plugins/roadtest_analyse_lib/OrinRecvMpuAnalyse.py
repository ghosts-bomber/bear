import matplotlib.pyplot as plt
# import matplotlib
from .PublicLib import *

# matplotlib.use('agg')


def AnalyseTimePoint(timepoint, rcvCntDict, byteCntDict) -> str:
    if timepoint not in rcvCntDict:
        return ''

    ratio = 100 * byteCntDict[timepoint] / 8710
    ret = f'time: {timepoint} receive count: {rcvCntDict[timepoint]}; \
        mpu data received in 1 second: {byteCntDict[timepoint]}\n'                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                +\
        f'Ratio to normal: {round(ratio, 2)}%, \
            missing: {max(0, 8710 - byteCntDict[timepoint])}\n'

    return ret


def AnalyseOrinReceiveMpu(lines: list, targetDir: str, beg: int, end: int):
    text_results = []
    plt_results = []
    result = 'Normally, Orin receive mpu data rate is: 8710 byte/s\n\n'

    byteStatistics = {}
    recvCountStatistics = {}

    for line in lines:
        t = line.split(' ')[1][0:8]
        val = int(line.split(' ')[-1].split('/')[0])
        if t not in byteStatistics.keys():
            byteStatistics[t] = val
            recvCountStatistics[t] = 1
        else:
            byteStatistics[t] += val
            recvCountStatistics[t] += 1

    for hour in range(0, 24, 1):
        h: str
        if hour < 10:
            h = f'0{hour}'
        else:
            h = f'{hour}'
        for minute in range(0, 60, 1):
            m: str
            if minute < 10:
                m = f'0{minute}'
            else:
                m = f'{minute}'
            for second in range(0, 60, 1):
                s: str
                if second < 10:
                    s = f'0{second}'
                else:
                    s = f'{second}'
                bugTime = f'{h}:{m}:{s}'
                result += AnalyseTimePoint(bugTime, recvCountStatistics,
                                           byteStatistics)

    with open(f'{targetDir}/OrinRecvMpu.txt', 'w+') as f:
        f.write(result)
    text_results.append(result)

    time = []
    byteRecv = []
    for k, v in byteStatistics.items():
        time.append(ConvertStrToTime(k))
        byteRecv.append(v)
    time.pop(0)
    time.pop(-1)
    byteRecv.pop(0)
    byteRecv.pop(-1)

    fig = plt.figure(figsize=(12, 4))
    rcv = fig.add_subplot(1, 1, 1)
    rcv.plot(time,
             byteRecv,
             marker='o',
             markersize=1.5,
             linestyle='solid',
             linewidth=1)
    rcv.grid(which='major', axis='both', linestyle='--', linewidth=0.5)
    rcv.set_title(
        f'OrinRecvMpu data rate {ConvertTimeToStr(beg)} ~ {ConvertTimeToStr(end)}'
    )
    rcv.set_ylabel('bytes per second')
    time_xtick_list = list(
        range(time[0], time[-1], max(1, (time[-1] - time[0]) // 30)))
    rcv.set_xticks(time_xtick_list)
    rcv.set_xticklabels([f'{ConvertTimeToStr(t)}' for t in time_xtick_list],
                        rotation='vertical')
    rcv.axhline(y=8710, c='r', linewidth=0.5)

    fig.tight_layout()
    fig.savefig(f'{targetDir}/OrinRecvMpu.png', dpi=300)
    plt_results.append(fig)
    return text_results,plt_results

