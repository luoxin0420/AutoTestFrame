#!/usr/bin/evn python
# -*- coding:utf-8 -*-

__author__ = 'Xuxh'
import sys
import argparse
from testcases import test_performance
from library import adbtools
from library.myglobal import performance_config


if __name__ == '__main__':

    # func_list = get_kw_list()

    newParser = argparse.ArgumentParser()

    newParser.add_argument("uid", help="Your device uid")

    args = newParser.parse_args()
    uid = args.uid

    devices = adbtools.AdbTools(uid).get_devices()
    if uid not in devices:
        print "Device is not connected, please check"
        sys.exit(0)

    try:
        loop = performance_config.getValue(uid, 'loop')
        process_name = performance_config.getValue(uid, 'app_process_name')
        case_list = performance_config.getValue(uid, 'case_list').split(';')
        case_exe = test_performance.CaseExecutor(int(loop), uid)
        case_exe.exec_test_cases(case_list)

    except Exception, ex:
        print ex

