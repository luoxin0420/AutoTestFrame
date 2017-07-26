#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Xuxh'

import os
import sys
import ddt
try:
    import unittest2 as unittest
except(ImportError):
    import unittest
from time import sleep
from library import configuration
from library import logcat as dumplog
from library import device
from library import desktop
from library import uiautomator
from library import HTMLTestRunner

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)

@ddt.ddt
class TestTaskNetworkChange(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        self.master_service = CONFIG.getValue(DEVICENAME,'master_service')
        self.slave_service = CONFIG.getValue(DEVICENAME,'slave_service')
        self.slave_main_process = self.slave_service + ':main'
        self.omit_cases = CONFIG.getValue(DEVICENAME, 'omit_cases')
        self.set_theme = bool(CONFIG.getValue(DEVICENAME, 'set_theme'))
        self.set_theme_pkg = CONFIG.getValue(DEVICENAME, 'set_theme_pkg')

    def setUp(self):

        self.log_name = None
        self.log_path = None
        self.log_reader = None
        self.result = False
        self.log_count = 1
        self.double_process = False
        self.proc_name = 'lockscreen'

        for title in self.omit_cases.split(':'):
            if self._testMethodName.find(title) != -1:
                self.skipTest('this case is not supported by this version')

        if LOOP_NUM != 0 and not self.set_theme:
            self.set_magazine_init_env()

        # only connect wifi
        DEVICE.gprs_operation('OFF')
        sleep(5)
        DEVICE.wifi_operation('ON')
        sleep(5)

    def tearDown(self):

        #self._outcomeForDoCleanups = result   # Python 3.2, 3.3
        try:
                if hasattr(self, '_outcome'):  # Python 3.4+
                    result = self.defaultTestResult()  # these 2 methods have no side effects
                    self._feedErrorsToResult(result, self._outcome.errors)
                else:  # Python 3.2 - 3.3 or 2.7
                    result = getattr(self, '_outcomeForDoCleanups', self._resultForDoCleanups)
                error = self.list2reason(result.errors)
                failure = self.list2reason(result.failures)
                ok = not error and not failure

                #Save all test result
                #init result dict at the first time
                if LOOP_NUM == 0:
                    RESULT_DICT.setdefault(self._testMethodName, {})['Result'] = []
                    RESULT_DICT.setdefault(self._testMethodName, {})['Log'] = []

                if ok:
                    RESULT_DICT[self._testMethodName]['Result'].append('PASS')
                    RESULT_DICT[self._testMethodName]['Log'].append('')
                else:
                    RESULT_DICT[self._testMethodName]['Result'].append('FAILED')
                    RESULT_DICT[self._testMethodName]['Log'].append(os.path.basename(self.log_name))
                    # insert into fail case list
                    FAIL_CASE.append(self._testMethodName)

        except Exception,ex:
                print ex

        # # only connect wifi
        # DEVICE.gprs_operation('OFF')
        # sleep(5)
        # DEVICE.wifi_operation('ON')
        # sleep(5)

        if self.set_theme:
            #self.set_device_theme(self.set_theme_pkg, 'system')
            pass
        # close all adb to avoid 5037 port occupation
        desktop.close_all_program('adb')
        # restart adb server
        sleep(1)
        DEVICE.restart_adb_server()
        sleep(5)

    def list2reason(self, exc_list):
        if exc_list and exc_list[-1][0] is self:
            return exc_list[-1][1]

    def set_magazine_init_env(self):

        switcher = {
            'test_1': 'ON:ON',
            'test_2': 'ON:OFF',
            'test_3': 'OFF:ON',
            'test_4': 'OFF:OFF'
        }

        value = self._testMethodName[0:6]
        action = switcher.get(value,'ON:ON').split(':')
        self.set_magazine_app_switch(action[0])
        self.set_security_magazine_switch(action[1])

    def dump_log_start(self, service,filter_condition):

        name =''.join([self._testMethodName,'_',str(LOOP_NUM),'_',str(self.log_count)])
        self.log_name = os.path.join(LogPath,name)
        self.log_count += 1
        self.log_reader = dumplog.DumpLogcatFileReader(self.log_name,DEVICENAME,service,filter_condition)
        self.log_reader.clear_logcat()
        self.log_reader.start()

    def dump_log_stop(self):

        self.log_reader.stop()

    def get_pid(self):

        pid_list = []
        try:
            if self.double_process:
                plist = [self.slave_main_process, self.master_service]
            elif self.proc_name == 'lockscreen':
                plist = [self.master_service]
            else:
                plist = [self.slave_main_process]

            for name in plist:
                pid = dumplog.DumpLogcatFileReader.get_PID(DEVICENAME,name)
                if str(pid) > 0:
                    pid[0] = pid[0].strip()
                    pid_list.append(pid[0])
        except Exception,ex:
            print ex
            return []

        return pid_list

    def filter_log_result(self, findstr='Judgment result can run , task type is'):

        result = False
        pid = self.get_pid()
        contens = []
        if self.double_process:
            print 'This is a case of double process, expected log lines are 2'
        with open(self.log_name) as reader:
            for line in reader:
                # remove redundance space
                line = ' '.join(filter(lambda x: x, line.split(' ')))
                values = line.split(' ')
                # values[6:] is text column
                try:
                    text = ' '.join(values[6:])
                    if values[2] in pid and text.find(findstr) != -1:
                        if not self.double_process:
                            result = True
                            print 'Find log:' + line
                            break
                        else:
                            print 'Find log:' + line
                            if values[2] not in contens:
                                contens.append(values[2])
                except Exception, ex:
                    print ex
                    continue

        # 验证双进程日志
        if len(contens) == 2 and self.double_process:
            result = True

        return result

    def start_app(self):

        if not self.set_theme:
            DEVICE.app_operation('START', service=self.slave_service)
            sleep(5)
        else:
            self.set_device_theme(self.set_theme_pkg, 'vlife')
            pass

    def close_app(self):

        DEVICE.app_operation('CLOSE', service=self.slave_service)
        sleep(5)

    def clear_app(self):

        DEVICE.app_operation('CLEAR', service=self.slave_service)
        DEVICE.app_operation('CLEAR', service='com.android.systemui')
        sleep(5)

    def set_device_theme(self, activity_name, theme_type):

        # log in theme app like i theme
        DEVICE.app_operation(action='LAUNCH',service=activity_name)
        sleep(2)
        if theme_type.upper()== 'VLIFE':
            vlife_theme_path = CONFIG.getValue(DEVICENAME,'vlife_theme_path').split(',')
        else:
            vlife_theme_path = CONFIG.getValue(DEVICENAME,'system_theme_path').split(',')
        element = uiautomator.Element(DEVICENAME)
        event = uiautomator.Event(DEVICENAME)

        for text in vlife_theme_path:
            x = 0
            y = 0
            if text.find(':') == -1:
                value = unicode(text)
            # 因为一些点击文字没有响应，需要点击周边的元素
            else:
                value = unicode(text.split(':')[0])
                x = text.split(':')[1]
                y = text.split(':')[2]
            ele = element.findElementByName(value)
            if ele is not None:
                event.touch(ele[0]-int(x), ele[1]-int(y))
                sleep(2)
        # return to HOME
        DEVICE.send_keyevent(3)

    def set_magazine_app_switch(self,action):

        DEVICE.app_operation('START', service=self.slave_service)
        sleep(1)
        findstr = [u'开启',u'安装',u'允许',u'确定']
        DEVICE.do_popup_windows(6,findstr)

        # click setting button
        setting_path = CONFIG.getValue(DEVICENAME,'magazine_wifi_switch').split('|')
        temp =  setting_path[0].split('::')
        location = temp[0]
        index = int(temp[1])

        # click setting button
        uiautomator.click_element_by_id(DEVICENAME,location,index)
        sleep(1)

        # get current state of switch
        temp =  setting_path[1].split('::')
        location = temp[0]
        index = int(temp[1])
        state = uiautomator.get_element_attribute(DEVICENAME,location,index,'checked')

        if action.upper() == 'ON' and state != 'true':
            uiautomator.click_element_by_id(DEVICENAME,location,index)

        if action.upper() == 'OFF' and state == 'true':
            uiautomator.click_element_by_id(DEVICENAME,location,index)

        DEVICE.do_popup_windows(2,[u'关闭'])
        sleep(1)
        #return back to HOME
        DEVICE.send_keyevent(4)
        sleep(3)
        DEVICE.send_keyevent(3)
        sleep(3)

    def set_security_magazine_switch(self,action):

        # open set security UI
        value = CONFIG.getValue(DEVICENAME,'security_setting')
        DEVICE.app_operation('LAUNCH', service=value)
        sleep(1)

         # click setting button
        setting_path = CONFIG.getValue(DEVICENAME,'security_magazine_switch').split('::')
        location = setting_path[0]
        index = int(setting_path[1])

        # check current state
        state = uiautomator.get_element_attribute(DEVICENAME,location,index,'checked')

        if action.upper() == 'ON' and state != 'true':
            uiautomator.click_element_by_id(DEVICENAME,location,index)

        if action.upper() == 'OFF' and state == 'true':
            uiautomator.click_element_by_id(DEVICENAME,location,index)

        #return back to HOME
        DEVICE.send_keyevent(3)

    test_data1 = [{"username": "zhangsan", "pwd": "zhangsan"},
             {"username": "lisi", "pwd": "lisi"},
             {"username": "wangwu", "pwd": "wangwu"},
             ]

    @ddt.data(*test_data1)
    def test_101_double_proc_gprs_to_wifi(self,data):

        print 'STEPS: WIFI_OFF>GPRS_ON>UPDATE_TIME>GPRS_OFF>WIFI_ON'

        print(data['username'])
        print(data['pwd'])
        # self.double_process = True
        # self.start_app()
        # DEVICE.send_keyevent(3)
        #
        # DEVICE.wifi_operation('OFF')
        # sleep(3)
        # DEVICE.gprs_operation('ON')
        # sleep(3)
        #
        # self.dump_log_start(self.master_service,'')
        # sleep(2)
        # DEVICE.update_android_time(1,interval_unit='day')
        # sleep(1)
        # #self.dump_log_start(self.master_service,'')
        # sleep(1)
        # DEVICE.gprs_operation('OFF')
        # sleep(15)
        # DEVICE.wifi_operation('ON')
        # sleep(60)
        # self.dump_log_stop()
        #
        # self.result = self.filter_log_result()
        # self.assertEqual(self.result,True)


def init_env():

    #copy files to device
    file_list = CONFIG.getValue(DEVICENAME,'pushfile').split(';')
    # try:
    #     for fname in file_list:
    #         orgi,dest = fname.split(':')
    #         orgi = PATH('../ext/' + orgi)
    #         if os.path.isfile(orgi):
    #             DEVICE.device_file_operation('push',orgi,dest)
    # except Exception, ex:
    #     print ex
    #     print "initial environment is failed"
    #     sys.exit(0)


def run(dname, loop, rtype):

    global DEVICENAME,CONFIG, DEVICE, LogPath
    global LOOP_NUM, RESULT_DICT, FAIL_CASE

    CONFIG = configuration.configuration()
    fname = PATH('../config/' + 'configuration.ini')
    CONFIG.fileConfig(fname)

    DEVICENAME = dname
    DEVICE = device.Device(DEVICENAME)

    # initial test environment
    init_env()

    # run test case
    logname = desktop.get_log_name(dname,'TestTasks')
    LogPath = os.path.dirname(os.path.abspath(logname))
    utest_log = os.path.join(LogPath,'unittest.html')

    # ##RESULT_DICT format {casename:{Result:['PASS','PASS'],Log:['','']}}#####
    RESULT_DICT = {}
    FAIL_CASE = []

    try:
        for LOOP_NUM in range(loop):

            fileobj = file(utest_log,'a+')
            if LOOP_NUM == 0 or rtype.upper() == 'ALL':
                suite = unittest.TestLoader().loadTestsFromTestCase(TestTaskNetworkChange)
            else:
                suite = unittest.TestSuite()
                for name in FAIL_CASE:
                    suite.addTest(TestTaskNetworkChange(name))
                FAIL_CASE = []

            if suite.countTestCases() > 0:
                runner = HTMLTestRunner.HTMLTestRunner(stream=fileobj, verbosity=2, title='Task Testing Report', description='Test Result',)
                runner.run(suite)
            fileobj.close()
            sleep(5)
            # write log to summary report
            if LOOP_NUM == loop - 1:
                desktop.summary_result(utest_log, True, RESULT_DICT)
            else:
                desktop.summary_result(utest_log, False, RESULT_DICT)

    except Exception, ex:
        print ex

if __name__ == '__main__':

    run("ZX1G22TG4F",2)




