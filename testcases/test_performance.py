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
from business import action
import sys
import os
import shutil
from uiautomator import Device
from business import theme


def common_tear_down(data_file, number, data_type):

    # get statistical data
    value = dataAnalysis.handle_performance_data(data_file, data_type)

    # get suffix name
    temp = os.path.splitext(data_file)
    desfile = ''.join([temp[0], '_', str(number), temp[1]])
    shutil.copy(data_file, desfile)
    with open(data_file, 'wb') as wfile:
         wfile.write('')

    return value


def common_suite_down(uid, result_list, diagram_type, desc_list, flag):

    out_path = performance_config.getValue(uid,'result_path')
    out_file = os.path.join(out_path,diagram_type+'.png')

    max_length = max(map(len, [result_list]))

    if diagram_type.lower() == 'plot':
        diagram.draw_plot(range(max_length), [result_list], desc_list, out_file, flag)

    if diagram_type.lower() == 'bar':
        diagram.draw_bar(range(max_length), [result_list], desc_list, out_file, flag)

    # write summary result to file

    summary = os.path.join(out_path, 'summary.txt')

    with open(summary,'wb') as wfile:
        wfile.write(','.join(map(str, result_list)))
        wfile.write('\r\n')
        wfile.write('average:' + str(sum(result_list)/len(result_list)))


class LaunchSpeedTest(object):

    def __init__(self, deviceId, processname):
        self.launch = performance.LaunchTimeCollector(deviceId, processname)
        self.robot = self.launch.adbTunnel
        self.result = []

    def suite_up(self):
        pass

    def set_up(self):
        self.launch.start()

    def test(self):
        pass

    def tear_down(self, num, data_type):

        self.launch.stop()
        if self.robot.get_lock_screen_state():
            # unlock screen
            myaction = action.DeviceAction(self.uid)
            myaction.unlock_screen('DEFAULT')
        value = common_tear_down(self.launch.result_path, num, data_type)
        self.result.append(value)

    def suite_down(self, uid, diagram):
        pass


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

    def suite_down(self, uid, diagram):
        pass


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

    def suite_down(self, uid, diagram):
        pass


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


class MemoryTest(object):

    def __init__(self, deviceId, processname):
        self.launch = performance.MemoryCollector(deviceId, processname)
        self.robot = self.launch.adbTunnel
        self.uid = deviceId
        self.result = []
        self.name = self.__get_name(processname)

    def __get_name(self,pname):

        if pname.lower() == 'com.android.systemui':
            return 'system'
        else:
            return 'vlife'

    def suite_up(self):
        pass

    def set_up(self):
        self.launch.start()

    def test(self):
        pass

    def tear_down(self, num, data_type):

        self.launch.stop()
        if self.robot.get_lock_screen_state():
            # unlock screen
            myaction = action.DeviceAction(self.uid)
            myaction.unlock_screen('DEFAULT')
        value = common_tear_down(self.launch.result_path, num, data_type)
        self.result.append(value)

    def suite_down(self, uid, diagram_type):

        common_suite_down(uid, self.result, diagram_type, ['memory'], 'MEMORY')


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


class MemoryPeakOnLockScreen(MemoryTest):

    def set_up(self):

        # set vlife theme
        theme.set_device_theme(self.uid, self.name)
        # clear background app
        self.launch.start()

    def test(self):
        try:
            super(MemoryPeakOnLockScreen, self).test()

            s_size = self.robot.get_screen_normal_size()
            width = int(s_size[0])
            height = int(s_size[1])
            cmd = 'input swipe {0} {1} {2} {3} 200'.format(int(width/3), int(height/4), int(width/3)*2, int(height/4))
            # screen on/off
            state = self.robot.get_display_state()
            if not state:
                self.robot.send_keyevent(26)
            else:
                self.robot.send_keyevent(26)
                sleep(1)
                self.robot.send_keyevent(26)
            for i in range(30):
                self.robot.shell(cmd)
                sleep(1)
        except Exception, ex:
            print ex


class MemoryNoLoad(MemoryTest):

    def set_up(self):

        # set vlife theme
        theme.set_device_theme(self.uid, self.name)
        # clear background app

    def test(self):
        try:
            super(MemoryNoLoad, self).test()
            # screen on/off
            state = self.robot.get_display_state()
            if state:
                self.robot.send_keyevent(26)
            # stand for 30s
            sleep(30)
            # start to filter log
            self.launch.start()
            sleep(60)
        except Exception, ex:
            print ex


