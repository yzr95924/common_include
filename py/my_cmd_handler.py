#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess
import time

from py import my_logger
from py import util

class CmdHandler():
    def __init__(self, handler_name: str="cmd",
                    log_level=my_logger.G_LOG_LEVEL_DEBUG, is_persist=False):
        self._handler_name = handler_name
        self.logger = my_logger.get_logger(name=handler_name + "_cmd",
                                        log_file_level=my_logger.G_LOG_LEVEL_DEBUG,
                                        is_persist=is_persist)

    def run_shell(self, cmd: str="", timeout=0, is_dry_run=False, is_debug=False):
        '''
        run a simple shell cmd, output its result

        Args:
            cmd:
                the cmd to execute
            timeout:
                the timeout, exceeds this will raise TimeoutError()
            is_dry_run:
                only print the cmd without real execution

        Returns:
            output:
                stdout output of the cmd
            error_output:
                stderr output of the cmd
            returncode:
                return code of the cmd
        '''
        if is_dry_run:
            self.logger.info("DRY_RUN: %s" % cmd)
            return None, None, 0

        if timeout < 0:
            self.logger.error("timeout is invalid")
            return None, None, -1

        self.logger.info("run cmd: {}".format(
            util.Color.set_text(cmd, util.Color.BLUE)))
        process = subprocess.Popen(cmd, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        if timeout != 0:
            # with timeout
            start_time = time.time()
            while process.poll() is None:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    process.terminate()
                    self.logger.error("command execution timed out")
                    raise TimeoutError()

                time.sleep(0.1)

        # check return code
        output, error_output = process.communicate()
        if process.returncode == 0:
            if is_debug:
                self.logger.info("run successful: {}\noutput: {}".format(
                    util.Color.set_text(cmd, util.Color.BLUE),
                    output.decode("utf-8")))
            else:
                self.logger.info("run successful: {}".format(
                    util.Color.set_text(cmd, util.Color.BLUE)))
        else:
            if is_debug:
                self.logger.error("run failed: {}\nerror: {}\nret: {}".format(
                    util.Color.set_text(cmd, util.Color.BLUE),
                    error_output.decode("utf-8"),
                    process.returncode))
            else:
                self.logger.error("run failed: {}".format(
                    util.Color.set_text(cmd, util.Color.BLUE)))

        return output.decode("utf-8"), error_output.decode("utf-8"), process.returncode