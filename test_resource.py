#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Xuxh'

import argparse
import sys
from time import sleep
import os
import threading

from library import device
from library.mylog.logger import log
from library import desktop
from library import myuiautomator
from library.myglobal import resource_config
from business import querydb as tc
from library import unlock as ul
reload(sys)
sys.setdefaultencoding("utf-8")


# 需要安装ADBKEYBOARD 输入法,并且设置为默认输入法
# 需要设置开发者选项-保持响醒状态
# 确保设置锁屏或者主题的应用是在其主界面


def write_html_header(logname,title):

    htmlhead = '''<html>
<head>
<title></title>
<meta http-equiv="Content-Type" content="text/html; charset=gbk">
<style type="text/css">
<!--
table{empty-cells:show;table-layout:fixed;}
#wrap{word-wrap:break-word;overflow:hidden;}
.table_whole {width:320px;}
.table_whole td{background-color:#E0E0E0;}
.table_whole th{background-color:#d0d0d0;}
-->
</style>
<script type="text/javascript">
function resetResultTable()
{
var pass_count = document.getElementsByName("pass").length
var fail_count = document.getElementsByName("fail").length
var error_count = document.getElementsByName("error").length
var all_count = pass_count + fail_count + error_count
document.getElementById('all_count').innerHTML=all_count
document.getElementById('pass_count').innerHTML=pass_count
document.getElementById('fail_count').innerHTML=fail_count
document.getElementById('error_count').innerHTML=error_count
}
</script>
</head>
<body onload="resetResultTable()">
<center><h1>''' + title + '''</h1></center>
<table class="table_whole" border="1">
<tr align="right">
<th>ALL</th>
<th>PASS</th>
<th>FAIL</th>
<th>ERROR</th>
</tr>
<tr align="right">
<td><font color="Black" id="all_count"></font></td>
<td><font color="#007500" id="pass_count"></font></td>
<td><font color="Red" id="fail_count"></font></td>
<td><font color="Red" id="error_count"></font></td>
</tr>
</table>
'''
    tableheader = '''
<br>
<table border="1" width="1000">
<thead bgcolor="#d0d0d0">
<tr>
<th width="15%">TIME</th>
<th width="15%">TAG</th>
<th>MESSAGE</th>
</tr>
</thead>
<tbody id="wrap" bgcolor="#E0E0E0">'''
    with open(logname,'a+') as wfile:

        wfile.write(htmlhead)
        wfile.write(tableheader)


def get_screenshots_name(logname,number):

    dirname = os.path.dirname(os.path.abspath(logname))
    image_path = os.path.join(dirname,'image')

    if not os.path.isdir(image_path):
        os.makedirs(image_path)
    basename = ''.join(['screen',str(number), '.png'])
    filename = os.path.join(image_path,basename)
    return filename


def get_test_resource(vendor):

    # filter data from database

    # data = []
    # with open(r'E:\work\resource.csv') as rfile:
    #     reader = csv.reader(rfile)
    #     for line in reader:
    #         data.append(line[0])
    data = tc.filter_image_source(vendor)
    return data


def set_resource_action(uid, action, qstr):

    if action.upper() == 'SEARCH':
        my_logger.write('TEST_STEP','Search resource ' + qstr)
        activity_name = resource_config.getValue(uid,'set_resource_pkg')
        my_device.app_operation(action='LAUNCH', pkg=activity_name)
        sleep(2)
        steps = resource_config.getValue(uid,'search_path').split('|')
    # found source is used
    else:
        steps = resource_config.getValue(uid,'set_path').split('|')
    try:

        for text in steps:

            if text.find(':') != -1:
                x = text.split(':')[1]
                y = text.split(':')[2]
                value = text.split(':')[0]
            else:
                value = text
                x, y = 0, 0
            # click element
            if text.find('CLICK') != -1:
                my_device.click_screen_by_coordinate(x, y)
                sleep(2)
            else:
                element = myuiautomator.Element(uid)
                event = myuiautomator.Event(uid)
                if text.find('RNAME') == -1:
                    ele = element.findElementByName(unicode(value))
                else:
                    ele = element.findElementsByName(unicode(qstr, 'gbk'))
                if ele is not None:
                    if isinstance(ele, list):
                        index = len(ele) - 1
                        event.touch(ele[index][0]-int(x), ele[index][1]-int(y))
                    else:
                        #my_logger.write('TEST_STEP','Click ' + value)
                        event.touch(ele[0]-int(x), ele[1]-int(y))
                    if text.find(u'下载') != -1:
                        timeout = resource_config.getValue(uid,'download_timeout')
                        sleep(int(timeout))
                    else:
                        sleep(3)
    except Exception, ex:
        print ex


