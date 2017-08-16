#! /usr/bin/python
# -*- coding: utf-8 -*-

import re
from library.myglobal import logger
from business import querydb as tc


def verify_moduleupdate_log(logname, match_type, findstr=''):

    logger.debug('Step: Start to filter test log')

    regular_flag = False
    qindex = 0
    expe_list = []

    # get optional verification point list, save index value
    index = 0
    options = []
    elist = findstr.split("||")
    for el in elist:
        if el.endswith(':opt'):
            temp = el.split(':opt')[0]
            expe_list.append(temp)

            options.append(index)
        else:
            expe_list.append(el)
        index += 1

    if match_type.upper() in ['MATCH']:
        regular_flag = True

    # according to pid to query log file, so will query same file multiple times
    logger.debug('Filter log starting')
    re_flag = False
    find_result = {}
    for i in range(len(expe_list)):
        find_result[i] = False
    loop = 0

    find_row_num = 0
    try:
        while loop < len(expe_list):
            with open(logname) as reader:
                current_line = 0
                for line in reader:
                    if current_line <= find_row_num + 1:
                        current_line += 1
                        continue
                    # remove redundance space
                    line = ' '.join(filter(lambda x: x, line.split(' ')))
                    values = line.split(' ')
                    # values[6:] is text column
                    text = ' '.join(values[6:])
                    if not regular_flag:
                        if text.find(expe_list[qindex]) != -1:
                            print 'Find log:' + line
                            logger.debug('Find log:' + line)
                            find_result[qindex] = True
                            qindex += 1
                            find_row_num = current_line
                    else:
                        if not re_flag:
                            content = re.compile(expe_list[qindex])
                            re_flag = True

                        match = content.match(text)
                        if match:
                            value = match.group(1)
                            print 'Find log:' + value
                            logger.debug('Find log:' + line)
                            find_result[qindex] = True
                            find_row_num = current_line
                            # exit loop when find all matched logs
                            if qindex == len(expe_list) - 1:
                                break
                            else:
                                qindex += 1
                                re_flag = False
                    current_line += 1

                if not find_result[qindex]:
                    print 'log not found:' + expe_list[qindex]
                    logger.error('log not found:' + expe_list[qindex])

                # if filter all conditions, then exit
                if qindex == len(expe_list) - 1:
                    break
                else:
                    # Don't found corresponding log, find new log from the first line
                    qindex += 1
                    re_flag = False
                    loop = qindex

    except Exception, ex:
        logger.error(ex)

    # summary result, find_result{0:True,1:True}, vp index is key value
    res = True
    for k, v in find_result.items():
        # if vp is optional, set value to True whether or not actual result
        if k in options:
            res = res and True
        else:
            res = res and v

    logger.debug('Found all log:' + str(res))

    return res


def filter_log_result(logname, pid_list, match_type, findstr=''):

    logger.debug('Step: Start to filter test log')

    result_dict = {}
    qindex = 0
    expe_list = findstr.split("||")

    if match_type.upper() in ['MATCH']:
        regular_flag = True
        # according to pid to query log file, so will query same file multiple times
        for pi in pid_list:
            logger.debug('Filter log according to PID:' + str(pi))
            result_dict[pi] = False
            re_flag = False
            try:
                with open(logname) as reader:
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
                                    logger.debug('Find log:' + line)
                                    qindex += 1
                            else:
                                if not re_flag:
                                    content = re.compile(expe_list[qindex])
                                    re_flag = True

                                match = content.match(text)
                                if match:
                                    value = match.group(1)
                                    print 'Find log:' + line
                                    logger.debug('Find log:' + line)
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


def verify_excepted_number(value_list, vp_type_name, expected, dtype):

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

    logname = r'E:\AutoTestFrame\log\20170816\ZX1G22TG4F_\1540TestModuleUpdate\test_module_update_8_0_1'
    fstr = '(.*new_download_task onStart logcat taskType plugin_update.*)||(.*new_download_task onRun logcat taskType plugin_update.*)||(.*new_download_task onStart logcat taskType plugin_update.*)||(.*new_download_task onRun logcat taskType plugin_update.*)||(.*new_download_task onFinish logcat taskType plugin_update.*)'
    result = verify_moduleupdate_log(logname,'Match',fstr)
    print result
