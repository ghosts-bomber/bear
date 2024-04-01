# import matplotlib
import matplotlib.pyplot as plt
from .PublicLib import *
import math
import os

# matplotlib.use('agg')
'''
BestGnss = namedtuple("BestGnss",
                      ("timestamp", "x", "y", "z", "gnss_status", "longitude",
                       "latitude", "altitude", "diff_age"))

Tf = namedtuple("Tf", ("timestamp", "x", "y", "z", "roll", "pitch", "yaw",
                       "ndt_flag", "sensor_error_code"))

InspvaxGnss = namedtuple("InspvaxGnss",
                         ("timestamp", "x", "y", "z", "roll", "pitch", "yaw",
                          "lat", "lon", "height"))

InspvaxNdtPoseAttitude = namedtuple(
    "InspvaxNdtPoseAttitude", ("timestamp", "x", "y", "z", "roll", "pitch",
                               "yaw", "lidar_status", "lidar_consistency"))
'''


def AnalysePosition(bestGnssPosLog: list, tfLog: list, inspvaxGnssLog: list,
                    inspvaxNdtPoseAttitudes: list, targetDir: str, beg: int,
                    end: int):

    text_results = [] 
    plt_results = []
    bestGnssX = []
    bestGnssY = []
    bestGnssZ = []

    tfX = []
    tfY = []
    tfZ = []

    inspvaxGnssX = []
    inspvaxGnssY = []
    inspvaxGnssZ = []

    inspvaxNdtPoseAttitudesX = []
    inspvaxNdtPoseAttitudesY = []
    inspvaxNdtPoseAttitudesZ = []

    bestGnssCSV = 'timestamp,x,y,z,gnss_status,longitude,latitude,altitude,diff_age\n'
    tfCSV = 'timestamp,x,y,z,roll,pitch,yaw,ndt_flag,sensor_error_code\n'
    inspvaxGnssCSV = 'timestamp,x,y,z,roll,pitch,yaw,lat,lon,height\n'
    inspvaxNdtPoseAttitudeCSV = 'timestamp,x,y,z,roll,pitch,yaw,lidar_status,lidar_consistency\n'

    for line in bestGnssPosLog:
        fields = line.split(' ')
        for id, val in enumerate(fields):
            if val == ',' or val == '' or val == '\n':
                fields.pop(id)

        id_timestamp = fields.index('gnss_status:')
        timestamp = float(fields[id_timestamp - 1].split(',')[0])

        id_pose = fields.index('pose:')
        x = float(fields[id_pose + 1][:-1])
        y = float(fields[id_pose + 2][:-1])
        z = float(fields[id_pose + 3][:-1])

        id_gnss_status = fields.index('gnss_status:')
        gnss_status = float(fields[id_gnss_status + 1][:-1])

        id_gps = fields.index('alti:')
        longitude = float(fields[id_gps + 1])
        latitude = float(fields[id_gps + 2])
        altitude = float(fields[id_gps + 3])

        id_diff_age = fields.index('age:')
        diff_age = float(fields[id_diff_age + 1])
        bestGnssCSV += f'{timestamp},{x},{y},{z},{gnss_status},{longitude},{latitude},{altitude},{diff_age}\n'
        bestGnssX.append(x)
        bestGnssY.append(y)
        bestGnssZ.append(z)

    for line in tfLog:
        fields = line.split(' ')
        for id, val in enumerate(fields):
            if val == ',' or val == '' or val == '\n':
                fields.pop(id)

        id_x = fields.index('x:')
        timestamp = float(fields[id_x + 1])
        x = float(fields[id_x + 2])

        id_y = fields.index('y:')
        y = float(fields[id_y + 1])

        id_z = fields.index('z:')
        z = float(fields[id_z + 1])

        id_attitude = fields.index('attitude:')
        roll = float(fields[id_attitude + 3])
        pitch = float(fields[id_attitude + 2])
        yaw = float(fields[id_attitude + 1])

        id_ndt_flag = fields.index('only_ndt_used_flag:')
        ndt_flag = fields[id_ndt_flag + 1][:4]

        sensor_error_code = fields[-7]
        tfCSV += f'{timestamp},{x},{y},{z},{roll},{pitch},{yaw},{ndt_flag},{sensor_error_code}\n'
        tfX.append(x)
        tfY.append(y)
        tfZ.append(z)

    for line in inspvaxGnssLog:
        fields = line.split(' ')
        for id, val in enumerate(fields):
            if val == ',' or val == '' or val == '\n':
                fields.pop(id)
        timestamp = float(fields[-19])
        x = float(fields[-17])
        y = float(fields[-15])
        z = float(fields[-13])
        roll = float(fields[-7])
        pitch = float(fields[-9])
        yaw = float(fields[-11])
        latitude = float(fields[-5])
        longitude = float(fields[-3])
        height = float(fields[-1])
        inspvaxGnssCSV += f'{timestamp},{x},{y},{z},{roll},{pitch},{yaw},{latitude},{longitude},{height}\n'
        inspvaxGnssX.append(x)
        inspvaxGnssY.append(y)
        inspvaxGnssZ.append(z)

    for line in inspvaxNdtPoseAttitudes:
        fields = line.split(' ')
        for id, val in enumerate(fields):
            if val == ',' or val == '' or val == '\n':
                fields.pop(id)
        id_timestamp = fields.index('at--------------------------:')
        timestamp = float(fields[id_timestamp + 1])

        id_pose = fields.index('pose:')
        x = float(fields[id_pose + 1])
        y = float(fields[id_pose + 2])
        z = float(fields[id_pose + 3])

        id_attitude = fields.index('attitude:')
        roll = float(fields[id_attitude + 3])
        pitch = float(fields[id_attitude + 2])
        yaw = float(fields[id_attitude + 1])

        lidar_status = float(fields[id_timestamp + 2])
        lidar_consistency = float(fields[-1])

        inspvaxNdtPoseAttitudeCSV += f'{timestamp},{x},{y},{z},{roll},{pitch},{yaw},{lidar_status},{lidar_consistency}\n'
        inspvaxNdtPoseAttitudesX.append(x)
        inspvaxNdtPoseAttitudesY.append(y)
        inspvaxNdtPoseAttitudesZ.append(z)

    if not os.path.exists(f'{targetDir}/localization'):
        os.mkdir(f'{targetDir}/localization')
    with open(f'{targetDir}/localization/bestGnss.csv', 'w+') as f:
        f.write(bestGnssCSV)
    with open(f'{targetDir}/localization/tf.csv', 'w+') as f:
        f.write(tfCSV)
    with open(f'{targetDir}/localization/inspvaxGnss.csv', 'w+') as f:
        f.write(inspvaxGnssCSV)
    with open(f'{targetDir}/localization/inspvaxNdtPoseAttitude.csv',
              'w+') as f:
        f.write(inspvaxNdtPoseAttitudeCSV)

    minX, maxX = GetMinMaxFromMultipleLists(
        [bestGnssX, tfX, inspvaxGnssX, inspvaxNdtPoseAttitudesX])

    minY, maxY = GetMinMaxFromMultipleLists(
        [bestGnssY, tfY, inspvaxGnssY, inspvaxNdtPoseAttitudesY])

    if maxX - minX == 0 or maxY - minY == 0:
        FormatedPrint('Position data abnormal, abort analysis')
        return

    HvsVRatio = (maxX - minX) / (maxY - minY)
    tick_interval = max(1, min((maxY - minY), (maxX - minX)) // 20)

    AnnotationInterval = max(1, (end - beg) //
                             (max(maxX - minX, maxY - minY) // tick_interval))
    time = []
    AnnotationX = []
    AnnotationY = []

    for line in bestGnssPosLog:
        fields = line.split(' ')
        for id, val in enumerate(fields):
            if val == ',' or val == '' or val == '\n':
                fields.pop(id)
        id_timestamp = fields.index('gnss_status:')
        timestamp = float(fields[id_timestamp - 1].split(',')[0])

        id_pose = fields.index('pose:')
        x = float(fields[id_pose + 1][:-1])
        y = float(fields[id_pose + 2][:-1])
        if len(time) == 0 or timestamp - time[-1] >= AnnotationInterval:
            time.append(timestamp)
            AnnotationX.append(x)
            AnnotationY.append(y)

    pictureSize = None
    if HvsVRatio >= 1:
        pictureSize = (math.ceil(10 * HvsVRatio), 10)
    else:
        pictureSize = (10, math.ceil(10 / HvsVRatio))

    fig = plt.figure(figsize=pictureSize)
    poseFig = fig.add_subplot(1, 1, 1)
    poseFig.scatter(bestGnssX,
                    bestGnssY,
                    marker='o',
                    s=1.5,
                    c='r',
                    label='BestGnssPos')
    poseFig.plot(tfX,
                 tfY,
                 marker=',',
                 linestyle='solid',
                 linewidth=1,
                 c='m',
                 alpha=1,
                 label='TF')
    poseFig.plot(inspvaxGnssX,
                 inspvaxGnssY,
                 marker=',',
                 linestyle='solid',
                 linewidth=1,
                 c='g',
                 alpha=1,
                 label='InspvaxGnssPos')
    poseFig.plot(inspvaxNdtPoseAttitudesX,
                 inspvaxNdtPoseAttitudesY,
                 marker=',',
                 linestyle='solid',
                 linewidth=1,
                 c='b',
                 alpha=1,
                 label='InspvaxNdtAttitude')
    poseFig.set_title(
        f'Position Trace {ConvertTimeToStr(beg)} ~ {ConvertTimeToStr(end)}')

    poseFig.set_xlabel('X')
    poseFig.set_xticks(list(range(minX, maxX, tick_interval)))
    poseFig.set_xticklabels(
        [f'{x}' for x in list(range(minX, maxX, tick_interval))],
        rotation='vertical')

    poseFig.set_ylabel('Y')
    poseFig.set_yticks(list(range(minY, maxY, tick_interval)))
    poseFig.set_yticklabels(
        [f'{y}' for y in list(range(minY, maxY, tick_interval))])

    poseFig.grid(which='major', axis='both', linestyle='--', linewidth=0.5)

    poseFig.scatter(AnnotationX,
                    AnnotationY,
                    marker='o',
                    s=3,
                    c='black',
                    label='timestamp')
    index = 0
    for x, y in zip(AnnotationX, AnnotationY):
        poseFig.annotate(f'{ConvertUnixTimeToStr(time[index])}',
                         xy=(x, y),
                         xytext=(0, 0),
                         textcoords='offset points',
                         ha='center',
                         va='top',
                         rotation='vertical')
        index += 1

    poseFig.legend()
    fig.tight_layout()
    fig.savefig(f'{targetDir}/Position.png', dpi=300)
    plt_results.append(fig)

    heightFig = plt.figure(figsize=(12, 7))
    subfig_height = heightFig.add_subplot(1, 1, 1)
    subfig_height.scatter(list(range(0, 10 * len(bestGnssZ), 10)),
                          bestGnssZ,
                          marker='o',
                          s=1.5,
                          c='r',
                          label='BestGnssPos')
    subfig_height.plot(list(range(len(tfZ))),
                       tfZ,
                       marker=',',
                       linestyle='solid',
                       linewidth=1,
                       c='m',
                       alpha=1,
                       label='TF')
    subfig_height.plot(list(range(len(inspvaxGnssZ))),
                       inspvaxGnssZ,
                       marker=',',
                       linestyle='solid',
                       linewidth=1,
                       c='g',
                       alpha=1,
                       label='InspvaxGnssPos')
    subfig_height.plot(list(range(len(inspvaxNdtPoseAttitudesZ))),
                       inspvaxNdtPoseAttitudesZ,
                       marker=',',
                       linestyle='solid',
                       linewidth=1,
                       c='b',
                       alpha=1,
                       label='InspvaxNdtAttitude')
    subfig_height.set_title(
        f'Vehicle Height {ConvertTimeToStr(beg)} ~ {ConvertTimeToStr(end)}')
    subfig_height.set_ylabel('Height / m')
    subfig_height.grid(which='major',
                       axis='both',
                       linestyle='--',
                       linewidth=0.5)
    subfig_height.legend()
    heightFig.tight_layout()
    heightFig.savefig(f'{targetDir}/Height.png', dpi=300)
    plt_results.append(heightFig)
    return text_results,plt_results
