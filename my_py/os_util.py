'''
native os-related util
'''

import os
import errno
import socket
import json
import sys
import psutil
from threading import Thread

from my_py import cmd_handler
from my_py import logger

_g_mod_name = "os_util"
_g_is_dry_run = False
_g_is_debug = False

_G_MY_PLATFORM_OS_ID_LIST = [
    "ubuntu",
    "centos"
]

_G_MY_PLATFORM_KEYWORD = [
    "VERSION_ID",
    "ID"
]

_g_logger = logger.get_logger(name=_g_mod_name)
_g_cmd_handler = cmd_handler.CmdHandler(handler_name=_g_mod_name)


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
    output, error_output, returncode = _g_cmd_handler.run_shell(cmd=cmd,
                                                                is_debug=_g_is_debug,
                                                                is_dry_run=False)
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
        return "{}:{}".format(err_code, os.strerror(err_code))
    else:
        return "not standard linux err code: {}".format(err_code)


class Network:
    def get_ip_address():
        """get ip address

        Returns:
            ip_address: ip address in string
        """
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address


class FS:
    def check_if_file_exist(path: str):
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

    def delete_file_if_exist(path: str):
        if (not os.path.exists(path)):
            return 0

        cmd = "rm" + " " + path
        _, _, ret = _g_cmd_handler.run_shell(cmd=cmd,
                                             is_dry_run=_g_is_dry_run,
                                             is_debug=_g_is_debug)
        return ret

    def mkdir_p(path: str, is_root=False):
        if (is_root):
            cmd = "sudo mkdir -p" + " " + path
        else:
            cmd = "mkdir -p" + " " + path
        _, _, ret = _g_cmd_handler.run_shell(cmd=cmd,
                                             is_dry_run=_g_is_dry_run,
                                             is_debug=_g_is_debug)
        return ret

    def change_file_mode(file_path: str, mode: str):
        '''
        change file mode

        Args:
            file_path: input file path
            mode: mode in str e.g., "600"
        '''
        cmd = "chmod" + " " + mode + " " + file_path
        _, _, ret = _g_cmd_handler.run_shell(cmd=cmd,
                                             is_dry_run=_g_is_dry_run,
                                             is_debug=_g_is_debug)
        if (ret != 0):
            _g_logger.error("change file ({}) mode failed: {}".format(
                file_path,
                translate_linux_err_code(ret)
            ))
            return ret
        return ret

    def rm_file(file_path: str):
        cmd = "rm" + " " + file_path
        _, _, ret = _g_cmd_handler.run_shell(cmd=cmd,
                                             is_dry_run=_g_is_dry_run,
                                             is_debug=_g_is_debug)
        if (ret != 0):
            _g_logger.error("remove file ({}) failed: {}".format(
                file_path,
                translate_linux_err_code(ret)
            ))
            return ret
        return ret

    def write_str_to_file(input_data: str, file_path: str, is_append: bool):
        ret = 0
        if (is_append):
            cmd = "echo" + " " + input_data + " " + ">>" + " " + \
                file_path
        else:
            cmd = "echo" + " " + input_data + " " + ">" + " " + \
                file_path
        _, _, ret = _g_cmd_handler.run_shell(cmd=cmd,
                                             is_dry_run=_g_is_dry_run,
                                             is_debug=_g_is_debug)
        if (ret != 0):
            _g_logger.error("write str to file ({}) failed: {}".format(
                file_path,
                translate_linux_err_code(ret)
            ))
            return ret
        return ret

    def is_folder_mount(mount_point: str):
        if (os.path.ismount(mount_point)):
            return True
        else:
            return False


class Permission:
    def is_current_root():
        current_uid = os.getuid()
        if (current_uid == 0):
            return True
        else:
            return False


class ThreadWithRet(Thread):
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        super().join()
        return self._return


class ProcessStat:
    def find_process_with_keyword(keyword: str, is_exact_match=False):
        """find the pid with keyword

        Args:
            keyword (str): input keyword
            is_exact_match (bool, optional): exact match the keyword. Defaults to False.

        Returns:
            pid_list: the pid of the input keyword
        """
        pid_list = []
        for cur_process in psutil.process_iter():
            if (is_exact_match):
                if (keyword.lower() == cur_process.name()):
                    pid_list.append(cur_process.pid)
            else:
                if (keyword.lower() in cur_process.name()):
                    pid_list.append(cur_process.pid)
        return pid_list

class Config:
    def load_json_config(config_path: str):
        """load json config and return dict

        Args:
            config_path (str): path of config file

        Returns:
            json_data: json data in dict
        """
        json_data = {}
        _g_logger.info("start to load json file: {}".format(config_path))
        try:
            with open(config_path, "r") as json_file:
                json_data = json.load(json_file)
        except FileNotFoundError:
            _g_logger.error("json file not found: {}".format(config_path))
            sys.exit(errno.EEXIST)
        except PermissionError:
            _g_logger.error("json file permission error: {}".format(config_path))
            sys.exit(errno.EPERM)
        except json.JSONDecoder:
            _g_logger.error("json file decode failed: {}".format(config_path))
            sys.exit(errno.EIO)
        except Exception as e:
            _g_logger.error("load json file with exception: {}".format(str(e)))
            sys.exit(errno.EIO)

        _g_logger.info("load json file done: {}".format(config_path))
        return json_data