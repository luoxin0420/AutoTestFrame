#! /usr/bin/python
# -*- coding: utf-8 -*-

import testlink
from library.myglobal import testlink_config

# reference doc: https://github.com/lczub/TestLink-API-Python-client/blob/master/example/TestLinkExample.py

def write_result_to_testlink(uid, RESULT_DICT):

    #RESULT_DICT = {'TEST1':{'Result':['pass','fail'],'Log': ['test1','test2'],'TLID':'986'},'TEST2':{'Result':['pass','fail'],'Log':['test1','test2'],'TLID':'986'}}
    tlink = TestLinkObject()

    for key, value in RESULT_DICT.items():

        if 'FAILED' in value['Result']:
            test_result = 'f'
        else:
            test_result = 'p'
        product_name = testlink_config.getValue(uid, 'project_name')
        plan_name = testlink_config.getValue(uid, 'plan_name')
        build_name = testlink_config.getValue(uid, 'build_name')
        suffix = testlink_config.getValue(uid, 'case_suffix')
        case_id = ''.join([suffix,'-',str(value['TLID'])])
        tlink.report_test_result(unicode(product_name), unicode(plan_name), unicode(build_name), case_id, test_result)


class TestLinkObject(object):

    MANUAL = 1
    AUTOMATED = 2
    READFORREVIEW = 2
    REWORK = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1

    def __init__(self):

        self.url = testlink_config.getValue('TESTLINK', 'url')
        self.key = testlink_config.getValue('TESTLINK', 'key')

        self.tlc = testlink.TestlinkAPIClient(self.url, self.key)

    def get_information_test_project(self):

        print("Number of Projects      in TestLink: %s " % self.tlc.countProjects())
        print("Number of Platforms  (in TestPlans): %s " % self.tlc.countPlatforms())
        print("Number of Builds                   : %s " % self.tlc.countBuilds())
        print("Number of TestPlans                : %s " % self.tlc.countTestPlans())
        print("Number of TestSuites               : %s " % self.tlc.countTestSuites())
        print("Number of TestCases (in TestSuites): %s " % self.tlc.countTestCasesTS())
        print("Number of TestCases (in TestPlans) : %s " % self.tlc.countTestCasesTP())
        self.tlc.listProjects()

    def get_test_suite(self,id):

        #projects = self.tlc.getProjects()
        top_suites = self.tlc.getFirstLevelTestSuitesForTestProject(id)
        for suite in top_suites:
            print (suite["id"], suite["name"])

    def create_test_suite(self, project_id, test_suite_name, test_suite_describe, father_id):

        if father_id == "":
            self.tlc.createTestSuite(project_id, test_suite_name, test_suite_describe)
        else:
            self.tlc.createTestSuite(project_id, test_suite_name, test_suite_describe, parentid=father_id)

    def create_test_case(self, suite_id, data):

        # 2:step, 3:step result, manual or automated
        self.tlc.initStep(data[0][2], data[0][3], TestLinkObject.AUTOMATED)
        for i in range(1, len(data)):
            self.tlc.appendStep(data[i][2], data[i][3], TestLinkObject.AUTOMATED)

        # 0:case_title, suite_id, 5:projectID, 6:user_name, 4:summary, preconditons, importance=LOW, \
        # state=READFORREVIEW, estimatedexecduration=10.
        self.tlc.createTestCase(data[0][0], suite_id, data[0][5], data[0][6], data[0][4], preconditions=data[0][1])

    def get_test_case(self, test_case_id):

        test_case = self.tlc.getTestCase(None, testcaseexternalid=test_case_id)
        for i in test_case:
            print "step_number", "actions", "expected_results"
        for m in i.get("steps"):
            print (m.get("step_number"), m.get("actions"), m.get("expected_results"))

    def get_plan_id(self, product_name, plan_name):

        pld = ''
        pid = self.tlc.getProjectIDByName(product_name)
        plan_list = self.tlc.getProjectTestPlans(pid)
        for pl in plan_list:
            if pl['name'] == plan_name:
                pld = pl['id']
                break
        return pld

    def report_test_result(self, product_name, plan_name, build_name, test_case_id, test_result):

        try:
            plan_id = self.get_plan_id(product_name, plan_name)
            #self.tlc.reportTCResult(test_case_id, plan_id, build_name, test_result, 'autotest result', platformname="0")
            self.tlc.reportTCResult(None, plan_id, build_name, test_result, 'autotest result', testcaseexternalid=test_case_id, platformname="0")
        except Exception,ex:
            print ex

if __name__ == '__main__':

    # tl_helper = TestLinkHelper()
    # tl_helper.setParamsFromArgs('''Shows how to use the TestLinkAPI.
    # => Counts and lists the Projects
    # => Create a new Project with the following structure:''')
    # myTestLink = tl_helper.connect(TestlinkAPIClient)

    temp = write_result_to_testlink('84B7N15C15000774',{})
    tobj = TestLinkObject()
    temp = tobj.tlc.about()
    temp1 = tobj.tlc.getProjects()
    str1 = unicode('00_产品交付')

    #count = tobj.tlc.countPlatforms()
    pid = tobj.tlc.getProjectIDByName(str1)
    plan_list = tobj.tlc.getProjectTestPlans(pid)
    for pl in plan_list:
        if pl['name'] == u'test':
            pld = pl['id']
            break
    build_list = tobj.tlc.getBuildsForTestPlan(pld)

    for bl in build_list:
        if bl['name'] == 'test':
            bld = bl['id']
            break
    case_list = tobj.tlc.getTestCasesForTestPlan(pld)
    tobj.tlc.reportTCResult(None,pld, 'test', 'p', 'first try', testcaseexternalid='lockscreen-228', platformname="0")



