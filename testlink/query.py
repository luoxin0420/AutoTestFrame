__author__ = 'Administrator'


import testlink
from library import myglobal


class TestLinkObject(object):

    MANUAL = 1
    AUTOMATED = 2
    READFORREVIEW = 2
    REWORK = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1

    def __init__(self):

        url = myglobal.testlink_config.getValue('TESTLINK', 'url')
        key = myglobal.testlink_config.getValue('TESTLINK', 'key')

        self.tlc = testlink.TestlinkAPIClient(url, key)

    def get_information_test_project(self):

        print("Number of Projects      in TestLink: %s " % self.tlc.countProjects())
        print("Number of Platforms  (in TestPlans): %s " % self.tlc.countPlatforms())
        print("Number of Builds                   : %s " % self.tlc.countBuilds())
        print("Number of TestPlans                : %s " % self.tlc.countTestPlans())
        print("Number of TestSuites               : %s " % self.tlc.countTestSuites())
        print("Number of TestCases (in TestSuites): %s " % self.tlc.countTestCasesTS())
        print("Number of TestCases (in TestPlans) : %s " % self.tlc.countTestCasesTP())
        self.tlc.listProjects()

    def get_test_suite(self):

        projects = self.tlc.getProjects()
        top_suites = self.tlc.getFirstLevelTestSuitesForTestProject(projects[0]["id"])
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

    def report_test_result(self, test_plan_id, test_case_id, test_result):
        self.tlc.reportTCResult(None, test_plan_id, None, test_result, "", guess=True, testcaseexternalid=test_case_id, platformname="0")