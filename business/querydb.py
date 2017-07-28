#! /usr/bin/python
# -*- coding: utf-8 -*-

from library.myglobal import PATH
from library.db import dbmysql

autodb = dbmysql.MysqlDB(PATH('../config/dbconfig.ini'),'AUTOTEST')


def filter_cases(suite_id):

    """
    filter test cases according to test suite ID
    :param suite_id:
    :return: result list
    """
    query = 'select * from TestCase where teca_enable=1 and teca_id in (select tsca_teca_id from TestSuiteCase ' \
            'where tsca_tesu_id = {0} )'.format(suite_id)
    cases = autodb.select_many_record(query)
    return cases


def get_action_list(comp_id):

    """
    get component is mapping with action
    :param comp_id:
    :return:
    """

    action_list = []

    # query = 'select * from Component where comp_name like "{0}" '.format(comp_name)
    # result = autodb.select_one_record(query)
    # comp_id = result[0]['comp_id']

    query = 'select * from ActionGroup where acgr_comp_id={0} order by acgr_index'.format(comp_id)
    result = autodb.select_many_record(query)

    for re in result:

        actid = re['acgr_acti_id']
        query = 'select * from Action where acti_id={0}'.format(actid)
        result = autodb.select_one_record(query)
        action_list.append(result[0]['acti_name'])

    return action_list


def get_vp_name(vp_id):

    """
    get vp name according to id
    :param vp_id:
    :return:
    """

    query = 'select * from VPName where vp_id={0} '.format(vp_id)
    result = autodb.select_one_record(query)
    vp_name = result[0]['vp_name']
    return vp_name


def get_vp_type(vpt_id):

    """
    get vp type according to id
    :param vp_id:
    :return:
    """

    query = 'select * from VPType where vpt_id={0} '.format(vpt_id)
    result = autodb.select_one_record(query)
    vpt_name = result[0]['vpt_name']
    return vpt_name


def get_prodcut_name_byID(pid):

    """
    get product name according to pid
    :param pid:
    :return:
    """

    query = 'select prod_name from Product where prod_id={0}'.format(pid)
    result = autodb.select_one_record(query)
    pname = result[0]['prod_name']
    return pname
