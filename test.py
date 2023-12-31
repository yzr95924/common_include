#!/usr/bin/python3
# -*- coding: utf-8 -*-

from py import my_logger
from py import my_cmd_handler
from py import util
from py import my_os_util

import platform

def test_func():
    info_logger = my_logger.get_logger("test", my_logger.G_LOG_LEVEL_INFO,
                                        True)
    info_logger.info("test")
    info_logger.error("test")

if __name__ == "__main__":
    test_func()
    cmd_handler = my_cmd_handler.CmdHandler(handler_name="test")
    cmd_handler.run_shell("ls")

    text = "hello world"
    print(util.Color.set_text(text, util.Color.RED))

    release = platform.release()
    version = platform.version()
    system = platform.system()
    release_os = platform.freedesktop_os_release()
    uname_os = platform.uname()

    print("release: %s" % release)
    print("version: %s" % version)
    print("system: %s" % system)
    print("release os: %s" % release_os["ID"])
    print(uname_os)

    os_info = my_os_util.get_current_os_release()
    print(os_info)