#! /usr/bin/python3

import socket
import threading
import time

from gpsd_parser import GpsdParser
from observer import Observer


class GpsdClient(threading.Thread):
    def set_params(self, hostname, port, observer):
        self.server_address = (hostname, port)
        self.do_run = True
        self.parser = GpsdParser(observer)
        self.socket = None
        self.thread = None

    def connect(self):
        try:
            print("GPSDC: trying to connect to ", self.server_address)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect(self.server_address)
            self.send_enable_command()
        except Exception as err:
            print(f"GPSDC: connecting to server failed: {err=}, {type(err)=}")
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
        print("GPSDC: client thread: starting")

        while self.do_run:
            try:
                if self.socket == None:
                    while not self.connect():
                        if self.do_run:
                            print("GPSDC: ... retrying connection to gpsd ...")
                            time.sleep(1)
                        else:
                            print("GPSDC: stopping retrying connection to gpsd ...")
                            return

                data = self.socket.recv(50).decode("utf-8")
                if len(data) > 0:
                    self.parser.add_data(data)
                else:
                    self.connect()
            except ConnectionResetError as e:
                print(f"GPSDC: Connection reset error: {e=}, {type(e)=}")
            except socket.error as e:
                print(f"GPSDC: Socket error: {e=}, {type(e)=}")
            except Exception as e:
                print(f"GPSDC: Unexpected: {e=}, {type(e)=}")
                break

        print("GPSDC: Thread finishing")

    def send_enable_command(self):
        print("GPSDC: sending enable command.")
        cmd = '?WATCH={"enable":true,"json":true,"nmea":true}'
        self.socket.send(cmd.encode())

    def send_disable_command(self):
        print("GPSDC: sending disable command.")
        cmd = '?WATCH={"enable":false,"json":false,"nmea":false}'
        self.socket.send(cmd.encode())
