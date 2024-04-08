from IPlugin import IPlugin
from Result import IResult, TextResult,ImageResult
from PyQt5.QtGui import QImage
import typing
import logging

from plugins.roadtest_analyse_lib.PublicLib import *
from plugins.roadtest_analyse_lib.OrinRecvMpuAnalyse import AnalyseOrinReceiveMpu
from plugins.roadtest_analyse_lib.LidarAnalyse import AnalyseLidarFpsAndLatency,AnalyseLidarFrameLost,AnalysePointCloudSize,AnalyseNanRatio,AnalyseNanRatio
from plugins.roadtest_analyse_lib.GnssAnalyse import AnalyseGnss
from plugins.roadtest_analyse_lib.LocalizationDynamicMapLoadAnalyse import AnalyseDynamicMapLoad
from plugins.roadtest_analyse_lib.WheelSpeedAnalyse import AnalyseWheelSpeed
from plugins.roadtest_analyse_lib.PositionAnalyse import AnalysePosition
from plugins.roadtest_analyse_lib.LidarUdpPacketAnalyse import AnalyseLidarUdpPacket


class GnssLidarWheelStatic(IPlugin):
    def __init__(self) -> None:
        pass

    def GetPluginInfo(self) -> str:
        return 'gnss雷达轮速图表'

    def Process(self,text_data)->typing.List['IResult']:
        self.results:typing.List['IResult'] = []
        self.results.append(TextResult('gnss、雷达频率、轮速绘图'))
        self.results = self.results + self.get_common_result('行驶中触发升降级','雷达nan点过高导致 / 雷达帧率不足导致 / 串口数据延迟导致')

        originLog = text_data.get_lines()

        originLog.pop(-1)
        end_index = -1
        while len(originLog[end_index]) < 25 or len(originLog[end_index].split(' ')) < 2 or (
                not originLog[end_index].split(' ')[1][0].isdigit()):
            end_index = end_index - 1

        begPos = 0
        while not originLog[begPos].split(' ')[1][0].isdigit():
            begPos += 1
        fields = originLog[begPos].split(' ')
        beginLogTimeStr = fields[1][:8]
        beginTime = ConvertStrToTime(beginLogTimeStr)

        fields = originLog[end_index].split(' ')
        endLogTimeStr = fields[1][:8]
        endTime = ConvertStrToTime(endLogTimeStr)

        FormatedPrint(f'Log time range: {beginLogTimeStr} ~ {endLogTimeStr}', 50)

        # log sort and filter

        FormatedPrint('Sorting Log File', 50)
        orinRecvMpuLog = []

        lidarFpsLog = []
        lidarFrameLostLog = []
        lidarNanRatioLog = []
        lidarNanPointTopLog = []
        lidarNanPointFrontLog = []

        gnssImuLog = []

        dynamiceMapLoadLog = []
        wheelSpeedLog = []

        bestGnssPosLog = []
        tfLog = []
        inspvaxGnssLog = []
        inspvaxNdtPoseAttitudes = []

        hesaiPacketReceiveLog = []
        livoxPacketReceiveLog = []
        robosensePacketReceiveLog = []

        for line in originLog:
            if 'raw_stream' in line and 'read data' in line:
                orinRecvMpuLog.append(line)
            elif 'publisher' in line and 'pointsize' in line:
                lidarFpsLog.append(line)
            elif 'publisher' in line and 'lost frame' in line:
                lidarFrameLostLog.append(line)
            elif 'novatel_ros_parser' in line:
                gnssImuLog.append(line)
            elif 'LoadDynamicMap______________________________' in line:
                dynamiceMapLoadLog.append(line)
            elif 'wheel_speed' in line or \
                 'wheel speed' in line and 'dr_core.cc' in line or \
                 'bestgnssvel  measurement at' in line:
                wheelSpeedLog.append(line)
            elif 'bestgnsspos measurement at' in line and 'lon_lat_hgt_std' in line:
                bestGnssPosLog.append(line)
            elif 'Publishing tf with' in line:
                tfLog.append(line)
            elif 'inspvax_gnss at timestamp' in line:
                inspvaxGnssLog.append(line)
            elif 'ndt measurement at' in line and 'post_msf_localization.cc' in line:
                inspvaxNdtPoseAttitudes.append(line)
            elif 'Hesai packet receive:' in line:
                hesaiPacketReceiveLog.append(line)
            elif 'Robosense packet receive:' in line:
                robosensePacketReceiveLog.append(line)
            elif 'Livox packet receive:' in line:
                livoxPacketReceiveLog.append(line)
            elif 'NAN ratio in pointcloud is too high' in line:
                lidarNanRatioLog.append(line)
            else:
                pass
        FormatedPrint('Log File sorted', 50)

        for line in lidarFpsLog:
            if 'publish 0 pointcloud' in line and '/sensor/lidar/top/pointcloud' in line:
                lidarNanPointTopLog.append(line)
            elif 'publish 1 pointcloud' in line and '/sensor/lidar/front/pointcloud' in line:
                lidarNanPointFrontLog.append(line)
            else:
                pass

        # analyse
        FormatedPrint('Analysis Starts', 50)
        # lidar fps and latency
        dir = './tmp/'
        if len(lidarFpsLog) != 0:
            try:
                text_results,plt_results = AnalyseLidarFpsAndLatency(lidarFpsLog, dir, beginTime, endTime)
                self.process_text_plt_results(text_results,plt_results)
                FormatedPrint('Lidar FPS Analysis Done', 50)
            except Exception as e:
                FormatedPrint(f'AnalyseLidarFpsAndLatency: {e}')
            try:
                text_results,plt_results = AnalysePointCloudSize(lidarFpsLog, dir, beginTime, endTime)
                self.process_text_plt_results(text_results,plt_results)
                FormatedPrint('PointCloud Size Analysis Done', 50)
            except Exception as e:
                FormatedPrint(f'AnalysePointCloudSize: {e}')
        else:
            FormatedPrint('Missing lidar log', 50)

        # lidar nan ratio
        if len(lidarNanRatioLog) != 0:
            try:
                text_results,plt_results = AnalyseNanRatio(lidarNanRatioLog, dir, beginTime, endTime)
                self.process_text_plt_results(text_results,plt_results)
                FormatedPrint(f'NAN Ratio Analysis Done', 50)
            except Exception as e:
                FormatedPrint(f'AnalyseNanRatio: {e}')
        else:
            FormatedPrint('No problem of NAN ratio', 50)

        # lidar nan point Top
        if len(lidarNanPointTopLog) != 0:
            try:
                text_results,plt_results = AnalyseNanPoint(lidarNanPointTopLog, dir, beginTime, endTime,
                                'PointCloudNanRatio_Top')
                self.process_text_plt_results(text_results,plt_results)
                FormatedPrint(f'NAN Point in Top Lidar Analysis Done', 50)
            except Exception as e:
                FormatedPrint(f'AnalyseNanPoint: {e}')
        else:
            FormatedPrint('No related log of top lidar nan point', 50)

        # lidar nan point Front
        if len(lidarNanPointFrontLog) != 0:
            try:
                text_results,plt_results = AnalyseNanPoint(lidarNanPointFrontLog, dir, beginTime, endTime,
                                'PointCloudNanRatio_Front')
                self.process_text_plt_results(text_results,plt_results)
                FormatedPrint(f'NAN Point in Front Lidar Analysis Done', 50)
            except Exception as e:
                FormatedPrint(f'AnalyseNanPoint: {e}')
        else:
            FormatedPrint('No related log of front lidar nan point', 50)

        # lidar frame lost
        if len(lidarFrameLostLog) != 0:
            try:
                text_results,plt_results = AnalyseLidarFrameLost(lidarFrameLostLog, dir, beginTime, endTime)
                self.process_text_plt_results(text_results,plt_results)
                FormatedPrint('Lidar Frame Lost Analysis Done', 50)
            except Exception as e:
                FormatedPrint(f'AnalyseLidarFrameLost: {e}')
        else:
            FormatedPrint('No frame lost in lidar', 50)

        # lidar udp packet
        if len(hesaiPacketReceiveLog) !=0 or \
           len(robosensePacketReceiveLog)!=0 or \
           len(livoxPacketReceiveLog)!=0:
            try:
                text_results,plt_results = AnalyseLidarUdpPacket(hesaiPacketReceiveLog, livoxPacketReceiveLog,
                                      robosensePacketReceiveLog, dir, beginTime,
                                      endTime)
                self.process_text_plt_results(text_results,plt_results)
                FormatedPrint('Lidar UDP Packet Analysis Done', 50)
            except Exception as e:
                FormatedPrint(f'AnalyseLidarUdpPacket: {e}')
        else:
            FormatedPrint('No Anormally in lidar udp packet receive', 50)

        # orin receive mpu data
        if len(orinRecvMpuLog) != 0:
            try:
                text_results,plt_results = AnalyseOrinReceiveMpu(orinRecvMpuLog, dir, beginTime, endTime)
                self.process_text_plt_results(text_results,plt_results)
                FormatedPrint('OrinInput Analysis Done', 50)
            except Exception as e:
                FormatedPrint(f'AnalyseOrinReceiveMpu: {e}')
        else:
            FormatedPrint('Missing orin receive mpu log', 50)

        # gnss and imu lost frame and latency
        if len(gnssImuLog) != 0:
            try:
                text_results,plt_results = AnalyseGnss(gnssImuLog, dir, beginTime, endTime)
                self.process_text_plt_results(text_results,plt_results)
                FormatedPrint('Gnss Analysis Done', 50)
            except Exception as e:
                FormatedPrint(f'AnalyseGnss: {e}')
        else:
            FormatedPrint('Missing gnss log', 50)

        # dynamic map load
        if len(dynamiceMapLoadLog) != 0:
            try:
                text_results,plt_results = AnalyseDynamicMapLoad(dynamiceMapLoadLog, dir, beginTime, endTime)
                self.process_text_plt_results(text_results,plt_results)
                FormatedPrint('Dynamic load Analysis Done', 50)
            except Exception as e:
                FormatedPrint(f'AnalyseDynamicMapLoad: {e}')
        else:
            FormatedPrint('Missing Dynamic Load Log', 50)

        # wheel speed
        if len(wheelSpeedLog) != 0:
            try:
                text_results,plt_results = AnalyseWheelSpeed(wheelSpeedLog, dir)
                self.process_text_plt_results(text_results,plt_results)
                FormatedPrint('WheelSpeed Analysis Done', 50)
            except Exception as e:
                FormatedPrint(f'AnalyseWheelSpeed: {e}')
        else:
            FormatedPrint('Missing WheelSpeed Log', 50)

        # position
        if len(bestGnssPosLog) != 0 or len(tfLog) != 0 or len(
                inspvaxGnssLog) != 0 or len(inspvaxNdtPoseAttitudes) != 0:
            try:
                text_results,plt_results = AnalysePosition(bestGnssPosLog, tfLog, inspvaxGnssLog,
                                inspvaxNdtPoseAttitudes, dir, beginTime, endTime)
                self.process_text_plt_results(text_results,plt_results)
                FormatedPrint('Position Analysis Done', 50)
            except Exception as e:
                FormatedPrint(f'AnalysePosition: {e}')
        else:
            FormatedPrint('Missing Position Log', 50)

        return self.results

    def process_text_plt_results(self,text_results,plt_results):
        for item in text_results:
            self.results.append(TextResult(item))
        for item in plt_results:
            self.results.append(ImageResult(self.figure_to_qimage(item)))

    def figure_to_qimage(self,figure):
        buffer = figure.canvas.buffer_rgba()
        width, height = figure.canvas.get_width_height()
        image = QImage(buffer, width, height, QImage.Format_ARGB32)
        return image

