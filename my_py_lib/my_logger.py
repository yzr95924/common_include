#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
native logging lib
"""

import os
import logging
import threading
import sys
import traceback
import inspect
import re
import typing

from my_py_lib import util
from my_py_lib import cmd_handle

_G_DEBUG_LOG_FNAME = "debug.log"
_G_INFO_LOG_FNAME = "info.log"
_G_WARNING_LOG_FNAME = "warning.log"
_G_ERR_LOG_FNAME = "error.log"

_G_SRC_FILE = util.get_format_cur_filename(__file__)
_G_FMT_NORMAL = "%(levelname)s: %(message)s"
_G_FMT_QUIET = "%(message)s"
_G_FMT_FULL = ("[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)s] %(message)s")
_G_FMT_TIME = "[%(asctime)s][%(levelname)s] %(message)s"
_G_DATE_FMT = "%Y/%m/%d-%H:%M:%S"

# Sequences need to get colored ouput
_G_COLOR_SEQ_BLACK = '\033[0;30m'
_G_COLOR_SEQ_RED = '\033[0;31m'
_G_COLOR_SEQ_GREEN = '\033[0;32m'
_G_COLOR_SEQ_BROWN = '\033[0;33m'
_G_COLOR_SEQ_BLUE = '\033[0;34m'
_G_COLOR_SEQ_PURPLE = '\033[0;35m'
_G_COLOR_SEQ_CYAN = '\033[0;36m'
_G_COLOR_SEQ_GREY = '\033[0;37m'
_G_COLOR_SEQ_DARK_GREY = '\033[1;30m'
_G_COLOR_SEQ_LIGHT_RED = '\033[1;31m'
_G_COLOR_SEQ_LIGHT_GREEN = '\033[1;32m'
_G_COLOR_SEQ_YELLOW = '\033[1;33m'
_G_COLOR_SEQ_LIGHT_BLUE = '\033[1;34m'
_G_COLOR_SEQ_LIGHT_PURPLE = '\033[1;35m'
_G_COLOR_SEQ_LIGHT_CYAN = '\033[1;36m'
_G_COLOR_SEQ_WHITE = '\033[1;37m'
_G_COLOR_SEQ_RESET = "\033[0m"

# The exported colors, do not use sequences out of this list
_G_COLOR_WARNING = "WARNING"
_G_COLOR_INFO = "INFO"
_G_COLOR_DEBUG = "DEBUG"
_G_COLOR_CRITICAL = "CRITICAL"
_G_COLOR_ERROR = "ERROR"
_G_COLOR_RED = "RED"
_G_COLOR_GREEN = "GREEN"
_G_COLOR_YELLOW = "YELLOW"
_G_COLOR_LIGHT_BLUE = "LIGHT_BLUE"
_G_COLOR_TABLE_FIELDNAME = "TABLE_FIELDNAME"

_G_COLORS_TBL = {
    _G_COLOR_WARNING: _G_COLOR_SEQ_YELLOW,
    _G_COLOR_INFO: _G_COLOR_SEQ_LIGHT_BLUE,
    _G_COLOR_DEBUG: _G_COLOR_SEQ_GREY,
    _G_COLOR_CRITICAL: _G_COLOR_SEQ_RED,
    _G_COLOR_ERROR: _G_COLOR_SEQ_RED,
    _G_COLOR_LIGHT_BLUE: _G_COLOR_SEQ_LIGHT_BLUE,
    _G_COLOR_RED: _G_COLOR_SEQ_RED,
    _G_COLOR_GREEN: _G_COLOR_SEQ_GREEN,
    _G_COLOR_YELLOW: _G_COLOR_SEQ_YELLOW,
    _G_COLOR_TABLE_FIELDNAME: _G_COLOR_SEQ_CYAN,
}

_G_COLOR_SEQS = [_G_COLOR_SEQ_RESET]
for color_seq in _G_COLORS_TBL.values():
    if color_seq not in _G_COLOR_SEQS:
        _G_COLOR_SEQS.append(color_seq)

def get_colorful_msg(color, message):
    """
    return colorful message
    """
    if color not in _G_COLORS_TBL:
        return str(message)
    return _G_COLORS_TBL[color] + str(message) + _G_COLOR_SEQ_RESET

def get_msg_without_color(message):
    """
    remove ANSI color/style sequences from a string
    '\x1b[K', '\x1b[m', '\x1b[0m'
    """
    return re.sub('\x1b\\[(K|.*?m)', '', message)

def find_caller(src_file: str):
    """
    find the stack frame of the caller
    """
    cur_frame = inspect.currentframe()
    if cur_frame is not None:
        cur_frame = cur_frame.f_back
    ret = "(unknown file)", 0, "(unknown function)"
    while hasattr(cur_frame, "f_code"):
        code_object = cur_frame.f_code
        filename = os.path.normcase(code_object.co_filename)
        if filename.startswith("/"):
            if filename == src_file:
                cur_frame = cur_frame.f_back
                continue
        else:
            if src_file.endswith(filename):
                cur_frame = cur_frame.f_back
                continue
        ret = (code_object.co_filename, cur_frame.f_lineno, code_object.co_name)
        break
    return ret

class ColorfulLogFormatter(logging.Formatter):
    """
    colorful log formatter
    """
    def __init__(self, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, log_record):
        levelname = log_record.levelname
        if levelname in _G_COLORS_TBL:
            levelname_color = get_colorful_msg(levelname, levelname)
            log_record.level = levelname_color
        text = logging.Formatter.format(self, log_record)
        log_record.levelname = levelname
        return text

class MyLogRecord():
    """
    a log record in MyLog
    """
    def __init__(self, level, message, is_stdout=False, is_raw_stderr=False):
        self.mlr_level = level # e.g., logging.Info
        self.mlr_message = message
        self.mlr_is_stdout = is_stdout
        self.mlr_is_raw_stderr = is_raw_stderr # do not add format prefix

    def mlr_log_func(self, my_log):
        """
        print itself to the log
        """
        if self.mlr_is_stdout:
            my_log.ml_stdout(self.mlr_message)
        elif self.mlr_is_raw_stderr:
            my_log.ml_raw_stderr(self.mlr_message)
        else:
            my_log.ml_log(self.mlr_level, self.mlr_message)

class MyLog():
    """
    log the output of a command
    """
    def __init__(self, name=None, result_dir=None, console_fmt=_G_FMT_FULL,
        condition=None, stdout_color=None, stderr_color=None, remember_records=False,
        stdout=None, stderr=None):
        self.ml_name = name
        self.ml_result = cmd_handle.CmdResult()
        self.ml_result_dir = result_dir
        self.ml_console_fmt = console_fmt
        self.ml_logger: logging.Logger = None
        if condition is not None:
            self.my_condition = condition
        else:
            self.my_condition = threading.Condition()
        self.ml_debug_handler = None
        self.ml_info_handler = None
        self.ml_warning_handler = None
        self.ml_error_handler = None
        self.ml_console_handler = None
        self.ml_stdout_color = stdout_color # print colorful msg to stdout
        self.ml_stderr_color = stderr_color # print colorful msg to stderr
        # list of MyLogRecord
        if remember_records:
            self.ml_records = []
        else:
            self.ml_records = None
        if stdout is None:
            self.ml_sys_stdout = sys.stdout
        else:
            self.ml_sys_stdout = stdout
        if stderr is None:
            self.ml_sys_stderr = sys.stderr
        else:
            self.ml_sys_stderr = stderr

    def ml_set_log_propagate_func(self):
        self.ml_logger.propagate = True

    def ml_clear_log_propagate_func(self):
        self.ml_logger.propagate = False

        #TODO: fix here

class LogController():
    """
    control what logs have been allocated
    """
    def __init__(self):
        self.lc_condition = threading.Condition()
        self.lc_logs_map = {}
        self.lc_root_log = None #FIXME: root log??

    def lc_log_add_or_get_func(self, log: MyLog):
        """
        add a new log
        """
        name = log.ol_name
        old_log = None
        self.lc_condition.acquire()
        if name is None:
            if self.lc_root_log is not None:
                old_log = self.lc_root_log
                self.lc_condition.release()
                return old_log
            self.lc_root_log = log
        else:
            if name in self.lc_logs_map:
                old_log = self.lc_logs_map[name]
                self.lc_condition.release()
                return old_log
            self.lc_logs_map[name] = log
        self.lc_condition.release()
        return log

    def lc_log_cleanup_func(self, log: MyLog):
        """
        cleanup a log
        """
        name = log.ol_name
        self.lc_condition.acquire()
        if self.lc_root_log is log:
            self.lc_root_log = None
        elif name in self.lc_logs_map:
            del self.lc_logs_map[name]
        else:
            #TODO:
            pass
        self.lc_condition.release()

_G_LOG_CONTROLLER = LogController()
