#! /usr/bin/python
# -*- coding: utf-8 -*-

from time import sleep

from library import uiautomator
from library import device
from library.myglobal import magazine_config


def set_magazine_app_switch(dname,action):
    """
    set magazine wifi switch in app
    :param dname:  device name
    :param action:  on/off
    :return: None
    """
    DEVICE = device.Device(dname)
    activity_name = magazine_config.getValue(dname,'magazine_pkg')
    DEVICE.app_operation('START', service=activity_name)
    sleep(1)
    findstr = [u'开启',u'安装',u'允许',u'确定']
    DEVICE.do_popup_windows(6,findstr)

    # click setting button
    setting_path = magazine_config.getValue(dname,'magazine_wifi_switch').split('|')
    temp =  setting_path[0].split('::')
    location = temp[0]
    index = int(temp[1])

    # click setting button
    uiautomator.click_element_by_id(dname,location,index)
    sleep(1)

    # get current state of switch
    temp =  setting_path[1].split('::')
    location = temp[0]
    index = int(temp[1])
    state = uiautomator.get_element_attribute(dname,location,index,'checked')

    if action.upper() == 'ON' and state != 'true':
        uiautomator.click_element_by_id(dname,location,index)

    if action.upper() == 'OFF' and state == 'true':
        uiautomator.click_element_by_id(dname,location,index)

    DEVICE.do_popup_windows(2,[u'关闭'])
    sleep(1)
    #return back to HOME
    DEVICE.send_keyevent(4)
    sleep(3)
    DEVICE.send_keyevent(3)
    sleep(3)


def set_security_magazine_switch(dname,action):

    """
    set magazine lockscreen in setting page
    :param dname: device name
    :param action: on/off
    :return: NONE
    """

    # open set security UI
    DEVICE = device.Device(dname)
    value = magazine_config.getValue(dname,'security_setting')
    DEVICE.app_operation('LAUNCH', service=value)
    sleep(1)

     # click setting button
    setting_path = magazine_config.getValue(dname,'security_magazine_switch').split('::')
    location = setting_path[0]
    index = int(setting_path[1])

    # check current state
    state = uiautomator.get_element_attribute(dname,location,index,'checked')

    if action.upper() == 'ON' and state != 'true':
        uiautomator.click_element_by_id(dname,location,index)

    if action.upper() == 'OFF' and state == 'true':
        uiautomator.click_element_by_id(dname,location,index)

    #return back to HOME
    DEVICE.send_keyevent(3)


def magazine_task_init_resource(dname,parameter):

    if parameter.upper() == 'SYSTEM':
        set_security_magazine_switch(dname, 'OFF')
    else:
        set_security_magazine_switch(dname, 'ON')