#! /usr/bin/python
# -*- coding: utf-8 -*-

from time import sleep

from library import myuiautomator
from library import device
from library.myglobal import wallpaper_config


def set_device_wallpaper(dname, theme_type):

    """
    SET wallpaper accroding to configration theme path in advance
    :param dname: device uid
    :param wallpaper_type:  VLIFE OR SYSTEM
    :return: NONE
    """

    # log in theme app like i theme
    DEVICE = device.Device(dname)
    if theme_type.upper() == 'VLIFE':
        activity_name = wallpaper_config.getValue(dname,'set_vlife_wallpaper_pkg')
        DEVICE.app_operation(action='LAUNCH', pkg=activity_name)
        sleep(2)
        vlife_path = wallpaper_config.getValue(dname,'vlife_wallpaper_path').split('|')
    else:
        activity_name = wallpaper_config.getValue(dname,'set_system_wallpaper_pkg')
        DEVICE.app_operation(action='LAUNCH', pkg=activity_name)
        sleep(2)
        vlife_path = wallpaper_config.getValue(dname,'system_wallpaper_path').split('|')
    element = myuiautomator.Element(dname)
    event = myuiautomator.Event(dname)

    for text in vlife_path:
        x = 0
        y = 0
        if text.find(':') == -1:
            value = unicode(text)
        # because there is not 'click' action on text, so have to click next to element
        else:
            value = unicode(text.split(':')[0])
            x = text.split(':')[1]
            y = text.split(':')[2]
        # There is no name for some component
        if value == u'坐标':
            event.touch(int(x), int(y))
        else:
            ele = element.findElementByName(value)
            if ele is not None:
                event.touch(abs(ele[0]-int(x)), abs(ele[1]-int(y)))
                sleep(2)
    # return to HOME
    DEVICE.send_keyevent(3)


def wallpaper_task_init_resource(dname, parameter):

    if parameter.upper() == 'SYSTEM':
        set_device_wallpaper(dname,'SYSTEM')
    else:
        set_device_wallpaper(dname,'VLIFE')

