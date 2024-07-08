#! /usr/bin/python3
import serial
import threading
import time
import logging
import json
from gpsd_parser import GpsdParser
from observer import Observer


import logger


class TtyClient(threading.Thread):
    def __init__(self):
        super().__init__()

        self.tty_name = ""
        self.baudrate = 9600
        self.serial = None

        self.logger = logger.get_logger("ttyc")

    def set_params(self, tty_name, baudrate, observer):
        self.tty_name = tty_name
        self.baudrate = baudrate

        self.do_run = True

        self.parser = GpsdParser(observer)
        self.thread = None

    def connect(self):
        try:
            self.logger.info("trying to connect to %s", self.tty_name)
            self.serial = serial.Serial(self.tty_name, self.baudrate)
        except Exception as err:
            self.logger.error(f"connecting to tty failed: %s, %s", err, type(err))
            self.serial.close()
            self.serial = None
            return False
        return True

    def signalize_stop(self):
        self.do_run = False

    def run(self):
        self.logger.info("client thread: starting")

        while self.do_run:
            try:
                if self.serial == None:
                    while not self.connect():
                        if self.do_run:
                            self.logger.info("... retrying connection to tty ...")
                            time.sleep(1)
                        else:
                            self.logger.info("stopping retrying connection to tty ...")
                            return

                data = self.serial.read(20).decode("utf-8")
                # self.logger.debug(str(data))
                if len(data) > 0:
                    self.parser.add_data(data)
                else:
                    self.connect()
            except Exception as e:
                self.logger.error(f"unexpected: {e=}, {type(e)=}")
                break

        if self.serial != None:
            self.serial.close()

        self.logger.info("thread finishing")
