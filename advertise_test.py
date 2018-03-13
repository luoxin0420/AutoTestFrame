#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'xuxh'

import os
import re
from time import sleep
import subprocess
import argparse
import sys
import threading
import datetime
import math


from library import adbtools
from business import action
from library.myglobal import logger
from library import desktop
from library import imagemagick


def get_circle_location(loop_number):

    angle = (loop_number % 10) * 10

    r = 70
    x1 = 1274 + r*math.cos(angle*math.pi/180)
    y1 = 370 + r*math.sin(angle*math.pi/180)
    return x1, y1


def get_rectangle_location(loop_number):

    #[1224,320][1324,420]

    mid = loop_number % 10

    if mid <= 2:
        x1 = 1224 - mid
        y1 = 320 - mid

    if 2<mid<=5:
        x1 = 1224 - mid
        y1 = 370 - mid

    if 5<mid<=7:
        x1 = 1324 +(mid-5)
        y1 = 370 - mid

    if 7<mid<=9:
        x1 = 1324 + (mid-5)
        y1 = 420 + (mid-5)

    return x1, y1


def get_big_rectangle_location(loop_number):

    #[120,480] [1320,2112]

    mid = loop_number % 10

    if mid <= 2:
        x1 = 120 - mid
        y1 = 480 - mid

    if 2<mid<=5:
        x1 = 120 - mid
        y1 = 816 - mid

    if 5<mid<=7:
        x1 = 1320 + mid
        y1 = 816 + mid

    if 7<mid<=9:
        x1 = 1320 + mid
        y1 = 2112 + mid

    return x1, y1


def run(uid, device, loop_number, loop_unit):

    log_path = desktop.get_log_path(uid, 'advertise_test')
    valid_count = 1
    output = device.shell('ls -l /data/data/com.vlife.vivo.wallpaper/files/ua/log/f7235a61fd.dat').readlines()[0].split(' ')
    logger.debug('*****file size:******' + output[12])
    for i in range(loop_number):
        value = False
        logger.debug('loop number:' + str(i))
        # restart adb every 3 times
        desktop.close_all_program('adb')
        # restart adb server
        sleep(1)
        device.adb('kill-server')
        sleep(5)
        device.adb('start-server')
        sleep(5)

        display_state = device.get_display_state()

        if not display_state:
            da = action.DeviceAction(uid)
            da.unlock_screen('default')
            sleep(1)
        # change wifi every 5 times
        if i % 5 == 0:
            logger.debug('close_open wifi')
            #da.connect_network_trigger('CLOSE_ALL:ONLY_WIFI')
            device.shell('svc wifi disable')
            sleep(2)
            device.shell('svc wifi enable')
            sleep(3)

        logger.debug('clear UC app')
        device.clear_app_data('com.UCMobile')
        logger.debug('waiting time for 20s')
        sleep(20)
        logger.debug('log in application')

        # access to app and screenshot
        device.start_application('com.UCMobile/com.uc.browser.InnerUCMobile')
        sleep(4)
        fname = device.screenshot('loop_'+str(i)+'_',os.path.abspath(log_path))
        screenshot_full_path = os.path.join(os.path.abspath(log_path),fname+'.png')

        logger.debug('verify if pop-up advertisement')
        crop_name = os.path.join(os.path.abspath(log_path), 'crop'+str(i)+'.png')
        imagemagick.crop_image(screenshot_full_path, 100, 100, 1224, 320, crop_name)
        value = imagemagick.compare_image(crop_name, r'E:/crop_expected.png')
        if value:
            valid_count += 1
            logger.debug('Advertisement is pop-up successful')
            # x1, y1 = get_circle_location(valid_count)
            # device.shell('input tap {0} {1}'.format(x1, y1))
            # sleep(1)
        else:
            logger.debug('Advertisement is not pop-up')

        if valid_count % loop_unit == 0:
            logger.debug('*****valid_count=*******' + str(valid_count))
            output = device.shell('ls -l /data/data/com.vlife.vivo.wallpaper/files/ua/log/f7235a61fd.dat').readlines()[0].split(' ')
            logger.debug('*****file size:*****' + output[12])

        if int(valid_count/loop_unit) == 1:
            x1, y1 = get_circle_location(valid_count)
            device.shell('input tap {0} {1}'.format(x1, y1))
            sleep(1)
        if int(valid_count/loop_unit) == 2:
            x1, y1 = get_rectangle_location(valid_count)
            device.shell('input tap {0} {1}'.format(x1, y1))
            sleep(1)
        if int(valid_count/loop_unit) == 3:
            x1, y1 = get_big_rectangle_location(valid_count)
            device.shell('input tap {0} {1}'.format(x1, y1))
            sleep(1)

        sleep(1)


if __name__ == '__main__':

    global device

    newParser = argparse.ArgumentParser()
    newParser.add_argument("uid", help="Your device uid")
    newParser.add_argument("-l", "--ln", dest="lnum", default=200, type=int, help="Loop number")
    newParser.add_argument("-n", "--un", dest="unit", default=1, type=int, help="Loop number")
    args = newParser.parse_args()
    uid = args.uid
    loop_number = args.lnum
    loop_unit = args.unit
    if uid is None:
        sys.exit(0)

    device = adbtools.AdbTools(uid)
    devices = device.get_devices()
    if uid not in devices:
        print "Device is not connected, please check"
        sys.exit(0)

    run(uid, device, loop_number, loop_unit)