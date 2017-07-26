#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'xuxh'

import sys
import mysql.connector
import mysql.connector.cursor
from library import configuration
from library.myglobal import logger


class MysqlDB(object):

    def __init__(self, config_file, db):

        config = configuration.configuration()
        config.fileConfig(config_file)
        self.host = config.getValue(db, 'host')
        self.port = config.getValue(db, 'port')
        self.user = config.getValue(db, 'user')
        self.passwd = config.getValue(db, 'passwd')
        self.db_name = config.getValue(db, 'db')
        self.charset = config.getValue(db, 'charset')

        try:
            self.dbconn = mysql.connector.connect(host=self.host, port=self.port, user=self.user, password=self.passwd, database=self.db_name, charset=self.charset)
        except Exception as e:
            logger.error('Initial database is failed：%s' % e)
            sys.exit()

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_conn(self):
        return self.dbconn

    def execute_create(self,query):
        logger.info('query：%s' % query)
        try:
            db_cursor = self.dbconn.cursor()
            db_cursor.execute(query)
            db_cursor.execute('commit')
            db_cursor.close()
            return True
        except Exception as e:
            logger.error('Create database is failed：%s' % e)
            db_cursor.execute('rollback')
            db_cursor.close()
            exit()

    def execute_insert(self, query, data=""):
        logger.info('query：%s  data：%s' % (query, data))
        try:
            db_cursor = self.dbconn.cursor()
            db_cursor.execute(query, data)
            db_cursor.execute('commit')
            db_cursor.close()
            return True
        except Exception as e:
            logger.error('Insert database is failed：%s' % e)
            db_cursor.execute('rollback')
            db_cursor.close()
            exit()

    def execute_update(self, query, data=""):
        #query = query % data
        logger.info('query：%s' % query)
        try:
            db_cursor = self.dbconn.cursor()
            db_cursor.execute(query)
            db_cursor.execute('commit')
            db_cursor.close()
            return ('',True)
        except Exception as e:
            logger.error('update database is failed：%s' % e)
            db_cursor.execute('rollback')
            db_cursor.close()
            return (e, False)

    def select_one_record(self, query, data=""):

        logger.info('query：%s  data：%s' % (query, data))
        try:
            db_cursor = self.dbconn.cursor(dictionary=True)
            if data:
                db_cursor.execute(query, data)
            else:
                db_cursor.execute(query)
            query_result = db_cursor.fetchone()
            db_cursor.close()
            return (query_result,True)
        except Exception as e:
            logger.error('query database is failed：%s' % e)
            db_cursor.close()
            return(e,False)

    def select_many_record(self, query, data=""):

        logger.info('query：%s  data：%s' % (query, data))
        try:
            db_cursor = self.dbconn.cursor(dictionary=True)
            if data:
                db_cursor.execute(query, data)
            else:
                db_cursor.execute(query)
            query_result = db_cursor.fetchall()
            db_cursor.close()
            return query_result
        except Exception as e:
            logger.error('query database is failed：%s' % e)
            db_cursor.close()
            exit()

    def close(self):
        self.dbconn.close



