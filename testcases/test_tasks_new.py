#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Xuxh'

import os
import ddt
import re
import sys
try:
    import unittest2 as unittest
except(ImportError):
    import unittest

from time import sleep
from library import logcat as dumplog
from library import device
from library import desktop
from library import HTMLTestRunner
from library.myglobal import device_config,logger,TASK_COMPONENT,testlink_config
from business import action, vp
from business import querydb as tc
from business import testdata as td
from library import TestLinkObj


def get_test_data():

    dname = sys.argv[1]
    prod_name = device_config.getValue(dname, 'product_type')
    pid = ','.join(tc.get_product_ID_byName(prod_name))
    suite_list = sys.argv[2]
    return tc.filter_cases(suite_list, TASK_COMPONENT, pid)


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
        self.run_loop = 1
        self.filter_log = {}
        self.case_id = None
        self.testlink_id = None

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
                RESULT_DICT.setdefault(self._testMethodName, {})['TLID'] = self.testlink_id

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

    def execute_action(self, aname, value):

        try:
            if aname.startswith('log_start'):
                logger.debug('Step: start to collect log')
                self.dump_log_start()
            elif aname.startswith('log_stop'):
                logger.debug('Step: stop collecting log')
                self.dump_log_stop()
            elif aname.startswith('wait_time'):
                logger.debug('Step: wait time: ' + str(value))
                sleep(int(value))
            else:
                aname = aname.split('-')[0]
                self.device_action.choose(aname, value)
        except Exception, ex:
            self.result = False
            print ex
            logger.error('Unknown action name:' + aname)

    def dump_log_start(self):

        sleep(2)
        name = ''.join([self._testMethodName,'_',str(LOOP_NUM),'_',str(self.log_count)])
        self.log_name = os.path.join(LogPath,name)
        self.log_count += 1
        self.log_reader = dumplog.DumpLogcatFileReader(self.log_name, DEVICENAME)
        self.log_reader.clear_logcat()
        self.log_reader.start()

    def dump_log_stop(self):

        self.log_reader.stop()

    def verify_login_package(self, lines):
        result = True
        res = False
        for ln in lines:
            if ln.find('jabber:iq:auth') != -1:
                keyword =r'.*(<query.*/query>).*'
                content = re.compile(keyword)
                m = content.match(ln)
                if m:
                    contents = m.group(1)
                    res = vp.verify_login_pkg_content(DEVICENAME,contents)
            result = result and res
        return result

    def get_user_id(self,lines):
        res = []
        for ln in lines:
            keyword =r'.*key:uid,value:(\d+).*'
            content = re.compile(keyword)
            m = content.match(ln)
            if m:
                logger.debug('UID is:' + str(m.group(1)))
                res.append(m.group(1))
        return res

    @ddt.data(*get_test_data())
    def test_tasks(self,data):

        print('CaseName:' + str(data['teca_mid']) + '_' + data['teca_mname'])
        logger.debug('CaseName:' + str(data['teca_mid']) + '_' + data['teca_mname'])
        self.testlink_id = data['teca_mid']
        self.case_id = data['teca_id']
        new_data, dict_data, business_order, vp_type_name = td.handle_db_data(data)
        vpname = tc.get_vp_name(data['teca_vp_id'])
        # action will be run multiple times,for compare uid value
        if vpname.find('Verify_Register_UID') != -1:
            self.run_loop = 2

        # set parameters value for operation_module_upgrade
        if vpname.startswith('OperModule_Upgrade'):
            module_config = device_config.getValue(DEVICENAME, 'operation_module_upgrade_first')
            device_config.setValue(DEVICENAME, 'operation_module_upgrade_current', module_config)
        elif vpname.startswith('OperModule_Second_Upgrade'):
            module_config = device_config.getValue(DEVICENAME, 'operation_module_upgrade_second')
            device_config.setValue(DEVICENAME, 'operation_module_upgrade_current', module_config)

        try:
            for loop_num in range(self.run_loop):
                temp = {}
                for act in business_order:
                    # if len(self.pid) == 0 or prev_act.startswith('reboot'):
                    plist = td.get_pid_by_vpname(DEVICENAME, vpname)
                    if len(plist) > 0:
                        self.pid = plist
                    if act not in temp.keys():
                        temp[act] = 0
                    # maybe same action is executed multiple times
                    else:
                        temp[act] += 1
                        act = '-'.join([act,str(temp[act])])
                    act = act.encode('gbk')
                    #self.execute_action(act, dict_data[act])
                    # Just for duplicate single action
                    vlist = str(dict_data[act]).split('|')
                    try:
                        self.execute_action(act, vlist[loop_num])
                    except Exception, ex:
                        self.execute_action(act, vlist[0])

                    if not self.result:
                        break
                # find special log
                if self.result:
                    self.result, found_lines= vp.filter_log_result(self.log_name, self.pid, 'MATCH', DEVICENAME, new_data['teca_expe_result'])
                    # if log is found, then get detail content and compare
                    if self.result:
                        if vpname.upper().find('LOG') != -1 and data['teca_comp_id'] == 5:
                            # verify detail log contents(login package, register & login)
                            logger.debug('Verify contentS of login package')
                            self.result = self.verify_login_package(found_lines)
                        # get uid according to log
                        elif vpname.find('Verify_Register_UID') != -1:
                            value = self.get_user_id(found_lines)
                            self.filter_log[loop_num] = value
                            # waiting for session invalid
                            logger.debug('Step: waiting for session invalid')
                            sleep(120)
                    else:
                        break

        except Exception, ex:
            logger.error(ex)

        # Verify UID for register precoess
        if vpname.find('Verify_Register_UID') != -1 and len(self.filter_log.keys())> 1:
            self.result = vp.verify_user_id(self.filter_log[0],self.filter_log[1],vp_type_name)

        self.assertEqual(self.result, True)


def run(dname, loop, rtype):

    global DEVICENAME, DEVICE, LogPath
    global LOOP_NUM, RESULT_DICT, FAIL_CASE, RUN_ID


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
        # insert run info to database
        dname = sys.argv[1]
        slist = sys.argv[2]
        vname = device_config.getValue(dname,'version')
        RUN_ID = tc.insert_runinfo(slist, dname, vname, loop, rtype)

        # start to test
        for LOOP_NUM in range(loop):

            fileobj = file(utest_log, 'a+')
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
                # insert result to testlink
                TestLinkObj.write_result_to_testlink(DEVICENAME, RESULT_DICT)
            else:
                desktop.summary_result(utest_log, False, RESULT_DICT)


    except Exception, ex:
        print ex

if __name__ == '__main__':
    run("ZX1G22TG4F", 1, 'all')




