import matplotlib.pyplot as plt
# import matplotlib
from .PublicLib import *
import datetime
import pytz

# matplotlib.use('agg')


def AnalyseLidarFpsAndLatency(lines: list, targetDir: str, beg: int,
                              end: int) -> None:
    text_results = []
    plt_results = []
    fpsAndLatencyDict = {}
    lastTime = 0
    for line in lines:
        fields = line.split(' ')
        logTimeStr = fields[1][:8]
        tp = ConvertStrToTime(logTimeStr)

        sysTime = float(fields[7][:-1])
        pclTime = float(fields[10][:-1])

        while len(fpsAndLatencyDict) != 0 and tp - lastTime > 1:
            fpsAndLatencyDict[lastTime + 1] = [0, [0]]
            lastTime += 1

        if tp not in fpsAndLatencyDict.keys():
            fpsAndLatencyDict[tp] = [1, [sysTime - pclTime]]
        else:
            fpsAndLatencyDict[tp][0] += 1
            fpsAndLatencyDict[tp][1].append(sysTime - pclTime)
        lastTime = tp

    sortedDict = sorted(fpsAndLatencyDict.items(), key=lambda d: d[0])

    time = [key for (key, _) in sortedDict]
    frameCountList = [val[0] for (_, val) in sortedDict]
    latencyList = [
        sum(val[1]) / len(val[1]) if len(val[1]) != 0 else 0
        for (_, val) in sortedDict
    ]

    time.pop(0)
    time.pop(-1)
    frameCountList.pop(0)
    frameCountList.pop(-1)
    latencyList.pop(0)
    latencyList.pop(-1)

    framePeakTime = []
    framePeakValue = []

    frameValleyTime = []
    frameValleyValue = []

    latencyPeakTime = []
    latencyPeakValue = []

    for i in range(1, len(time) - 1):
        if frameCountList[i] > 60 and \
            frameCountList[i-1] < frameCountList[i] and \
                frameCountList[i] >= frameCountList[i+1]:
            framePeakTime.append(time[i])
            framePeakValue.append(frameCountList[i])

        if frameCountList[i] < 40 and \
            frameCountList[i-1] > frameCountList[i] and \
                frameCountList[i] <= frameCountList[i+1]:
            frameValleyTime.append(time[i])
            frameValleyValue.append(frameCountList[i])

    for i in range(1, len(time) - 1):
        if latencyList[i] > 0.5 and \
            latencyList[i-1] < latencyList[i] and \
                latencyList[i] >= latencyList[i+1]:
            latencyPeakTime.append(time[i])
            latencyPeakValue.append(latencyList[i])
        if latencyList[i] == 0 and latencyList[i - 1] != 0:
            latencyPeakTime.append(time[i])
            latencyPeakValue.append(latencyList[i])

    avgFrameRate, sigmaFrameRate = GetAvgAndSigma(frameCountList)
    avgLatency, sigmaLatency = GetAvgAndSigma(latencyList)

    result = f'{ConvertTimeToStr(beg)} ~ {ConvertTimeToStr(end)}:\n' + \
    f'Average frame rate: {round(avgFrameRate,2)}\n' + \
        f'standard deviation: {round(sigmaFrameRate,2)}\n\n' + \
            f'Average latency:    {round(avgLatency*1000,2)}ms\n' + \
                f'standard deviation: {round(sigmaLatency*1000,2)}ms\n\n'
    text_results.append(result)
    with open(f'{targetDir}/LidarFpsLatencyFrameLost.txt', 'w+') as f:
        f.write(result)

    fig = plt.figure(figsize=(12, 9))
    time_xtick_list = list(
        range(time[0], time[-1], max(1, (time[-1] - time[0]) // 30)))
    fps = fig.add_subplot(2, 1, 1)
    fps.plot(time,
             frameCountList,
             marker='o',
             markersize=1.5,
             linestyle='solid',
             linewidth=1)
    fps.grid(which='major', axis='both', linestyle='--', linewidth=0.5)

    fps.scatter(framePeakTime, framePeakValue, c='r', marker='x', s=2)
    fps.scatter(frameValleyTime, frameValleyValue, c='r', marker='x', s=2)
    fps.set_title(
        f'pointcloud frame rate {ConvertTimeToStr(beg)} ~ {ConvertTimeToStr(end)}'
    )
    fps.set_ylabel('frames per second')
    fps.set_xticks(time_xtick_list)
    fps.set_xticklabels([f'{ConvertTimeToStr(t)}' for t in time_xtick_list],
                        rotation='vertical')
    fps.axhline(y=avgFrameRate, c='r', linewidth=0.5)
    for x, y in zip(framePeakTime, framePeakValue):
        fps.annotate(f'({ConvertTimeToStr(x)}, {y})',
                     xy=(x, y),
                     xytext=(0, 10),
                     textcoords='offset points',
                     ha='center',
                     va='top')
    for x, y in zip(frameValleyTime, frameValleyValue):
        fps.annotate(f'({ConvertTimeToStr(x)}, {y})',
                     xy=(x, y),
                     xytext=(0, 10),
                     textcoords='offset points',
                     ha='center',
                     va='top')

    latencyFig = fig.add_subplot(2, 1, 2)
    latencyFig.plot(time,
                    latencyList,
                    marker='x',
                    markersize=1.5,
                    linestyle='solid',
                    linewidth=1)
    latencyFig.grid(which='major', axis='both', linestyle='--', linewidth=0.5)
    latencyFig.scatter(latencyPeakTime,
                       latencyPeakValue,
                       c='r',
                       marker='x',
                       s=2)
    latencyFig.set_title(
        f'pointcloud latency {ConvertTimeToStr(beg)} ~ {ConvertTimeToStr(end)}'
    )
    latencyFig.set_xticks(time_xtick_list)
    latencyFig.set_xticklabels(
        [f'{ConvertTimeToStr(t)}' for t in time_xtick_list],
        rotation='vertical')
    latencyFig.set_ylabel('latency / s')
    latencyFig.axhline(y=avgLatency, c='r', linewidth=0.5)
    for x, y in zip(latencyPeakTime, latencyPeakValue):
        latencyFig.annotate(f'({ConvertTimeToStr(x)}, {round(y*1000,0)}ms)',
                            xy=(x, y),
                            xytext=(0, 10),
                            textcoords='offset points',
                            ha='center',
                            va='top')

    fig.tight_layout()
    fig.savefig(f'{targetDir}/LidarFpsLatency.png', dpi=300)
    plt.close(fig)
    plt_results.append(fig)
    return text_results,plt_results



def AnalyseLidarFrameLost(lines: list, targetDir: str, beg: int, end: int):
    text_results = []
    plt_results = []
    time = list(range(beg, end + 1, 1))
    frameLostCount = [0] * len(time)
    totalLostCount = 0

    AnnotationTime = []
    AnnotationLost = []

    for line in lines:
        fields = line.split(' ')
        logTimeStr = fields[1][:8]
        tp = ConvertStrToTime(logTimeStr)
        lostCount = (float(fields[12][:-2]) - float(fields[8][:-1])) * 50
        frameLostCount[tp - beg] += lostCount
        totalLostCount += lostCount

    for i in range(len(time)):
        if frameLostCount[i] > 0:
            AnnotationTime.append(time[i])
            AnnotationLost.append(frameLostCount[i])

    totalLostCount = round(totalLostCount, 0)

    result = f'PointCloud Frame Lost in {end - beg} seconds (Approximate): {totalLostCount}\n'
    result += f'PointCloud Frame Lost Percentage (Approximate): {round(100 * totalLostCount/((end-beg+1)*50), 2)}%\n'

    with open(f'{targetDir}/LidarFpsLatencyFrameLost.txt', 'a+') as f:
        f.write(result)
    text_results.append(result)

    fig = plt.figure(figsize=(12, 4))
    frameLostFig = fig.add_subplot(1, 1, 1)
    frameLostFig.plot(time,
                      frameLostCount,
                      marker='o',
                      markersize=1.5,
                      linestyle='solid',
                      linewidth=1)
    frameLostFig.grid(which='major',
                      axis='both',
                      linestyle='--',
                      linewidth=0.5)
    frameLostFig.scatter(AnnotationTime,
                         AnnotationLost,
                         c='r',
                         marker='o',
                         s=3)
    for x, y in zip(AnnotationTime, AnnotationLost):
        frameLostFig.annotate(f'({ConvertTimeToStr(x)}, {round(y,0)})',
                              xy=(x, y),
                              xytext=(0, 10),
                              textcoords='offset points',
                              ha='center',
                              va='top')

    frameLostFig.set_title(
        f'pointcloud frame lost {ConvertTimeToStr(beg)} ~ {ConvertTimeToStr(end)}'
    )
    frameLostFig.set_ylabel('frame lost per second')
    time_xtick_list = list(
        range(time[0], time[-1], max(1, (time[-1] - time[0]) // 30)))
    frameLostFig.set_xticks(time_xtick_list)
    frameLostFig.set_xticklabels(
        [f'{ConvertTimeToStr(t)}' for t in time_xtick_list],
        rotation='vertical')

    fig.tight_layout()
    fig.savefig(f'{targetDir}/LidarFrameLost.png', dpi=300)
    plt_results.append(fig)
    return text_results,plt_results
    


def AnalysePointCloudSize(lines: list, targetDir: str, beg: int, end: int):
    text_results = []
    plt_results = []
    time0 = []
    time1 = []
    time2 = []
    pclsz0 = []  # top
    pclsz1 = []  # surroundings
    pclsz2 = []  # fusion
    for line in lines:
        fields = line.split(' ')
        logTimeStr = fields[1][:15]
        label = int(fields[fields.index('pointcloud,') - 1])
        temp_pclsz_str: str = fields[fields.index('pointsize') + 2]
        pclsz_str: str
        for i in range(len(temp_pclsz_str)):
            if not temp_pclsz_str[i].isdigit():
                pclsz_str = temp_pclsz_str[:i]
                break
        pclsz = int(pclsz_str)
        tp = ConvertStrToTimePrecise(logTimeStr)
        if label == 0:
            time0.append(tp)
            pclsz0.append(pclsz)
        if label == 1:
            time1.append(tp)
            pclsz1.append(pclsz)
        if label == 2:
            time2.append(tp)
            pclsz2.append(pclsz)

    fig = plt.figure(figsize=(12, 6))
    pclszfig = fig.add_subplot(1, 1, 1)

    pclszfig.plot(time0,
                  pclsz0,
                  marker='o',
                  markersize=1.5,
                  linestyle='solid',
                  linewidth=0.5,
                  label='Top')
    pclszfig.plot(time1,
                  pclsz1,
                  marker='o',
                  markersize=1.5,
                  linestyle='solid',
                  linewidth=0.5,
                  label='surroundings')
    pclszfig.plot(time2,
                  pclsz2,
                  marker='o',
                  markersize=1.5,
                  linestyle='solid',
                  linewidth=0.5,
                  label='fusion')
    pclszfig.grid(which='major', axis='both', linestyle='--', linewidth=0.5)
    pclszfig.axhline(y=57600, c='r', linewidth=0.5)
    pclszfig.axhline(y=20000, c='r', linewidth=0.5)
    pclszfig.axhline(y=77600, c='r', linewidth=0.5)

    pclszfig.set_title(
        f'PointcloudSize {ConvertTimeToStr(beg)} ~ {ConvertTimeToStr(end)}')
    pclszfig.set_ylabel('PointCloud Size')
    b, e = GetMinMaxFromMultipleLists([time0, time1, time2])
    time_xtick_list = list(range(b, e, max(1, (e - b) // 30)))
    pclszfig.set_xticks(time_xtick_list)
    pclszfig.set_xticklabels(
        [f'{ConvertTimeToStr(t)}' for t in time_xtick_list],
        rotation='vertical')
    pclszfig.legend()

    fig.tight_layout()
    fig.savefig(f'{targetDir}/PointCloudSize.png', dpi=300)
    plt_results.append(fig)
    return text_results,plt_results


def AnalyseNanRatio(lines: list, targetDir: str, beg: int, end: int):
    '''
    LOG_WARN("NAN ratio in pointcloud is too high: {}/{}={}", nan, all, ratio);
    '''
    text_results = []
    plt_results = []
    statistics = {}
    for line in lines:
        fields = line.split(' ')
        logTimeStr = fields[1][:15]
        tp = ConvertStrToTimePrecise(logTimeStr)
        statistics[tp] = float(fields[-1].split('=')[-1]) * 100

    list_for_plot = sorted(statistics.items())

    fig = plt.figure(figsize=(12, 6))
    nanRatioFig = fig.add_subplot(1, 1, 1)

    nanRatioFig.scatter([x[0] for x in list_for_plot],
                        [x[1] for x in list_for_plot],
                        marker='o',
                        s=1.5)
    nanRatioFig.grid(which='major', axis='both', linestyle='--', linewidth=0.5)
    nanRatioFig.axhline(y=100, c='r', linewidth=0.5)
    nanRatioFig.axhline(y=0, c='b', linewidth=0.5)

    nanRatioFig.set_title(
        f'PointcloudNanRatio {ConvertTimeToStr(beg)} ~ {ConvertTimeToStr(end)}'
    )
    nanRatioFig.set_ylabel('PointCloud NAN Ratio')
    time_xtick_list = list(range(beg, end, max(1, (end - beg) // 30)))
    nanRatioFig.set_xticks(time_xtick_list)
    nanRatioFig.set_xticklabels(
        [f'{ConvertTimeToStr(t)}' for t in time_xtick_list],
        rotation='vertical')
    nanRatioFig.set_yticks([i for i in range(0, 110, 10)])
    nanRatioFig.set_yticklabels([str(i) for i in range(0, 110, 10)],
                                rotation='horizontal')

    fig.tight_layout()
    fig.savefig(f'{targetDir}/PointCloudNanRatio.png', dpi=300)
    plt_results.append(fig)
    return text_results,plt_results

def AnalyseNanPoint(lines: list, targetDir: str, beg: int, end: int, titleName: str):
    '''
    LOG_INFO(publish {} pointcloud, system time is {}, timestamp is {}, pointsize"
    "is {}, channel is {}, nan ratio is {}",
        config_.fusion_mode(), time_now, pointcloud_time,
        cloud_msg->point_size(), config_.channel_name(), (double)cloud_msg->nan_point_size()/cloud_msg->point_size());
    '''
    text_results = []
    plt_results = []

    statistics = {}
    for line in lines:
        fields = line.split(' ')
        packet_tp = fields[10]
        packet_tp = packet_tp.rstrip(',')
        unix_tp = float(packet_tp)
        beijing_tz = pytz.timezone('Asia/Shanghai')
        dt = datetime.datetime.fromtimestamp(unix_tp, beijing_tz)
        time_str = dt.strftime('%H:%M:%S.%f')
        tp = ConvertStrToTimePrecise(time_str)
        statistics[tp] = float(fields[-1].split('=')[-1]) * 100
        
    list_for_plot = sorted(statistics.items())

    fig = plt.figure(figsize=(12, 6))
    nanRatioFig = fig.add_subplot(1, 1, 1)

    nanRatioFig.scatter([x[0] for x in list_for_plot],
                        [x[1] for x in list_for_plot],
                        marker='o',
                        s=1.5)
    nanRatioFig.grid(which='major', axis='both', linestyle='--', linewidth=0.5)
    nanRatioFig.axhline(y=70, c='r', linewidth=0.5)
    nanRatioFig.axhline(y=0, c='b', linewidth=0.5)
    nanRatioFig.set_title(f'{titleName} {ConvertTimeToStr(beg)} ~ {ConvertTimeToStr(end)}')
    nanRatioFig.set_ylabel('PointCloud NAN Ratio')
    time_xtick_list = list(range(beg, end, max(1, (end - beg) // 30)))
    nanRatioFig.set_xticks(time_xtick_list)
    nanRatioFig.set_xticklabels([f'{ConvertTimeToStr(t)}' for t in time_xtick_list], rotation='vertical')
    nanRatioFig.set_yticks([i for i in range(0, 110, 10)])
    nanRatioFig.set_yticklabels([str(i) for i in range(0, 110, 10)], rotation='horizontal')

    fig.tight_layout()
    fig.savefig(f'{targetDir}/{titleName}.png', dpi=300)

    plt_results.append(fig)
    return text_results,plt_results

