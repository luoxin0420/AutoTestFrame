__author__ = 'xuxh'

import subprocess
import threading
import time
import os
import sys
import argparse
from time import sleep
from library import adbtools
from business import action
from library.myglobal import logger


class DumpLogcat(threading.Thread):

    def __init__(self, out,uid,cmd):

        threading.Thread.__init__(self)
        self.logcat = out
        self.uid = uid
        self.process = None
        self.cmd = cmd

    def clear_logcat(self):

        cmd = 'adb -s {0} logcat -c'.format(self.uid)
        subprocess.call(cmd, shell=True)

    def run(self):

        with open(self.logcat, 'w') as self.outfile:
            self.process = subprocess.Popen(self.cmd, shell=True, stdout=self.outfile)

    def stop(self):
        try:
            self.process.kill()
            time.sleep(3)
        except Exception, ex:
            print ex


def verify_log(fname):

    logger.debug('Search key word in the log file')
    filter_text = "localVersionName != currentVersionName | random and test exception"

    with open(fname,'rb') as rfile:

        for line in rfile:
            if line.find(filter_text) != -1:
                logger.debug('test log is found in the file ' + outfile)
                return True

    return False


if __name__ == '__main__':

    newParser = argparse.ArgumentParser()
    newParser.add_argument("uid", help="Your device uid")
    newParser.add_argument("-p", dest="pkg", type=str, help="package name")
    newParser.add_argument("-o", dest="out", type=str, help="output file name")

    args = newParser.parse_args()
    uid = args.uid
    pkg = args.pkg
    out = args.out

    if uid is None or out is None or pkg is None:
        sys.exit(0)

    Found = False
    my_device = adbtools.AdbTools(uid)
    my_action = action.DeviceAction(uid)
    #pid = my_device.get_pid(pkg)

    cmd = 'adb logcat -b main -b system -v threadtime'

    for i in range(3):

        temp = os.path.splitext(out)
        outfile = ''.join([temp[0], '_', str(i), temp[1]])
        logger.debug('Loop Number:' + str(i))
        logger.debug('Start to grasp the log')
        log_reader = DumpLogcat(outfile, uid, cmd)
        log_reader.start()
        ######verify main process
        # my_action.network_change('CLOSE_ALL')
        # sleep(1)
        # my_action.network_change('ONLY_WIFI')
        # sleep(60)
        # log_reader.stop()
        # logger.debug('Stop logging')
        # result = verify_log(outfile)
        #
        # # if find log, then exit loop
        # if result:
        #     Found = True
        #     break
        #
        # # otherwise, clear app data and reboot
        # my_device.clear_app_data(pkg)
        # sleep(1)
        # my_device.clear_app_data('com.android.systemui')
        #
        # my_device.reboot()
        # sleep(30)
        # my_action.unlock_screen('DEFAULT')

        ###### verify systemui process

        my_action.network_change('ONLY_WIFI')
        # otherwise, clear app data and reboot
        my_device.clear_app_data(pkg)
        sleep(1)
        my_device.clear_app_data('com.android.systemui')
        sleep(1)
        pid = my_device.get_pid('com.android.systemui')
        if pid is not None:
            cmd = 'kill -9 {0}'.format(pid)
            my_device.shell(cmd)
        sleep(10)
        log_reader.stop()
        logger.debug('Stop logging')
        result = verify_log(outfile)
        # if find log, then exit loop
        if result:
            Found = True
            break
        my_action.unlock_screen('DEFAULT')

    if not Found:
        print 'test log is not found'


