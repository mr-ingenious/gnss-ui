#! /usr/bin/python3

import socket
import threading
import time

from gpsd_parser import GpsdParser
from observer import Observer


class GpsdClient:
    def __init__(self, hostname, port, observer):
        self.server_address = (hostname, port)
        self.do_run = False
        self.parser = GpsdParser(observer)

    def connect(self):
        try:
            print("trying to connect to localhost")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect(self.server_address)
            self.send_enable_command()
        except Exception as err:
            print(f"connecting to server failed, {err=}, {type(err)=}")
            self.socket.close()
            self.socket = None
            return False
        return True

    def thread_function(self):
        print("gpsd client thread: starting")

        while self.do_run:
            try:
                if not hasattr(self, "socket"):
                    while not self.connect():
                        print("... retrying connection to gpsd ...")
                        time.sleep(1)

                data = self.socket.recv(50).decode("utf-8")
                if len(data) > 0:
                    self.parser.add_data(data)
                else:
                    self.connect()
            except ConnectionResetError as e:
                print(f"Connection reset error: {e=}, {type(e)=}")
            except socket.error as e:
                print(f"Socket error: {e=}, {type(e)=}")
            except TimeoutError as e:
                print("socket read timeout!")
                self.connect()
            except Exception as e:
                print(f"Unexpected: {e=}, {type(e)=}")
                break

        print("Thread finishing")

    def send_enable_command(self):
        print("sending enable command.")
        cmd = '?WATCH={"enable":true,"json":true,"nmea":true}'
        self.socket.send(cmd.encode())

    def send_disable_command(self):
        print("sending disable command.")
        cmd = '?WATCH={"enable":false,"json":false,"nmea":false}'
        self.socket.send(cmd.encode())

    def start(self):
        print("trying to connect to gpsd ...")

        if self.do_run:
            print("already started. NOP")
            return

        # while not self.connect():
        #    print("retrying to connect to gpsd ...")
        #
        #    time.sleep(1)

        # print("connected to gpsd")
        self.do_run = True
        self.thread = threading.Thread(
            target=self.thread_function, name="client_receive_thread"
        )

        self.thread.start()

    def stop(self):
        if hasattr(self, "thread") and self.thread.is_alive():
            print("stopping gpsd client ...")
            self.send_disable_command()
            self.do_run = False
            self.thread.join(5)
