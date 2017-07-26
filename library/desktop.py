#! /usr/bin/python
# -*- coding: utf-8 -*-
import urllib2

__author__ = 'Xuxh'

import os
import sys
import logging
import time
import datetime
import subprocess
import smtplib
import psutil
import signal
import ctypes
from email import Encoders
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
import platform
import zipfile

import configuration
import myglobal

CONFIG = configuration.configuration()
CONFIG.fileConfig(myglobal.CONFIGURATONINI)


def send_mail(subj, att):

    smtp_server = CONFIG.getValue("Report","smtp")
    sender = CONFIG.getValue("Report","sender")
    recipients = CONFIG.getValue("Report","to")
    passwd = CONFIG.getValue("Report","passwd")
    recipients = recipients
    session = smtplib.SMTP()
    session.connect(smtp_server)
    session.login(sender, passwd)
    msg = MIMEMultipart()
    msg['Subject'] = subj
    msg.attach(MIMEText(subj,'plain-text'))
    file = open(att, "r")
    part = MIMEBase('application', "octet-stream")
    part.set_payload(file.read())
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="test_report.html"')
    msg.attach(part)
    smtpresult = session.sendmail('no-reply@dianhua.cn', recipients, msg.as_string())
    session.close()


def get_desktop_os_type():

    return platform.system()


def kill_child_processes(parent_pid, sig=signal.SIGTERM):

    try:
        p = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return
    child_pid = p.children(recursive=True)

    for pid in child_pid:
        os.kill(pid.pid, sig)


def create_logger(filename):

    logger = logging.getLogger("VlifeTest")
    formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stderr)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.DEBUG)

    return logger


def get_log_name(device_name,basename):

    cur_date = datetime.datetime.now().strftime("%Y%m%d")
    now = datetime.datetime.now().strftime("%H%M")
    name = CONFIG.getValue(device_name,'name')
    parent_path = os.path.join('log',cur_date, device_name+'_'+name, now+basename)

    # create multi layer directory
    if not os.path.isdir(parent_path):
        os.makedirs(parent_path)

    filename = os.path.join(parent_path,'result.log')

    return filename


def launch_appium(uid, port, bport):

    status = ""
    try:
        temp = "".join(["appium -p ", str(port), " -bp ", str(bport), " -U ",  uid, " --command-timeout 600"])
        #temp = "".join(["node.exe ", js, " -p ", str(port), " -bp ", str(bport), " -U ",  uid, " --command-timeout 600"])
        ap = subprocess.Popen(temp, shell=True)
        time.sleep(4)
        if ap.poll() is None:
            status = "READY"
    except Exception, ex:
        print ex
        status = "FAIL"
        pid = None
    return status, ap


# Note: program without extension
def close_all_program(program):

    temp = ""

    if platform.system() == "Windows":
        temp = ''.join(["taskkill /F /IM ",program,'.exe'])
    if platform.system() == "Linux":
        temp = ''.join(["killall ",program])
    subprocess.Popen(temp, shell=True)
    time.sleep(1)


def download_data(url, fname):

    f = urllib2.urlopen(url)
    data = f.read()
    with open(fname, "wb") as wfile:
        wfile.write(data)


def remove_sufix_name(full_name):

    fname = os.path.basename(full_name)
    dirpath = os.path.dirname(full_name)

    if os.path.splitext(fname)[1] == '.pet':
        newname = fname.split('.')[:-2]
        newfile = os.path.join(dirpath,newname)
        os.rename(full_name,newfile)


def unzip_file(fname,despath):

    zfile = zipfile.ZipFile(fname,'r')

    for f in zfile.namelist():
        if f.endswith('/'):
            os.makedirs(f)
        else:
            zfile.extract(f,despath)


def get_file_rows(filename):

    count = 0
    try:
        thefile = open(filename, 'rb')
        while True:
            buffer = thefile.read(8192*1024)
            if not buffer:
                break
            count += buffer.count('\n')
        thefile.close()
    except Exception,ex:
        print ex
    return count


def summary_result(logname,flag,RESULT_DICT):

    #logname = r'E:\AutoTestDemo\TestLockScreen\log\20170713\ZX1G22TG4F_Nesux6\1523TestTasks\unittest.html'
    #RESULT_DICT = {'TEST1':{'Result':['pass','fail'],'Log': ['test1','test2']},'TEST2':{'Result':['pass','fail'],'Log':['test1','test2']}}
    count = get_file_rows(logname)
    report = os.path.join(os.path.dirname(logname),'summary_report.html')
    count2 = get_file_rows(report)
    if not flag:
        with open(report, 'a+') as wfile, open(logname) as rfile:
            i = 1
            for line in rfile:
                if i > count2:
                    wfile.write(line)
                i += 1
    else:
        summary_table = '''
        <h1>Summary Report</h1>
        <table id = 'summary_table'>
    <tr id = 'summary_header_row'>
    <th>TestCase_Name</th>
    <th>Test_Result</th>
    <th>Log</th>
    </tr>
    <tr align="right">
    ${content}
    </tr>
    </table>
    '''
        lines = ''
        for key, value in RESULT_DICT.items():

            result = '<Br/>'.join(value['Result'])
            log = '<Br/>'.join(value['Log'])
            single = ''.join(['<tr><td>',key,'</td>','<td>',result,'</td>','<td>',log,'</td><tr>'])
            lines = lines + single

        summary_table = summary_table.replace('${content}',lines)

        i = 1
        with open(report, 'a+') as wfile, open(logname) as rfile:
            for line in rfile:
                if i > count2:
                    if line.find('</body>') == -1:
                        wfile.write(line)
                    else:
                        if count - i == 1:
                            summary_table += '</body>'
                            wfile.write(summary_table)
                        else:
                            wfile.write(line)
                i += 1


class Logger:

    FOREGROUND_WHITE = 0x0007
    FOREGROUND_BLUE = 0x01 # text color contains blue.
    FOREGROUND_GREEN= 0x02 # text color contains green.
    FOREGROUND_RED  = 0x04 # text color contains red.
    FOREGROUND_YELLOW = FOREGROUND_RED | FOREGROUND_GREEN

    STD_OUTPUT_HANDLE= -11
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    def __init__(self, path,clevel = logging.DEBUG,Flevel = logging.DEBUG):
        self.logger = logging.getLogger("VlifeTest")
        self.logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(clevel)
        #设置文件日志
        fh = logging.FileHandler(path)
        fh.setFormatter(fmt)
        fh.setLevel(Flevel)
        self.logger.addHandler(sh)
        self.logger.addHandler(fh)

    def set_color(self,color, handle=std_out_handle):
        bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return bool

    def debug(self,message):
        self.logger.debug(message)

    def info(self,message):
        self.logger.info(message)

    def war(self,message):
        self.set_color(self.FOREGROUND_YELLOW)
        self.logger.warn(message)
        self.set_color(self.FOREGROUND_WHITE)

    def error(self,message):
        self.set_color(self.FOREGROUND_RED)
        self.logger.error(message)
        self.set_color(self.FOREGROUND_WHITE)

    def cri(self,message):
        self.logger.critical(message)


if __name__ == '__main__':

    pass



