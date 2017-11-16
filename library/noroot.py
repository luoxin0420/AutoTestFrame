#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Xuxh'

from library.myglobal import device_config
import device
import myuiautomator
from time import sleep


def set_wifi_connection(dname,action):

    # open set security UI
    DEVICE = device.Device(dname)
    DEVICE.app_operation('LAUNCH', pkg='com.android.settings/.Settings')
    sleep(5)

    # click WLAN
    element = myuiautomator.Element(dname)
    event = myuiautomator.Event(dname)
    try:
        ele = element.findElementByName("WLAN")
        if ele is not None:
            event.touch(ele[0], ele[1])
            sleep(2)
    except Exception,ex:
        print ex

     # click setting button
    setting_path = device_config.getValue(dname, 'wifi_setting').split('::')
    location = setting_path[0]
    index = int(setting_path[1])

    # Whether checked nor non_checked, attribute value are both 'false' on VIVO
    name = device_config.getValue(dname,'name')
    if name.upper().find('VIVO') != -1:
        element = myuiautomator.Element(dname)
        try:
            ele = element.findElementByName(u"选取网络")
            if ele is None:
                state = 'false'
            else:
                state = 'true'
        except Exception, ex:
            print ex
    else:
        # check current state
        state = myuiautomator.get_element_attribute(dname,location,index,'checked')

    if action.upper() == 'ON' and state != 'true':
        myuiautomator.click_element_by_id(dname,location,index)

    if action.upper() == 'OFF' and state == 'true':
        myuiautomator.click_element_by_id(dname,location,index)

    #return back to HOME
    DEVICE.send_keyevent(3)

if __name__ == '__main__':

    set_wifi_connection('329af263','on')