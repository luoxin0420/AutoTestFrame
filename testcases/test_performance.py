#!/usr/bin/evn python
# -*- coding:utf-8 -*-

__author__ = 'Xuxh'

from library import performance
from library import desktop
from library.myglobal import  performance_config
from time import sleep
import sys


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


class MagazineLaunchSpeed(LaunchSpeedTest):

    def test(self):
        super(MagazineLaunchSpeed, self).test()
        for i in range(0, 2):
            self.robot.clear_app_data(self.launch.pkg_name)
            sleep(1)
            self.robot.start_application(self.launch.processName)
            sleep(3)
            self.robot.send_keyevent(4)
            sleep(1)
            self.robot.start_application(self.launch.processName)
            sleep(1)
            self.robot.send_keyevent(4)


class CaseExecutor(object):

    def __init__(self, times, uid, pkg):
        self.__times = times
        self.__dviceId = uid
        self.__name = pkg
        pass

    __alias = {
        "MagazineLaunchSpeed": MagazineLaunchSpeed
        }

    def exec_test_cases(self, caselist=None):

        if caselist and len(caselist) == 0:
            print "no case in your caselist"
        for testcase in caselist:
            result_path = desktop.get_log_path(self.__dviceId, testcase)
            performance_config.setValue(self.__dviceId, 'result_path', result_path)
            self.exec_test_case(testcase)
        pass

    def exec_test_case(self, caseName):

        instance = self.__alias[caseName](self.__dviceId, self.__name)
        instance.suite_up()
        for i in range(0, self.__times):
            instance.set_up()
            instance.test()
            instance.tear_down()
        instance.suite_down()


