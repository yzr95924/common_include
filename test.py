#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
sys.path.append(".") # if "py module" not in current dir

from py import my_logger
from py import my_cmd_handler
from py import util

def test_func():
    info_logger = my_logger.get_logger("test", my_logger.G_LOG_LEVEL_INFO,
                                        True)
    info_logger.info("test")
    info_logger.error("test")

if __name__ == "__main__":
    test_func()
    cmd_handler = my_cmd_handler.CmdHandler(handler_name="test_cmd")
    cmd_handler.run_shell("ls")

    text = "hello world"
    print(util.Color.set_text(text, util.Color.RED))