def unlock_screen(uid, dt):

    # actual screen size
    my_logger.write('TEST_STEP', 'Unlock Screen')
    uobj = ul.unlockScreen(uid)
    # reference_resolution
    res = dt['ref_resolution'].split(',')
    # start point
    if dt['start_point'] is not None and dt['start_point'] != '':
        start = dt['start_point'].split(',')
    else:
        start = [0,0]
    actu_start = uobj.convert_coordinate(int(start[0]),int(start[1]),int(res[0]),int(res[1]))
    # end point
    if dt['end_point'] is not None and dt['start_point'] != '':
        end = dt['end_point'].split(',')
    else:
        end = [0,0]
    actu_end = uobj.convert_coordinate(int(end[0]),int(end[1]),int(res[0]),int(res[1]))
    #unlock type
    utype = int(dt['unlock_type'])
    # distance
    if dt['distance'] is not None and dt['distance'] != '':
        distance = int(dt['distance'])
        if utype == 3 or utype == 4:
            distance = (distance * uobj.width)/int(res[0])
        else:
            distance = (distance * uobj.height)/int(res[1])
    else:
        distance = 0
    #duration
    if dt['duration'] is not None and dt['duration'] != '':
        duration = int(dt['duration'])
    else:
        duration = 200


    # unlock screen according to different type
    if utype == 4:
        uobj.right_slide(actu_start,actu_end,distance, duration)
    elif utype == 3:
        uobj.left_slide(actu_start,actu_end,distance, duration)
    elif utype == 2:
        uobj.down_slide(actu_start,actu_end,distance, duration)
    elif utype == 1:
        uobj.up_slide(actu_start,actu_end,distance, duration)
    else:
        uobj.other_slide(actu_start,actu_end,distance, duration)

    sleep(2)


def verify_animation(dt,sname,uid):

    loop = 0
    # verify loop image resource
    if dt['loop_flag'] != 0:
        my_logger.write('TEST_STEP', 'Verify different images')
        loop = int(dt['loop_numer'])
        for i in range(loop):
            my_device.screen_on_off('OFF')
            sleep(1)
            my_device.screen_on_off('ON')
            name = sname + '_' + str(i)
            save_screenshots(name)

    # Verify animation effect
    loop += 1
    action = dt['animation_action']
    desc = dt['animation_desc']
    if dt['animation_para'] is not None:
        location = dt['animation_para'].split(',')
    else:
        location = [0,0]
    if dt['animation_flag'] != 0:
        my_logger.write('TEST_STEP', 'Verify animation effect')
        my_logger.write('TEST_DEBUG', desc.encode('gbk'))
        try:
            threads = []
            proc_process = threading.Thread(target=save_animation_screenshot, args=(4, sname, loop))
            install_app = threading.Thread(target=screen_operation, args=(uid, action, 10, location))
            threads.append(install_app)
            threads.append(proc_process)
            for t in threads:
                t.setDaemon(True)
                t.start()
                sleep(1)
            t.join()
        except Exception, ex:
            pass
    sleep(2)


