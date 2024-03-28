#!/usr/bin/python3
# -*- coding: utf-8 -*-

from my_py import logger
from my_py import cmd_handler
from my_py import common_tool
from my_py import crypto_tool
from my_py import os_util

import platform
import os
import base64

def test_func():
    info_logger = logger.get_logger("test", logger.G_LOG_LEVEL_INFO,
                                        True)
    info_logger.info("test")
    info_logger.error("test")

if __name__ == "__main__":
    test_func()
    cmd_handler = cmd_handler.CmdHandler(handler_name="test")
    cmd_handler.run_shell("ls", is_debug=False, is_verbose=False)
    print(os_util.get_current_os_release())