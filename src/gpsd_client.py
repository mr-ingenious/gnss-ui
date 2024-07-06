#! /usr/bin/python3

import socket
import threading
import time
import logging
import json
from gpsd_parser import GpsdParser
from observer import Observer


class GpsdClient(threading.Thread):
    def __init__(self):
        super().__init__()

        logging.config.fileConfig("gnss-ui/assets/log.ini")
        self.logger = logging.getLogger("gpsd")

    def set_params(self, hostname, port, observer):
        self.server_address = (hostname, port)
        self.do_run = True
        self.parser = GpsdParser(observer)
        self.socket = None
        self.thread = None

    def connect(self):
        try:
            self.logger.info("trying to connect to %s", self.server_address)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect(self.server_address)
            self.send_enable_command()
        except Exception as err:
            self.logger.error(f"connecting to server failed: %s, %s", err, type(err))
            self.socket.close()
            self.socket = None
            return False
        return True

    def signalize_stop(self):
        if self.socket:
            self.send_disable_command()
        # time.sleep(1)
        self.do_run = False

    def run(self):
        self.logger.info("client thread: starting")

        while self.do_run:
            try:
                if self.socket == None:
                    while not self.connect():
                        if self.do_run:
                            self.logger.info("... retrying connection to gpsd ...")
                            time.sleep(1)
                        else:
                            self.logger.info("stopping retrying connection to gpsd ...")
                            return

                data = self.socket.recv(50).decode("utf-8")
                if len(data) > 0:
                    self.parser.add_data(data)
                else:
                    self.connect()
            except ConnectionResetError as e:
                self.logger.error(f"connection reset error: {e=}, {type(e)=}")
            except socket.error as e:
                self.logger.error(f"socket error: {e=}, {type(e)=}")
            except Exception as e:
                self.logger.error(f"unexpected: {e=}, {type(e)=}")
                break

        self.logger.info("thread finishing")

    def send_enable_command(self):
        self.logger.info("sending enable command.")
        # cmd = '?WATCH={"enable":true,"json":true,"nmea":true}'
        cmd = '?WATCH={"enable":true,"json":true,"nmea":false}'
        self.socket.send(cmd.encode())

    def send_disable_command(self):
        self.logger.info("sending disable command.")
        cmd = '?WATCH={"enable":false,"json":false,"nmea":false}'
        self.socket.send(cmd.encode())
