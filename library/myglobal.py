__author__ = 'Xuxh'

import os

from library.mylog import log
from library import configuration

__all__= ['logger','theme_config','magazine_config','device_config']

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)
logsignleton = log.LogSignleton(PATH('../config/logconfig.ini'))
logger = logsignleton.get_logger()

# theme configuration file
theme_config = configuration.configuration()
fname = PATH('../config/theme.ini')
theme_config.fileConfig(fname)

# magazine configuration file
magazine_config = configuration.configuration()
fname = PATH('../config/magazine.ini')
magazine_config.fileConfig(fname)

# device config
device_config = configuration.configuration()
fname = PATH('../config/device.ini')
device_config.fileConfig(fname)



POSITIVE_VP_TYPE = ['CONTAIN', 'EQUAL', 'MATCH']
DEVICE_ACTION = [
            'network',
            'update_date',
            'reboot',
            'unlock_screen',
            'update_para',
            'install_app',
            'screen_on',
            'task_init_source']