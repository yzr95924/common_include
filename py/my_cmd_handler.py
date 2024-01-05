#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess

from py import my_logger
from py import util

class CmdHandler():
    def __init__(self, handler_name: str="cmd",
                    log_level=my_logger.G_LOG_LEVEL_DEBUG):
        self._handler_name = handler_name
        self.logger = my_logger.get_logger(name=handler_name + "_cmd",
                                        log_file_level=my_logger.G_LOG_LEVEL_DEBUG,
                                        is_persist=True)

    def run_shell(self, cmd: str=""):
        '''
        run a simple shell cmd, output its result
        '''
        process = subprocess.Popen(cmd, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        output, error_output = process.communicate()
        if process.returncode == 0:
            self.logger.info("run successful: \ncmd: %s\noutput: %s" %
                            (util.Color.set_text(cmd, util.Color.BLUE),
                            output.decode("utf-8")))
        else:
            self.logger.error("run failed: \ncmd: %s\nerror: %s\n"
                                "ret: %d" % (util.Color.set_text(cmd, util.Color.BLUE),
                                error_output.decode("utf-8"),
                                process.returncode))
        return output.decode("utf-8"), error_output.decode("utf-8"), process.returncode