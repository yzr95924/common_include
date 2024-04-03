#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess
import time
import select
import selectors
import fcntl
import os
import threading
import errno
import signal
from typing import Dict

from my_py import logger
from my_py import common_tool

_g_mod_name = "cmd_handler"
_g_logger = logger.get_logger(name=_g_mod_name)
_g_running_subprocess_map: Dict[str, subprocess.Popen]= {}
_g_running_subprocess_map_lock = threading.Lock()
_g_interrupt_enable = False
_g_interrupt_lock = threading.Lock()


def keyboard_interrupt_handler(signal, frame):
    """keyboard interrupt handler

    Args:
        signal (_type_): signal
        frame (_type_): frame
    """
    _g_logger.warning("receive ctrl+c interrupt, stop all running sub-process")
    _g_running_subprocess_map_lock.acquire()
    for cmd in list(_g_running_subprocess_map.keys()):
        if (_g_running_subprocess_map[cmd].poll() is not None):
            del _g_running_subprocess_map[cmd]
        else:
            _g_running_subprocess_map[cmd].terminate()
            _g_logger.warning("terminate: {}".format(
                common_tool.Color.set_text(cmd, common_tool.Color.BLUE)))
            del _g_running_subprocess_map[cmd]
    _g_running_subprocess_map_lock.release()


def set_keyboard_interrupt():
    """set the keyboard interrupt handler

    Returns:
        ret_code: return code
    """
    global _g_interrupt_enable, _g_interrupt_lock
    _g_interrupt_lock.acquire()
    signal.signal(signal.SIGINT, keyboard_interrupt_handler)
    _g_logger.info("set keyboard interrupt")
    _g_interrupt_enable = True
    _g_interrupt_lock.release()
    return 0


def remove_keyboard_interrupt():
    """remove keyboard interrupt handler

    Returns:
        ret_code: return code
    """
    global _g_interrupt_enable, _g_interrupt_lock
    _g_interrupt_lock.acquire()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    _g_logger.info("remove keyboard interrupt")
    _g_interrupt_enable = False
    _g_interrupt_lock.release()
    return 0


def output_reader_thd(process: subprocess.Popen,
                      stdout_buf: bytearray,
                      stderr_buf: bytearray,
                      is_verbose=False):
    """thread of reading output

    Args:
        process (subprocess.Popen): input process
        stdout_buf (bytearray): buffer of stdout
        stderr_buf (bytearray): buffer of stderr

    Returns:
        None
    """
    local_selector = selectors.DefaultSelector()
    local_selector.register(process.stdout, selectors.EVENT_READ)
    local_selector.register(process.stderr, selectors.EVENT_READ)

    while True:
        events = local_selector.select()
        for key, _ in events:
            if (key.fileobj == process.stdout):
                data = process.stdout.read()
                if (len(data.strip()) != 0):
                    if (is_verbose):
                        print(data.strip())
                    stdout_buf.extend("{}".format(data.strip()).encode(
                        common_tool._g_encode_fmt))
            if (key.fileobj == process.stderr):
                data = process.stderr.read()
                if (len(data.strip()) != 0):
                    if (is_verbose):
                        print(data.strip())
                    stderr_buf.extend("{}".format(data.strip()).encode(
                        common_tool._g_encode_fmt))
        if (process.poll() is not None):
            break
    return None

def set_stdout_stderr_non_block(process: subprocess.Popen):
        """set stdout and stderr of a process

        Args:
            process (subprocess.Popen): input process
        """
        stdout_fd = process.stdout.fileno()
        stderr_fd = process.stderr.fileno()
        stdout_flags = fcntl.fcntl(stdout_fd, fcntl.F_GETFL)
        stderr_flags = fcntl.fcntl(stderr_fd, fcntl.F_GETFL)
        fcntl.fcntl(stdout_fd, fcntl.F_SETFL, stdout_flags | os.O_NONBLOCK)
        fcntl.fcntl(stderr_fd, fcntl.F_SETFL, stderr_flags | os.O_NONBLOCK)
        return None


