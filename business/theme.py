#! /usr/bin/python
# -*- coding: utf-8 -*-

from time import sleep

from library import myuiautomator
from library.myglobal import theme_config
from library import adbtools
import threading

def click_text(dname,text):

    flag = False

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
        flag = True

    return flag


def set_device_theme(dname, theme_type, number=0):

    """
    SET theme accroding to configration theme path in advance
    :param dname: device uid
    :param theme_type:  VLIFE OR SYSTEM
    :return: NONE
    """

    # log in theme app like i theme
    activity_name = theme_config.getValue(dname,'set_theme_pkg')
    #DEVICE = device.Device(dname)
    #DEVICE.app_operation(action='LAUNCH', pkg=activity_name)
    DEVICE = adbtools.AdbTools(dname)
    #DEVICE.start_application(activity_name)
    find_text = [u'忽略本次']
    try:
        threads = []
        install_app = threading.Thread(target=DEVICE.start_application(), args=(activity_name,))
        proc_process = threading.Thread(target=DEVICE.do_popup_windows, args=(5, find_text))
        threads.append(proc_process)
        threads.append(install_app)
        for t in threads:
            t.setDaemon(True)
            t.start()
            sleep(2)
        t.join()
    except Exception, ex:
        print ex
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

    width, height = DEVICE.get_screen_normal_size()

    try:

        for text in vlife_theme_path:
            # try to swipe screen multiple times
            if text.startswith('NAME'):
                search_text = text.split('_')[1]
                for i in range(5):
                    result = click_text(dname, search_text)
                    if result:
                        break
                    else:
                        # swipe screen
                        cmd = 'input swipe {0} {1} {2} {3} 200'.format(int(width)/2, int(height)/2, int(width)/2, int(height)/2-300)
                        DEVICE.shell(cmd)
                        sleep(1)
            else:
                click_text(dname,text)

            # for i in range(3):
            #     x = 0
            #     y = 0
            #     element = myuiautomator.Element(dname)
            #     event = myuiautomator.Event(dname)
            #     if text.find(':') == -1:
            #         value = unicode(text)
            #     # because there is not 'click' action on text, so have to click next to element
            #     else:
            #         value = unicode(text.split(':')[0])
            #         x = text.split(':')[1]
            #         y = text.split(':')[2]
            #     ele = element.findElementByName(value)
            #     if ele is not None:
            #         event.touch(ele[0]-int(x), ele[1]-int(y))
            #         sleep(2)
            #         break
            #     else:
            #         # swipe screen
            #         cmd = 'input swipe {0} {1} {2} {3} 200'.format(int(width)/2, int(height)/2, int(width)/2, int(height)/2-300)
            #         DEVICE.shell(cmd)
            #         sleep(1)

    except Exception,ex:
        print ex
    # return to HOME
    for i in range(3):
        DEVICE.send_keyevent(4)


def theme_task_init_resource(dname, parameter):

    if parameter.upper() == 'SYSTEM':
        set_device_theme(dname,'SYSTEM')
    else:
        set_device_theme(dname,'VLIFE')
