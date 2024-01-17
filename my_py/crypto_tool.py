#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
simple crypto tool for encryption, decryption, and hashing
'''

from my_py import logger
from my_py import cmd_handler
from my_py import os_util

import errno
import hashlib
import os

_g_mod_name = "crypto_tool"
_g_is_dry_run = False
_g_is_debug = False

_g_logger = logger.get_logger(name=_g_mod_name)
_g_cmd_handler = cmd_handler.CmdHandler(handler_name=_g_mod_name)

_g_tmp_path = "/tmp"

class Hasher:
    '''
    Hasher sha256
    '''
    def cal_sha256_hash(in_data: str):
        sha256_hash = hashlib.sha256(in_data.encode()).hexdigest()
        return sha256_hash.encode()


class AESCipher:
    '''
    AES cipher for encryption/decryption
    '''
    def encrypt_with_key(in_file_path: str, key_data: bytes, out_file_path: str):
        _g_logger.info("encrypt file: {}".format(in_file_path))
        if (not os_util.FS.check_if_file_exist(in_file_path)):
            _g_logger.error("input file cannot find")
            return errno.EEXIST

        ret = 0
        cmd = "openssl enc -aes-256-cbc" + " " + "-salt" + " " + \
            "-in" + " " + in_file_path + " " + \
            "-out" + " " + out_file_path + " " + \
            "-k" + " " + key_data.decode()
        _, _, ret = _g_cmd_handler.run_shell(cmd=cmd,
                                       is_dry_run=_g_is_dry_run,
                                       is_debug=_g_is_debug)
        if (ret != 0):
            _g_logger.error("enc file ({}) failed: {}".format(
                in_file_path, os_util.translate_linux_err_code(ret)))
            return ret
        return 0


    def decrypt_with_key(in_file_path: str, key_data: bytes, out_file_path: str):
        _g_logger.info("decrypt file: {}".format(in_file_path))
        if (not os_util.FS.check_if_file_exist(in_file_path)):
            _g_logger.error("input file cannot find")
            return errno.EEXIST

        ret = 0
        cmd = "openssl enc -aes-256-cbc" + " " + "-d" + " " + \
            "-in" + " " + in_file_path + " " + \
            "-out" + " " + out_file_path + " " + \
            "-k" + " " + key_data.decode()
        _, _, ret = _g_cmd_handler.run_shell(cmd=cmd,
                                       is_dry_run=_g_is_dry_run,
                                       is_debug=_g_is_debug)
        if (ret != 0):
            _g_logger.error("dec file ({}) failed: {}".format(
                in_file_path, os_util.translate_linux_err_code(ret)))
            return ret
        return 0
