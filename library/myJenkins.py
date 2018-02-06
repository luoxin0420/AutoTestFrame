#! /usr/bin/python
# -*- coding: utf-8 -*-


import jenkins
import time
import sys


class JenkinsObject():

    def __init__(self,url,user,pwd):

        self.server = jenkins.Jenkins(url=url, username=user, password=pwd)


    def build_job(self, jobName, jobToken):

        self.server.build_job(name=jobName, token=jobToken)
        while True:
            time.sleep(1)
            print 'check running job...'
            if len(self.server.get_running_builds()) == 0:
                break
            else:
                time.sleep(20)
        last_build_number = self.server.get_job_info(jobName)['lastCompletedBuild']['number']
        build_info = self.server.get_build_info(jobName, last_build_number)
        build_result = build_info['result']
        print 'Build result is ' + build_result
        if build_result == 'SUCCESS':
            sys.exit(0)
        else:
            sys.exit(-1)

