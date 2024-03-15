'''
setup my module
'''

from my_py import os_util
from my_py import crypto_tool
from my_py import common_tool

def init_dry_run_debug_flag(is_dry_run: bool, is_debug: bool):
    os_util._g_is_dry_run = is_dry_run
    os_util._g_is_debug = is_debug

    crypto_tool._g_is_dry_run = is_dry_run
    crypto_tool._g_is_debug = is_debug