#! /usr/bin/python3

import sys
import gi

from left_menu_panel import LeftMenuPanel
from gpsd_client import GpsdClient
from observer import Observer

from position_info_panel import PositionInfoPanel
from satellites_info_panel import SatellitesInfoPanel
from satellites_graphic_panel import SatellitesGraphicPanel

from preferences_dialog import PreferencesDialog

from gpsd_panel import GpsdPanel

# from map_panel import MapPanel
from shumate_map import ShumateMapPanel

from datamodel import DataModel

import json

import logging

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("WebKit", "6.0")

from gi.repository import Gtk, Gdk, Gio, GLib, Adw, WebKit

css_provider = Gtk.CssProvider()
css_provider.load_from_path("./gnss-ui/appstyle.css")
Gtk.StyleContext.add_provider_for_display(
    Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        logging.config.fileConfig("gnss-ui/log.ini")
        self.logger = logging.getLogger("app")

        self.gpsd_hostname = "localhost"
        self.gpsd_port = 2947
        self.received_nmea_message_ct = 0
        self.received_json_message_ct = 0

        self.set_default_size(1024, 768)
        self.set_title("GNSS UI")

        self.add_header_menu()
        
        self.data = DataModel()

        self.rootbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.mainbox = Gtk.Box()
        self.mainbox.set_hexpand(True)
        self.mainbox.set_vexpand(True)

        # self.gpsd_panel = GpsdPanel(self, self.gpsd_hostname, self.gpsd_port)
        # self.mainbox.append(self.gpsd_panel)

        self.scrolled_main_box = Gtk.ScrolledWindow()
        self.scrolled_main_box.set_min_content_width(800)
        self.scrolled_main_box.set_min_content_width(600)
        self.scrolled_main_box.set_child(self.mainbox)
        self.rootbox.append(self.scrolled_main_box)

        self.left_menu_panel = LeftMenuPanel(self)
        self.mainbox.append(self.left_menu_panel)

        self.position_info_panel = PositionInfoPanel()
        self.mainbox.append(self.position_info_panel)

        self.satellites_info_panel = SatellitesInfoPanel()
        self.satellites_info_panel.set_visible(True)
        self.mainbox.append(self.satellites_info_panel)

        self.satellites_graphic_panel = SatellitesGraphicPanel()
        self.satellites_graphic_panel.set_visible(False)
        self.mainbox.append(self.satellites_graphic_panel)

        self.map_panel = ShumateMapPanel()  # MapPanel()
        self.map_panel.set_visible(True)
        self.mainbox.append(self.map_panel)

        self.main_statusbar = Gtk.Box()
        self.main_statusbar.set_css_classes(["statusbar"])
        self.main_status_text = Gtk.Label()
        self.main_statusbar.append(self.main_status_text)
        self.rootbox.append(self.main_statusbar)

        self.set_child(self.rootbox)

        self.gpsdc = GpsdClient()
        self.gpsdc.set_params(self.gpsd_hostname, self.gpsd_port, self)

        self.main_status_text.set_label("started.")

        self.connect("close-request", self.handle_close_request)

    def handle_close_request(self, data):
        self.logger.debug("AW: close-request")
        self.gpsdc.signalize_stop()

    def handle_exit(self):
        self.logger.info("stopping gpsd client")
        self.gpsdc.signalize_stop()
        self.gpsdc.join(5)

    def updateNmea(self, msg):
        self.received_nmea_message_ct += 1

        GLib.idle_add(self.update_panels, msg)
        GLib.idle_add(self.update_statusbar)

    def update_panels(self, msg):
        self.data.updateNMEA(msg)

        self.position_info_panel.update(self.data.position)

        self.satellites_info_panel.update(self.data.satellites)

        self.satellites_graphic_panel.update(self.data.satellites)

        self.map_panel.update(self.data.position)

    def updateJSON(self, jobject):
        self.data.updateJSON(jobject)
        self.received_json_message_ct += 1
        GLib.idle_add(self.update_statusbar)

    def update_statusbar(self):
        self.main_status_text.set_label(
            "received messages: NMEA="
            + str(self.received_nmea_message_ct)
            + ", JSON="
            + str(self.received_json_message_ct)
        )

    def on_position_button_pressed(self, button):
        self.position_info_panel.set_visible(not self.position_info_panel.get_visible())

    def on_satellites_button_pressed(self, button):
        self.satellites_info_panel.set_visible(
            not self.satellites_info_panel.get_visible()
        )

    def on_satellites_graphic_button_pressed(self, button):
        self.satellites_graphic_panel.set_visible(
            not self.satellites_graphic_panel.get_visible()
        )

    def on_map_button_pressed(self, button):
        self.map_panel.set_visible(not self.map_panel.get_visible())

    def add_header_menu(self):
        self.header = Gtk.HeaderBar()
        self.set_titlebar(self.header)
        # self.open_button = Gtk.Button(label="Open")
        # self.header.pack_start(self.open_button)

        # Create a new menu, containing that action
        menu = Gio.Menu.new()
        # menu.append(
        #    "Connect to GPSD", "win.connect_to_gpsd"
        # )

        # Create a popover
        self.popover = Gtk.PopoverMenu()  # Create a new popover menu
        self.popover.set_menu_model(menu)

        # Create a menu button
        self.hamburger = Gtk.MenuButton()
        self.hamburger.set_popover(self.popover)
        self.hamburger.set_icon_name("open-menu-symbolic")

        # Add menu button to the header bar
        self.header.pack_start(self.hamburger)

        # set app name
        GLib.set_application_name("My App")

        # Add start gpsd menu point
        action = Gio.SimpleAction.new("start-gpsd", None)
        action.connect("activate", self.on_start_gpsd_button_pressed)
        self.add_action(action)
        menu.append("start gpsd", "win.start-gpsd")

        # Add settings menu point
        settings_action = Gio.SimpleAction.new("settings", None)
        settings_action.connect("activate", self.show_settings_dialog)
        self.add_action(settings_action)
        menu.append("settings", "win.settings")

        # Add an about dialog
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.show_about_dialog)
        self.add_action(about_action)
        menu.append("About", "win.about")

    def create_and_start_gpsdc(self):
        self.logger.info("creating and starting GPSD ...")
        if not hasattr(self, "gpsdc"):
            self.gpsdc = GpsdClient()
            self.gpsdc.set_params("localhost", 2947, self)

        if not self.gpsdc.is_alive():
            self.gpsdc.start()

    def on_start_gpsd_button_pressed(self, action, param):
        self.create_and_start_gpsdc()

    def show_about_dialog(self, action, param):
        dialog = Adw.AboutWindow(transient_for=app.get_active_window())

        dialog.set_application_name("GNSS UI")
        dialog.set_version("0.1")
        dialog.set_developer_name("mr-ingenious")
        dialog.set_license_type(Gtk.License(Gtk.License.GPL_3_0))
        dialog.set_comments("A simple GNSS UI for Linux")
        # dialog.set_website("https://github.com/Tailko2k/GTK4PythonTutorial")
        # dialog.set_issue_url("https://github.com/Tailko2k/GTK4PythonTutorial/issues")
        dialog.add_credit_section("Contributors", ["Name1 url"])
        dialog.set_translator_credits("Name1 url")
        dialog.set_copyright("© 2024 mr-ingenious")
        dialog.set_developers(["Developer"])
        dialog.set_application_icon(
            "com.github.mr-ingenious.gnss-ui"
        )  # icon must be uploaded in ~/.local/share/icons or /usr/share/icons

        dialog.set_visible(True)

    def show_settings_dialog(self, action, param):
        self.logger.info("showing settings dialog")

        dialog = PreferencesDialog()
        # dialog.set_visible(True)


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)
        self.connect("window-removed", self.on_exit)
        self.connect("shutdown", self.on_shutdown)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()
        # dialog = PreferencesDialog()

    def on_exit(self, window, data):
        # print("exiting ...")
        # self.win.handle_exit()
        pass

    def on_shutdown(self, data):
        # print("shutting down ...")
        # self.win.handle_exit()
        pass


app = MyApp(application_id="mr-ingenious.gnss-ui")
app.run(sys.argv)
