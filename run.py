__author__ = 'Xuxh'

import sys
import argparse
try:
    import unittest2 as unittest
except(ImportError):
    import unittest

from library import device
from library import configuration
from library import myglobal
from testcases import test_startup_register
from testcases import test_module_update
from testcases import test_tasks_new

if __name__ == '__main__':


    newParser = argparse.ArgumentParser()

    newParser.add_argument("uid", help="Your device uid")
    newParser.add_argument("-l", "--ln", dest="lnum", default=1, type=int, help="Loop number")
    newParser.add_argument("-t", "--lt", dest="ltype", default='Only_Fail', type=str, help="Loop type")
    args = newParser.parse_args()
    uid = args.uid
    loop_number = args.lnum
    loop_type = args.ltype

    if uid is None:
        sys.exit(0)


    # verify if device is connected
    devices = device.Device.get_connected_devices()
    if uid not in devices:
        print "Device is not connected, please check"
        sys.exit(0)

    try:
        # verify if device is configuration
        config = configuration.configuration()
        config.fileConfig(myglobal.CONFIGURATONINI)
    except Exception, ex:
        print "There is no related configuration information"
        sys.exit(0)

    try:
        case_list = config.getValue(uid,'test_list').split(';')
        for cases in case_list:
            if cases.startswith('test_startup_register'):
                test_startup_register.run(uid, loop_number, loop_type)
            if cases.startswith('test_tasks'):
                test_tasks_new.run(uid, loop_number, loop_type)
            if cases.startswith('test_module'):
                myglobal.logger.debug('Start to test module')
                test_module_update.run(uid, loop_number, loop_type, myglobal.logger)

    except Exception, ex:
        print ex



