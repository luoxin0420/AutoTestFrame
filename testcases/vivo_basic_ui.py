#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import uiautomator
try:
    import unittest2 as unittest
except(ImportError):
    import unittest
from time import sleep
from library.myglobal import device_config,theme_config,logger
from library import adbtools
from library import desktop
from business import querydb as tc
from library import HTMLTestRunner
from business import theme, action


class TestVivoBasicUI(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        self.pkg = device_config.getValue(DEVICENAME, 'set_theme_pkg')

    def setUp(self):

        self.log_name = None
        self.log_path = LogPath
        self.log_reader = None
        self.result = True
        self.log_count = 1
        self.pid = []
        self.run_loop = 1
        self.filter_log = {}
        self.case_id = None

    def tearDown(self):

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
                tc.insert_test_result(RUN_ID, self.case_id, LOOP_NUM, 'PASS', os.path.abspath(self.log_name))
            else:
                RESULT_DICT[self._testMethodName]['Result'].append('FAILED')
                RESULT_DICT[self._testMethodName]['Log'].append(os.path.basename(self.log_name))
                # insert into fail case list
                FAIL_CASE.append(self._testMethodName)
                tc.insert_test_result(RUN_ID, self.case_id, LOOP_NUM, 'FAILED', os.path.abspath(self.log_name))

        except Exception,ex:

                print ex

        desktop.close_all_program('adb')
        # restart adb server
        sleep(1)
        DEVICE.restart_adb_server()
        sleep(5)

    def list2reason(self, exc_list):
        if exc_list and exc_list[-1][0] is self:
            return exc_list[-1][1]

    def unlock_screen(self):

        result = False
        # screen off/on
        if DEVICE.get_display_state():
            DEVICE.send_keyevent(26)
            sleep(2)
            DEVICE.send_keyevent(26)
            DEVICE.screenshot(self._testMethodName, target_path=self.log_path)
            # unlock
            device_action = action.DeviceAction(DEVICENAME)
            device_action.unlock_screen('default')
            result = DEVICE.get_lock_screen_state()
        return result

    def test_vlife_theme(self):

        logger.debug(u'TestCase: 下载并应用主题')
        self.case_id = '11'
        theme.set_device_theme(DEVICENAME, 'VLIFE')
        result = self.unlock_screen()

        self.assertEqual(True, result)

    def test_multiple_vlife_theme(self):

        logger.debug(u'TestCase: 切换不同vlife主题')
        self.case_id = '12'
        for i in range(3):

            # set theme1
            theme.set_device_theme(DEVICENAME, 'VLIFE')
            result = self.unlock_screen()
            self.assertEqual(True, result)
            # set theme2
            theme.set_device_theme(DEVICENAME, 'VLIFE', 1)
            result = self.unlock_screen()
            self.assertEqual(True, result)

    def test_vlife_system_switch(self):

        logger.debug(u'TestCase:不同引擎间多次切换')
        self.case_id = '13'
        theme.set_device_theme(DEVICENAME, 'VLIFE')
        result = self.unlock_screen()
        self.assertEqual(True, result)
        theme.set_device_theme(DEVICENAME, 'SYSTEM')
        result = self.unlock_screen()
        self.assertEqual(True, result)

    def test_third_party_theme(self):

        logger.debug(u'TestCase: 解锁到三方应用')
        self.case_id = '14'
        theme.set_device_theme(DEVICENAME, 'VLIFE')
        # access to the third party of app
        custom_app = device_config.getValue(DEVICENAME, 'custom_third_app')
        DEVICE.start_application(custom_app)
        sleep(2)
        result = self.unlock_screen()
        self.assertEqual(True,result)
        DEVICE.screenshot(self._testMethodName, self.log_path)

    def test_dropdown_notification_recovery(self):
        logger.debug(u'TestCase: 下拉通知栏可复原')
        self.case_id = '15'
        theme.set_device_theme(DEVICENAME, 'VLIFE')
        result = self.unlock_screen()
        width, height = DEVICE.get_screen_normal_size()
        DEVICE.shell('input swipe {1} {2} {3} {4} 200'.format(width/2, 50, width/2, height/2))
        DEVICE.send_keyevent(26)
        sleep(2)
        result = self.unlock_screen()
        self.assertEqual(True, result)

    def test_home_back_key(self):

        logger.debug(u'TestCase: Home、Back键不会解锁')
        self.case_id = '16'
        theme.set_device_theme(DEVICENAME, 'VLIFE')

        DEVICE.send_keyevent(26)
        sleep(2)
        DEVICE.send_keyevent(26)
        DEVICE.screenshot(self._testMethodName, target_path=self.log_path)
        # press home
        DEVICE.send_keyevent(3)
        sleep(1)
        result = DEVICE.get_lock_screen_state()
        self.assertEqual(False, result)
        # press back key
        DEVICE.send_keyevent(3)
        sleep(1)
        result = DEVICE.get_lock_screen_state()
        self.assertEqual(False, result)

    def test_reboot(self):

        logger.debug(u'TestCase: 有sim卡重启验证锁屏')
        self.case_id = '17'
        theme.set_device_theme(DEVICENAME, 'VLIFE')
        result = self.unlock_screen()
        self.assertEqual(True, result)
        DEVICE.reboot()
        sleep(20)
        DEVICE.screenshot(self._testMethodName, target_path=self.log_path)

    def test_screen_on_off_30(self):

        logger.debug(u'TestCase: 反复亮灭屏')
        theme.set_device_theme(DEVICENAME, 'VLIFE')
        self.case_id = '18'
        for i in range(30):
            DEVICE.send_keyevent(26)
            sleep(2)
            DEVICE.send_keyevent(26)
        DEVICE.screenshot(self._testMethodName, target_path=self.log_path)

    def test_unlock_30(self):

        logger.debug(u'TestCase: 反复亮灭屏解锁')
        theme.set_device_theme(DEVICENAME, 'VLIFE')
        self.case_id = '19'
        for i in range(30):
            result = self.unlock_screen()
            self.assertEqual(True, result)
            DEVICE.screenshot(self._testMethodName, target_path=self.log_path)

    def test_landscape_app(self):

        logger.debug(u'TestCase: 三方应用横屏状态锁屏解锁')
        theme.set_device_theme(DEVICENAME, 'VLIFE')
        self.case_id = '20'
        custom_app = device_config.getValue(DEVICENAME, 'custom_third_app')
        DEVICE.start_application(custom_app)
        sleep(2)
        DEVICE.rotation_screen(1)
        sleep(2)
        result = self.unlock_screen()
        self.addCleanup(True, result)


def run(dname, loop, rtype):

    global DEVICENAME, DEVICE, LogPath
    global LOOP_NUM, RESULT_DICT, FAIL_CASE, RUN_ID


    DEVICENAME = dname
    DEVICE = adbtools.device(DEVICENAME)

    # run test case
    logname = desktop.get_log_name(dname,'TestVivoBasicUI')
    LogPath = os.path.dirname(os.path.abspath(logname))
    utest_log = os.path.join(LogPath,'unittest.html')

    # ##RESULT_DICT format {casename:{Result:['PASS','PASS'],Log:['','']}}#####
    RESULT_DICT = {}
    FAIL_CASE = []

    try:
        # insert run info to database

        vname = device_config.getValue(dname,'version')
        RUN_ID = tc.insert_runinfo(17, dname, vname, loop, rtype)

        # start to test
        for LOOP_NUM in range(loop):

            fileobj = file(utest_log, 'a+')
            if LOOP_NUM == 0 or rtype.upper() == 'ALL':
                suite = unittest.TestLoader().loadTestsFromTestCase(TestVivoBasicUI)
            else:
                suite = unittest.TestSuite()
                for name in FAIL_CASE:
                    suite.addTest(TestVivoBasicUI(name))
                FAIL_CASE = []

            if suite.countTestCases() > 0:

                runner = HTMLTestRunner.HTMLTestRunner(stream=fileobj, verbosity=2, loop=LOOP_NUM, title='VivoBasicUI Testing Report', description='Test Result',)
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
    run("ZX1G22TG4F", 1, 'all')