#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Xuxh'

import sys
import json
from jsonpath_rw import jsonpath, parse
import objectpath
reload(sys)
sys.setdefaultencoding('utf-8')


class parseJson(object):
    
    """ Json parser reference
    http://objectpath.org/reference.html
    """
    def __init__(self,dataobj):
        self.jsondata = json.loads(dataobj,encoding='utf-8')
        self.len = 0
        self.res = ''
    
    def extract_element_value(self,jsonpath):
        lines = []
        jsonpath_expr = parse(jsonpath)
        value = []
        for match in jsonpath_expr.find(self.jsondata):
            # print match.value.encode('gbk')s
            value.append(match.value)
        lines.append(value)
        return lines
    
    def extract_element_path(self,jsonpath):
        lines = []
        jsonpath_expr = parse(jsonpath)
        path = []
        for match in jsonpath_expr.find(self.jsondata):
            path.append(match.full_path)
        
        return lines.append(path)
    
    def filter_special_elements(self,jsonpath):

        lines = []
        tree = objectpath.Tree(self.jsondata)
        value = tree.execute(jsonpath)
        temp = []
        for v in list(value):
            temp.append(v)
        lines.append(temp)
        return lines


if __name__ == '__main__':

    pass