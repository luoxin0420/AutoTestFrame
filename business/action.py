#! /usr/bin/python
# -*- coding: utf-8 -*-

from time import sleep
from library import device

from library.myglobal import logger
from business import magazine,theme
from business import querydb as tc


class DeviceAction(object):

    """
    main operation on mobile
    """
    
    def __init__(self,dname):
        
        self.device = device.Device(dname)
        self.dname = dname

    def network_change(self,operation):

        """

        :param operation:
        :return:
        """

        logger.debug('Step: network change:' + operation)
    
        if operation.upper() == 'CLOSE_ALL':
            self.device.wifi_operation('OFF')
            sleep(2)
            self.device.gprs_operation('OFF')
            sleep(2)
    
        if operation.upper() == 'OPEN_ALL':
            self.device.wifi_operation('ON')
            sleep(2)
            self.device.gprs_operation('ON')
            sleep(2)
    
        if operation.upper() == 'ONLY_GPRS':
            self.device.wifi_operation('OFF')
            sleep(2)
            self.device.gprs_operation('ON')
            sleep(2)
    
        if operation.upper() == 'ONLY_WIFI':
            self.device.wifi_operation('ON')
            sleep(2)
            self.device.gprs_operation('OFF')
            sleep(2)

    def update_time(self, value):

        """

        :param value:
        :return:
        """
    
        logger.debug('Step:update time:' + value)
        unit,num = value.split('-')
        self.device.update_android_time(num,interval_unit=unit)
        sleep(3)
        logger.debug('Step:update time is success')
    
    def start_app(self,type,pkg_name):

        """

        :param type:
        :param pkg_name:
        :return:
        """
    
        if type == 'magazine':
            self.device.app_operation('START', service=pkg_name)
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
            self.device.app_operation('CLOSE', service=pkg_name)
            sleep(5)
    
    def clear_app(self,type,pkg_name):

        """

        :param type:
        :param pkg_name:
        :return:
        """
    
        if type == 'magazine':
            self.device.app_operation('CLEAR', service=self.pkg_name)
            self.device.app_operation('CLEAR', service='com.android.systemui')
            sleep(5)

    def task_init_resource(self,pid,value):

        """

        :param pid:
        :param value:
        :return:
        """

        pname = tc.get_prodcut_name_byID(pid)

        if pname == 'magazine':
            logger.debug('Step: set resource for magazine')
            magazine.magazine_task_init_resource(self.dname,value)
        elif pname == 'theme':
            logger.debug('Step: set resource for theme')
            theme.theme_task_init_resource(self.dname,value)
        elif pname == 'wallpaper':
            logger.debug('Step: set resource for wallpaper')
            pass
        elif pname == 'theme_wallpaper':
            logger.debug('Step: set resource for theme_wallpaper')
            pass
        else:
            logger.error('Unknown product type')