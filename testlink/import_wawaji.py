#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Administrator'

from xml.dom.minidom import Document
import csv
import datetime
import argparse
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def format_preconditions(input_str):
    out_str = ""
    if input_str is not None:
        for line in input_str.split('\n'):
            ln = '<li>' + line + '</li>'
            out_str += ln
        out_str = '<ol>' + out_str + '</ol>'
    return out_str


def format_test_steps(doc, man_steps, exe_type, exp_result):

    test_steps = unicode(man_steps.decode('gbk').encode('utf-8')).split('\n')
    exp_results = unicode(exp_result.decode('gbk').encode('utf-8')).split('\n')
    node_steps = doc.createElement('steps')
    number = 1
    for s in test_steps:


        step = doc.createElement('step')
        # step_number
        step_number = doc.createElement('step_number')
        step_number_text = doc.createCDATASection(str(number))
        step_number.appendChild(step_number_text)
        step.appendChild(step_number)
        # actions
        actions = doc.createElement('actions')
        format_action = '<p>' + s + '</p>'
        actions_text = doc.createCDATASection(format_action)
        actions.appendChild(actions_text)
        step.appendChild(actions)
        # execution_type
        etype1 = doc.createElement('execution_type')
        etype1_text = doc.createCDATASection(str(exe_type))
        etype1.appendChild(etype1_text)
        step.appendChild(etype1)
        # expectedresults
        result = doc.createElement('expectedresults')
        if len(exp_results) >= number:
            result_text = doc.createCDATASection(exp_results[number-1])
        else:
            result_text = doc.createCDATASection("")
        result.appendChild(result_text)
        step.appendChild(result)
        node_steps.appendChild(step)
        number +=1
    return node_steps


def writeInfoToXml(input_fn, output_fn, suite_name, only_import_case=False):

    doc = Document()
    # add suite information to xml
    if not only_import_case:
        root = doc.createElement('testsuite')
        root.setAttribute('name', suite_name)
        doc.appendChild(root)
        details = doc.createElement('details')
        details_text = doc.createCDATASection('test')
        details.appendChild(details_text)
        root.appendChild(details)
    else:
        testcases = doc.createElement('testcases')
        doc.appendChild(testcases)

    # add test cases information to xml
    with open(input_fn) as rfile:

        reader = csv.reader(rfile)

        for line in reader:

            (c_category, c_component, importance, case_name, preconditions, man_steps, exp_result, esti_time) = \
                (line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7])
            testcase = doc.createElement('testcase')
            unicode_str = unicode(case_name.decode('gbk').encode('utf-8'))
            testcase.setAttribute('name', unicode_str)

            # summary
            summary = doc.createElement('summary')
            # wawaji has no summary
            unicode_str = ''
            summary_text = doc.createCDATASection(unicode_str)
            summary.appendChild(summary_text)
            testcase.appendChild(summary)
            # preconditions
            precond = doc.createElement('preconditions')
            unicode_str = format_preconditions(unicode(preconditions.decode('gbk').encode('utf-8')))
            precond_text = doc.createCDATASection(unicode_str)
            precond.appendChild(precond_text)
            testcase.appendChild(precond)
            # execution_type
            etype = doc.createElement('execution_type')
            # 1 是手动， 2 是自动
            etype_text = doc.createCDATASection(str(1))
            etype.appendChild(etype_text)
            testcase.appendChild(etype)
            # importance
            case_importance = doc.createElement('importance')
            case_importance_text = doc.createCDATASection(str(importance))
            case_importance.appendChild(case_importance_text)
            testcase.appendChild(case_importance)

            # estimated time
            case_estim = doc.createElement('estimated_exec_duration')
            case_estim_value = doc.createTextNode(str(line[7]))
            case_estim.appendChild(case_estim_value)
            testcase.appendChild(case_estim)
            # steps
            # steps = doc.createElement('steps')
            # testcase.appendChild(steps)

            # step
            steps = format_test_steps(doc, man_steps, str(1), exp_result)
            testcase.appendChild(steps)
            #custom_fields
            cfields = doc.createElement('custom_fields')

            # custom_field name
            dict = {u'娃娃机投放类型':c_category, u'娃娃机模块':c_component}

            for (k, v) in dict.iteritems():
                cfield = doc.createElement('custom_field')
                c_name = doc.createElement('name')
                c_name_text = doc.createCDATASection(k)
                c_name.appendChild(c_name_text)
                cfield.appendChild(c_name)
                 # custom_field value
                c_value = doc.createElement('value')
                unicode_str = unicode(v.decode('gbk').encode('utf-8'))
                c_value_text = doc.createCDATASection(unicode_str)
                c_value.appendChild(c_value_text)
                cfield.appendChild(c_value)
                cfields.appendChild(cfield)

            testcase.appendChild(cfields)
            if not only_import_case:
                root.appendChild(testcase)
            else:
                testcases.appendChild(testcase)

    with open(output_fn, 'w+') as wfile:
        wfile.write(doc.toprettyxml(indent='\t', encoding='utf-8'))


if __name__ == '__main__':

    newParser = argparse.ArgumentParser()

    newParser.add_argument("-i", dest="infile", type=str, help="Need import csv file")
    newParser.add_argument("-o", dest="outfile", type=str, help="Output xml file")
    # make sure suite name is not exist in the testlink
    newParser.add_argument("-n", dest="sname", default='Test', type=str, help="Suite name")
    newParser.add_argument("-f", dest="flag", default=False, type=bool, help="Flag of only import new cases")

    args = newParser.parse_args()
    infile = args.infile
    outfile = args.outfile
    sname = args.sname
    if sname == 'Test':
        sname = 'Test' + '_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    flag = args.flag
    # handle with suite name with Chinese
    suite_name = unicode(sname.decode('gbk').encode('utf-8'))
    writeInfoToXml(infile, outfile, suite_name, flag)


