#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
sys.path.append(".") # if "py module" not in current dir

from py import my_logger

def test_func():
    info_logger = my_logger.get_logger("test", my_logger.G_LOG_LEVEL_INFO,
                                        True)
    info_logger.info("test")
    info_logger.error("test")

if __name__ == "__main__":
    test_func()