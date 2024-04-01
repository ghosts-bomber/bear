from .PublicLib import *
import matplotlib.pyplot as plt
# import matplotlib

# matplotlib.use('agg')


def AnalyseDynamicMapLoad(arr: list, targetDir: str, beginTime: int,
                          endTime: int):
    text_results = []
    plt_results = []
    stack = []
    time = list(range(beginTime, endTime + 1, 1))
    loadCost = [0.0] * len(time)

    loadHappenTime = []
    loadHappenCost = []
    loadBeginTime = 0
    for line in arr:
        fields = line.split(' ')
        timeStrPrecise = fields[1][:fields[1].find(']')]
        preciseTime = ConvertStrToTimePrecise(timeStrPrecise)
        if line.find('start') != -1:
            logTimeStr = fields[1][:8]
            loadBeginTime = ConvertStrToTime(logTimeStr)
            stack.append(preciseTime)
        else:
            if len(stack) == 0:
                continue
            cost = 1000 * (preciseTime - stack[-1])
            loadCost[loadBeginTime - beginTime] = cost
            stack.pop(-1)
            loadHappenTime.append(loadBeginTime)
            loadHappenCost.append(cost)

    fig = plt.figure(figsize=(12, 4))
    time_xtick_list = list(
        range(time[0], time[-1], max(1, (time[-1] - time[0]) // 30)))
    mapLoad = fig.add_subplot(1, 1, 1)
    mapLoad.plot(time,
                 loadCost,
                 marker='o',
                 markersize=1.5,
                 linestyle='solid',
                 linewidth=1)
    mapLoad.grid(which='major', axis='both', linestyle='--', linewidth=0.5)
    mapLoad.scatter(loadHappenTime, loadHappenCost, c='r', marker='x', s=2)
    mapLoad.set_title(
        f'Dynamic Map Load {ConvertTimeToStr(beginTime)} ~ {ConvertTimeToStr(endTime)}'
    )
    mapLoad.set_ylabel('Load Cost / ms')
    mapLoad.set_xticks(time_xtick_list)
    mapLoad.set_xticklabels(
        [f'{ConvertTimeToStr(t)}' for t in time_xtick_list],
        rotation='vertical')
    for x, y in zip(loadHappenTime, loadHappenCost):
        mapLoad.annotate(f'({ConvertTimeToStr(x)}, {round(y,0)}ms)',
                         xy=(x, y),
                         xytext=(0, 10),
                         textcoords='offset points',
                         ha='center',
                         va='top')
    fig.tight_layout()
    fig.savefig(f'{targetDir}/DynamicMapLoad.png', dpi=300)
    plt_results.append(fig)
    return text_results,plt_results
