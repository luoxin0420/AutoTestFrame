#! /usr/bin/python
# -*- coding: utf-8 -*-

from time import sleep
import os
import sys
from library import device
from library.myglobal import device_config

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


def common_init_env(dname):

    DEVICE = device.Device(dname)
    file_list = device_config.getValue(dname,'pushfile').split(';')
    try:
        for fname in file_list:
            orgi,dest = fname.split(':')
            orgi = PATH('../external/' + dname + '/' + orgi)
            if os.path.isfile(orgi):
                DEVICE.device_file_operation('push',orgi,dest)
    except Exception, ex:
        print ex
        print "initial environment is failed"
        sys.exit(0)

def init_env(dname, ptype):

    common_init_env(dname)
    pass