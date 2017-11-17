#!/usr/bin/evn python
# -*- coding:utf-8 -*-

__author__ = 'Xuxh'

import adbtools
import desktop as dt
from abc import abstractmethod,ABCMeta
import threading
import time
import re
import subprocess
from library import pJson
import csv
import os
from library.myglobal import performance_config


class Performance(object):

    __metaclass__ = ABCMeta

    def __init__(self, deviceId='', processName='', resultpath=None, log=None):

        self.processName = processName
        self.pkg_name = self.__get_pkg_name(processName)
        self.deviceId = deviceId
        self.isFirst = True
        self.adbTunnel = adbtools.AdbTools(deviceId)
        self.pid = self.adbTunnel.get_pid(processName)
        pre_log_path = performance_config.getValue(deviceId, 'result_path')
        self.logcat = os.path.join(pre_log_path, 'logcat.txt')
        self.result_path = resultpath
        if resultpath is None:
            #self.result_path = self.__class__.__name__ + ".csv"
            self.result_path = os.path.join(pre_log_path, 'result.csv')
        self.log = log
        if log is None:
            fname = os.path.join(pre_log_path, 'log.txt')
            self.log = dt.create_logger(fname)

        pass

    def __get_pkg_name(self, name):

        pkg = ''
        if name.find('/'):
            pkg = self.processName.split('/')[0]
        return pkg


    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass


class MemoryUnit(object):

    def __init__(self,ts,mem_value):

        self.format_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
        self.totalmem = mem_value


class MemoryCollector(Performance):

    def __init__(self, deviceId='', processName= '', resultpath=None, log=None):
        super(MemoryCollector,self).__init__(deviceId, processName, resultpath, log)
        self.__mem_list = []
        self.timer = None
        pass

    def start(self):

        self.timer = threading.Timer(1, self.__fun_get_mem)
        self.timer.start()
        pass

    def __get_mem(self):

        cmd = "dumpsys meminfo {0} | {1} TOTAL".format(self.processName, self.adbTunnel.find)
        output = self.adbTunnel.shell(cmd).read()
        try:
            return output.strip().split()[1]
        except Exception:
            pass
        return 0

    def __fun_get_mem(self):
        timestamp = time.time()
        self.timer = threading.Timer(3, self.__fun_get_mem)
        self.timer.start()
        memItem = MemoryUnit(timestamp, self.__get_mem())
        self.__mem_list.append(memItem)
        self.__write_line(memItem)
        print memItem.format_time, ",", memItem.totalmem

    def __write_line(self, item=None):

        if item:
            fp = open(self.result_path, "a")
            line = ",".join([str(item.format_time), str(item.totalmem), "\n"])
            fp.write(line)
            fp.close()

    def stop(self):
        self.timer.cancel()


class JiffsUnit(object):

    def __init__(self, ts, utime,stime):

        self.format_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
        self.utime = utime
        self.stime = stime


class CPUJiffiesCollector(Performance):

    def __init__(self, deviceId='', processName= '', resultpath=None, log=None):
        super(CPUJiffiesCollector, self).__init__(deviceId, processName, resultpath, log)
        self.__jiffs_list = []
        self.timer = None
        self.__last_utime = None
        self.__last_stime = None
        self.__start_jiffs_item = None

    def start(self):

        self.timer = threading.Timer(1, self.__fun_get_jiffs)
        self.timer.start()

    def __get_jiffs(self):

        cmd = "cat /proc/{0}/stat".format(self.pid)
        output = self.adbTunnel.shell(cmd).read()
        if not output:
            return -1, -1
        self.log.info(output)
        vec_line = re.split(r'[\s]', output)
        try:
            utime = int(vec_line[13])
            stime = int(vec_line[14])
        except Exception:
            utime = -1
            stime = -1

        return utime, stime

    def __fun_get_jiffs(self):
        timestamp = time.time()
        self.timer = threading.Timer(5, self.__fun_get_jiffs)
        self.timer.start()
        utime, stime = self.__get_jiffs()
        if self.isFirst:
            self.isFirst = False
            self.__start_jiffs_item = JiffsUnit(timestamp, utime, stime)
            self.__last_stime = stime
            self.__last_utime = utime
        elif utime > 0 and stime > 0:
            u = utime - self.__last_utime
            s = stime - self.__last_stime
            item = JiffsUnit(timestamp, u, s)
            self.__jiffs_list.append(item)
            self.__write_line(item)
            self.__last_utime = utime
            self.__last_stime = stime

    def __write_line(self, item=None):

        if item:
            fp = open(self.result_path, "a")
            line = ",".join([str(item.format_time), str(item.utime), str(item.stime), "\n"])
            fp.write(line)
            fp.close()

    def stop(self):
        self.timer.cancel()


