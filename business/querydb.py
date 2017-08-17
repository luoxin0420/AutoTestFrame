#! /usr/bin/python
# -*- coding: utf-8 -*-

from library.myglobal import PATH,device_config
from library.db import dbmysql

autodb = dbmysql.MysqlDB(PATH('../config/dbconfig.ini'),'AUTOTEST')
stagedb = dbmysql.MysqlDB(PATH('../config/dbconfig.ini'),'STAGE')


def filter_cases(suite_id, comp_list):

    """
    filter test cases according to test suite ID
    :param suite_id:
    :return: result list
    """
    comp = []
    for cn in comp_list:
        query = 'select * from TestCaseManage_component where comp_name="{0}" '.format(cn)
        result = autodb.select_one_record(query)
        temp = result[0]['comp_id']
        comp.append(str(temp))
    compstr = ','.join(comp)

    query = 'select * from TestCaseManage_testcase where teca_enable=1 and teca_comp_id in ({0}) and teca_id in (select tsca_teca_id from TestCaseManage_testsuitecase ' \
            'where tsca_tesu_id in ({1}))'.format(compstr, suite_id)
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

    query = 'select * from TestCaseManage_actiongroup where acgr_comp_id={0} order by acgr_index'.format(comp_id)
    result = autodb.select_many_record(query)

    for re in result:

        actid = re['acgr_acti_id']
        query = 'select * from TestCaseManage_action where acti_id={0}'.format(actid)
        result = autodb.select_one_record(query)
        action_list.append(result[0]['acti_name'])

    return action_list


def get_comp_name(comp_id):

    """
    get component name according to id
    :param vp_id:
    :return:
    """

    query = 'select * from TestCaseManage_component where comp_id={0} '.format(comp_id)
    result = autodb.select_one_record(query)
    comp_name = result[0]['comp_name']
    return comp_name


def get_vp_name(vp_id):

    """
    get vp name according to id
    :param vp_id:
    :return:
    """

    query = 'select * from TestCaseManage_vpname where vp_id={0} '.format(vp_id)
    result = autodb.select_one_record(query)
    vp_name = result[0]['vp_name']
    return vp_name


def get_vp_type(vpt_id):

    """
    get vp type according to id
    :param vp_id:
    :return:
    """

    query = 'select * from TestCaseManage_vptype where vpt_id={0} '.format(vpt_id)
    result = autodb.select_one_record(query)
    vpt_name = result[0]['vpt_name']
    return vpt_name


def get_prodcut_name_byID(pid):

    """
    get product name according to pid
    :param pid:
    :return:
    """

    query = 'select TestCaseManage_product from Product where prod_id={0}'.format(pid)
    result = autodb.select_one_record(query)
    pname = result[0]['prod_name']
    return pname


def get_memory_info(uid,ts,version,qtype):

    if qtype.upper() == 'MAX':
        sql = "select max(mi_rss) as value from TestCaseManage_meminfo "
    elif qtype.upper() == 'AVG':
        sql = "select avg(mi_rss) as value from TestCaseManage_meminfo "
    else:
        sql = "select max(mi_rss) as value from TestCaseManage_meminfo "

    sql = sql + "where mi_uid='{0}' and mi_ver='{1}' and mi_ts='{2}' " \
                "group by mi_uid,mi_ver,mi_ts".format(uid,version,ts)

    result = autodb.select_one_record(sql)
    value = result[0]['value']
    return int(value)


def get_cpu_info(uid,ts,version):

    sql = "select avg(ci_cpu) as value from TestCaseManage_cpuinfo " +\
            "where ci_uid='{0}' and ci_ver='{1}' and ci_ts='{2}' " \
                "group by ci_uid,ci_ver,ci_ts".format(uid,version,ts)

    result = autodb.select_one_record(sql)
    avg_val = result[0]['value']

    # get the max value
    sql = "select max(ci_cpu) as value from TestCaseManage_cpuinfo " +\
            "where ci_uid='{0}' and ci_ver='{1}' and ci_ts='{2}' " \
                "group by ci_uid,ci_ver,ci_ts".format(uid,version,ts)

    result = autodb.select_one_record(sql)
    max_val = result[0]['value']

    #get the last 6 cpu value
    sql = "select sum(test.ci_cpu) as value from (select ci_cpu from TestCaseManage_cpuinfo " +\
            "where ci_uid='{0}' and ci_ver='{1}' and ci_ts='{2}' " \
                "order by ci_id DESC limit 6) as test".format(uid,version,ts)

    result = autodb.select_one_record(sql)
    last_val = result[0]['value']

    return [avg_val, max_val, last_val]


# just for memory and cpu information
def insert_info_to_db(filename,ts,uid,version,dtype):

    """

    :param filename:
    :param ts:
    :param uid:
    :return:
    """
    with open(filename) as rfile:
        if dtype.upper() == 'MEMORY':
            row = 0
            for ln in rfile:
                if row % 2 == 1:
                    row +=1
                    continue
                #ln = ' '.join(filter(lambda x: x, ln.split(' ')))
                value = ln.split(':')
                if len(value) > 0:
                    temp = value[0].replace('K','')
                    pss = temp.replace(',','').strip()
                    query = "insert into TestCaseManage_meminfo(mi_uid,mi_ts,mi_ver,mi_vss,mi_rss) values('{0}','{1}','{2}',{3},{4})".\
                        format(uid, ts, version, int(0), int(pss))
                    result = autodb.execute_insert(query)
                    if not result:
                        return False
                row +=1
        elif dtype.upper() == 'CPU':
            for ln in rfile:
                ln = ' '.join(filter(lambda x: x, ln.split(' ')))
                value = ln.split(' ')
                if len(value) > 4:
                    cpu = value[4].replace('%','')
                    cpu = float(cpu)/100
                    query = "insert into TestCaseManage_cpuinfo(ci_uid,ci_ts,ci_ver,ci_cpu) values('{0}','{1}','{2}',{3})".\
                        format(uid, ts, version, cpu)
                    result = autodb.execute_insert(query)
                    if not result:
                        return False

    return True


# update stage db for module update
def update_stage_module_network(dname, wififlag):

    updateFlag = False
    mid = device_config.getValue(dname,'background_module_id1')
    query = 'select network from fun_plugin_file where id = {0}'.format(mid)
    result = stagedb.select_one_record(query)
    value = result[0]['network']

    query1 = ''
    if wififlag.upper() == 'TRUE' and int(value) != 1:
        query1 = 'update fun_plugin_file set network = 1 where id = {0}'.format(mid)
    if wififlag.upper() == 'FALSE' and int(value) != 5:
        query1 = 'update fun_plugin_file set network = 5 where id = {0}'.format(mid)

    if query1 != '':
        stagedb.execute_update(query1)
        updateFlag = True

    return updateFlag


def get_module_info(id):

    query = 'select encryption_client_path, encryption_length, encryption_path, encryption_hash from fun_plugin_file where id = {0}'.format(id)
    result = stagedb.select_one_record(query)
    res = {}
    res['path'] = result[0]['encryption_client_path'].encode('utf8')
    res['length'] = result[0]['encryption_length']
    res['url'] = result[0]['encryption_path'].encode('utf8')
    res['hash'] = result[0]['encryption_hash'].encode('utf8')

    return res

if __name__ == '__main__':

    insert_info_to_db(r'E:\AutoTestFrame\log\20170817\ZX1G22TG4F_\1801TestMemory\test_memory_cpu_1_0_1','201708081629','ZX1G22TG4F','2.01','memory')
    #value = get_memory_info('ZX1G22TG4F', '201708081629', '1.01', 'avg')
