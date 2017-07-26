#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Xuxh'

import datetime
import subprocess
import re
import tempfile
from time import sleep
import platform
import os
from os import path

import configuration
import myglobal
import uiautomator
from library.myglobal import logger


class Device(object):

    def __init__(self, uid):
        self.CONFIG = configuration.configuration()
        self.CONFIG.fileConfig(myglobal.CONFIGURATONINI)
        self.uid = uid
        self.pkg = self.CONFIG.getValue(uid,'apppackage')
        self.activity = self.CONFIG.getValue(uid,'appactivity')
        self.name = self.CONFIG.getValue(uid,'name')

    @staticmethod
    def shellPIPE(cmd):

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        return out

    @staticmethod
    def get_connected_devices():

        cmd = "adb devices"
        counter = 0
        devices =[]
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
        for line in p.stdout.readlines():
            if len(line.strip()) > 0 and counter != 0:
                temp = line.split('device')
                devices.append(temp[0].strip())
            counter += 1
        return devices

    def getProcessId(self): # get the top activity PID

        cmd = 'adb -s {0} shell dumpsys activity top'.format(self.uid)
        out = self.shellPIPE(cmd)
        filename = ''.join([self.uid,datetime.now().strftime('%Y%m%d%H%M%S'),'top.txt'])
        curdir = os.getcwd()
        topProcessFile = path.join(curdir, filename)
        myFile = open(topProcessFile, 'w+')
        myFile.write(out)
        myFile.seek(0, 0);

        pid = ""

        for eachLine in myFile:
            if "pid=" in eachLine:
                activity = eachLine.split(" ")[3].strip()
                pid = eachLine.split("pid=")[-1].strip()
                break
        myFile.close()
        return pid

    def wifi_operation(self, action):

        if action.upper() == "OFF":
            cmd = "".join(["adb -s ", self.uid, " shell svc wifi disable "])
        if action.upper() == "ON":
            cmd = "".join(["adb -s ",self.uid," shell svc wifi enable "])
        try:

            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            p.wait()
        except Exception,ex:
            print ex

    def gprs_operation(self, action):

        if action.upper() == "OFF":
            cmd = "".join(["adb -s ", self.uid, " shell svc data disable "])
        if action.upper() == "ON":
            cmd = "".join(["adb -s ",self.uid," shell svc data enable "])
        try:

            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            p.wait()
        except Exception,ex:
            print ex

    def device_file_operation(self, action, orig_path, dest_path):

        if action.upper() == "PULL":
            cmd = "".join(["adb -s ", self.uid, " pull ",orig_path," ",dest_path])
        if action.upper() == "PUSH":
            cmd = "".join(["adb -s ", self.uid, " push ",orig_path," ", dest_path])
        if action.upper()== "DELETE":
            cmd = "".join(["adb -s ", self.uid, " shell rm ",orig_path])

        try:
            out_temp = tempfile.SpooledTemporaryFile(bufsize=10*1000)
            fileno = out_temp.fileno()
            p = subprocess.Popen(cmd, shell=True, stdout=fileno, stderr=subprocess.STDOUT)
            p.wait()
        except Exception,ex:
            print ex

    def app_operation(self,action,path='',service=''):

        if service != '':
            pkg = service
            pname = service
        else:
            pkg = self.pkg
            pname = ''.join([pkg, '/', self.activity])

        if pkg != '':
            if action.upper() == "LAUNCH":
                cmd = "".join(["adb -s ", self.uid, " shell am start -n ", pname])
            if action.upper() == "START":
                cmd = "".join(["adb -s ", self.uid, " shell am start ", pkg])
            if action.upper() == "CLOSE":
                cmd = "".join(["adb -s ", self.uid, " shell am force-stop ", pkg])
            if action.upper() == "INSTALL":
                cmd = "".join(["adb -s ", self.uid, " shell pm install -f ", path])
            if action.upper() == "CLEAR":
                cmd = "".join(["adb -s ", self.uid, " shell pm clear ", pkg])
            if action.upper() == "UNINSTALL":
                cmd = "".join(["adb -s ", self.uid, " shell pm uninstall ", pkg])

            try:
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                p.wait()
            except Exception,ex:
                print ex

    def get_os_version(self):

        cmd = "".join(["adb -s ", self.uid, " shell getprop ro.build.version.release "])
        out = self.shellPIPE(cmd).split('.')

        if len(out) > 0:
            return int(out[0])
        else:
            return 0

    def get_screen_size(self):

        width = 0
        height = 0
        # cmd = "adb shell dumpsys window displays |head -n 3" (linux)
        # this command is supported above android 4.3, wm tool must be installed
        cmd = "".join(["adb -s ", self.uid, " shell wm size"])
        out = self.shellPIPE(cmd).split(':')
        if len(out) > 1:
            width, height = out[1].strip().split('x')
        return int(width),int(height)

    def emulate_swipe_action(self):

        # get resolution of screen
        width,height = self.get_screen_size()
        unlock_style = self.CONFIG.getValue(self.uid,'unlock_style')
        unlock_location = self.CONFIG.getValue(self.uid,'unlock_location')
        if unlock_style.upper() == 'LANDSCAPE':
            cmd = "adb -s {0} shell input swipe {1} {2} {3} {4}".format(self.uid,int(width/5),int(height/2),int(width/5*4),int(height/2))
        else:
            if unlock_location.upper() == 'CENTER':
                cmd = "adb -s {0} shell input swipe {1} {2} {3} {4}".format(self.uid,int(width/2),int(height/2),int(width/2),int(height/4))
            if unlock_location.upper() == 'BOTTOM':
                cmd = "adb -s {0} shell input swipe {1} {2} {3} {4} {5}".format(self.uid,int(width/2),int(height/4*3),int(width/2),int(0),int(200))
        self.shellPIPE(cmd)
        sleep(2)

    def find_package(self):

        out = ''
        cmd = "".join(["adb -s ", self.uid, " shell pm list package ", self.pkg])
        out = self.shellPIPE(cmd)
        return out

    def screen_on_off(self, screen_action):
        sysstr = platform.system()
        if sysstr == "Windows":
            cmd = "".join(["adb -s ", self.uid, " shell dumpsys power | findstr  ","Display"])
        elif sysstr == "Linux":
            cmd = "".join(["adb -s ", self.uid, " shell dumpsys power | grep  ","Display"])
        else:
            cmd=""

        if cmd != "":
            out = self.shellPIPE(cmd)
            if screen_action.upper() == "ON":
                while out.find("state=OFF") != -1:
                    cmd = "".join(["adb -s ", self.uid, " shell input keyevent 26"])
                    out = self.shellPIPE(cmd)
            elif screen_action.upper() == "OFF":
                while out.find("state=ON") != -1 :
                    cmd = "".join(["adb -s ", self.uid, " shell input keyevent 26"])
                    out = self.shellPIPE(cmd)

    def update_android_time(self,delta,interval_unit='hour'):

        # delta is interval time, like 1, -1
        interval_num = int(delta)
        #interval_unit = self.CONFIG.getValue(self.uid, 'frequence_unit')

        # get android time, then get expected time stamp
        cmd = "".join(["adb -s ", self.uid, " shell date +%Y%m%d.%H%M%S "])
        out = self.shellPIPE(cmd)
        for char in ['\r','\n']:
            out = out.replace(char,'')
        cur_time = datetime.datetime.strptime(out,'%Y%m%d.%H%M%S')
        if interval_unit.lower() == 'hour':
            expe_time = cur_time + datetime.timedelta(hours=interval_num)
        elif interval_unit.lower() == 'minutes':
            expe_time = cur_time + datetime.timedelta(minutes=interval_num)
        else:
            expe_time = cur_time + datetime.timedelta(days=interval_num)
        #time_stamp = time.mktime(expe_time.timetuple())
        version = self.get_os_version()

        if version < 6:
            expe_time = datetime.datetime.strftime(expe_time,'%Y%m%d.%H%M%S')
            cmd = 'adb -s {0} shell su 0 date -s {1} '.format(self.uid,expe_time)

            if self.name.upper().find('VIVO') != -1:
                cmd = 'adb -s {0} shell date -s {1} '.format(self.uid,expe_time)

        else:
            expe_time = datetime.datetime.strftime(expe_time,'%m%d%H%M%Y.00')
            cmd = 'adb -s {0} shell date {1} ; am broadcast -a android.intent.action.TIME_SET'.format(self.uid,expe_time)

        self.shellPIPE(cmd)

    def uninstall_app(self):

        try:
            pkg = self.CONFIG.getValue(self.uid,'apppackage')
            result =self.find_package()
            if result.find(pkg) != -1:
                self.app_operation('UNINSTALL')
        except Exception,ex:
            print ex

    def device_service_operation(self,action):

        service = self.CONFIG.getValue(self.uid,'service')

        if service != "":
            if action.upper() == "START":
                cmd = "".join(["adb -s ", self.uid, " shell am startservice -n ", service])
            if action.upper() == "STOP":
                cmd = "".join(["adb -s ", self.uid, " shell am stopservice -n ", service])
            self.shellPIPE(cmd)

    def get_device_screenshot(self,fname):

        cmd = "".join(["adb -s ",self.uid," shell /system/bin/screencap -p /sdcard/screenshot.png "])
        self.shellPIPE(cmd)
        cmd = "".join(["adb -s ",self.uid," pull /sdcard/screenshot.png ", fname])
        self.shellPIPE(cmd)

    def device_reboot(self):

        cmd = ''.join(["adb -s ",self.uid," reboot"])
        self.shellPIPE(cmd)

    def install_app_from_desktop(self,action,path=''):

        if path != '' and os.path.isfile(path):
            if action.upper() == "INSTALL":
                cmd = "".join(["adb -s ", self.uid, " install ", path])
            if action.upper() == "COVER_INSTALL":
                cmd = "".join(["adb -s ", self.uid, " install -r ", path])
            try:
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                p.wait()
            except Exception,ex:
                print ex

    def get_device_mac_address(self):

        try:
            cmd = "".join(["adb -s ", self.uid, " shell cat /sys/class/net/wlan0/address "])
            out = self.shellPIPE(cmd)
        except Exception,ex:
            return ''

        return out

    def sdcard_operation(self,action,path):

        #https://raspberrypi.stackexchange.com/questions/3800/find-the-right-device-name-of-an-sd-card-connected-via-a-usb-card-reader
        #https://stackoverflow.com/questions/22549489/mount-an-sd-card-manually-from-adb-shell-in-android
        if action.upper() == "MOUNT":
            cmd = "".join(["adb -s ", self.uid, " shell su mount -o bind  ", path])
        if action.upper() == "UMONNT":
            cmd = "".join(["adb -s ", self.uid, " shell su umount", path])
        self.shellPIPE(cmd)

    def get_IMEI(self):

        # IMEI由15位数字组成，其组成为：　　1、前6位数（TAC，Type Approval Code)是"型号核准号码"，一般代表机型
        # 2、接着的2位数（FAC，Final Assembly Code)是"最后装配号"，一般代表产地
        # 3、之后的6位数（SNR)是"串号"，一般代表生产顺序号
        # 4、最后1位数（SP)通常是"0"，为检验码，目前暂备用。
        # adb shell dumpsys iphonesubinfo (仅适用<4.4以下版本）
        #       Result: Parcel(
        # 0x00000000: 00000000 0000000f 00350033 00340035 '........3.5.5.4.'
        # 0x00000010: 00350035 00360030 00330031 00380033 '5.5.0.6.1.3.3.8.'
        # 0x00000020: 00340033 00000036                   '3.4.6...        ')
        try:
            cmd = "".join(["adb -s ", self.uid, " shell service call iphonesubinfo 1"])
            out = self.shellPIPE(cmd)
            temp = out.split("'")
            imei = ''.join([temp[1],temp[3],temp[5]]).replace('.','').strip()
        except Exception,ex:
            return ''
        return imei

    # 0 -->  "KEYCODE_UNKNOWN" 1 -->  "KEYCODE_MENU" 2 -->  "KEYCODE_SOFT_RIGHT" 3 -->  "KEYCODE_HOME"
    # 4 -->  "KEYCODE_BACK"    5 -->  "KEYCODE_CALL" 6 -->  "KEYCODE_ENDCALL"
    # 7-16 -->  "KEYCODE_0" -->  "KEYCODE_9"
    # 29-54 -->  "KEYCODE_A" -->  "KEYCODE_Z"
    # 24 -->  "KEYCODE_VOLUME_UP"
    # 25 -->  "KEYCODE_VOLUME_DOWN"
    # 26 -->  "KEYCODE_POWER"
    # 27 -->  "KEYCODE_CAMERA"
    # 28 -->  "KEYCODE_CLEAR"
    # 187 --> KEYCODE_APP_SWITCH
    def send_keyevent(self,value):

        cmd = "".join(["adb -s ", self.uid, " shell input keyevent ", str(value)])
        self.shellPIPE(cmd)

    def restart_adb_server(self):

        cmd = "".join(["adb ", " kill-server "])
        self.shellPIPE(cmd)
        sleep(2)
        cmd = "".join(["adb ", " start-server "])
        self.shellPIPE(cmd)

    def do_popup_windows(self,number, find_text):

        for i in range(number):
            uiautomator.click_popup_window(self.uid,find_text)

    def unlock_screen(self):

        self.screen_on_off("OFF")
        sleep(2)
        self.screen_on_off("ON")
        sleep(2)
        self.emulate_swipe_action()
        sleep(1)


def get_userid_from_file(devicename):

    cmd = "".join(["adb -s ", devicename, " shell cat /data/data/com.vlife/shared_prefs/userinfo.xml"])
    out = Device.shellPIPE(cmd)
    keyword = r'.* <string name="uid">(.*)</string>.*'
    content = re.compile(keyword)
    for char in ['\r','\n']:
        out = out.replace(char,'')
    m = content.match(out)
    if m:
        userid = m.group(1)
    else:
        userid = ''

    return userid









