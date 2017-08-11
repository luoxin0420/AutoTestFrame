#! /usr/bin/python
# -*- coding: utf-8 -*-

import re
from library.myglobal import logger
from business import querydb as tc


def filter_log_result(logname, pid_list, match_type, findstr=''):

    logger.debug('Step: Start to filter test log')

    regular_flag = False
    match_list = []
    result_dict = {}
    qindex = 0
    expe_list = findstr.split("||")

    if match_type.upper() in ['MATCH']:
        regular_flag = True

    with open(logname) as reader:
        # according to pid to query log file, so will query same file multiple times
        for pi in pid_list:
            logger.debug('Filter log according to PID:' + str(pi))
            result_dict[pi] = False
            re_flag = False
            try:
                for line in reader:
                    # remove redundance space
                    line = ' '.join(filter(lambda x: x, line.split(' ')))
                    values = line.split(' ')
                    # values[6:] is text column
                    text = ' '.join(values[6:])
                    if values[2] == str(pi):
                        if not regular_flag:
                            if text.find(expe_list[qindex]) != -1:
                                print 'Find log:' + line
                                qindex += 1
                        else:
                            if not re_flag:
                                content = re.compile(expe_list[qindex])
                                re_flag = True

                            match = content.match(text)
                            if match:
                                value = match.group(1)
                                print 'Find log:' + value
                                qindex += 1
                                re_flag = False
                    # exit loop when find all matched logs
                    if qindex == len(expe_list):
                        result_dict[pi] = True
                        break
            except Exception, ex:
                logger.error(ex)
                continue

    # summary result
    if len(result_dict) > 0:
        res = True
        for key, value in result_dict.items():
            logger.debug('PID:' + str(key) + ':Found all log:' + str(value))
            res = res and value
    else:
        res = False
    return res


def get_current_memory_info(ts, DEVICENAME, vpname, version):

    value = 0
    try:

        if vpname.upper() == 'MEMORY_PEAK':
            value = tc.get_memory_info(DEVICENAME, ts, version, 'max')
        if vpname.upper() == 'MEMORY_AVG':
            value = tc.get_memory_info(DEVICENAME, ts, version, 'avg')
    except Exception,ex:
        logger.error(ex)

    return value


def get_current_cpu_info(ts, DEVICENAME, version):


    value = tc.get_cpu_info(DEVICENAME, ts, version)

    return value


def verify_excepted_number(value_list, vp_type_name,expected, dtype):

    result = True

    # verify memory
    if dtype.upper()== 'MEMORY':
        # get average value and compare result
        avg_value = int(sum(value_list)/len(value_list))
        logger.debug('Expected Memory Value:' + str(expected))
        print 'Excepted Memory Value:' + str(expected)
        logger.debug('Actual Memory Value:' + str(avg_value))
        print 'Actual Memory Value:' + str(avg_value)

        if vp_type_name.upper() == 'LESSTHAN':
            if avg_value > int(expected):
                result = False
        elif vp_type_name.upper() == 'GREATERTHAN':
            if avg_value < int(expected):
                result = False
        else:
            result = False

    # verify cpu
    # There is five group data,,[[avg,max,last],[avg1,max1,last1]......]
    if dtype.upper() == 'CPU':
        val2 = []
        last_value = 0
        for val in value_list:
            temp = val[0]
            # avg value change range 5%
            if abs(val[0]-temp) > 0.05:
                result = False
            val2.append(val[1])
            last_value = last_value + val[2]
        if result:
            max_value = max(val2)
            if last_value != 0 or max_value > float(expected):
                result = False

        logger.debug('Expected CPU Value:' + str(expected))
        print 'Excepted CPU Value:' + str(expected)
        logger.debug('Actual Max CPU Value:' + str(max_value))
        print 'Actual Max CPU Value:' + str(max_value)
        logger.debug('Actual last CPU Value:' + str(last_value))
        print 'Actual last CPU Value:' + str(last_value)

    return result

if __name__ == '__main__':

    logname = r'E:\AutoTestFrame\log\20170802\ZX1G22TG4F_\1526TestTasks\test_timer_task_1_0_1'
    fstr = '.*Judgment result can not run , reason :network is not allowed , task type is (get_push_message|magazine_update|ua_time_send|plugin_update).*'
    #fstr = '.*Judgment result can not run , reason :network is not allowed , task type is (aa|ua_time_send)'
    result = filter_log_result(logname,[1813],'Match',fstr)
    print result