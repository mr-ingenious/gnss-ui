#! /usr/bin/python3

import gi
import time

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("WebKit", "6.0")

from gi.repository import Gtk, Adw, WebKit

from panel import Panel


class MapPanel(Panel):
    def __init__(self):
        super().__init__()
        self.last_values_update = time.time()
        self.last_map_update = time.time()
        self.lat = 0.0
        self.lon = 0.0
        self.lat_dec = 0.0
        self.lon_dec = 0.0

        self.set_css_classes(["map_panel", "panel"])

        network_session = WebKit.NetworkSession(
            data_directory="/tmp/data", cache_directory="/tmp/cache"
        )
        self.webview = WebKit.WebView(network_session=network_session)
        self.webview.get_network_session().get_cookie_manager().set_persistent_storage(
            "/tmp/cookies.sqlite", WebKit.CookiePersistentStorage.SQLITE
        )
        self.webview.set_vexpand(True)

        self.append(self.webview)

        self.connect("destroy", lambda *args: self.webview.try_close())

        self.set_vexpand(True)
        self.set_hexpand(True)

    def show_map(self):

        if False:
            # https://opentopomap.org/#map=17/

            uri = (
                " http://www.opentopomap.org/#map=20/"
                + str(self.lat_dec)
                + "/"
                + str(self.lon_dec)
            )
        else:
            uri = (
                " http://www.openstreetmap.org/?mlat="
                + str(self.lat_dec)
                + "&mlon="
                + str(self.lon_dec)
            )
        print("MAP: show " + uri)

        self.webview.load_uri(uri)

    def __convert_coordinates_to_decimal(self):
        self.lat_dec = round(self.lat)
        lat_fract = self.lat - self.lat_dec
        lat_fract = lat_fract / 0.60
        self.lat_dec += lat_fract

        self.lon_dec = round(self.lon)
        lon_fract = self.lon - self.lon_dec
        lon_fract = lon_fract / 0.60
        self.lon_dec += lon_fract

    def update(self, msg):
        if msg["type"] == "RMC" and msg["latitude"] != "" and msg["longitude"] != "":

            self.lat = float(msg["latitude"]) / 100
            self.lon = float(msg["longitude"]) / 100

            self.__convert_coordinates_to_decimal()

            self.last_values_update = time.time()

            if (self.get_visible()) and time.time() - self.last_map_update > 5:
                self.last_map_update = time.time()
                self.show_map()
