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
import numpy as np
import matplotlib.pyplot as plt


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

    if 2 < mid <= 5:
        x1 = 1224 - mid
        y1 = 370 - mid

    if 5 < mid <= 7:
        x1 = 1324 +(mid-5)
        y1 = 370 - mid

    if 7 < mid <= 9:
        x1 = 1324 + (mid-5)
        y1 = 420 + (mid-5)

    return x1, y1


def get_big_rectangle_location(loop_number):

    #[120,480] [1320,2112]

    mid = loop_number % 10

    if mid <= 2:
        x1 = 120 - mid
        y1 = 480 - mid

    if 2 < mid <= 5:
        x1 = 120 - mid
        y1 = 816 - mid

    if 5 < mid <= 7:
        x1 = 1320 + mid
        y1 = 816 + mid

    if 7 < mid <= 9:
        x1 = 1320 + mid
        y1 = 2112 + mid

    return x1, y1


def get_point(triangle_point):

    x1, y1 = triangle_point[0][0], triangle_point[0][1]
    x3, y3 = triangle_point[1][0],triangle_point[1][1]
    x2, y2 = triangle_point[2][0],triangle_point[2][1]
    sample_size = 500
    theta = np.arange(0,1,0.001)
    x = theta * x1 + (1 - theta) * x2
    y = theta * y1 + (1 - theta) * y2
    plt.plot(x,y,'g--',linewidth=2)
    x = theta * x1 + (1 - theta) * x3
    y = theta * y1 + (1 - theta) * y3
    plt.plot(x, y, 'g--', linewidth=2)
    x = theta * x2 + (1 - theta) * x3
    y = theta * y2 + (1 - theta) * y3
    plt.plot(x, y, 'g--', linewidth=2)
    rnd1 = np.random.random(size = sample_size)
    rnd2 = np.random.random(size=sample_size)
    rnd2 = np.sqrt(rnd2)
    x = rnd2 * (rnd1 * x1 + (1 - rnd1) * x2) + (1 - rnd2) * x3
    y = rnd2 * (rnd1 * y1 + (1 - rnd1) * y2) + (1 - rnd2) * y3

    length = len(x)

    return x, y


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
            if valid_count > 160:
                break
            logger.debug('Advertisement is pop-up successful')
            # x1, y1 = get_circle_location(valid_count)
            # device.shell('input tap {0} {1}'.format(x1, y1))
            # sleep(1)
            index = 0
            if int(valid_count/loop_number) == 0:
                index = 0
            if int(valid_count/loop_unit) + 1 > (valid_count/loop_unit) >= int(valid_count/loop_unit):
                index = int(valid_count/loop_unit)

            triangle = [[[0, 95], [180, 95], [0, 2560]], [[180, 2560], [180, 95], [0, 2560]],
                    [[180, 95], [220, 550], [1230, 550]], [[180, 95], [1230, 95], [1230, 550]],
                    [[1230, 95], [1230, 2560], [1440, 2560]], [[1230, 95], [1440, 95], [1440, 2560]],
                    [[210, 2050], [210, 2560], [1220, 2560]], [[210, 2050], [210, 2560], [1220, 2560]]]

            x1, y1 = get_point(triangle[index])
            x = x1[valid_count]
            y = y1[valid_count]
            logger.debug('click x1,y1'+str(x)+','+str(y))
            device.shell('input tap {0} {1}'.format(x, y))
            sleep(1)
        else:
            logger.debug('Advertisement is not pop-up')

        if valid_count % loop_unit == 0:
            logger.debug('*****valid_count=*******' + str(valid_count))
            output = device.shell('ls -l /data/data/com.vlife.vivo.wallpaper/files/ua/log/f7235a61fd.dat').readlines()[0].split(' ')
            logger.debug('*****file size:*****' + output[12])

        # if int(valid_count/loop_unit) < 1:
        #     x1, y1 = get_circle_location(valid_count)
        #     logger.debug('click x1,y1'+str(x1)+','+str(y1))
        #     device.shell('input tap {0} {1}'.format(x1, y1))
        #     sleep(1)
        # if 1 < int(valid_count/loop_unit) <= 2:
        #     x1, y1 = get_rectangle_location(valid_count)
        #     logger.debug('click x1,y1'+str(x1)+','+str(y1))
        #     device.shell('input tap {0} {1}'.format(x1, y1))
        #     sleep(1)
        # if 2 < int(valid_count/loop_unit) <= 3:
        #     x1, y1 = get_big_rectangle_location(valid_count)
        #     logger.debug('click x1,y1'+str(x1)+','+str(y1))
        #     device.shell('input tap {0} {1}'.format(x1, y1))
        #     sleep(1)


if __name__ == '__main__':

    global device
    # triangle = [[[0, 95], [180, 95], [0, 2560]], [[180, 2560], [180, 95], [0, 2560]],
    #     [[180, 95], [220, 550], [1230, 550]], [[180, 95], [1230, 95], [1230, 550]],
    #     [[1230, 95], [1230, 2560], [1440, 2560]], [[1230, 95], [1440, 95], [1440, 2560]],
    #     [[210, 2050], [210, 2560], [1220, 2560]], [[210, 2050], [210, 2560], [1220, 2560]]]
    # x, y = get_point(triangle[0])
    # x1 = x[0]

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