class LaunchTimeUnit(object):

    def __init__(self, ts, ltime):

        self.format_time = ts
        self.launch_time = ltime


class LaunchTimeCollector(Performance):

    def __init__(self, deviceId='', processName= '', resultpath=None, log=None):
        super(LaunchTimeCollector, self).__init__(deviceId, processName, resultpath, log)
        self.__launch_speed_list = []
        self.timer = None

    def start(self):

        # clear logcat
        self.adbTunnel.adb('logcat -c')
        cmd = "logcat -v time ActivityManager:I *:S > {0}".format(self.logcat)
        self.timer = threading.Thread(target=self.adbTunnel.adb, args=cmd)
        self.timer.start()

    #log example "Displayed com.qihoo.appstore/com.morgoo.droidplugin.stub.ActivityStub$P01SingleInstance00: +4s906ms (total +5s243ms)
    @staticmethod
    def get_launchspeed_from_line(log_line):

        if log_line.find('total') != -1:
            s1 = re.findall("total\\s\\+(\\w+)ms", log_line)[0]
        else:
            s1 = re.findall("\+(\\w+)ms", log_line)[0]

        # 将4s906ms统一成为ms为单位的数值

        if s1.find('s') > 0:
            s2 = s1.split('s')
            total_time = int(s2[0]) * 1000 + int(s2[1])
        else:
            total_time = s1
        return total_time

    def __collect_data(self):

        with open(self.logcat) as rfile:
            for line in rfile:
                if "Displayed" not in line:
                    continue
                if self.processName not in line:
                    continue
                # if "QuickLoadActivity" not in line:
                #     continue
                time_stamp = " ".join(line.split(" ")[0:2])
                launch_time = float(self.get_launchspeed_from_line(line))
                item = LaunchTimeUnit(time_stamp, launch_time)
                self.__launch_speed_list.append(item)
                self.__write_line(item)

    def __write_line(self, item=None):

        if item:
            with open(self.result_path, "a") as wfile:
                line = ",".join([str(item.format_time), str(item.launch_time), "\n"])
                wfile.write(line)

    def stop(self):
        os.system('adb kill')
        self.__collect_data()


class SMUnit(object):

    def __init__(self, ts, data):

        self.format_time = ts
        self.data = data


