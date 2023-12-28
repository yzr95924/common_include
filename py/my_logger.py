#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import logging
from logging import handlers as logging_handler

_G_FMT_FULL = ("[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)s:%(funcName)s] %(message)s")

G_LOG_LEVEL_INFO = logging.INFO
G_LOG_LEVEL_ERROR = logging.ERROR
G_LOG_LEVEL_WARNING = logging.WARNING
G_LOG_LEVEL_DEBUG = logging.DEBUG
G_LOG_LEVEL_CRITICAL = logging.CRITICAL

class ColorHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()
        self._colors = {
            'DEBUG': '\033[94m',    # 蓝色
            'INFO': '\033[92m',     # 绿色
            'WARNING': '\033[93m',  # 黄色
            'ERROR': '\033[91m',    # 红色
            'CRITICAL': '\033[95m'  # 紫色
        }
        self._reset = '\033[0m'  # 重置颜色代码

    def format(self, record: logging.LogRecord):
        levelname = record.levelname
        colored_levelname = f'{self._colors.get(levelname, "")}{levelname}{self._reset}'

        # construct the final log
        record.levelname = colored_levelname
        return super().format(record)

def get_logger(name: str, level=G_LOG_LEVEL_DEBUG, is_persist: bool=False,
                log_file_level=G_LOG_LEVEL_DEBUG):
    ret_logger = logging.getLogger(name=name)
    ret_logger.setLevel(level=level)
    colored_handler = ColorHandler()
    colored_handler.setFormatter(logging.Formatter(_G_FMT_FULL))
    ret_logger.addHandler(colored_handler)

    if (is_persist):
        file_handler = logging.FileHandler(name + ".log", encoding="utf-8", mode="w")
        file_handler.setLevel(log_file_level)
        file_handler.setFormatter(logging.Formatter(_G_FMT_FULL))
        ret_logger.addHandler(file_handler)

    return ret_logger
