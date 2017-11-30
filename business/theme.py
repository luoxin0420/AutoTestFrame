#! /usr/bin/python
# -*- coding: utf-8 -*-

from time import sleep

from library import myuiautomator
from library import device
from library.myglobal import theme_config


def set_device_theme(dname, theme_type, number=0):

    """
    SET theme accroding to configration theme path in advance
    :param dname: device uid
    :param theme_type:  VLIFE OR SYSTEM
    :return: NONE
    """

    # log in theme app like i theme
    activity_name = theme_config.getValue(dname,'set_theme_pkg')
    DEVICE = device.Device(dname)
    DEVICE.app_operation(action='LAUNCH', pkg=activity_name)
    sleep(5)
    if number == 0:
        if theme_type.upper() == 'VLIFE':
            vlife_theme_path = theme_config.getValue(dname, 'vlife_theme_path').split('|')
        elif theme_type.upper() == 'SYSTEM':
            vlife_theme_path = theme_config.getValue(dname, 'system_theme_path').split('|')
        else:
            vlife_theme_path = theme_config.getValue(dname, 'third_party_theme_path').split('|')
    else:
        tag = 'vlife_theme_path_' + str(number)
        vlife_theme_path = theme_config.getValue(dname, tag).split('|')

    try:

        for text in vlife_theme_path:
            x = 0
            y = 0
            element = myuiautomator.Element(dname)
            event = myuiautomator.Event(dname)
            if text.find(':') == -1:
                value = unicode(text)
            # because there is not 'click' action on text, so have to click next to element
            else:
                value = unicode(text.split(':')[0])
                x = text.split(':')[1]
                y = text.split(':')[2]
            ele = element.findElementByName(value)
            if ele is not None:
                event.touch(ele[0]-int(x), ele[1]-int(y))
                sleep(2)
    except Exception,ex:
        print ex
    # return to HOME
    DEVICE.send_keyevent(3)


def theme_task_init_resource(dname, parameter):

    if parameter.upper() == 'SYSTEM':
        set_device_theme(dname,'SYSTEM')
    else:
        set_device_theme(dname,'VLIFE')
