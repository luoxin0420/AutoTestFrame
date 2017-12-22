#! /usr/bin/python
# -*- coding: utf-8 -*-

from library.myglobal import PATH,device_config
from library.db import dbmysql
from library.myglobal import logger
from library import desktop
import time
import datetime

autodb = dbmysql.MysqlDB(PATH('../config/dbconfig.ini'),'AUTOTEST')
stagedb = dbmysql.MysqlDB(PATH('../config/dbconfig.ini'),'STAGE')


def filter_cases(suite_id, comp_list, pid):

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

    query = 'select * from TestCaseManage_testcase where teca_enable=1 and teca_comp_id in ({0}) ' \
            'and teca_prod_id in ({1}) and teca_id in (select tsca_teca_id from TestCaseManage_testsuitecase ' \
            'where tsca_tesu_id in ({2}))'.format(compstr, pid, suite_id)
    cases = autodb.select_many_record(query)
    if len(cases) == 0:
        logger.warning('There are not test cases')
    return cases


def filter_image_source(vendor):

    # get vendor ID
    query = 'select id  from resource_vendor where vendor="{0}"'.format(vendor)
    result = autodb.select_one_record(query)
    vid = str(result[0]['id'])

    query = 'select A.*, B.alias from resource_image A INNER JOIN resource_verification B ON A.id = B.img_id where B.vendor_id = {0} and B.enable = 1'.format(vid)
    cases = autodb.select_many_record(query)
    if len(cases) == 0:
        logger.warning('There are not test cases')
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


def get_product_ID_byName(pname):

    """

    :param pname:
    :return:
    """

    query = "select prod_id from TestCaseManage_product where prod_name REGEXP '[[:<:]]{0}[[:>:]]'".format(pname.lower())
    result = autodb.select_many_record(query)
    res = []
    for re in result:
        res.append(str(re['prod_id']))
    return res


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
                    query = "insert into TestCaseManage_meminfo(mi_uid,mi_ts,mi_ver,mi_uss,mi_pss) values('{0}','{1}','{2}',{3},{4})".\
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


def insert_runinfo(slist,dname, vname, loop,ltype):

    cur_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if ltype.upper() == 'ALL':
        lt = 0
    else:
        lt = 1

    query = "insert into TestCaseManage_runinfo(run_tesu_id,run_device_name,run_build_name,run_date,run_loop_number, run_loop_type, run_name) " \
                "values('{0}','{1}','{2}','{3}',{4},{5}, '{6}')".format(slist, dname, vname, cur_date, loop, lt, 'qatest')
    autodb.execute_insert(query)

    # get new id value
    query = "select MAX(run_id) from TestCaseManage_runinfo"
    result = autodb.select_one_record(query)
    id = str(result[0]['MAX(run_id)'])

    # update run name
    query = ""
    return id


def insert_test_result(run_id, teca_id, lp_num, teca_result, log):

    # get suite id
    query = "select run_tesu_id from TestCaseManage_runinfo where run_id={0}".format(run_id)
    result = autodb.select_one_record(query)
    sid = result[0]['run_tesu_id'].encode('utf8').split(',')

    # get case mapping suite_id
    query = "select distinct tsca_tesu_id from TestCaseManage_testsuitecase where tsca_teca_id = {0}".format(teca_id)
    result = autodb.select_many_record(query)
    sid2 = []
    for re in result:
        sid2.append(str(re['tsca_tesu_id']))
    # get insection set
    final_sid = ','.join(list(set(sid) & set(sid2)))

    # insert result to db
    cur_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = log.replace('\\', '/')
    query = "insert into TestCaseManage_testresult(resu_run_id,resu_tesu_id,resu_teca_id,resu_loop,resu_date_time, resu_result, resu_log_info) " \
                "values({0},'{1}',{2},{3},'{4}','{5}','{6}')".format(run_id, final_sid, teca_id, lp_num, cur_date, teca_result, log)
    autodb.execute_insert(query)


# update stage db for module update
def update_stage_module_network(mid, exp_network, exp_killself):

    updateFlag = False
    query = 'select * from fun_plugin_file where id = {0}'.format(mid)
    result = stagedb.select_one_record(query)
    network = result[0]['network']
    killself = result[0]['killself']
    query = ''
    if exp_network != network or exp_killself != killself:
        query = 'update fun_plugin_file set network = {0},killself={1} where id = {2}'.format(exp_network, exp_killself, mid)
    if query != '':
        stagedb.execute_update(query)
        updateFlag = True

    return updateFlag


# update stage db for module enalbe/disable
def update_stage_module_status(mid, flag):

    if flag:
        query = 'update fun_plugin_file set enable = {0} where id = {1}'.format(1, mid)
    else:
        query = 'update fun_plugin_file set enable = {0} where id = {1}'.format(0, mid)

    stagedb.execute_update(query)


def get_module_info(id):

    query = 'select encryption_client_path, encryption_length, encryption_path, encryption_hash from fun_plugin_file where id = {0}'.format(id)
    result = stagedb.select_one_record(query)
    res = {}
    res['path'] = result[0]['encryption_client_path'].encode('utf8')
    res['length'] = str(result[0]['encryption_length'])
    res['url'] = result[0]['encryption_path'].encode('utf8')
    res['hash'] = result[0]['encryption_hash'].encode('utf8')
    res['soft_version'] = result[0]['soft_version']
    return res


