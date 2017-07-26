#!/usr/bin/env python
# -*- coding:utf-8 -*-

#import urllib ( python 3.0)
#import ssl (python 3.0)
import http.cookiejar
import urllib2

from library import configuration
from library.myglobal import logger

class MyHttp:

    """config server ip, port, headers """

    def __init__(self, config_file,server_name):

        config = configuration.configuration()
        config.fileConfig(config_file)
        self.protocol = config.getValue(server_name, 'protocol')
        self.host = config.getValue(server_name, 'host')
        self.port = config.getValue(server_name, 'port')
        self.headers = dict(config.getValue(server_name, 'headers'))

        # install cookie
        cj = http.cookiejar.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)

        # support ssl, note port is 443, use 3.0 'urllib'
        # https_sslv3_handler = urllib2.HTTPSHandler(context=ssl.SSLContext(ssl.PROTOCOL_SSLv2))
        # opener = urllib2.build_opener(https_sslv3_handler)
        # urllib.request.install_opener(opener)

    def set_host(self, host):
        self.host = host

    def get_host(self):
        return self.host

    def get_protocol(self):
        return self.protocol

    def set_port(self, port):
        self.port = port

    def get_port(self):
        return  self.port

    # set http header
    def set_header(self, headers):
        self.headers = headers

    # get method
    def get(self, url, params=''):

        if self.port != '0':
            url = self.protocol + '://' + self.host + ':' + str(self.port) + url + params
        else:
            url = self.protocol + '://' + self.host + url + params

        logger.info('Request：%s' % url)
        logger.info('Header：%s' % self.headers)
        request = urllib2.Request(url, headers=self.headers)
        try:
            response = urllib2.urlopen(request)
            response_body = response.read()
            # response_info = response.info()
            # for key, value in response_info.items():
            #     if key == 'headers':
            #         response_header = value
            response_header = ''
            response_status_code = response.getcode()
            response = [response_body, response_header, response_status_code]
            return response
        except Exception as e:
            logger.error('Send Request is failed，reasons：%s' % e)
            return None

    # post method
    def post(self, url, data=''):
        url = self.protocol + '://' + self.host + ':' + str(self.port) + url

        logger.info('Request：%s' % url)
        logger.info('parameters：%s' % data)
        logger.info('Header：%s' % self.headers)
        request = urllib2.Request(url, headers=self.headers)
        try:
            response = urllib2.urlopen(request, data)
            response_body = response.read()
            response_header = response.getheaders()
            response_status_code = response.status
            response = [response_body, response_header, response_status_code]
            return response
        except Exception as e:
            logger.error('Send Request is failed, reasons：%s' % e)
            return None

