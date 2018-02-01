#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'xuxh'

import os
import re
from time import sleep
import subprocess
import argparse
import sys

from library import adbtools
from library.myglobal import device_config,module_config, logger
from library import desktop
from business import action
from business import theme
from business import querydb as tc
from business import config_srv
from library import logcat as dumplog
from library import pXml


def filter_log_result(logname, findstr, pid):

    find_content = ''

    with open(logname,'rb') as reader:
        for line in reader:
            # remove redundance space
            line = ' '.join(filter(lambda x: x, line.split(' ')))
            values = line.split(' ')
            # values[6:] is text column
            try:
                text = ' '.join(values[6:])
                if values[2] == pid:
                    if text.find(findstr) != -1:
                        #keyword =r'.*(<query.*/query>).*'
                        keyword = r'.*(<product.*/product>).*'
                        content = re.compile(keyword)
                        m = content.match(text)
                        if m:
                            find_content = ':::'.join(([str(values[2]),m.group(1)]))
                            break
            except Exception, ex:
                print ex
                continue
    return find_content


def verify_pkg_content(loginfo, exp_value):

    try:
        if len(loginfo) > 0:
            data = pXml.parseXml(loginfo.split(':::')[1])
            value = data.get_elements_attribute_value('product', 'soft')[0]

            temp = exp_value.encode('utf-8').split('.')
            length = len(temp)
            temp = '.'.join(temp[0:length-1])

            if value == temp:
                return True
            else:
                return False
    except Exception, ex:
        print ex

    return False


def delete_files_from_device():

    # delete apk file
    logger.debug('step: delete old apk file')
    del_path = module_config.getValue('SHELL_MODULE', 'push_apk_path')
    del_path = os.path.join(del_path, '*.apk')
    device.remove(del_path)

    # delete so file
    logger.debug('step: delete old so file')
    del_path = module_config.getValue('SHELL_MODULE', 'push_so_path')
    del_path = os.path.join(del_path, 'libvlife_*.so')
    device.remove(del_path)


def get_full_name(file_path,suffix):

    file_list = []
    for dirpath, dirnames, filenames in os.walk(file_path):
        for file in filenames:
            temp = os.path.splitext(file)[1]
            if suffix == temp:
                fullpath=os.path.join(dirpath,file)
                file_list.append(fullpath)

    return file_list


def collect_log(uid):

    da = action.DeviceAction(uid)
    logger.debug('Reboot device and unlock screen')
    da.reboot_device('default')
    da.unlock_screen('default')
    # get root
    device.adb('root')
    device.adb('remount')
    for i in range(2):
        da.connect_network_trigger('CLOSE_ALL:ONLY_WIFI')
    # start collect log
    name = desktop.get_log_name(uid, 'SmokeModule')
    log_reader = dumplog.DumpLogcatFileReader(name, uid)
    log_reader.clear_logcat()
    log_reader.start()
    logger.debug('step: connect network and download module')
    for i in range(2):
        da.connect_network_trigger('CLOSE_ALL:ONLY_WIFI')
    sleep(10)
    log_reader.stop()
    return name


def install_new_shell(shell_path, pkg_name, soft_version, uid):

    # cover install
    logger.debug('Cover install new shell')
    files = get_full_name(shell_path, '.apk')
    device.adb('install -r ' + files[0])

    # collect log
    name = collect_log(uid)
    # get pid of app
    pkg_pid = device.get_pid(pkg_name)
    #check log for login package and verify if module update
    loginfo = filter_log_result(name, 'jabber:iq:auth', pkg_pid)
    result = verify_pkg_content(loginfo, soft_version)

    return result


