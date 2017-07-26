#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import time


from library import html
from library import stropt
from library.myglobal import logger


def enableModule(config_file, sname):

    config_file = r'E:\AutoTestDemo\config\htmlconfig.ini'
    sname = 'STAGECONFIG'
    htmlObj = html.MyHttp(config_file, sname)

    url = '/clearapi.do?'

    # combine all parameters

    project = 'vlife'
    version = 'major'
    t = str(int(time.time()) * 1000)
    t1 = '1500878198000'
    component = ['interactive','adcenter']
    username = 'auto_test'

    for comp in component:

        temp = '-'.join([project,comp,'paper',project,t])
        md = stropt.get_md5(temp)
        paras = '&'.join(['component='+comp,'project='+project,'t='+t,'check='+ md, 'from='+username,'user='+username,'version='+version])
        logger.debug('Read for enable module')
        res = htmlObj.get(url,paras)
        if json.loads(res[0]).get('result', '') == 'success':
            logger.info('Enable module is passed for ' + comp)
        else:
            logger.error('Enable module is not failed ' + comp)

if __name__ == '__main__':

    enableModule('test','test')

