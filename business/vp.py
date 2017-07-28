#! /usr/bin/python
# -*- coding: utf-8 -*-

import re
from library.myglobal import logger


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
    res = True
    for key, value in result_dict.items():
        logger.debug('PID:' + str(key) + ':Found all log:' + str(value))
        res = res and value
    return res

if __name__ == '__main__':

    logname = r'E:\AutoTestFrame\log\20170727\ZX1G22TG4F_\1736TestTasks\test_network_change_1_0_1'
    fstr = '(.*awake backstage task system success.*)||(.*Judgment result can run , task type is (get_push_message|magazine_update|ua_time_send|plugin_update) , triggerType is :NET_CHANGE.*)'

    result = filter_log_result(logname,[3730],'Match',fstr)