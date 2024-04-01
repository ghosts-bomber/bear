# import matplotlib
import time
import matplotlib.pyplot as plt
from .PublicLib import *

# matplotlib.use('agg')
'''
"Hesai packet receive: SysTime {} PointCloudTime {}"
"Robosense packet receive: SysTime {} PointCloudTime {}"
"Livox packet receive: SysTime {} PointCloudTime {}"
'''


def AnalyseLidarUdpPacket(hesaiPacketReceiveLog, livoxPacketReceiveLog,
                          robosensePacketReceiveLog, targetDir, beg, end):
    text_results = []
    plt_results = []

    time = list(range(beg, end + 1))

    hesaiDerivation = [0] * len(time)
    hesaiCnt = {}

    livoxDerivation = [0] * len(time)
    livoxCnt = {}

    robosenseDerivation = [0] * len(time)
    robosenseCnt = {}

    for line in hesaiPacketReceiveLog:
        fields = line.split(' ')
        tp = ConvertStrToTime(fields[1][:8])
        systime = float(fields[-3]) / 10**6
        pkttime = float(fields[-1]) / 10**6
        hesaiDerivation[tp - beg] += (systime - pkttime)
        if tp not in hesaiCnt.keys():
            hesaiCnt[tp] = 1
        else:
            hesaiCnt[tp] += 1

    for line in livoxPacketReceiveLog:
        fields = line.split(' ')
        tp = ConvertStrToTime(fields[1][:8])
        systime = float(fields[-3]) / 10**6
        pkttime = float(fields[-1]) / 10**6
        livoxDerivation[tp - beg] += (systime - pkttime)
        if tp not in livoxCnt.keys():
            livoxCnt[tp] = 1
        else:
            livoxCnt[tp] += 1

    for line in robosensePacketReceiveLog:
        fields = line.split(' ')
        tp = ConvertStrToTime(fields[1][:8])
        systime = float(fields[-3]) / 10**6
        pkttime = float(fields[-1]) / 10**6
        robosenseDerivation[tp - beg] += (systime - pkttime)
        if tp not in robosenseCnt.keys():
            robosenseCnt[tp] = 1
        else:
            robosenseCnt[tp] += 1

    hesaiAnnotationTime = []
    hesaiAnnotationDerivation = []
    for id, val in enumerate(hesaiDerivation):
        if val != 0:
            hesaiDerivation[id] /= hesaiCnt[id + beg]
            hesaiAnnotationTime.append(id + beg)
            hesaiAnnotationDerivation.append(hesaiDerivation[id])

    livoxAnnotationTime = []
    livoxAnnotationDerivation = []
    for id, val in enumerate(livoxDerivation):
        if val != 0:
            livoxDerivation[id] /= livoxCnt[id + beg]
            livoxAnnotationTime.append(id + beg)
            livoxAnnotationDerivation.append(livoxDerivation[id])

    robosenseAnnotationTime = []
    robosenseAnnotationDerivation = []
    for id, val in enumerate(robosenseDerivation):
        if val != 0:
            robosenseDerivation[id] /= robosenseCnt[id + beg]
            robosenseAnnotationTime.append(id + beg)
            robosenseAnnotationDerivation.append(robosenseDerivation[id])

    time_xtick_list = list(range(beg, end, max(1, (end - beg) // 30)))
    fig = plt.figure(figsize=(12, 18))

    hesaiFig = fig.add_subplot(3, 1, 1)
    hesaiFig.set_xticks(time_xtick_list)
    hesaiFig.set_xticklabels(
        [f'{ConvertTimeToStr(t)}' for t in time_xtick_list],
        rotation='vertical')

    hesaiYAxisTicks = list(
        range(
            int(min(hesaiDerivation)), int(max(hesaiDerivation)),
            max((int(max(hesaiDerivation)) - int(min(hesaiDerivation))) // 20,
                1)))
    hesaiFig.set_yticks(hesaiYAxisTicks)
    hesaiFig.set_yticklabels([f'{int(t)}' for t in hesaiYAxisTicks],
                             rotation='horizontal')
    hesaiFig.plot(time,
                  hesaiDerivation,
                  marker=',',
                  linestyle='solid',
                  linewidth=1)
    hesaiFig.scatter(hesaiAnnotationTime,
                     hesaiAnnotationDerivation,
                     marker='o',
                     s=3,
                     c='g',
                     label='udp packet count')
    for x, y in zip(hesaiAnnotationTime, hesaiAnnotationDerivation):
        hesaiFig.annotate(f'{hesaiCnt[x]}',
                          xy=(x, y),
                          xytext=(0, 30),
                          textcoords='offset points',
                          ha='center',
                          va='top',
                          rotation='vertical')
    hesaiFig.axhline(y=0, c='r', linestyle='--', linewidth=0.5, label='ZERO')
    hesaiFig.set_title(
        f'Hesai UDP packet derivation  {ConvertTimeToStr(beg)} ~ {ConvertTimeToStr(end)}'
    )
    hesaiFig.set_xlabel('System time / s')
    hesaiFig.set_ylabel('time diff (sys - pkt) / ms')
    hesaiFig.grid(which='major', axis='both', linestyle='--', linewidth=0.5)
    hesaiFig.legend()

    livoxFig = fig.add_subplot(3, 1, 2)
    livoxFig.set_xticks(time_xtick_list)
    livoxFig.set_xticklabels(
        [f'{ConvertTimeToStr(t)}' for t in time_xtick_list],
        rotation='vertical')

    livoxYAxisTicks = list(
        range(
            int(min(livoxDerivation)), int(max(livoxDerivation)),
            max((int(max(livoxDerivation)) - int(min(livoxDerivation))) // 20,
                1)))
    livoxFig.set_yticks(livoxYAxisTicks)
    livoxFig.set_yticklabels([f'{int(t)}' for t in livoxYAxisTicks],
                             rotation='horizontal')
    livoxFig.plot(time,
                  livoxDerivation,
                  marker=',',
                  linestyle='solid',
                  linewidth=1)
    livoxFig.scatter(livoxAnnotationTime,
                     livoxAnnotationDerivation,
                     marker='o',
                     s=3,
                     c='g',
                     label='udp packet count')
    for x, y in zip(livoxAnnotationTime, livoxAnnotationDerivation):
        livoxFig.annotate(f'{livoxCnt[x]}',
                          xy=(x, y),
                          xytext=(0, 30),
                          textcoords='offset points',
                          ha='center',
                          va='top',
                          rotation='vertical')
    livoxFig.axhline(y=0, c='r', linestyle='--', linewidth=0.5, label='ZERO')
    livoxFig.set_title(
        f'Livox UDP packet derivation  {ConvertTimeToStr(beg)} ~ {ConvertTimeToStr(end)}'
    )
    livoxFig.set_xlabel('System time / s')
    livoxFig.set_ylabel('time diff (sys - pkt) / ms')
    livoxFig.grid(which='major', axis='both', linestyle='--', linewidth=0.5)
    livoxFig.legend()

    robosenseFig = fig.add_subplot(3, 1, 3)
    robosenseFig.set_xticks(time_xtick_list)
    robosenseFig.set_xticklabels(
        [f'{ConvertTimeToStr(t)}' for t in time_xtick_list],
        rotation='vertical')
    robosenseYAxisTicks = list(
        range(
            int(min(robosenseDerivation)), int(max(robosenseDerivation)),
            max((int(max(robosenseDerivation)) - int(min(robosenseDerivation)))
                // 20, 1)))
    robosenseFig.set_yticks(robosenseYAxisTicks)
    robosenseFig.set_yticklabels([f'{int(t)}' for t in robosenseYAxisTicks],
                                 rotation='horizontal')
    robosenseFig.plot(time,
                      robosenseDerivation,
                      marker=',',
                      linestyle='solid',
                      linewidth=1)
    robosenseFig.scatter(robosenseAnnotationTime,
                         robosenseAnnotationDerivation,
                         marker='o',
                         s=3,
                         c='g',
                         label='udp packet count')
    for x, y in zip(robosenseAnnotationTime, robosenseAnnotationDerivation):
        robosenseFig.annotate(f'{robosenseCnt[x]}',
                              xy=(x, y),
                              xytext=(0, 30),
                              textcoords='offset points',
                              ha='center',
                              va='top',
                              rotation='vertical')
    robosenseFig.axhline(y=0,
                         c='r',
                         linestyle='--',
                         linewidth=0.5,
                         label='ZERO')
    robosenseFig.set_title(
        f'Robosense UDP packet derivation  {ConvertTimeToStr(beg)} ~ {ConvertTimeToStr(end)}'
    )
    robosenseFig.set_xlabel('System time / s')
    robosenseFig.set_ylabel('time diff (sys - pkt) / ms')
    robosenseFig.grid(which='major',
                      axis='both',
                      linestyle='--',
                      linewidth=0.5)
    robosenseFig.legend()

    fig.tight_layout()
    fig.savefig(f'{targetDir}/LidarUdpPacketLatency.png', dpi=300)
    plt_results.append(fig)
    return text_results,plt_results
