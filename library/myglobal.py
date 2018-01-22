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

# wallpaper configuration file
wallpaper_config = configuration.configuration()
fname = PATH('../config/wallpaper.ini')
wallpaper_config.fileConfig(fname)

# device config
device_config = configuration.configuration()
fname = PATH('../config/device.ini')
device_config.fileConfig(fname)

html_config = configuration.configuration()
fname = PATH('../config/htmlconfig.ini')
html_config.fileConfig(fname)

# performance config
# device config
performance_config = configuration.configuration()
fname = PATH('../config/performance.ini')
performance_config.fileConfig(fname)

# testlink configuration file
testlink_config = configuration.configuration()
fname = PATH('../config/testlink.ini')
testlink_config.fileConfig(fname)

resource_config = configuration.configuration()
fname = PATH('../config/resource.ini')
resource_config.fileConfig(fname)

module_config = configuration.configuration()
fname = PATH('../config/smoke_module.ini')
module_config.fileConfig(fname)

POSITIVE_VP_TYPE = ['CONTAIN', 'EQUAL', 'MATCH', 'LESSTHAN', 'GREATERTHAN']
DEVICE_ACTION = [
            'network',
            'update_date',
            'reboot',
            'unlock_screen',
            'update_para',
            'install_app',
            'screen_on',
            'task_init_source']

TASK_COMPONENT = ['Task_NetChange', 'Task_NetChange_With_Reboot', 'Task_Timer', 'Task_Wallpaper_Visible',\
                  'Task_Screen_On', 'Task_Timer_Alarm', 'Self_Activation', 'Register',\
                  'Push_TaskType', 'Push_TimeInterval', 'Push_Switch', \
                  'Operation_Module_Upgrade']
PERFORMANCE_COMPONENT = ['Magazine_Monitor_Memory', 'Magazine_Monitor_CPU']
MODULE_COMPONENT = ['ModuleUpdate']