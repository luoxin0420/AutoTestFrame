
import time
import html
import os

dict = {'msg':[''],
        #define tags here:
        'tag':['TEST_START', 'TEST_STEP', 'TEST_DEBUG', 'TEST_COMPLETE', 'TEST_PASS', 'TEST_FAIL', 'TEST_ERROR', 'TEST_WARN', 'VP_FAIL','VP_PASS']}

class ParameterError(Exception):
    def __init__(self, ele):
        Exception.__init__(self)
        self.ele = ele

def currenttime():
    currenttime = time.strftime("%b %d %H:%M:%S", time.localtime())
    return currenttime

def currentdate():
    currentdate = time.strftime("%Y%m%d", time.localtime())
    #print currentdate
    currentdatafull = time.strftime("%Y%m%d%H%M%S", time.localtime())
    return currentdate, currentdatafull

def readpath(pathfile):
    path = os.path.dirname(pathfile)
    if os.path.isdir(path) == False:
        os.makedirs(path)
    title = pathfile.replace(path + '\\','').replace('.html','')
    #creat path
    #print title, pathfile
    return title, pathfile

class Log:
    def __init__(self, path):
        self.htmltitle, self.filename = readpath(path)
        self.time = currenttime()
        self.dict = dict
        self.htmltest = html.HTML(self.htmltitle, self.filename)
        #self.htmltest.insertTableHead()

    def insertTableBody(self, tag, msg):
        self.htmltest.insertTableBody(tag)
        self.htmltest.insertTableBody(msg)

    def write(self, tag, msg):
        if tag not in self.dict['tag']:
            print 'wrong element: %s' %tag
        self.htmltest.insertTableBody_Time(time=currenttime())
        self.insertTableBody(tag, msg)
        self.htmltest.finishTableBody()

    def close(self):
        self.htmltest.finishHTML()



