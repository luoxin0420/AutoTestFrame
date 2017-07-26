__author__ = 'Xuxh'

global CONFIGURATONINI
from library.mylog import log
from library.db import dbmysql

CONFIGURATONINI = "config/configuration.ini"
CONFIGUI = "config/uiconfig.ini"

logsignleton = log.LogSignleton('../config/logconfig.ini')
logger = logsignleton.get_logger()

autodb = dbmysql.MysqlDB('../config/dbconfig.ini')