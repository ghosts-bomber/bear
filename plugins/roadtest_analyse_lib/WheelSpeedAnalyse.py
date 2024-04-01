from .PublicLib import *
# import matplotlib
import matplotlib.pyplot as plt
import math

# matplotlib.use('agg')


def AnalyseWheelSpeed(lines: list, targetDir: str):
    text_results = []
    plt_results = []

    time = []
    FL = []
    FR = []
    RL = []
    RR = []
    bestGnssMeasureTime = []
    bestGnssVels = []
    GearState = []

    GearSwitchTime = []
    GearSwitchFrom = []

    lastTimeStamp = 0 
    lastGear = ''

    anormallyLogs = ''
    for line in lines:
        if line.find('wheel speed') != -1 and line.find('dr_core.cc') != -1:
            anormallyLogs += f'{line}\n'
        elif line.find('bestgnssvel  measurement at') != -1:
            gnssFields = line.split(' ')
            for id, val in enumerate(gnssFields):
                if val == '' or val == '\n':
                    gnssFields.pop(id)
            bestGnssMeasureTime.append(float(gnssFields[-10][:-1]))
            x = float(gnssFields[-5][1:])
            y = float(gnssFields[-4])
            z = float(gnssFields[-3][:-1])
            bestGnssVels.append(math.sqrt(x**2 + y**2 + z**2))
        else:
            fields = line.split(' ')
            for id, val in enumerate(fields):
                if val == '' or val == '\n':
                    fields.pop(id)

            time.append(float(fields[-6]))
            FL.append(float(fields[-5]))
            FR.append(float(fields[-4]))
            RL.append(float(fields[-3]))
            RR.append(float(fields[-2]))
            GearState.append(fields[-1])

            if lastTimeStamp != 0 and lastGear != fields[-1]:
                GearSwitchTime.append(lastTimeStamp)
                GearSwitchFrom.append(lastGear)

            lastTimeStamp = float(fields[-6])
            lastGear = fields[-1]

    beg = int(time[0])
    end = int(time[-1])
    time_xtick_list = list(range(beg, end, max(1, (end - beg) // 30)))

    fig = plt.figure(figsize=(16, 9))
    WheelSpeedFig = fig.add_subplot(3, 1, (1, 2))
    WheelSpeedFig.set_title(
        f'Wheel Speed {ConvertUnixTimeToStr(beg)} ~ {ConvertUnixTimeToStr(end)}'
    )
    WheelSpeedFig.set_ylabel('Speed / m/s')
    WheelSpeedFig.set_xticks(time_xtick_list)
    WheelSpeedFig.set_xticklabels(
        [ConvertUnixTimeToStr(t) for t in time_xtick_list],
        rotation='vertical')
    WheelSpeedFig.plot(time,
                       FL,
                       marker=',',
                       linestyle='solid',
                       c='m',
                       linewidth=1,
                       label='FrontLeft',
                       alpha=0.7)
    WheelSpeedFig.plot(time,
                       FR,
                       marker=',',
                       linestyle='solid',
                       c='y',
                       linewidth=1,
                       label='FrontRight',
                       alpha=0.7)
    WheelSpeedFig.plot(time,
                       RL,
                       marker=',',
                       linestyle='solid',
                       c='g',
                       linewidth=1,
                       label='RearLeft',
                       alpha=0.7)
    WheelSpeedFig.plot(time,
                       RR,
                       marker=',',
                       linestyle='solid',
                       c='b',
                       linewidth=1,
                       label='RearRight',
                       alpha=0.7)
    WheelSpeedFig.scatter(bestGnssMeasureTime,
                          bestGnssVels,
                          marker='o',
                          s=2,
                          c='r',
                          label='GnssVelocity')
    WheelSpeedFig.legend()
    WheelSpeedFig.axhline(y=0, c='black', linewidth=1)
    WheelSpeedFig.grid(which='major',
                       axis='both',
                       linestyle='--',
                       linewidth=0.5)

    GearFig = fig.add_subplot(3, 1, 3)
    GearFig.set_title(
        f'Gear State {ConvertUnixTimeToStr(beg)} ~ {ConvertUnixTimeToStr(end)}'
    )
    GearFig.set_ylabel('Gear')
    GearFig.set_xticks(time_xtick_list)
    GearFig.set_xticklabels([ConvertUnixTimeToStr(t) for t in time_xtick_list],
                            rotation='vertical')
    GearFig.set_yticks([-1, 0, 1])
    GearFig.set_yticklabels(['REVERSE', 'NEUTRAL', 'DRIVE'])
    GearFig.plot(time, [ConvertGearToNumber(g) for g in GearState],
                 marker=',',
                 linestyle='solid',
                 linewidth=1)
    GearFig.scatter(GearSwitchTime,
                    [ConvertGearToNumber(g) for g in GearSwitchFrom],
                    c='r',
                    marker='o',
                    s=3)
    for x, y in zip(GearSwitchTime,
                    [ConvertGearToNumber(g) for g in GearSwitchFrom]):
        GearFig.annotate(
            f'({ConvertUnixTimeToStr(x)}, {ConvertNumberToGear(y)})',
            xy=(x, y),
            xytext=(0, 10),
            textcoords='offset points',
            ha='center',
            va='top')

    fig.tight_layout()
    fig.savefig(f'{targetDir}/WheelSpeed.png', dpi=300)
    plt_results.append(fig)
    with open(f'{targetDir}/anormallyWheelSpeedLog.txt', 'w+') as f:
        if len(anormallyLogs) != 0:
            f.write(anormallyLogs)
            text_results.append(anormallyLogs)
        else:
            text = 'No anormally wheel speed logs'
            f.write(text)
            text_results.append(anormallyLogs)
    return text_results,plt_results
