#! /usr/bin/python
# -*- coding: utf-8 -*-

from time import sleep

from library import device
from library.myglobal import logger,device_config
from business import magazine,theme
from NeoPySwitch import PySwitch,SwitchCase


class DeviceAction(object):

    """
    main operation on mobile
    """

    def __init__(self,dname):
        
        self.device = device.Device(dname)
        self.dname = dname
        self.pname = device_config.getValue(dname,'product_type')

    def network_change(self,operation):

        """

        :param operation:
        :return:
        """

        logger.debug('Step: network change:' + operation)

        switcher = {
            'OPEN_ALL': 'ON:ON',
            'ONLY_WIFI': 'ON:OFF',
            'ONLY_GPRS': 'OFF:ON',
            'CLOSE_ALL': 'OFF:OFF'
        }

        value = operation.upper()
        action = switcher.get(value,'ON:ON').split(':')
        self.device.wifi_operation(action[0])
        sleep(5)
        self.device.gprs_operation(action[1])
        sleep(5)

    def update_time(self, value):

        """

        :param value:
        :return:
        """
        # make sure previous action is completed, maybe date update is failed (block), so add extra time to wait
        sleep(3)
        logger.debug('Step:update time:' + value)
        unit,num = value.split('-')
        if int(num) != 0:
            self.device.update_android_time(num,interval_unit=unit)
            sleep(3)
            logger.debug('Step:update time is success')
        else:
            logger.debug('Step:skip update time')

    def start_app(self,type,pkg_name):

        """

        :param type:
        :param pkg_name:
        :return:
        """

        logger.debug('Step:start_app')
        if type == 'magazine':
            self.device.app_operation('START', pkg=pkg_name)
            sleep(5)
        elif type == 'theme':
            theme.set_device_theme(self.dname, 'vlife')
        elif type == 'wallpaper':
            pass
        else:
            pass

    def close_app(self,type,pkg_name):

        """

        :param type:
        :param pkg_name:
        :return:
        """
    
        if type == 'magazine':
            self.device.app_operation('CLOSE',pkg=pkg_name)
            sleep(5)

    def clear_app(self,type,pkg_name):

        """

        :param type:
        :param pkg_name:
        :return:
        """
        logger.debug('Step: clear app')
        if type == 'magazine':
            self.device.app_operation('CLEAR', pkg=pkg_name)
            self.device.app_operation('CLEAR', pkg='com.android.systemui')
            sleep(5)

    def unlock_screen(self):

        """
        unlock screen
        :return:
        """
        logger.debug('Step:unlock screen')
        # sometimes device start up is very slowly, so will try multiple times
        names = []
        for i in range(5):
            names = self.device.get_connected_devices()
            if self.dname in names:
                self.device.screen_on_off("OFF")
                sleep(2)
                self.device.screen_on_off("ON")
                sleep(2)
                self.device.emulate_swipe_action()
                break
            else:
                sleep(5)

    def screen_on(self,value):

        """
        make screen lighten or off
        :return:
        """
        logger.debug('Step:screen ' + value)
        self.device.screen_on_off(value)
        sleep(3)

    def reboot_device(self):

        """

        :return:
        """
        logger.debug('Step:reboot device')
        self.device.device_reboot()
        sleep(25)


    def update_para(self,value):

        """

        :param value:
        :return:
        """
        logger.debug('Step:update parameter file ' + value)
        if value.upper() == 'PUSH_MESS_FREQ':
            pass

    def install_app(self,pkg_name):

        """

        :return:
        """
        logger.debug('Step:install new app ' + pkg_name)
        pass

    def access_other_app(self,value):

        """
        open some app according to package and activity name from configuration file,
        :param value:
        :return:
        """
        logger.debug('Step:open other app')
        # open app, then return back home screen
        if value.lower() == 'android_system_app':
            pkg_name = device_config.getValue(self.dname,'android_system_app')
            self.device.app_operation('LAUNCH', pkg=pkg_name)
            logger.debug('Step: launch app ' + pkg_name)
        elif value.lower() == 'custom_third_app':
            pkg_name = device_config.getValue(self.dname,'custom_third_app')
            self.device.app_operation('LAUNCH',pkg_name)
            logger.debug('Step: launch app ' + pkg_name)
        else:
             logger.debug('Step: skip accessing the third app')

        sleep(3)
        # return back home
        self.device.send_keyevent(3)
        sleep(1)

    def task_init_resource(self,value):

        """

        :param pid:
        :param value:
        :return:
        """

        if self.pname == 'magazine':
            logger.debug('Step: set resource for magazine')
            magazine.magazine_task_init_resource(self.dname,value)
        elif self.pname == 'theme':
            logger.debug('Step: set resource for theme')
            theme.theme_task_init_resource(self.dname,value)
        elif self.pname == 'wallpaper':
            logger.debug('Step: set resource for wallpaper')
            pass
        elif self.pname == 'theme_wallpaper':
            logger.debug('Step: set resource for theme_wallpaper')
            pass
        else:
            logger.error('Unknown product type')
        sleep(2)

    def do_nothing(self):

        print 'do nothing'


def execute_device_action(da, act_name,value):

    """
    execute different device actions according to action name
    :param act_name:
    :param value:
    :return:
    """


    ret = PySwitch(act_name, {
        'network': da.network_change(value),
        'update_date': da.update_time(value),
        'reboot': da.reboot_device(),
        'unlock_screen': da.unlock_screen(),
        'update_para': da.unlock_screen(),
        'install_app': da.install_app(value),
        'task_init_source': da.task_init_resource(value),
        'screen_on': da.screen_on(value)
        }, da.do_nothing())

    print ret