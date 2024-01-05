'''
native os-related util
'''

import platform

from py import my_cmd_handler
from py import my_logger

_G_PLATFORM_MOD_NAME = "my_platform"

_G_MY_PLATFORM_OS_ID_LIST = [
    "ubuntu",
    "centos"
]

_G_MY_PLATFORM_KEYWORD = [
    "VERSION_ID",
    "ID"
]

_G_PLATFORM_LOGGER = my_logger.get_logger(name=_G_PLATFORM_MOD_NAME,
                                                level=my_logger.G_LOG_LEVEL_INFO,
                                                is_persist=True)
_G_PLATFORM_CMD = my_cmd_handler.CmdHandler(handler_name=_G_PLATFORM_MOD_NAME)

def get_current_os_release():
    cmd = "cat /etc/os-release"
    output, error_output, returncode = _G_PLATFORM_CMD.run_shell(cmd=cmd)

    if returncode == 0:
        lines = output.splitlines()
        for line in lines:
            line = line.replace("\"", "")
            if line.find("=") == -1:
                continue
            else:
                for attr in _G_MY_PLATFORM_KEYWORD:
                    if attr == line[:line.find("=")]:
                        print(attr)

    else:
        return None