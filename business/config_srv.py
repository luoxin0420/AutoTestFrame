#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import time


from library import html
from library import stropt
from library.myglobal import logger,html_config


def enableModule(sname):

    htmlObj = html.MyHttp(html_config, sname)

    url = '/clearapi.do?'

    # combine all parameters

    project = 'vlife'
    version = 'major'
    t = str(int(time.time()) * 1000)
    t1 = '1500878198000'
    # first two items for module download.'adcenter, cloud-upgrade for operation module upgrade'
    component = ['cm', 'adcenter', 'cloud-upgrade']
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
    # need wait for 5 minutes and enable validate on side
    logger.debug('Have to wait for 3 minutes server take effect')
    time.sleep(180)

if __name__ == '__main__':

    enableModule('test','test')

