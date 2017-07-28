__author__ = 'Xuxh'

import sys
import argparse
try:
    import unittest2 as unittest
except(ImportError):
    import unittest

from library import device
from library.myglobal import device_config


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
        # automation test database
        device_config.setValue(uid,'suite_info',1)
        from testcases import test_tasks_new
        test_tasks_new.run(uid, loop_number, loop_type)

    except Exception, ex:
        print ex



