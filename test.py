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
    cmd_handler.run_shell("ls")

    text = "hello world"
    print(common_tool.Color.set_text(text, common_tool.Color.RED))

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

    os_info = os_util.get_current_os_release()
    print(os_info)

    key_str = "test_key"
    key_bytes = crypto_tool.AESCipher.derive_key_from_str(key_str)
    in_file_path = "./test.log"
    abs_in_file_path = os.path.abspath(in_file_path)
    out_file_path = "./test.log.enc"
    abs_out_file_path = os.path.abspath(out_file_path)
    abs_final_file_path = os.path.abspath("./test.log.dec")

    returncode = crypto_tool.AESCipher.encrypt_with_key(abs_in_file_path, key_bytes, abs_out_file_path)
    returncode = crypto_tool.AESCipher.decrypt_with_key(abs_out_file_path, key_bytes, abs_final_file_path)
