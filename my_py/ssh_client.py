#!/usr/bin/python3
# -*- coding: utf-8 -*-

import paramiko
import errno

from my_py import logger
from my_py import common_tool

_g_mod_name = "ssh_client"
_g_logger = logger.get_logger(name=_g_mod_name)

class SSHCmd:
    def __init__(self, port: str, hostname: str, usr_name: str, pwd: str,
                 log_level=logger.G_LOG_LEVEL_DEBUG, is_persist=False):
        self._hostname: str = hostname
        self._port: str = port
        self._usr_name: str = usr_name
        self._pwd = pwd
        self._logger: logger.logging.Logger = logger.get_logger(name="{}@{}:{}".format(
            self._usr_name, self._hostname, self._port),
            log_file_level=log_level,
            is_persist=is_persist)
        self._ssh_client = paramiko.SSHClient()

    def connect(self):
        """connect to remote host

        Returns:
            ret_code: return code
        """
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._logger.info("start to setup connection")
        try:
            self._ssh_client.connect(hostname=self._hostname,
                                     port=self._port,
                                     username=self._usr_name,
                                     password=self._pwd)
        except paramiko.AuthenticationException:
            self._logger.error("authentication failed")
            return errno.EINVAL
        except paramiko.SSHException as ssh_exception:
            self._logger.error("ssh connection failed: {}".format(str(ssh_exception)))
            return errno.EIO

        self._logger.info("connection to host done")
        return 0

    def run_shell(self, cmd: str,
                  timeout=None,
                  is_debug=False,
                  is_dry_run=False):
        """run a shell command in remote host

        Args:
            cmd (str): shell command
            timeout (float, optional): timeout setting. Defaults to None.
            is_debug (bool, optional): only print command. Defaults to False.
            is_dry_run (bool, optional): print the output command after. Defaults to False.

        Returns:
            stdout_buf: stdout buffer
            stderr_buf: stderr buffer
            ret_code: return code
        """
        if (is_dry_run):
            self._logger.info("DRY_RUN: {}".format(
                common_tool.Color.set_text(cmd, common_tool.Color.BLUE)
            ))
            return None, None, 0

        self._logger.info("run cmd: {}".format(
            common_tool.Color.set_text(cmd, common_tool.Color.BLUE)
        ))
        _, stdout, stderr = self._ssh_client.exec_command(command=cmd,
                                                       timeout=timeout)
        ret_code = stdout.channel.recv_exit_status()
        stdout_buf = stdout.read().decode(common_tool._g_encode_fmt).strip()
        stderr_buf = stderr.read().decode(common_tool._g_encode_fmt).strip()

        if (ret_code == 0):
            if (is_debug and
                len(stdout_buf) != 0):
                self._logger.info("run successful: {}\noutput: {}".format(
                    common_tool.Color.set_text(cmd, common_tool.Color.BLUE),
                    stdout_buf))
            else:
                self._logger.info("run successful: {}".format(
                    common_tool.Color.set_text(cmd, common_tool.Color.BLUE)))
        else:
            # if error, print the error info
            if (len(stderr_buf) == 0):
                self._logger.error("run failed: {}\nret: {}".format(
                    common_tool.Color.set_text(cmd, common_tool.Color.BLUE),
                    ret_code))
            else:
                self._logger.error("run failed: {}\nerror: {}\nret: {}".format(
                    common_tool.Color.set_text(cmd, common_tool.Color.BLUE),
                    stdout_buf, ret_code))
        return (stdout_buf, stderr_buf, ret_code)

    def close(self):
        """close the connection
        """
        self._ssh_client.close()
        self._logger.info("close the connection done")

    def combine_multiple_cmd(self, cmd_list: list):
        """combine multiple shell cmd into a single string

        Args:
            cmd_list (list): cmd list

        Returns:
            final_cmd: final cmd
        """
        final_cmd = ""
        for cur_cmd in cmd_list:
            if (len(final_cmd) == 0):
                final_cmd = cur_cmd
            else:
                final_cmd = final_cmd + "; " + cur_cmd
        return final_cmd