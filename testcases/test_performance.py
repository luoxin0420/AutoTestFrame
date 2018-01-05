#!/usr/bin/evn python
# -*- coding:utf-8 -*-

__author__ = 'Xuxh'

from library import performance
from library import desktop
from library.myglobal import  performance_config
from time import sleep
from library import myuiautomator
from library import dataAnalysis
from library import diagram
import sys
import os
from uiautomator import Device


class LaunchSpeedTest(object):

    def __init__(self, deviceId, processname):
        self.launch = performance.LaunchTimeCollector(deviceId, processname)
        self.robot = self.launch.adbTunnel

    def suite_up(self):
        pass

    def set_up(self):
        self.launch.start()

    def test(self):
        pass

    def tear_down(self):
        self.launch.stop()

    def suite_down(self):
        sys.exit(0)


class MemoryTest(object):

    def __init__(self, deviceId, processname):
        self.launch = performance.MemoryCollector(deviceId, processname)
        self.robot = self.launch.adbTunnel
        self.result = []

    def suite_up(self):
        pass

    def set_up(self):
        self.launch.start()

    def test(self):
        pass

    def tear_down(self, data_type):
        self.launch.stop()
        value = dataAnalysis.handle_performance_data(self.launch.result_path, data_type)
        self.result.append(value)

    def suite_down(self, diagram_type):

        if diagram_type.lower() == 'plot':
            diagram.draw_plot(range(1), self.result, ['test'])
        sys.exit(0)


class CPUTimeTest(object):

    def __init__(self, deviceId, processname):
        self.launch = performance.CPUJiffiesCollector(deviceId, processname)
        self.robot = self.launch.adbTunnel

    def suite_up(self):
        pass

    def set_up(self):
        self.launch.start()

    def test(self):
        pass

    def tear_down(self, data_type):
        self.launch.stop()

    def suite_down(self, diagram):
        sys.exit(0)


class UIFPSTest(object):

    def __init__(self, deviceId, processname):
        self.launch = performance.UIFPSCollector(deviceId, processname)
        self.robot = self.launch.adbTunnel

    def suite_up(self):
        pass

    def set_up(self):
        self.launch.start()

    def test(self):
        pass

    def tear_down(self, data_type):
        self.launch.stop()

    def suite_down(self, diagram):
        sys.exit(0)


class MagazineLaunchSpeed(LaunchSpeedTest):

    def test(self):
        super(MagazineLaunchSpeed, self).test()
        for i in range(0, 2):
            self.robot.clear_app_data(self.launch.pkg_name)
            sleep(1)
            self.robot.start_application(self.launch.start_activity)
            sleep(3)
            self.robot.send_keyevent(4)
            sleep(1)
            self.robot.start_application(self.launch.start_activity)
            sleep(1)
            self.robot.send_keyevent(4)


class MagazineMemoryMonitor(MemoryTest):

    def test(self):
        try:
            super(MagazineMemoryMonitor, self).test()
            self.robot.clear_app_data(self.launch.pkg_name)
            sleep(1)
            self.robot.start_application(self.launch.start_activity)
            sleep(3)
            for i in range(4):
                myuiautomator.click_popup_window(self.launch.deviceId, [u"允许"])
                sleep(2)
            self.robot.send_keyevent(4)
            self.robot.start_application(self.launch.start_activity)
            text = [[u"跳过"],[u"开启"],[u"欢迎使用"]]
            for te in text:
                myuiautomator.click_popup_window(self.launch.deviceId, te)
                sleep(2)
        except Exception,ex:
            print ex


class CaseExecutor(object):

    def __init__(self, times, uid, pkg):
        self.__times = times
        self.__dviceId = uid
        self.__name = pkg
        pass

    __alias = {
        "MagazineLaunchSpeed": MagazineLaunchSpeed,
        "MagazineMemoryMonitor": MagazineMemoryMonitor
        }

    def exec_test_cases(self, caselist=None):

        if caselist and len(caselist) == 0:
            print "no case in your caselist"
            sys.exit(0)

        diagram_type = performance_config.getValue(self.__dviceId, 'diagram_type')
        data_type = performance_config.getValue(self.__dviceId, 'collect_data_type').split(';')
        index = 0
        for testcase in caselist:
            result_path = desktop.get_log_path(self.__dviceId, testcase)
            performance_config.setValue(self.__dviceId, 'result_path', result_path)
            try:
                self.exec_test_case(testcase, data_type[index], diagram_type)
            except Exception,ex:
                self.exec_test_case(testcase, 'avg', diagram_type)
            index += 1

    def exec_test_case(self, caseName, data_type, diagram):

        instance = self.__alias[caseName](self.__dviceId, self.__name)
        instance.suite_up()
        for i in range(0, self.__times):
            instance.set_up()
            instance.test()
            instance.tear_down(data_type)
        instance.suite_down(diagram)


