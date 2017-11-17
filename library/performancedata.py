__author__ = 'Xuxh'

import subprocess
import threading
from time import sleep
import ctypes
import inspect


class ADBShell(object):

    @staticmethod
    def runShell(cmd):
        popen = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        popen.wait()
        result = popen.stdout.readlines()
        return result


class AppInfo(object):

    def __init__(self, sn, packagename):
        self.sn = sn
        self.packagename = packagename

    def getAppPID(self):

        pid = 0
        length = 0
        cmd = "adb -s %s shell ps | grep %s" % (self.sn, self.packagename)
        try:
            popen = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            popen.wait()
            for ln in popen.stdout.readlines():

                appinfo = ln.split(' ')
                length = len(appinfo) - 1
                if appinfo[length].strip() == self.packagename:
                    for p in appinfo:
                        if p.isalnum():
                            pid = p
                            return pid

        except KeyboardInterrupt:
            return pid

    def getAppUID(self):

        uid = 0
        length = 0
        cmd = "adb -s %s shell dumpsys package %s | grep userId=" % (self.sn, self.packagename)
        try:

            popen = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE)
            popen.wait()
            uid = popen.stdout.readline().split('gids')[0].strip().replace('userId=','')
            return uid

        except KeyboardInterrupt:
            return uid


class MemoryInfo(object):

    def __init__(self, sn, packagename):
        self.sn = sn
        self.packagename = packagename
        self.app = AppInfo(sn,packagename)

    def get_memoryInfo(self):

        res= []
        cmd = "adb -s %s shell top -n 1 | grep %s" % (self.sn, self.app.getAppPID())
        try:
            result = ADBShell.runShell(cmd)
            if len(result) > 0:
                value = result[0].split(' ')
                res.append(value[12]) # vss
                res.append(value[13]) # rss
            return res

        except KeyboardInterrupt:
            return res


class CPUInfo(object):

    def __init__(self, sn, packagename):
        self.sn = sn
        self.packagename = packagename

    def getCPUInfo(self):

        res= []
        cmd = "adb -s %s shell dumpsys cpuinfo | grep %s" % (self.sn, self.packagename)
        try:
            result = ADBShell.runShell(cmd)
            if len(result) > 0:
                percent = result[0].split(' ')
                res.append(percent[2])
                res.append(percent[4])
                res.append(percent[7])
            return res

        except KeyboardInterrupt:
            return res


class TrafficInfo(object):

    def __init__(self, sn, packagename):
        self.sn = sn
        self.packagename = packagename
        self.app = AppInfo(sn,packagename)

    def get_networkTraffic(self):

        floatTotalNetTraffic = 0.0
        cmd = "adb -s %s shell cat /proc/net/xt_qtaguid/stats" % (self.sn)
        popen = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE)
        popen.wait()

        # print flag_net
        if "No such file or directory" not in popen.stdout.readline():
            list_rx = [] # receive data
            list_tx = [] # send data
            # print str_uid_net_stats
            cmd = "adb -s %s shell cat /proc/net/xt_qtaguid/stats | grep %s" % (self.sn, self.app.getAppUID())
            popen = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE)
            popen.wait()
            try:
                for item in popen.stdout.readlines():
                    rx_bytes = item.split()[5] # receive traffic flow
                    tx_bytes = item.split()[7] # send traffic flow
                    list_rx.append(int(rx_bytes))
                    list_tx.append(int(tx_bytes))
                # print list_rx, sum(list_rx)
                floatTotalNetTraffic = (sum(list_rx) + sum(list_tx))/1024.0/1024.0
                floatTotalNetTraffic = round(floatTotalNetTraffic,4)
                return floatTotalNetTraffic
            except:
                print "[ERROR]: cannot get the /proc/net/xt_qtaguid/stats, return 0.0"
                return 0.0
        else:
            try:
                scmd = "adb -s % shell cat /proc/uid_stat/%s/tcp_snd" % (self.sn, self.app.getAppUID())
                rcmd = "adb -s % shell cat /proc/uid_stat/%s/tcp_rcv" % (self.sn, self.app.getAppUID())
                sp = subprocess.Popen(scmd,shell=True, stdout=subprocess.PIPE)
                rp = subprocess.Popen(rcmd,shell=True, stdout=subprocess.PIPE)
                floatTotalTraffic = (int(sp.stdout.readline) + int(rp.stdout.readlind))/1024.0/1024.0
                floatTotalTraffic = round(floatTotalTraffic,4)
                return floatTotalTraffic
            except:
                return 0.0


class MonitorSpecialData(threading.Thread):

    def __init__(self, log_name, uid, pkg, dtype):

        self._stopevent = threading.Event()
        self._sleepperiod = 2.0
        threading.Thread.__init__(self)
        self._uid = uid
        self._pkg = pkg
        self._process = None
        self._log = log_name
        self._type = dtype
        self.outfile = None

    def run(self):

        cmd = ''
        if self._type.upper() == 'MEMORY':
            cmd = "adb -s {0} shell dumpsys meminfo | grep {1}".format(self._uid, self._pkg)
        elif self._type.upper() == 'CPU':
            cmd = "adb -s {0} shell top -n 1 | grep {1}".format(self._uid, self._pkg)
        with open(self._log, 'w') as self.outfile:
            while not self._stopevent.isSet():
                self._process = subprocess.Popen(cmd, shell=True, stdout=self.outfile)
                self._stopevent.wait(self._sleepperiod)

    def join(self, timeout=None):
        """ Stop the thread and wait for it to end. """
        self._stopevent.set()
        threading.Thread.join(self, timeout)

    def stop(self):
        try:
            print 'wait for top command stopped...'
            self._process.kill()
            self.outfile.close()
        except Exception, ex:
            print ex


def _async_raise(tid, exctype):

    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        #exctype = type(exctype)
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, TypeError)

if __name__ == '__main__':

    myapp = MemoryInfo('NX511J','com.android.systemui')
    appid = myapp.get_memoryInfo()
    print appid