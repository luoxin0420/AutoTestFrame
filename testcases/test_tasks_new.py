#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Xuxh'

import os
import ddt
import json
try:
    import unittest2 as unittest
except(ImportError):
    import unittest

from time import sleep
from library import logcat as dumplog
from library import device
from library import desktop
from library import HTMLTestRunner
from library.myglobal import device_config,POSITIVE_VP_TYPE,logger,DEVICE_ACTION
from business import action,vp
from business import querydb as tc


def get_test_data():

    print len(tc.filter_cases(6))
    return tc.filter_cases(6)

@ddt.ddt
class TestTimerTask(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        self.master_service = device_config.getValue(DEVICENAME,'master_service')
        self.slave_service = device_config.getValue(DEVICENAME,'slave_service')
        self.slave_main_process = self.slave_service + ':main'
        self.set_env_flag = False
        # get network business order
        self.device_action = action.DeviceAction(DEVICENAME)

    def setUp(self):

        self.log_name = None
        self.log_path = None
        self.log_reader = None
        self.result = True
        self.log_count = 1
        self.pid = []

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
                else:
                    RESULT_DICT[self._testMethodName]['Result'].append('FAILED')
                    RESULT_DICT[self._testMethodName]['Log'].append(os.path.basename(self.log_name))
                    # insert into fail case list
                    FAIL_CASE.append(self._testMethodName)

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

    def execute_action(self, aname, value, data):

        # act_name = aname.lower()
        #
        # if act_name in DEVICE_ACTION:
        #     action.execute_device_action(self.device_action,aname, value)

        if aname.startswith('network'):

            self.device_action.network_change(value)

        elif aname.startswith('update_date'):

            sleep(3)
            self.device_action.update_time(value)

        elif aname.startswith('log_start'):

            logger.debug('Step: start to collect log')
            self.dump_log_start(self.pid)

        elif aname.startswith('log_stop'):
            logger.debug('Step: stop collecting log')
            self.dump_log_stop()

        elif aname.startswith('wait_time'):
            logger.debug('Step: wait time: ' + str(value))
            sleep(value)

        elif aname.startswith('reboot'):
            self.device_action.reboot_device()

        elif aname.startswith('unlock_screen'):
            self.device_action.unlock_screen()

        elif aname.startswith('update_para'):
            self.device_action.update_para(value)

        elif aname.startswith('install_app'):
            self.device_action.install_app(value)

        elif aname.startswith('screen_on'):
            logger.debug('Step: Screen on operation')
            DEVICE.screen_on_off(value)
            sleep(2)

        elif aname.startswith('task_init_source'):
            self.device_action.task_init_resource(value)
        else:
            self.result = False
            print 'Unknown action name:' + aname

    def dump_log_start(self, pid):

        name = ''.join([self._testMethodName,'_',str(LOOP_NUM),'_',str(self.log_count)])
        self.log_name = os.path.join(LogPath,name)
        self.log_count += 1
        self.log_reader = dumplog.DumpLogcatFileReader(self.log_name,DEVICENAME,pid)
        self.log_reader.clear_logcat()
        self.log_reader.start()

    def dump_log_stop(self):

        self.log_reader.stop()

    def get_pid(self,value):

        pid_list = []

        try:
            if value.upper() == 'DOUBLE_LOG':
                plist = [self.slave_main_process, self.master_service]
            elif value.upper() == 'SYSTEM_LOG':
                plist = [self.master_service]
            else:
                plist = [self.slave_main_process]

            for name in plist:
                pid = dumplog.DumpLogcatFileReader.get_PID(DEVICENAME,name)
                if str(pid) > 0:
                    pid[0] = pid[0].strip()
                    pid_list.append(pid[0])
        except Exception,ex:
            print 'canot get correlative PID'
            return []

        return pid_list


    @ddt.data(*get_test_data())
    def test_timer_task(self,data):

        print('CaseName:' + data['teca_mname'])
        logger.debug('CaseName:' + data['teca_mname'])
        # unicode to str
        new_data = {}
        for key, value in data.items():

            if isinstance(value,unicode):
                new_data[key.encode('gbk')] = value.encode('gbk')
            else:
                new_data[key.encode('gbk')] = value

        values = new_data['teca_action_detail']
        dict_data = json.loads(values)

        #get pid for verification

        vpname = tc.get_vp_name(data['teca_vp_id'])
        self.pid = self.get_pid(vpname)
        #print self.pid

        temp = {}
        business_order = tc.get_action_list(data['teca_comp_id'])
        prev_act = ''
        vp_type_name = tc.get_vp_type(new_data['teca_vp_type_id'])
        try:
            for act in business_order:
                # pid is changed after reboot device and unlock_screen
                if prev_act.startswith('unlock_screen'):
                    self.pid = self.get_pid(vpname)
                if act not in temp.keys():
                    temp[act] = 0
                # maybe same action is executed multiple times
                else:
                    temp[act] += 1
                    act = '-'.join([act,str(temp[act])])
                act = act.encode('gbk')
                self.execute_action(act,dict_data[act], new_data)
                prev_act = act

                if not self.result:
                    break
            if self.result:
                self.result = vp.filter_log_result(self.log_name, self.pid, vp_type_name, new_data['teca_expe_result'])

        except Exception, ex:
            logger.error(ex)

        if vp_type_name in POSITIVE_VP_TYPE:
            self.assertEqual(self.result, True)
        else:
            self.assertEqual(self.result, False)

    # def test_demo(self):
    #
    #     print 'this is only test demo'
    #     self.assertEqual(1, 2)


def run(dname, loop, rtype):

    global DEVICENAME, DEVICE, LogPath
    global LOOP_NUM, RESULT_DICT, FAIL_CASE


    DEVICENAME = dname
    DEVICE = device.Device(DEVICENAME)

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
                suite = unittest.TestLoader().loadTestsFromTestCase(TestTimerTask)
            else:
                suite = unittest.TestSuite()
                for name in FAIL_CASE:
                    suite.addTest(TestTimerTask(name))
                FAIL_CASE = []

            if suite.countTestCases() > 0:
                runner = HTMLTestRunner.HTMLTestRunner(stream=fileobj, verbosity=2, loop=LOOP_NUM, title='Task Testing Report', description='Test Result',)
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
    run("ZX1G22TG4F",1,'all')




