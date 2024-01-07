'''
native os-related util
@aut
'''

import os
import errno

from py import my_cmd_handler
from py import my_logger

_g_mod_name = "os_util"

_G_MY_PLATFORM_OS_ID_LIST = [
    "ubuntu",
    "centos"
]

_G_MY_PLATFORM_KEYWORD = [
    "VERSION_ID",
    "ID"
]

_g_logger = my_logger.get_logger(name=_g_mod_name,
                                                level=my_logger.G_LOG_LEVEL_INFO,
                                                is_persist=False)
_g_cmd_handler = my_cmd_handler.CmdHandler(handler_name=_g_mod_name)

def get_current_os_release():
    '''
    get os release info

    Args:
        None
    Returns:
        dict mapping attr --> info
        "ID": ubuntu, centos
        "VERSION_ID":
            ubuntu: 20.04, 22.04
            centos: 8
        err with None
    '''
    cmd = "cat /etc/os-release"
    output, error_output, returncode = _g_cmd_handler.run_shell(cmd=cmd)
    os_info = {}

    if (returncode == 0):
        lines = output.splitlines()
        for line in lines:
            line = line.replace("\"", "").replace(" ", "")
            if line.find("=") == -1:
                continue
            else:
                for attr in _G_MY_PLATFORM_KEYWORD:
                    if attr == line[:line.find("=")]:
                        os_info[attr] = line[line.find("=") + 1:]
    else:
        _g_logger.error("get current os release failed: %s" % error_output)
        return None

    return os_info

def check_if_file_exits(path: str):
    '''
    check file exists

    Args:
        path: file path

    Returns:
        True: exist
        False: not exist
    '''
    if (os.path.exists(path)):
        return True
    else:
        return False

def translate_linux_err_code(err_code: int):
    '''
    translate error code to str

    Args:
        err_code: input error code

    Returns:
        err_str: string of this err code
    '''
    is_std_linux_err_code = err_code in errno.errorcode

    if (is_std_linux_err_code):
        return os.strerror(err_code)
    else:
        return "not standard linux err code: {}".format(err_code)