class MemoryReboot(MemoryTest):

    def set_up(self):

        # set vlife theme
        theme.set_device_theme(self.uid, self.name)
        self.robot.reboot()
        sleep(20)
        # screen on/off
        state = self.robot.get_display_state()
        if not state:
            self.robot.send_keyevent(26)

        # unlock screen
        myaction = action.DeviceAction(self.uid)
        myaction.unlock_screen('DEFAULT')
        sleep(10)
        # clear background app
        self.launch.start()

    def test(self):
        try:
            super(MemoryReboot, self).test()
            sleep(60)
        except Exception, ex:
            print ex


class MemoryReboot_ScreenOnOff(MemoryTest):

    def set_up(self):

        # set vlife theme
        theme.set_device_theme(self.uid, self.name)
        self.robot.reboot()
        sleep(120)

        # clear background app
        self.launch.start()

    def test(self):
        try:
            super(MemoryReboot_ScreenOnOff, self).test()

            for i in range(200):
                self.robot.send_keyevent(26)
                sleep(1)

        except Exception, ex:
            print ex


class MemoryReboot_ScreenOnOff_Unlock(MemoryTest):

    def set_up(self):

        # set vlife theme
        theme.set_device_theme(self.uid, self.name)
        self.robot.reboot()
        sleep(120)
        # clear background app
        self.launch.start()

    def test(self):
        try:
            super(MemoryReboot_ScreenOnOff_Unlock, self).test()
            # screen on/off
            for i in range(200):
                state = self.robot.get_display_state()
                if not state:
                    self.robot.send_keyevent(26)
                # unlock screen
                myaction = action.DeviceAction(self.uid)
                myaction.unlock_screen('DEFAULT')
                # screen off
                self.robot.send_keyevent(26)
                sleep(1)
        except Exception, ex:
            print ex


class MemoryLeak(MemoryTest):

    def set_up(self):

        # set vlife theme
        theme.set_device_theme(self.uid, 'VLIFE')
        # clear background app
        self.launch.start()

    def test(self):
        try:
            super(MemoryLeak, self).test()
            # screen on/off
            for i in range(2):
                state = self.robot.get_display_state()
                if not state:
                    self.robot.send_keyevent(26)
                # unlock screen
                myaction = action.DeviceAction(self.uid)
                myaction.unlock_screen('DEFAULT')
                # screen off
                self.robot.send_keyevent(26)
                sleep(1)
        except Exception, ex:
            print ex


class CaseExecutor(object):

    def __init__(self, times, uid):
        self.__times = times
        self.__dviceId = uid
        self.__name = None
        pass

    __alias = {
        "MagazineLaunchSpeed": MagazineLaunchSpeed,
        "MagazineMemoryMonitor": MagazineMemoryMonitor,
        "MemoryNoLoad": MemoryNoLoad,
        "MemoryPeakOnLockScreen": MemoryPeakOnLockScreen,
        "MemoryReboot": MemoryReboot,
        "MemoryReboot_ScreenOnOff": MemoryReboot_ScreenOnOff,
        "MemoryReboot_ScreenOnOff_Unlock": MemoryReboot_ScreenOnOff_Unlock,
        "MemoryLeak": MemoryLeak
        }

    def exec_test_cases(self, caselist=None):

        if caselist and len(caselist) == 0:
            print "no case in your caselist"
            sys.exit(0)

        diagram_type = performance_config.getValue(self.__dviceId, 'diagram_type')
        data_type = performance_config.getValue(self.__dviceId, 'collect_data_type').split(';')
        process = performance_config.getValue(self.__dviceId, 'app_process_name').split(';')
        index = 0
        for testcase in caselist:
            result_path = desktop.get_log_path(self.__dviceId, testcase)
            performance_config.setValue(self.__dviceId, 'result_path', result_path)
            try:
                dtype = data_type[index]
            except Exception,ex:
                dtype = 'avg'

            try:
                self.__name = process[index]
            except Exception,ex:
                temp = len(process) - 1
                self.__name = process[temp]

            self.exec_test_case(testcase, dtype, diagram_type)
            index += 1

    def exec_test_case(self, caseName, data_type, diagram):

        instance = self.__alias[caseName](self.__dviceId, self.__name)
        instance.suite_up()
        for i in range(0, self.__times):
            instance.set_up()
            instance.test()
            instance.tear_down(i, data_type)
        instance.suite_down(self.__dviceId, diagram)


if __name__ == '__main__':

    temp = MemoryPeakOnLockScreen('abc', 'com.vlife.com' )