def init_module_version(uid, orig_path):

    # get root
    device.adb('root')
    device.adb('remount')

    # delete files
    delete_files_from_device()

    # clear app
    pkg_name = module_config.getValue('SHELL_MODULE', 'pkg_name')
    logger.debug('step: clear pkg content ' + pkg_name)
    device.clear_app_data(pkg_name)
    logger.debug('step: clear system ui')
    device.clear_app_data('com.android.systemui')

    # push new api file
    apk_path = module_config.getValue('SHELL_MODULE', 'push_apk_path')
    so_path = module_config.getValue('SHELL_MODULE', 'push_so_path')
    logger.debug('step: push apk file to device')
    files = get_full_name(orig_path, '.apk')
    device.push(files[0], apk_path)
    desktop_path = os.path.join(orig_path, 'so')
    files = get_full_name(desktop_path, '.so')
    logger.debug('step: push so files to device')
    for fl in files:
        device.push(fl, so_path)

    #########################################################################
    # # reboot and unlock screen
    da = action.DeviceAction(uid)
    logger.debug('step: reboot device and unlock screen')
    da.reboot_device('default')
    da.unlock_screen('default')

    # set root permission before reboot
    device.adb('root')
    device.adb('remount')

    # self-activation
    pkg_name = module_config.getValue('SHELL_MODULE', 'pkg_name')
    acti_flag = module_config.getValue('SHELL_MODULE', 'self_activation')
    product_type = device_config.getValue(uid, 'product_type')
    if acti_flag.upper() == 'FALSE':
        logger.debug('step: access to vlife theme, start-up main process')
        if product_type.upper() == 'THEME':
            theme.set_device_theme(uid, 'vlife')

    # configure server option

    mid = module_config.getValue('SHELL_MODULE', 'module_id')
    count = 0
    try:

        logger.debug('step: config server and enable module ')
        tc.update_stage_module_status(int(mid), True)
        flag1 = tc.update_stage_module_network(int(mid), 1, 0)
        flag2 = tc.check_amount_limit(int(mid))
        if flag1 or flag2:
            config_srv.enableModule('STAGECONFIG')
        #connect network and waiting for module download
        logger.debug('step: connect network and download module')
        for i in range(2):
            da.connect_network_trigger('CLOSE_ALL:ONLY_WIFI')

        #check module has download

        config_dict = {"module": mid}
        result = tc.get_all_module_info(config_dict)
        search_path = result['module']['path']
        soft_version = result['module']['version']
        full_path= os.path.join(r'/data/data/', pkg_name, os.path.dirname(search_path)).replace('\\', '/')
        base_name = os.path.basename(search_path)
        res = device.find_file_from_appfolder(pkg_name, full_path)

        if res.find(base_name) != -1:
            logger.debug('step: module is download successfully, ' + search_path + ' has found')
            # reboot and unlock screen for applying module
            name = collect_log(uid)
            # get pid of app
            pkg_pid = device.get_pid(pkg_name)
            #check log for login package and verify if module update
            loginfo = filter_log_result(name, 'jabber:iq:auth', pkg_pid)
            init_result = verify_pkg_content(loginfo, soft_version)

            if init_result:
                logger.debug('step: module is made effect for ' + str(mid))
                # test basic func
                sid = module_config.getValue('COMMON', 'basic_fun_suite_id')
                cmd = ' '.join(['run', uid, str(sid)])
                subprocess.Popen(cmd, shell=True, stdout=None)

                # test new shell for upgrade
                shell_paths = module_config.getValue('SHELL_MODULE', 'upgrade_shell_path').split(';')
                for tp in shell_paths:
                    result = install_new_shell(tp, pkg_name, soft_version, uid)
                    if result:
                        device.clear_app_data(pkg_name)
                        device.clear_app_data('com.android.systemui')
                        device.uninstall(pkg_name)
            else:
                logger.error('step: module is not downloaded successfully')

    except Exception, ex:
        print ex


if __name__ == '__main__':

    global device

    newParser = argparse.ArgumentParser()
    newParser.add_argument("uid", help="Your device uid")
    args = newParser.parse_args()
    uid = args.uid
    if uid is None:
        sys.exit(0)

    device = adbtools.AdbTools(uid)
    # verify if device is connected
    devices = device.get_devices()
    if uid not in devices:
        print "Device is not connected, please check"
        sys.exit(0)
    test_paths = module_config.getValue('SHELL_MODULE', 'orig_shell_path').split(';')
    for tp in test_paths:
        init_module_version(uid, tp)
        # delete files
        delete_files_from_device()