# duration unit is second
def screen_operation(uid, action, duration, location):

    #sleep
    if action == 4:
        sleep(duration)

    width, height = my_device.get_screen_size()
    # swipe
    if action == 3:
        loop = int(duration/3)
        for i in range(loop):
            cmd = "adb -s {0} shell input swipe {1} {2} {3} {4} {5}".format \
                    (uid,int(width/10),int(height/10*3),int(width/10),int(height/5*2), 500)
            my_device.shellPIPE(cmd)
            cmd = "adb -s {0} shell input swipe {1} {2} {3} {4} {5}".format \
                    (uid,int(width/10),int(height/5*2),int(width/10),int(height/10*3), 500)
            my_device.shellPIPE(cmd)
            sleep(2)
    # click
    if action == 1:
        loop = int(duration/0.5)
        if int(location[0]) == 0 and int(location[1]) == 0:
            x, y = width/10, height/10
        else:
            x, y = location[0], location[1]
        for i in range(loop):
            my_device.click_screen_by_coordinate(x, y)
            sleep(0.5)


def save_animation_screenshot(number, sname, loop):

    for i in range(number):
        sleep(2)
        name = sname + '_' + str(loop)
        save_screenshots(name)
        loop += 1



def save_screenshots(name):

    fname = os.path.join(logdir, name+'.png')
    my_device.get_device_screenshot(fname)
    temp = '<img src=\"' + fname + '\" width=120 height=200 />'
    my_logger.write('TEST_DEBUG','Actual Screen:'+ temp)

if __name__ == '__main__':

    global my_logger
    global my_device, logdir




    newParser = argparse.ArgumentParser()
    newParser.add_argument("-u", "--uid", dest="uid", help="Your device uid")

    args = newParser.parse_args()
    uid = args.uid

    if uid is None:
        sys.exit(0)

    # verify if device is connected
    devices = device.Device.get_connected_devices()
    if uid not in devices:
        print "Device is not connected, please check"
        sys.exit(0)

    my_device = device.Device(uid)
    logname = desktop.get_log_name(uid, 'resource','.html')
    logdir = os.path.abspath(os.path.dirname(logname))

    # create test log
    if not os.path.exists(logname):
        write_html_header(logname, 'Verify LockScreen Source')
    my_logger = log.Log(logname)

    # filter data

    vendor = resource_config.getValue(uid, 'vendor')
    datas = get_test_resource(vendor)
    try:
        for dt in datas:

            if dt['alias'] is not None and dt['alias'] != '':
                search_name = dt['alias'].encode('gbk')
            else:
                search_name = dt['name'].encode('gbk')

            my_logger.write('TEST_START','Start search source:' + search_name)

            # search resource in app
            set_resource_action(uid, 'search', search_name)
            # input resource name
            my_device.input_unicode_by_adb(search_name)
            sleep(15)
            # access to the next cycle
            my_logger.write('TEST_STEP','Set new resource')
            set_resource_action(uid, 'set', search_name)

            # return back HOME
            my_logger.write('TEST_STEP', 'Return back Home screen')
            for i in range(3):
                my_device.send_keyevent(4)
                sleep(1)
            my_device.send_keyevent(3)
            sleep(2)

            # use new resource and screen shots
            my_logger.write('TEST_STEP', 'Use new unlock')
            my_device.screen_on_off('OFF')
            sleep(1)
            my_device.screen_on_off('ON')
            save_screenshots(search_name)

            #animation effect verify
            verify_animation(dt, search_name,uid)

            #unlock screen and screenshots
            sleep(1)
            my_logger.write('TEST_STEP', 'Unlock Screen')
            unlock_screen(uid, dt)
            save_screenshots(search_name+'_unlock')
            cmd = "".join(["adb -s ", uid, " dumpsys activity activities"])
            out = my_device.shellPIPE(cmd)
            if out.find("Can't find service: activtiy:") != -1:
                my_logger.write('TEST_FAIL','Unlock screen is failed')
                break
            else:
                my_logger.write('TEST_PASS','Unlock screen is success')

            sleep(2)
    except Exception, ex:

        my_logger.write('TEST_WARN', 'Unlock screen is failed')









