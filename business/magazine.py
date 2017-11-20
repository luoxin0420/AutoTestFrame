#! /usr/bin/python
# -*- coding: utf-8 -*-

from time import sleep

from library import myuiautomator
from library import device, adbtools
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
    DEVICE.app_operation('START', pkg=activity_name)
    sleep(5)
    # there are some popup windows when start-up app
    findstr = [u'开启', u'安装', u'允许', u'确定', u'同意']
    DEVICE.do_popup_windows(3, findstr)
    sleep(2)

    # access to setting screen of the third party of app
    setting_page = magazine_config.getValue(dname, 'activity_setting_page')
    if setting_page.upper() != 'NONE':
        DEVICE.app_operation('LAUNCH', setting_page)

    setting_path = magazine_config.getValue(dname, 'magazine_wifi_switch').split('|')
    action_flag = False
    for ind, value in enumerate(setting_path):
        ltype, location, index = value.split('::')
        # check if this is the last option of setting path
        if ind == len(setting_path)-1:
            state = myuiautomator.get_element_attribute(dname, value, int(index), 'checked')
            if (action.upper() == 'ON' and state != 'true') or (action.upper() == 'OFF' and state == 'true'):
                action_flag = True
        if ind < len(setting_path)-1 or action_flag:
            if ltype.upper() == 'CLASS':
                myuiautomator.click_element_by_class(dname, location, int(index))
            if ltype.upper() == 'ID':
                myuiautomator.click_element_by_id(dname, location, int(index))
            if ltype.upper() == 'NAME':
                myuiautomator.click_element_by_name(dname, location, int(index))

    DEVICE.do_popup_windows(2, [u'关闭',u'打开'])
    sleep(1)
    #return back to HOME
    DEVICE.send_keyevent(4)
    sleep(3)
    DEVICE.send_keyevent(3)
    sleep(3)


def set_security_magazine_switch(dname, action):

    """
    set magazine lockscreen in setting page
    :param dname: device name
    :param action: on/off
    :return: NONE
    """

    # open set security UI
    DEVICE = device.Device(dname)
    value = magazine_config.getValue(dname, 'security_setting')
    DEVICE.app_operation('LAUNCH', pkg=value)
    sleep(5)

     # click setting button
    setting_path = magazine_config.getValue(dname, 'security_magazine_switch').split('::')
    location = setting_path[0]
    index = int(setting_path[1])

    # check current state
    state = myuiautomator.get_element_attribute(dname, location, index, 'checked')

    if action.upper() == 'ON' and state != 'true':
        myuiautomator.click_element_by_id(dname, location, index)

    if action.upper() == 'OFF' and state == 'true':
        myuiautomator.click_element_by_id(dname, location, index)

    #return back to HOME
    DEVICE.send_keyevent(3)


def magazine_task_init_resource(dname, parameter):

    device = adbtools.AdbTools(dname)

    if parameter.upper() == 'SYSTEM':
        device.set_magazine_keyguard(False)
    else:
        #set_security_magazine_switch(dname, 'ON')
        device.set_magazine_keyguard(True)
        # start main process using start magazine apk or the third party app
        set_magazine_app_switch(dname, 'ON')
        # activity_name = magazine_config.getValue(dname, 'magazine_pkg')
        # device.start_application(activity_name)
        # sleep(1)
        # findstr = [u'开启', u'安装', u'允许', u'确定']
        # device.do_popup_windows(6, findstr)

if __name__ == '__main__':
    set_magazine_app_switch('8681-M02-0x718b3dff', 'ON')