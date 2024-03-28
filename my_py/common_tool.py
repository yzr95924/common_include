#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
common tool library (native python3 lib)
"""

import importlib

from my_py import logger

_g_mod_name = "common_tool"
_g_encode_fmt = "utf-8"
RETURN_OK = 0

class Color:
    # 字符串颜色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'

    def set_text(message: str, color_opt: str):
        return ("%s%s%s" % (color_opt, message, Color.RESET))

def is_module_exist(module_name: str):
    module_loader = importlib.find_loader(module_name)
    if (module_loader is not None):
        return True
    return False