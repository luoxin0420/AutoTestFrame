#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Xuxh'

import os
import ddt
import json
import datetime
import sys
try:
    import unittest2 as unittest
except(ImportError):
    import unittest

from time import sleep
from library import performancedata as dumpdata
from library import device
from library import desktop
from library import HTMLTestRunner
from library.myglobal import device_config,POSITIVE_VP_TYPE,logger,PERFORMANCE_COMPONENT
from business import action, vp
from business import querydb as tc
from library import TestLinkObj


def get_test_data():

    dname = sys.argv[1]
    prod_name = device_config.getValue(dname, 'product_type')
    pid = ','.join(tc.get_product_ID_byName(prod_name))
    suite_list = sys.argv[2]
    return tc.filter_cases(suite_list, PERFORMANCE_COMPONENT, pid)

@ddt.ddt
class TestMemoryCPU(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        self.master_service = device_config.getValue(DEVICENAME,'master_service')
        self.version = device_config.getValue(DEVICENAME, 'version')
        self.device_action = action.DeviceAction(DEVICENAME)
        self.action_loop = int(device_config.getValue(DEVICENAME, 'performance_monitor_loop'))

    def setUp(self):

        self.log_name = None
        self.log_path = None
        self.log_reader = None
        self.result = True
        self.log_count = 1
        self.pid = []
        self.ts = None
        self.monitor_type = None
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
                tc.insert_test_result(RUN_ID, self.case_id, LOOP_NUM, 'PASS', os.path.abspath(self.log_name))

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
            if aname.startswith('monitor_memory_start') or aname.startswith('monitor_cpu_start'):
                logger.debug('Step: start to collect performance information')
                self.dump_log_start()
            elif aname.startswith('monitor_memory_stop') or aname.startswith('monitor_cpu_stop'):
                logger.debug('Step: stop collecting performance information')
                self.dump_log_stop()
            elif aname.startswith('wait_time'):
                logger.debug('Step: wait time: ' + str(value))
                sleep(value)
            else:
                aname = aname.split('-')[0]
                self.device_action.choose(aname, value)
        except Exception, ex:
            self.result = False
            print ex
            logger.error('Unknown action name:' + aname)

    def dump_log_start(self):

        name = ''.join([self._testMethodName,'_',str(LOOP_NUM),'_',str(self.log_count)])
        self.log_name = os.path.join(LogPath,name)
        self.log_count += 1
        self.log_reader = dumpdata.MonitorSpecialData(self.log_name, DEVICENAME, self.master_service, self.monitor_type)
        self.log_reader.start()

    def dump_log_stop(self):

        self.log_reader.join()
        sleep(5)

    @ddt.data(*get_test_data())
    def test_memory_cpu(self,data):

        print('CaseName:' + str(data['teca_mid']) + '_' + data['teca_mname'])
        logger.debug('CaseName:' + str(data['teca_mid']) + '_' + data['teca_mname'])
        self.case_id = data['teca_id']
        self.testlink_id = data['teca_mid']
        # handle with database data, unicode to str
        new_data = {}
        for key, value in data.items():

            if isinstance(value,unicode):
                new_data[key.encode('gbk')] = value.encode('gbk')
            else:
                new_data[key.encode('gbk')] = value

        action_values = new_data['teca_action_detail']
        dict_data = json.loads(action_values)

        # get necessary parameters by corresponding value of database
        business_order = tc.get_action_list(data['teca_comp_id'])
        comp_name = tc.get_comp_name(data['teca_comp_id'])
        if comp_name.upper().find('MEMORY') != -1:
            self.monitor_type = 'MEMORY'
        elif comp_name.upper().find('CPU') != -1:
            self.monitor_type = 'CPU'
        vpname = tc.get_vp_name(data['teca_vp_id'])
        vp_type_name = tc.get_vp_type(new_data['teca_vp_type_id'])
        value_list = []

        # start to execute action ( usually, performance testing run multiple times, here add self.action_loop parameters
        for i in range(self.action_loop):
            temp = {}
            self.ts = datetime.datetime.now().strftime("%Y%m%d%H%M")
            try:
                for act in business_order:
                    if act not in temp.keys():
                        temp[act] = 0
                    # maybe same action is executed multiple times
                    else:
                        temp[act] += 1
                        act = '-'.join([act, str(temp[act])])
                    act = act.encode('gbk')
                    self.execute_action(act, dict_data[act])
                    if not self.result:
                        break
                if self.result:
                    logger.debug('Step: Insert performance data into DB')
                    success = tc.insert_info_to_db(self.log_name, self.ts, DEVICENAME, self.version, self.monitor_type)
                    if success:
                        if self.monitor_type == 'MEMORY':
                            val = vp.get_current_memory_info(self.ts, DEVICENAME, vpname, self.version)
                        if self.monitor_type == 'CPU':
                            val = vp.get_current_cpu_info(self.ts, DEVICENAME, self.version)
                        value_list.append(val)
            except Exception, ex:
                logger.error(ex)

        self.result = vp.verify_excepted_number(value_list, vp_type_name, new_data['teca_expe_result'], self.monitor_type)
        if vp_type_name in POSITIVE_VP_TYPE:
            self.assertEqual(self.result, True)
        else:
            self.assertEqual(self.result, False)


def run(dname, loop, rtype):

    global DEVICENAME, DEVICE, LogPath
    global LOOP_NUM, RESULT_DICT, FAIL_CASE, RUN_ID


    DEVICENAME = dname
    DEVICE = device.Device(DEVICENAME)

    # run test case
    logname = desktop.get_log_name(dname,'TestMemory')
    LogPath = os.path.dirname(os.path.abspath(logname))
    utest_log = os.path.join(LogPath,'unittest.html')

    # ##RESULT_DICT format {casename:{Result:['PASS','PASS'],Log:['','']}}#####
    RESULT_DICT = {}
    FAIL_CASE = []

    # insert run info to database
    dname = sys.argv[1]
    slist = sys.argv[2]
    vname = device_config.getValue(dname,'version')
    RUN_ID = tc.insert_runinfo(slist, dname, vname, loop, rtype)

    try:
        for LOOP_NUM in range(loop):
            fileobj = file(utest_log,'a+')
            if LOOP_NUM == 0 or rtype.upper() == 'ALL':
                suite = unittest.TestLoader().loadTestsFromTestCase(TestMemoryCPU)
            else:
                suite = unittest.TestSuite()
                for name in FAIL_CASE:
                    suite.addTest(TestMemoryCPU(name))
                FAIL_CASE = []

            if suite.countTestCases() > 0:

                runner = HTMLTestRunner.HTMLTestRunner(stream=fileobj, verbosity=2, loop=LOOP_NUM, title='Test Memory&CPU Report', description='Test Result',)
                runner.run(suite)
                fileobj.close()
                sleep(5)

            # write log to summary report
            if LOOP_NUM == loop - 1:
                desktop.summary_result(utest_log, True, RESULT_DICT)
                TestLinkObj.write_result_to_testlink(DEVICENAME, RESULT_DICT)
            else:
                desktop.summary_result(utest_log, False, RESULT_DICT)

    except Exception, ex:
        print ex

if __name__ == '__main__':
    run("ZX1G22TG4F", 1, 'all')