def check_amount_limit(mid):

    flag = False
    cur_date = datetime.datetime.now().strftime("%Y-%m-%d")
    cur_date = " ".join([cur_date, "00:00:00"])
    start_time = desktop.get_time_stamp(cur_date, 0)
    end_time = desktop.get_time_stamp(cur_date, 1)

    query = "select * from fun_plugin_amount_limit where plugin_file_id= {0} and start_time= {1}".format(mid, start_time)
    result = stagedb.select_one_record(query)
    if result[0] is None:
        query = "insert into fun_plugin_amount_limit(plugin_file_id, enable, start_time, end_time, max_get_amount) values({0},1,{1},{2},1000)".format(mid, start_time,end_time)
        stagedb.execute_insert(query)
        flag = True

    return flag


def get_operation_module_info(key, id):

    if key.lower() == 'module':
        query = 'select path, length, hash, encryption_path, soft_version from fun_plugin_file where id = {0}'.format(id)
    else:
        query = 'select path, length, hash, client_path,version from fun_upgrade_operation where id = {0}'.format(id)
    result = stagedb.select_one_record(query)
    res = {}
    res['path'] = result[0]['path'].encode('utf8')
    res['length'] = str(result[0]['length'])
    res['hash'] = result[0]['hash'].encode('utf8')
    if key.lower() != 'module':
        res['cpath'] = result[0]['client_path'].encode('utf8')
        res['version'] = result[0]['version']
    else:
        res['cpath'] = result[0]['encryption_path'].encode('utf8')
        res['version'] = result[0]['soft_version']
    return res


def get_all_module_info(conf_dict):

    result = {}

    for key, value in conf_dict.items():
        if key.lower() == 'c_rule':
            continue
        else:
            result[key] = get_operation_module_info(key, value)
    return result


def update_push_interval(ruleID, value):

    interval = int(value)*60*1000

    query = "update fun_wallpaper_limit set sequence={0} where id=-1 and rule_id = {1} and type = '{2}'".format(str(interval), ruleID, 'push')
    stagedb.execute_update(query)


def update_switch(ruleID, stype, action):

    key = ''.join([stype, ':', action.upper()])

    # current this id is not changed, so here is hard code
    switcher = {
        'dev_statistic:OFF': 75,
        'dev_statistic:ON': 66,
        'init_operation_module:OFF': 91,
        'init_operation_module:ON': 89
    }
    id = switcher.get(key, 0)

    if id != 0:
        query = "select * from fun_wallpaper_limit where id={0} and rule_id = {1} and type = '{2}'".format(id, ruleID, 'switch')
        result = stagedb.select_one_record(query)
        if result[0] is None:
            query = "insert into fun_wallpaper_limit(id, rule_id, type, enabled, sequence, priority) values({0},{1},'{2}',1,0,0)".format(id,ruleID, 'switch')
            stagedb.execute_insert(query)
        else:
            query = "update fun_wallpaper_limit set enabled=1 where id={0} and rule_id = {1} and type = '{2}'".format(id, ruleID, 'switch')
            stagedb.execute_update(query)
        if id == 75 or id == 66:
            diff_id = list(set([75,66]) - set([id]))
        if id == 91 or id == 89:
            diff_id = list(set([91,89]) - set([id]))

        query = "update fun_wallpaper_limit set enabled=0 where id={0} and rule_id = {1} and type = '{2}'".format(diff_id[0], ruleID, 'switch')
        stagedb.execute_update(query)

        # update switch
        update_switch_time()


def start_c_process(ruleID, action):

    updateFlag = False
    query = "select * from fun_wallpaper_limit where id={0} and rule_id = {1} and type = '{2}'".format(7, ruleID, 'upgrade_c_setup')
    result = stagedb.select_one_record(query)
    value = result[0]['enabled']

    query = ''
    if action != value:
        query = "update fun_wallpaper_limit set enabled={0} where id={1} and rule_id = {2} and type = '{3}'".format(action, 7, ruleID, 'upgrade_c_setup')

    if query != '':
        stagedb.execute_update(query)
        updateFlag = True

    return updateFlag


# update stage db for operation module
# value format: wifi:killself
def update_operation_module(mid, exp_network, exp_killself, exp_enabled):

    updateFlag = False
    query = 'select * from fun_upgrade_operation where id = {0}'.format(mid)
    result = stagedb.select_one_record(query)
    network = result[0]['network_type']
    killself = result[0]['killself']
    enabled = result[0]['enable']
    query = ''
    if exp_network != network or exp_killself != killself or exp_enabled != enabled:
        query = 'update fun_upgrade_operation set network_type = {0},killself={1}, enable={2} where id = {3}'.format(exp_network, exp_killself, exp_enabled, mid)

    if query != '':
        stagedb.execute_update(query)
        updateFlag = True

    return updateFlag


def update_switch_time():

    t = time.time()
    timestamp = (int(round(t * 1000)))
    query = 'update fun_push_public set time={0} where type={1}'.format(timestamp, 'switch')
    result = stagedb.execute_update(query)


if __name__ == '__main__':

    #insert_info_to_db(r'E:\AutoTestFrame\log\20170817\ZX1G22TG4F_\1801TestMemory\test_memory_cpu_1_0_1','201708081629','ZX1G22TG4F','2.01','memory')
    #value = get_memory_info('ZX1G22TG4F', '201708081629', '1.01', 'avg')
    #update_switch('3423', 'dev_statistic', 'off')
    #insert_test_result(7, 1, 3, 'pass', '/test/log.txt')

    import csv

    with open(r'E:\work\vivo.csv') as rfile:
        reader = csv.reader(rfile)
        for line in reader:
            #name = unicode(line[0],'gbk')
            #query = 'insert resource_image(name,fid,xml_id) values("{0}",{1},{2})'.format(name, line[1], line[2])
            query = 'insert resource_verification(vendor_id, img_id, enable) values({0},{1},{2})'.format(line[3],line[4],line[5])
            autodb.execute_insert(query)
    pass