class CmdHandler():
    def __init__(self, handler_name: str = "cmd",
                 log_level=logger.G_LOG_LEVEL_DEBUG, is_persist=False):
        self._handler_name = handler_name
        self.logger = logger.get_logger(name=handler_name + "_cmd",
                                        log_file_level=log_level,
                                        is_persist=is_persist)
        self.print_lock = threading.Lock()

    def run_shell(self, cmd: str, timeout=0,
                  is_dry_run=False,
                  is_debug=False,
                  is_verbose=False):
        """run a shell command

        Args:
            cmd (str): shell command
            timeout (int, optional): timeout val, > timeout, exit. Defaults to 0.
            is_dry_run (bool, optional): only print command. Defaults to False.
            is_debug (bool, optional): print the output command after. Defaults to False.
            is_verbose (bool, optional): print output in real time. Defaults to False.

        Returns:
            stdout_buf: stdout buffer
            stderr_buf: stderr buffer
            ret_code: return code
        """
        local_is_verbose = is_verbose
        if is_dry_run:
            self.logger.info("DRY_RUN: {}".format(
                common_tool.Color.set_text(cmd, common_tool.Color.BLUE)))
            return None, None, 0

        if timeout < 0:
            self.logger.error("timeout is invalid")
            return None, None, -1

        if timeout > 0:
            local_is_verbose = True

        self.logger.info("run cmd: {}".format(
            common_tool.Color.set_text(cmd, common_tool.Color.BLUE)))
        process = subprocess.Popen(cmd, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)
        set_stdout_stderr_non_block(process)
        stdout_buf = bytearray()
        stderr_buf = bytearray()
        output_reader = threading.Thread(target=output_reader_thd, args=(
            process, stdout_buf, stderr_buf, local_is_verbose
        ))
        output_reader.start()

        _g_running_subprocess_map_lock.acquire()
        _g_running_subprocess_map[cmd] = process
        _g_running_subprocess_map_lock.release()

        if timeout > 0:
            # with timeout, set is_verbose to True
            start_time = time.time()
            while process.poll() is None:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    process.terminate()
                    process.wait()
                    output_reader.join()
                    self.logger.error("command execution timed out")
                    return None, None, errno.ETIMEDOUT
                time.sleep(0.1)

        # wait shell finishing
        ret_code = process.wait()
        output_reader.join()

        _g_running_subprocess_map_lock.acquire()
        if (cmd in _g_running_subprocess_map):
            del _g_running_subprocess_map[cmd]
        _g_running_subprocess_map_lock.release()

        self.print_lock.acquire()
        if ret_code == 0:
            if (is_debug and
                len(stdout_buf.decode(common_tool._g_encode_fmt).strip()) != 0):
                self.logger.info("run successful: {}\noutput: {}".format(
                    common_tool.Color.set_text(cmd, common_tool.Color.BLUE),
                    stdout_buf.decode(common_tool._g_encode_fmt).strip()))
            else:
                self.logger.info("run successful: {}".format(
                    common_tool.Color.set_text(cmd, common_tool.Color.BLUE)))
        else:
            # if error, print the error info
            if (len(stderr_buf.decode(common_tool._g_encode_fmt).strip()) == 0):
                self.logger.error("run failed: {}\nret: {}".format(
                    common_tool.Color.set_text(cmd, common_tool.Color.BLUE),
                    ret_code))
            else:
                self.logger.error("run failed: {}\nerror: {}\nret: {}".format(
                    common_tool.Color.set_text(cmd, common_tool.Color.BLUE),
                    stderr_buf.decode(common_tool._g_encode_fmt).strip(),
                    ret_code))
        self.print_lock.release()

        return (stdout_buf.decode(common_tool._g_encode_fmt).strip(),
                stderr_buf.decode(common_tool._g_encode_fmt).strip(),
                ret_code)