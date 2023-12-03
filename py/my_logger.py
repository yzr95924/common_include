#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
native logging lib
"""

import os
import logging
from logging import handlers as logging_handler
import threading
import sys
import traceback
import inspect
import re

from py import util
from py import cmd_handle

_G_DEBUG_LOG_FNAME = "debug.log"
_G_INFO_LOG_FNAME = "info.log"
_G_WARNING_LOG_FNAME = "warning.log"
_G_ERR_LOG_FNAME = "error.log"
_G_ROTATE_LOG_MAX_BYTES = 1024 * 1024 * 10
_G_ROTATE_LOG_BACKUP_COUNT = 5
_G_SKIP_CONSOLE = "skip_console"
_G_STDOUT_KEY = "@stdout@: "
_G_ERROR_KEY = "@error@: "

_G_SRC_FILE = util.get_format_cur_filename(__file__)
_G_FMT_NORMAL = "%(levelname)s: %(message)s"
_G_FMT_QUIET = "%(message)s"
_G_FMT_FULL = ("[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)s:%(funcName)s] %(message)s")
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
G_COLOR_WARNING = "WARNING"
G_COLOR_INFO = "INFO"
G_COLOR_DEBUG = "DEBUG"
G_COLOR_CRITICAL = "CRITICAL"
G_COLOR_ERROR = "ERROR"
G_COLOR_RED = "RED"
G_COLOR_GREEN = "GREEN"
G_COLOR_YELLOW = "YELLOW"
G_COLOR_LIGHT_BLUE = "LIGHT_BLUE"
G_COLOR_TABLE_FIELDNAME = "TABLE_FIELDNAME"

_G_COLORS_TBL = {
    G_COLOR_WARNING: _G_COLOR_SEQ_YELLOW,
    G_COLOR_INFO: _G_COLOR_SEQ_LIGHT_BLUE,
    G_COLOR_DEBUG: _G_COLOR_SEQ_GREY,
    G_COLOR_CRITICAL: _G_COLOR_SEQ_RED,
    G_COLOR_ERROR: _G_COLOR_SEQ_RED,
    G_COLOR_LIGHT_BLUE: _G_COLOR_SEQ_LIGHT_BLUE,
    G_COLOR_RED: _G_COLOR_SEQ_RED,
    G_COLOR_GREEN: _G_COLOR_SEQ_GREEN,
    G_COLOR_YELLOW: _G_COLOR_SEQ_YELLOW,
    G_COLOR_TABLE_FIELDNAME: _G_COLOR_SEQ_CYAN,
}

_G_COLOR_SEQS = [_G_COLOR_SEQ_RESET]
for color_seq in _G_COLORS_TBL.values():
    if color_seq not in _G_COLOR_SEQS:
        _G_COLOR_SEQS.append(color_seq)

def get_colorful_msg(color, msg):
    """
    return colorful message
    """
    if color not in _G_COLORS_TBL:
        return str(msg)
    return _G_COLORS_TBL[color] + str(msg) + _G_COLOR_SEQ_RESET

def _get_msg_without_color(msg):
    """
    remove ANSI color/style sequences from a string
    '\x1b[K', '\x1b[m', '\x1b[0m'
    """
    return re.sub('\x1b\\[(K|.*?m)', '', msg)

def _find_caller(src_file: str):
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

def _decide_print_record_to_console(record: logging.LogRecord):
    """
    check record flag --> do not print to console for log filter
    """
    if _G_SKIP_CONSOLE in record.__dict__:
        skip_console = record.__dict__[_G_SKIP_CONSOLE]
        if skip_console:
            return False
    return True

def _get_message(msg, args):
    """
    get and valid the message
    """
    try:
        msg = str(msg)
        if args:
            msg = msg % args # convert placeholder to str
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        sys.stderr.write("log error: %s" % traceback.format_exc())
        sys.stderr.write("msg: %r\n, args: %s\n" % (msg, args))
        msg = "==== LOG ERROR ====\n"
    return msg

class ColorfulLogFormatter(logging.Formatter):
    """
    colorful log formatter
    """
    def __init__(self, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, record):
        levelname = record.levelname
        if levelname in _G_COLORS_TBL:
            levelname_color = get_colorful_msg(levelname, levelname)
            record.levelname = levelname_color
        text = logging.Formatter.format(self, record)
        record.levelname = levelname
        return text

class MyLogRecord():
    """
    a log record in MyLog
    """
    def __init__(self, level, msg, is_stdout=False, is_raw_stderr=False):
        self._mlr_level = level # e.g., logging.Info
        self._mlr_msg = msg
        self._mlr_is_stdout = is_stdout
        self._mlr_is_raw_stderr = is_raw_stderr # do not add format prefix

    def mlr_log_func(self, my_log):
        """
        print itself to the log
        """
        if self._mlr_is_stdout:
            my_log.ml_stdout(self._mlr_msg)
        elif self._mlr_is_raw_stderr:
            my_log.ml_raw_stderr(self._mlr_msg)
        else:
            my_log.ml_log(self._mlr_level, self._mlr_msg)

class MyLog():
    """
    log the output of a command
    """
    def __init__(self, name=None, result_dir=None, console_fmt=_G_FMT_FULL,
        condition=None, stdout_color=None, stderr_color=None, remember_records=False,
        stdout=None, stderr=None):
        self._ml_name = name # log name
        self._ml_result = cmd_handle.CmdResult()
        self.ml_result_dir = result_dir # result file stored in the dir
        self.ml_console_fmt = console_fmt # log format
        self._ml_logger: logging.Logger = None # the logger used inside
        if condition is not None:
            self._ml_condition = condition # lock for this log instance record list
        else:
            self._ml_condition = threading.Condition()
        self._ml_debug_handler = None
        self._ml_info_handler = None
        self._ml_warning_handler = None
        self._ml_error_handler = None
        self._ml_console_handler = None
        self._ml_stdout_color = stdout_color # print colorful msg to stdout
        self._ml_stderr_color = stderr_color # print colorful msg to stderr
        if remember_records:
            self._ml_records = [] # list of MyLogRecord
        else:
            self._ml_records = None
        if stdout is None:
            self._ml_sys_stdout = sys.stdout
        else:
            self._ml_sys_stdout = stdout
        if stderr is None:
            self._ml_sys_stderr = sys.stderr
        else:
            self._ml_sys_stderr = stderr

    def ml_set_log_propagate_func(self):
        self._ml_logger.propagate = True

    def ml_clear_log_propagate_func(self):
        self._ml_logger.propagate = False

    def ml_get_child_log_func(self, name, result_dir=None, console_fmt=_G_FMT_FULL,
        overwrite=False, condition=None):
        """
        get a child log, if overwrite, the existing log will be overwritten
        """
        if self._ml_name is not None:
            name = self._ml_name + "." + name
        return get_log(name=name, result_dir=result_dir, console_fmt=console_fmt,
            overwrite=overwrite, condition=condition)

    def ml_config_func(self, console_level=logging.INFO):
        """
        config the log
        """
        result_dir = self.ml_result_dir
        name = self._ml_name
        console_fmt = self.ml_console_fmt
        default_formatter = logging.Formatter(_G_FMT_FULL, _G_DATE_FMT)

        if self._ml_stderr_color is None:
            self._ml_stderr_color = self._ml_sys_stderr.isatty()

        if self._ml_stdout_color is None:
            self._ml_stdout_color = self._ml_sys_stdout.isatty()
        colorful = self._ml_stderr_color or self._ml_stdout_color

        # check console_formatter
        if console_fmt == _G_FMT_QUIET:
            console_formatter = logging.Formatter(_G_FMT_QUIET, _G_DATE_FMT)
        elif console_fmt == _G_FMT_FULL:
            if colorful:
                console_formatter = ColorfulLogFormatter(console_fmt, _G_DATE_FMT)
            else:
                console_formatter = logging.Formatter(console_fmt, _G_DATE_FMT)
        else:
            if colorful:
                console_formatter = ColorfulLogFormatter(console_fmt, _G_DATE_FMT)
            else:
                console_formatter = logging.Formatter(console_fmt, _G_DATE_FMT)

        if result_dir is not None:
            # debug log
            fpath = os.path.join(result_dir, _G_DEBUG_LOG_FNAME)
            debug_handler = logging_handler.RotatingFileHandler(fpath,
                maxBytes=_G_ROTATE_LOG_MAX_BYTES, backupCount=_G_ROTATE_LOG_BACKUP_COUNT)
            debug_handler.setLevel(logging.DEBUG)
            debug_handler.setFormatter(default_formatter)

            # info log
            fpath = os.path.join(result_dir, _G_INFO_LOG_FNAME)
            info_handler = logging_handler.RotatingFileHandler(fpath,
                maxBytes=_G_ROTATE_LOG_MAX_BYTES, backupCount=_G_ROTATE_LOG_BACKUP_COUNT)
            info_handler.setLevel(logging.INFO)
            info_handler.setFormatter(default_formatter)

            # warning log
            fpath = os.path.join(result_dir, _G_WARNING_LOG_FNAME)
            warning_handler = logging_handler.RotatingFileHandler(fpath,
                maxBytes=_G_ROTATE_LOG_MAX_BYTES, backupCount=_G_ROTATE_LOG_BACKUP_COUNT)
            warning_handler.setLevel(logging.WARNING)
            warning_handler.setFormatter(default_formatter)

            # error log
            fpath = os.path.join(result_dir, _G_ERR_LOG_FNAME)
            error_handler = logging_handler.RotatingFileHandler(fpath,
                maxBytes=_G_ROTATE_LOG_MAX_BYTES, backupCount=_G_ROTATE_LOG_BACKUP_COUNT)
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(default_formatter)

        # config logger
        if name is None:
            logger = logging.getLogger()
        else:
            logger = logging.getLogger(name=name)

        logger.handlers = []
        logger.setLevel(logging.DEBUG)

        # register handler
        if name is None:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(console_level)
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            self._ml_console_handler = console_handler
            console_filter = logging.Filter()
            console_filter.filter = _decide_print_record_to_console
            self._ml_console_handler.addFilter(console_filter)

        if result_dir is not None:
            logger.addHandler(debug_handler)
            logger.addHandler(info_handler)
            logger.addHandler(warning_handler)
            logger.addHandler(error_handler)
            self._ml_debug_handler = debug_handler
            self._ml_info_handler = info_handler
            self._ml_warning_handler = warning_handler
            self._ml_error_handler = error_handler
        self._ml_logger = logger

    def ml_change_config_func(self, console_fmt=_G_FMT_FULL, result_dir=None):
        """
        change the config log
        """
        self.ml_result_dir = result_dir
        self.ml_console_fmt = console_fmt
        self.ml_config_func()

    def _ml_emit_func(self, name, level, filename, lineno, func, msg, skip_console=False):
        """
        emit a log
        """
        record_args = None
        exc_info = None
        extra = None
        if skip_console:
            extra = {_G_SKIP_CONSOLE: True}
        record = self._ml_logger.makeRecord(name=name, level=level, fn=filename,
                                        lno=lineno, msg=msg, args=record_args,
                                        exc_info=exc_info, func=func, extra=extra)
        self._ml_logger.handle(record)

    def _ml_append_record_func(self, level, msg, is_stdout=False, is_raw_stderr=False):
        """
        append the log the list
        """
        if self._ml_records is None:
            return
        record = MyLogRecord(level=level, msg=msg, is_stdout=is_stdout,
                            is_raw_stderr=is_raw_stderr)
        self._ml_condition.acquire()
        self._ml_records.append(record)
        self._ml_condition.release()

    def _ml_log_raw_func(self, level, msg, skip_console=False):
        """
        emit the raw log
        """
        try:
            filename, lineno, func = _find_caller(_G_SRC_FILE)
        except ValueError:
            filename, lineno, func = "(unknown file)", 0, "(unknown function)"

        name = self._ml_name
        self._ml_emit_func(name=name, level=level, filename=filename, lineno=lineno,
                    func=func, msg=msg, skip_console=skip_console)

    def _ml_log_func(self, level, msg, *args):
        """
        emit the log and handle the records
        """
        message = _get_message(msg, args)
        self._ml_append_record_func(level, msg=message)
        self._ml_log_raw_func(level, msg=message)

    def ml_debug_func(self, msg, *args):
        """
        print the debug log, but not stdout/stderr
        """
        self._ml_log_func(logging.DEBUG, msg, *args)

    def ml_info_func(self, msg, *args):
        """
        print the info log, but not stdout/stderr
        """
        self._ml_log_func(logging.INFO, msg, *args)

    def ml_warning_func(self, msg, *args):
        """
        print the warning log, but not stdout/stderr
        """
        self._ml_log_func(logging.WARN, msg, *args)

    def ml_error_func(self, msg, *args):
        """
        print the error log, but not stdout/stderr
        """
        self._ml_log_func(logging.ERROR, msg, *args)

    def ml_clean_log_func(self):
        """
        cleanup this log
        """
        return _cleanup_log(self)

    def ml_stdout_func(self, msg, *args):
        """
        print the message to stdout, log to info log and save to a file
        """
        message = _get_message(msg, args)
        colorless_message = _get_msg_without_color(msg=message)
        self._ml_append_record_func(logging.NOTSET, msg=colorless_message,
                                    is_stdout=True)
        self._ml_log_raw_func(logging.INFO, msg=_G_STDOUT_KEY + colorless_message,
                            skip_console=True)
        if self._ml_stdout_color:
            self._ml_sys_stdout.write(message + "\n")
        else:
            self._ml_sys_stdout.write(colorless_message + "\n")

    def ml_stderr_func(self, msg, *args):
        """
        print the message to stderr, log into error log and save to a file
        """
        message = _get_message(msg, args)
        colorless_message = _get_msg_without_color(msg=message)
        self._ml_append_record_func(logging.NOTSET, msg=message, is_raw_stderr=True)
        self._ml_log_raw_func(logging.ERROR, msg=colorless_message, skip_console=True)
        if self._ml_stderr_color:
            self._ml_sys_stderr.write(message + "\n")
        else:
            self._ml_sys_stderr.write(colorless_message + "\n")

class LogController():
    """
    control what logs have been allocated
    """
    def __init__(self):
        self._lc_condition = threading.Condition()
        self._lc_logs_map = {}
        self._lc_root_log = None #FIXME: root log??

    def lc_log_add_or_get_func(self, log: MyLog):
        """
        add a new log
        """
        name = log._ml_name
        old_log = None
        self._lc_condition.acquire()
        if name is None:
            if self._lc_root_log is not None:
                old_log = self._lc_root_log
                self._lc_condition.release()
                return old_log
            self._lc_root_log = log
        else:
            if name in self._lc_logs_map:
                old_log = self._lc_logs_map[name]
                self._lc_condition.release()
                return old_log
            self._lc_logs_map[name] = log
        self._lc_condition.release()
        return log

    def lc_log_cleanup_func(self, log: MyLog):
        """
        cleanup a log
        """
        name = log._ml_name
        self._lc_condition.acquire()
        if self._lc_root_log is log:
            self._lc_root_log = None
        elif name in self._lc_logs_map:
            del self._lc_logs_map[name]
        else:
            log.ml_warning_func("log [%s] doesn't exist when cleaning up, ignoring",
                                name)
        self._lc_condition.release()

_G_LOG_CONTROLLER = LogController()

def get_log(name=None, result_dir=None, console_fmt=_G_FMT_FULL,
    overwrite=False, condition=None, console_level=logging.INFO,
    stdout_color=None, stderr_color=None, remember_records=False) -> MyLog:
    """
    get the log
    if overwrite, the existing log will be overwritten
    """
    log = MyLog(name=name, result_dir=result_dir,
                console_fmt=console_fmt, condition=condition,
                stdout_color=stdout_color,
                stderr_color=stderr_color,
                remember_records=remember_records)
    old_log = _G_LOG_CONTROLLER.lc_log_add_or_get_func(log)
    if old_log is log:
        # new log --> config it
        old_log.ml_config_func(console_level=console_level)
    else:
        if not overwrite:
            reason = ("log with name [%s] already exists" % name)
            raise Exception(reason)

        # if config is not the same --> config it
        if (old_log.ml_result_dir != result_dir or
            old_log.ml_console_fmt != console_fmt):
            old_log.ml_change_config_func(console_fmt=console_fmt,
                                        result_dir=result_dir)
    return old_log

def _cleanup_log(log):
    """
    cleanup this log --> name can be re-used later
    """
    return _G_LOG_CONTROLLER.lc_log_cleanup_func(log)