# 使用logcat收集Choreographer丢帧数据
class UIFPSCollector(Performance):

    def __init__(self, deviceId='', processName= '', resultpath=None, log=None):
        super(UIFPSCollector, self).__init__(deviceId, processName, resultpath, log)
        self.__launch_speed_list = []
        self.timer = None
        self.logcat_file = "temp.txt"
        self.__last_data = 0
        self.__last_timestamp = None

    def start(self):

        cmd = "logcat -v time Choreographer:I *:S > {0}".format(self.logcat_file)
        self.timer = threading.Timer(1, self.adbTunnel.adb(cmd))
        self.timer.start()

    # => 10-31 15:43:29.715 I/Choreographer(25459): Skipped 1 frames!  The application may be doing too much work onits main thread
    def __collect_data(self):

        with open(self.logcat_file) as rfile:
            for line in rfile:
                if "Choreographer" not in line:
                    continue
                if self.processName not in line:
                    continue
                current_stamp = self.get_timestamp_from_line(line)
                skipped_frame = self.get_skipped_frame(line)
                if self.isFirst:
                    self.__last_timestamp = current_stamp
                    self.isFirst = False
                    continue
                elif current_stamp == self.__last_timestamp:
                    self.__last_data=int(self.__last_data) + int(skipped_frame)
                elif current_stamp == (self.__last_timestamp + 1):
                    str_time = self.get_format_time(self.__last_timestamp)
                    data = int(self.__last_data)
                    self.__fps_lists.append(SMUnit(str_time,data))
                    self.__last_timestamp = current_stamp
                    self.__last_data = skipped_frame
                else:
                    for i in range(self.__last_timestamp,current_stamp):
                        if i == self.__last_timestamp:
                            if int(self.__last_data) > 60:
                                self.__last_data = self.data_correction(int(self.__last_data))
                                str_time = self.get_format_time(self.__last_timestamp)
                                data =int(self.__last_data)
                                self.__fps_lists.append(SMUnit(str_time,data))
                            else:
                                str_time = self.get_format_time(i)
                                data = 0
                                self.__fps_lists.append(SMUnit(str_time,data))
                    self.__last_timestamp = current_stamp
                    self.__last_data = skipped_frame
        return None

    @staticmethod
    def get_format_time(timestamp):
        format_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        return format_time

    @staticmethod
    def get_skipped_frame(log_line):
        number = re.findall(".* Skipped (\d+) frames.*",log_line)[0]
        return number

    @staticmethod
    def get_timestamp_from_line(log_line):
        log_time = " ".join(log_line.split(" ")[0:2])
        # temp = "10-31 15:54:20.524"
        time_stamp = time.mktime(time.strptime(log_time,"%m-%d %H:%M:%S.%Y"))
        return time_stamp

    def __write_line(self, item=None):

        if item:
            with open(self.result_path, "a") as wfile:
                line = ",".join([str(item.format_time), str(item.launch_time), "\n"])
                wfile.write(line)

    def stop(self):
        self.timer.cancel()
        self.__collect_data()


# parse .har file by fiddler generate
class TrafficDataCollector(object):

    def __init__(self):

        self.json_path_list = ["$.log.entries[*].time",\
                      "$.log.entries[*].request.headersSize",\
                      "$.log.entries[*].request.bodySize",\
                      "$.log.entries[*].request.url",\
                      "$.log.entries[*].response.headersSize",\
                      "$.log.entries[*].response.bodySize"]

    def parse_data(self, fname, outfile, urlfile):
        with open(fname) as rfile:
            data = rfile.read()
            data = data[3:]
            results = []
            myJson = pJson.parseJson(data)

            for jp in self.json_path_list:
                res = myJson.extract_element_value(jp)
                results.append(res)

        #url_set = set(results[3][0])
        with open(outfile, 'wb+') as wfile, open(urlfile, 'r') as rfile:
            writer = csv.writer(wfile)
            writer.writerow(['url','send_count','avg_response_time', 'max_response_time', 'min_response_time',\
                             'sum_send_data', 'max_send_data', 'min_send_data',\
                             'sum_receive_data', 'max_receive_data', 'min_receive_data'])
            for url in rfile:
                time = []
                send_data = []
                receive_data = []
                url = url.replace('\n', '')
                for i in range(len(results[3][0])):
                    if results[3][0][i].find(url) != -1:
                        time.append(results[0][0][i])
                        send_data.append(results[1][0][i] + results[2][0][i])
                        receive_data.append(results[4][0][i] + results[5][0][i])
                if len(time) > 0:
                    temp = [url, len(time), sum(time)/float(len(time)), max(time), min(time), sum(send_data), max(send_data), min(send_data),\
                            sum(receive_data), max(receive_data), min(receive_data)]
                else:
                    temp = [url] + [0]*10
                writer.writerow(temp)


if __name__ == '__main__':

    tdata = TrafficDataCollector()

    tdata.parse_data(r'E:\test1.har', r'E:\output_traffic.csv', r'E:\urllist.txt')