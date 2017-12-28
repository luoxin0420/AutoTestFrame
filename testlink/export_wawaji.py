#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Administrator"

from xml.dom.minidom import *
import csv
import argparse
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def format_steps(steps_obj, dom):


    steps = steps_obj.getElementsByTagName("step")
    act = []
    exp = []
    for step in steps:

        try:
            step_number = step.getElementsByTagName("step_number")[0]
            node = step_number._get_childNodes()[0]
            if node.nodeType == dom.CDATA_SECTION_NODE:
                step_number_text = node._get_data().decode("utf-8")

            # actions
            actions = step.getElementsByTagName("actions")[0]
            node = actions._get_childNodes()[0]
            if node.nodeType == dom.CDATA_SECTION_NODE:
                act_text = node._get_data().decode("utf-8").encode("gbk")
                act_text = act_text.replace("<p>", "")
                act_text = act_text.replace("</p>", "\n")
                act.append(act_text)
            # expectedresults
            expectedresults = step.getElementsByTagName("expectedresults")[0]
            node = expectedresults._get_childNodes()[0]
            if node.nodeType == dom.CDATA_SECTION_NODE:
                exp_text = node._get_data().decode("utf-8").encode("gbk")
                exp_text = exp_text.replace("<p>", "")
                exp_text = exp_text.replace("</p>", "")
                exp.append(exp_text)

        except Exception,ex:

            print ex

    steps_text = "\n".join(act)
    expect_text = "\n".join(exp)

    return steps_text, expect_text


def format_custom_fields(custom_obj, dom):

    c_category = ""
    c_component = ""

    custom_fields = custom_obj.getElementsByTagName("custom_field")
    for cf in custom_fields:

        name = cf.getElementsByTagName("name")[0]
        node = name._get_childNodes()[0]
        if node.nodeType == dom.CDATA_SECTION_NODE:
            n_value = node._get_data().decode("utf-8")
        value = cf.getElementsByTagName("value")[0]
        node = value._get_childNodes()[0]
        if node.nodeType == dom.CDATA_SECTION_NODE:
            v_value = node._get_data().decode("utf-8").encode("gbk")

        if n_value == u"娃娃机投放类型":
            c_category = v_value
        elif n_value == u"娃娃机模块":
            c_component = v_value

    return c_category, c_component


def parseXmlToCsv(infile,outfile):

    dom = parse(infile)
    collection = dom.documentElement
    if collection.hasAttribute("shelf"):
       print "Root element : %s" % collection.getAttribute("shelf")

    # get all test cases
    testcases = collection.getElementsByTagName("testcase")
    with open(outfile,"wb+") as wfile:
        writer = csv.writer(wfile)
        for tc in testcases:
            case_name, summary_text, preconditions_text = ["","",""]
            importance_text, exe_type_text, steps_text = ["","",""]

            # case_name
            if tc.hasAttribute("name"):
                case_name = tc.getAttribute("name").decode("utf-8").encode("gbk")
            # # summary
            # summary = tc.getElementsByTagName("summary")[0]
            # node = summary._get_childNodes()[0]
            # if node.nodeType == dom.CDATA_SECTION_NODE:
            #     summary_text = node._get_data().decode("utf-8").encode("gbk")

            # preconditions
            try:
                preconditions = tc.getElementsByTagName("preconditions")[0]
                node = preconditions._get_childNodes()[0]
                if node.nodeType == dom.CDATA_SECTION_NODE:
                    preconditions_text = node._get_data().decode("utf-8").encode("gbk")
                    for char in ["</li>", "<ol>", "</ol>", "<li>", "<p>", "</p>"]:
                        if char == "</li>":
                            preconditions_text = preconditions_text.replace(char, "\n")
                        else:
                            preconditions_text = preconditions_text.replace(char, "")
            except Exception,ex:
                preconditions_text = ''

            #exe_type
            exe_type = tc.getElementsByTagName("execution_type")[0]
            node = exe_type._get_childNodes()[0]
            if node.nodeType == dom.CDATA_SECTION_NODE:
                exe_type_text = node._get_data().decode("utf-8")

            #importance
            importance = tc.getElementsByTagName("importance")[0]
            node = importance._get_childNodes()[0]
            if node.nodeType == dom.CDATA_SECTION_NODE:
                importance_text = node._get_data().decode("utf-8")

            #estimate time
            estimate = tc.getElementsByTagName("estimated_exec_duration")[0]
            try:
                estimate_text = estimate._get_childNodes()[0].data
            except Exception,ex:
                estimate_text = 0

            #steps
            steps = tc.getElementsByTagName("steps")[0]
            steps_text, expe_result_text = format_steps(steps,dom)

            #custom_fields
            custom_fields = tc.getElementsByTagName("custom_fields")[0]
            c_category, c_component = format_custom_fields(custom_fields, dom)

            line = [c_category, c_component, importance_text, case_name,\
                    preconditions_text, steps_text, expe_result_text, estimate_text]
            writer.writerow(line)

if __name__ == "__main__":

    newParser = argparse.ArgumentParser()

    newParser.add_argument("-i", dest="infile", type=str, help="Need import csv file")
    newParser.add_argument("-o", dest="outfile", type=str, help="Output xml file")

    args = newParser.parse_args()
    infile = args.infile
    outfile = args.outfile

    parseXmlToCsv(infile, outfile)

