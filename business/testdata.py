#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Xuxh'

import json
from library.myglobal import device_config
from library import logcat as dumplog
from business import querydb as tc


def handle_db_data(dbdata):
    new_data = {}
    for key, value in dbdata.items():

        if isinstance(value,unicode):
            new_data[key.encode('gbk')] = value.encode('gbk')
        else:
            new_data[key.encode('gbk')] = value

    values = new_data['teca_action_detail']
    dict_data = json.loads(values)

    business_order = tc.get_action_list(dbdata['teca_comp_id'])
    vp_type_name = tc.get_vp_type(new_data['teca_vp_type_id'])

    return new_data, dict_data, business_order, vp_type_name


def get_pid_by_vpname(dname, value):

    pid_list = []
    master_service = device_config.getValue(dname,'master_service')
    slave_service = device_config.getValue(dname,'slave_service') + ':main'

    try:
        if value.upper().find('DOUBLE') != -1:
            plist = [slave_service, master_service]
        elif value.upper().find('SYSTEMUI') != -1:
            plist = [master_service]
        elif value.upper().find('SYSTEM') != -1:
            plist = ['system_server']
        else:
            plist = [slave_service]

        for name in plist:
            pid = dumplog.DumpLogcatFileReader.get_PID(dname,name)
            if str(pid) > 0:
                pid[0] = pid[0].strip()
                pid_list.append(pid[0])
    except Exception,ex:
        #print 'canot get correlative PID'
        return []

    return pid_list