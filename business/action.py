#! /usr/bin/python
# -*- coding: utf-8 -*-

from time import sleep
import os
import re
import threading

from library import device
from library.myglobal import logger,  device_config, PATH
from business import magazine, theme, config_srv, wallpaper
# from NeoPySwitch import PySwitch,SwitchCase
from business import querydb as tc
from business import testdata as td


class DeviceAction(object):

    """
    main operation on mobile
    """

    def __init__(self,dname):
        
        self.device = device.Device(dname)
        self.dname = dname
        self.pname = device_config.getValue(dname, 'product_type')
        self.pkg = device_config.getValue(dname, 'slave_service')
        self.func_dict = {'network': self.network_change,
                          'clear_app': self.clear_app,
                          'access_other_app': self.access_other_app,
                          'click_screen': self.click_screen,
                          'close_app': self.close_app,
                          'close_backend_tasks': self.close_backend_tasks,
                          'connect_network_trigger': self.connect_network_trigger,
                          'install_app': self.install_app,
                          'module_effective': self.module_effective,
                          'reboot': self.reboot_device,
                          'screen_on': self.screen_on,
                          'start_app': self.start_app,
                          'task_init_source': self.task_init_resource,
                          'unlock_screen': self.unlock_screen,
                          'update_para': self.update_para,
                          'update_date': self.update_time,
                          'sdcard_action': self.sdcard_action,
                          'third_app_operation': self.install_third_app,
                          'kill_process': self.kill_process,
                          'SrvConfig_Switch': self.set_srvcon_switch,
                          'SrvConfig_Push_Interval': self.set_srvcon_Interval}

    def set_srvcon_switch(self, value):

        if value.upper() != 'NONE':

            logger.debug('Step: set switch' + str(value))

            stype, action = value.split(':')
            rule_id = device_config.getValue(self.dname, 'background_rule_id')

            # update database
            tc.update_switch(rule_id,stype,action)
            config_srv.enableModule('STAGECONFIG')

    def set_srvcon_Interval(self,value):

        if value != 0:

            logger.debug('Step: set push interval in server side:' + str(value))
            rule_id = device_config.getValue(self.dname, 'background_rule_id')

            # update database
            tc.update_push_interval(rule_id, value)
            config_srv.enableModule('STAGECONFIG')

    def install_third_app(self, operation):

        logger.debug('Step: install APP:' + operation)
        find_text = [u"安装", u"允许"]
        try:
            threads = []
            install_app = threading.Thread(target=self.third_app_operation, args=(operation,))
            proc_process = threading.Thread(target=self.device.do_popup_windows, args=(5, find_text))
            threads.append(proc_process)
            threads.append(install_app)
            for t in threads:
                t.setDaemon(True)
                t.start()
                sleep(3)
            t.join()
        except Exception, ex:
            pass

    # default third party of app is com.vlife.qateam.advhelp
    def third_app_operation(self, operation):

        if operation.upper() != 'NONE':
            app_path = PATH(PATH('../external/' + 'advhelp.apk'))
            self.device.install_app_from_desktop('INSTALL',app_path)
            pkg_name = device_config.getValue(self.dname,'custom_third_app').split('/')[0]
            out = self.device.find_package(pkg_name)
            if out.find(pkg_name) != -1:
                find_flag = True
            else:
                find_flag = False
            if operation.upper() == 'FIRST_INSTALL':
                logger.debug('Install the third party of APP')
                if find_flag:
                    self.device.app_operation('CLEAR', pkg=pkg_name)
                self.device.install_app_from_desktop('INSTALL')
            if operation.upper() == 'COVER_INSTALL':
                logger.debug('Cover install the third party of APP')
                if not find_flag:
                    self.device.install_app_from_desktop('INSTALL')
                self.device.install_app_from_desktop('COVER_INSTALL')
            if operation.upper() == 'UNINSTALL':
                logger.debug('Uninstall the third party of APP')
                if find_flag:
                    self.device.app_operation('UNINSTALL', pkg=pkg_name)

    def choose(self, act, value):
        return self.func_dict[act](value)

    def network_change(self, operation):

        """

        :param operation:
        :return:
        """

        logger.debug('Step: network change:' + operation)

        if operation.upper() != 'NONE':
            switcher = {
                'OPEN_ALL': 'ON:ON',
                'ONLY_WIFI': 'ON:OFF',
                'ONLY_GPRS': 'OFF:ON',
                'CLOSE_ALL': 'OFF:OFF'
            }

            value = operation.upper()
            action = switcher.get(value,  'ON:ON').split(':')
            self.device.wifi_operation(action[0])
            sleep(5)
            self.device.gprs_operation(action[1])
            sleep(5)

    def sdcard_action(self,value):

        pass

    def update_time(self, value):

        """

        :param value:
        :return:
        """
        if value.upper() != 'NONE':
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

    def start_app(self, value):

        """
        :return:
        """
        if value.upper() != 'NONE':
            logger.debug('Step:start_app')
            if self.pname.upper() == 'MAGAZINE':
                self.device.app_operation('START', pkg=self.pkg)
                sleep(5)
            elif self.pname.upper() == 'THEME':
                theme.set_device_theme(self.dname, 'vlife')
            elif self.pname.upper() == 'WALLPAPER':
                pass
            else:
                pass

    def close_app(self, value):

        """
        :return:
        """
        if value.upper() != 'NONE':
            if self.pname == 'MAGAZINE' or self.pname.upper() == 'THEME':
                self.device.app_operation('CLOSE', pkg=self.pkg)
                sleep(5)

    def clear_app(self, value):

        """
        :return:
        """
        if value.upper() != 'NONE':
            logger.debug('Step: clear app')
            self.device.app_operation('CLEAR', pkg=self.pkg)
            self.device.app_operation('CLEAR', pkg='com.android.systemui')
            sleep(5)

    def unlock_screen(self, value):

        """
        :param value:
        :return:
        """
        if value.upper() == 'NONE':
            print 'do nothing'
        elif value.upper() == 'DEFAULT':
            logger.debug('Step:unlock screen')
            # sometimes device start up is very slowly, so will try multiple times
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
        else:
            # redo unlock action multiple times
            logger.debug('Step:unlock screen')
            for i in range(int(value)):
                self.device.screen_on_off("OFF")
                sleep(2)
                self.device.screen_on_off("ON")
                sleep(2)
                self.device.emulate_swipe_action()
                sleep(5)

    def screen_on(self, value):

        """
        make screen lighten or off
        :return:
        """
        value = value.encode('gbk')
        if value.upper != 'NONE':
            logger.debug('Step:screen ' + value)
            temp = value.split(':')
            if len(temp) > 1:
                loop = int(temp[1])
            else:
                loop = 1
            for i in range(loop):
                for vl in temp[0].split('-'):
                    self.device.screen_on_off(vl)
                    sleep(3)

    def reboot_device(self, value):

        """

        :return:
        """
        if value.upper() != 'NONE':
            logger.debug('Step:reboot device')
            self.device.device_reboot()
            sleep(30)

    def click_screen(self, value):

        """

        :param value:
        :return:
        """

        if self.pname == 'magazine' and value.upper() != 'NONE':

            ts,location = value.split('-')
            loc_list = location.split(',')

            for i in range(int(ts)/len(loc_list)):

                for lc in loc_list:
                    x, y = lc.split(':')
                    self.device.click_screen_by_coordinate(x,y)
                    sleep(0.5)

    def close_backend_tasks(self,value):

        """

        :param value:
        :return:
        """
        self.network_change('CLOSE_ALL')

    def connect_network_trigger(self, value):

        logger.debug('Step: connect network by change of network status ' + value)

        if value.upper() != 'NONE':

            actions = value.split(':')

            self.network_change(actions[0])
            self.update_time('hour-7')
            sleep(15)
            self.network_change(actions[1])

    def kill_process(self, value):

        logger.debug('Step: kill process:' + value)
        if value.upper() != 'NONE':
            if value.upper() == 'MAIN':
                pid = td.get_pid_by_vpname(self.dname,'MAIN')
                self.device.device_kill_pid(pid)

    def update_para(self, value):

        """
        :param value:
        :return:
        """
        logger.debug('Step:update parameter file ' + value)
        pkg_name = device_config.getValue(self.dname,'slave_service')
        file_path = ''.join(['/data/data/', pkg_name, '/shared_prefs/'])
        if value.upper() == 'PUSH_MESS_FREQ':
            full_name = os.path.join(file_path,'push_message.xml')
            out = self.device.read_file_from_device(full_name)
            out = out.replace('\r\n','')
            keyword = r'.*value="(.*)".*'
            content = re.compile(keyword)
            m = content.match(out)
            if m:
                actu_freq = m.group(1)
            else:
                actu_freq = ''
            expe_freq = device_config.getValue(self.dname,'push_message_frequent')

            if expe_freq != actu_freq:

                reg_str = ''.join(["'",'s/','"',actu_freq,'"/','"',expe_freq,'"/g ',"'"])
                self.device.update_file_from_device(reg_str,full_name)

    def install_app(self, value):

        """
        :return:
        """
        if value.upper() != 'NONE':
            logger.debug('Step:install new app ' + self.pkg)
            pass

    def access_other_app(self, value):

        """
        open some app according to package and activity name from configuration file,
        :param value:
        :return:
        """
        if value.upper() != 'NONE':
            logger.debug('Step:open other app')
            # open app, then return back home screen
            if value.lower() == 'android_system_app':
                pkg_name = device_config.getValue(self.dname, 'android_system_app')
                self.device.app_operation('LAUNCH', pkg=pkg_name)
                logger.debug('Step: launch app ' + pkg_name)
            elif value.lower() == 'custom_third_app':
                pkg_name = device_config.getValue(self.dname, 'custom_third_app')
                self.device.app_operation('LAUNCH', pkg=pkg_name)
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
        if value.upper() != 'NONE':
            if self.pname.lower() == 'magazine':
                logger.debug('Step: set resource for magazine')
                magazine.magazine_task_init_resource(self.dname,value)
            elif self.pname.lower() == 'theme':
                logger.debug('Step: set resource for theme')
                theme.theme_task_init_resource(self.dname,value)
            elif self.pname.lower() == 'wallpaper':
                logger.debug('Step: set resource for wallpaper')
                wallpaper.wallpaper_task_init_resource(self.dname,value)
                pass
            elif self.pname.lower() == 'theme_wallpaper':
                logger.debug('Step: set resource for theme_wallpaper')
                pass
            else:
                logger.error('Unknown product type')
            sleep(2)

    def module_effective(self, value):

        if value.upper() != 'NONE':
            logger.debug('Step: update database and make module effective')
            flag = tc.update_stage_module_network(self.dname, value)
            if flag:
                config_srv.enableModule('STAGECONFIG')
            else:
                logger.debug('Data of DB is fit for test requirement')





# def execute_device_action(da, act_name,value):
#
#     """
#     execute different device actions according to action name
#     :param act_name:
#     :param value:
#     :return:
#     """
#
#     ret = PySwitch(act_name, {
#         'network': da.network_change(value),
#         'update_date': da.update_time(value),
#         'reboot': da.reboot_device(),
#         'unlock_screen': da.unlock_screen(),
#         'update_para': da.unlock_screen(),
#         'install_app': da.install_app(value),
#         'task_init_source': da.task_init_resource(value),
#         'screen_on': da.screen_on(value)
#         }, da.do_nothing())
#
#     print ret

if __name__ == '__main__':

    mydevice = DeviceAction('ZX1G22TG4F')
    mydevice.choose('third_app_operation', 'FIRST_INSTALL')
