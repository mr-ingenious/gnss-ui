#! /usr/bin/python3

import sys
import gi

import threading
import time

from left_menu_panel import LeftMenuPanel
from gpsd_client import GpsdClient
from observer import Observer

from position_info_panel import PositionInfoPanel
from gnss_info_panel import GnssInfoPanel
from satellites_info_panel import SatellitesInfoPanel
from satellites_graphic_panel import SatellitesGraphicPanel

from preferences_dialog2 import PreferencesDialog

from data_recorder import DataRecorder, DataRecorderStatus

from gpsd_panel import GpsdPanel

from shumate_map import ShumateMapPanel

from data_recorder_panel import DataRecorderPanel

from datamodel import DataModel

from config_provider import ConfigProvider

import json

import logging

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("WebKit", "6.0")

from gi.repository import Gtk, Gdk, Gio, GLib, Adw

css_provider = Gtk.CssProvider()
css_provider.load_from_path("./gnss-ui/assets/appstyle.css")
Gtk.StyleContext.add_provider_for_display(
    Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

APP_VERSION = "0.7.6"


class PanelRefresher(threading.Thread):
    def __init__(self, target, cycle_sec=2):
        threading.Thread.__init__(self)
        self.cycle_time_sec = cycle_sec
        self.do_run = True
        self.target = target

    def set_cycle_time_sec(self, cycle_sec):
        self.cycle_time_sec = cycle_sec

    def signalize_stop(self):
        self.do_run = False

    def run(self):
        while self.do_run:
            # print("[REFRESHER THREAD]")
            self.target.update_panels()
            time.sleep(self.cycle_time_sec)


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        logging.config.fileConfig("gnss-ui/assets/log.ini")
        self.logger = logging.getLogger("app")

        self.config = ConfigProvider()

        self.received_nmea_message_ct = 0
        self.received_json_message_ct = 0

        self.set_default_size(
            self.config.get_param("general/resolution/width", 1024),
            self.config.get_param("general/resolution/height", 768),
        )
        self.set_title("GNSS UI")

        self.add_header_menu()

        self.data = DataModel()

        self.root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.main_box = Gtk.Box()
        self.main_box.set_hexpand(True)
        self.main_box.set_vexpand(True)

        self.bg_image = Gtk.Picture()
        self.bg_image.set_filename("gnss-ui/assets/background.jpg")
        self.bg_image.set_content_fit(Gtk.ContentFit.COVER)

        self.overlay_box = Gtk.Overlay()
        self.overlay_box.set_hexpand(True)
        self.overlay_box.set_vexpand(True)
        self.overlay_box.set_child(self.bg_image)

        # self.gpsd_panel = GpsdPanel(self, self.gpsd_hostname, self.gpsd_port)
        # self.mainbox.append(self.gpsd_panel)

        self.overlay_root_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.scrolled_main_box = Gtk.ScrolledWindow()
        self.scrolled_main_box.set_min_content_width(800)
        self.scrolled_main_box.set_min_content_width(600)
        self.scrolled_main_box.set_child(self.main_box)

        self.overlay_box.add_overlay(self.overlay_root_box)
        self.root_box.append(self.overlay_box)

        self.position_info_panel = PositionInfoPanel()
        if "position" in self.config.get_param("startup/panels_shown"):
            self.position_info_panel.set_visible(True)
        else:
            self.position_info_panel.set_visible(False)
        self.main_box.append(self.position_info_panel)

        self.gnss_info_panel = GnssInfoPanel()
        if "position" in self.config.get_param("startup/panels_shown"):
            self.gnss_info_panel.set_visible(True)
        else:
            self.gnss_info_panel.set_visible(False)
        self.main_box.append(self.gnss_info_panel)

        self.satellites_info_panel = SatellitesInfoPanel()
        if "satellites_list" in self.config.get_param("startup/panels_shown"):
            self.satellites_info_panel.set_visible(True)
        else:
            self.satellites_info_panel.set_visible(False)
        self.main_box.append(self.satellites_info_panel)

        self.satellites_radar_panel = SatellitesGraphicPanel()
        if "satellites_radar" in self.config.get_param("startup/panels_shown"):
            self.satellites_radar_panel.set_visible(True)
        else:
            self.satellites_radar_panel.set_visible(False)
        self.main_box.append(self.satellites_radar_panel)

        # Recorder
        self.recorder = DataRecorder()

        # Map Panel
        self.map_panel = ShumateMapPanel(
            with_title=False,
            initial_zoom_level=self.config.get_param("map_panel/initial_zoom_level", 5),
            autocenter_map=self.config.get_param("map_panel/auto_center", True),
            show_satellites_radar_dashboard=self.config.get_param(
                "map_panel/show_satellites_dashboard", True
            ),
            show_position_dashboard=self.config.get_param(
                "map_panel/show_position_dashboard", True
            ),
            start_latitude=self.config.get_param("map_panel/start_latitude", 0.0),
            start_longitude=self.config.get_param("map_panel/start_longitude", 0.0),
            recorder=None,
            export_directory=self.config.get_param("recording/export/directory", "./"),
        )
        if "map" in self.config.get_param("startup/panels_shown"):
            self.map_panel.set_visible(True)
        else:
            self.map_panel.set_visible(False)
        self.main_box.append(self.map_panel)

        self.recorder_panel = DataRecorderPanel(
            recorder=self.recorder,
            main_window=self,
            export_directory=self.config.get_param("recording/export/directory", "./"),
        )

        if "recorder" in self.config.get_param("startup/panels_shown"):
            self.recorder_panel.set_visible(True)
        else:
            self.recorder_panel.set_visible(False)
        self.main_box.append(self.recorder_panel)

        self.left_menu_panel = LeftMenuPanel(
            self.position_info_panel,
            self.gnss_info_panel,
            self.satellites_info_panel,
            self.satellites_radar_panel,
            self.map_panel,
            self.recorder_panel,
        )
        self.overlay_root_box.append(self.left_menu_panel)
        self.overlay_root_box.append(self.scrolled_main_box)

        self.main_statusbar = Gtk.Box()
        self.main_statusbar.set_css_classes(["statusbar"])
        self.main_status_text = Gtk.Label()
        self.main_statusbar.append(self.main_status_text)
        self.root_box.append(self.main_statusbar)

        self.set_child(self.root_box)

        if self.config.get_param("startup/connect_to_gpsd"):
            self.create_and_start_gpsdc()

        self.panels_update_thread = PanelRefresher(
            self, cycle_sec=self.config.get_param("general/panel_refresh_cycle_sec", 2)
        )
        self.panels_update_thread.start()

        self.main_status_text.set_label("started.")

        self.connect("close-request", self.handle_close_request)

    def handle_close_request(self, data):
        self.logger.debug("App: close-request")

        if self.recorder.get_status() != DataRecorderStatus.RECORDING_IDLE:
            self.logger.info("App: recording is still in progress, closing aborted.")
            self.dialog = Gtk.AlertDialog()
            self.dialog.set_detail("Recording still in progress!")
            self.dialog.set_modal(True)
            self.dialog.show(self)
            return True  # True: abort closing the main window

        self.logger.info("App: exiting")
        self.handle_exit()
        return False

    def handle_exit(self):
        self.logger.info("stopping gpsd client and panels update thread")
        self.panels_update_thread.signalize_stop()
        self.panels_update_thread.join(5)

        self.gpsdc.signalize_stop()
        self.gpsdc.join(5)

    def updateNmea(self, msg):
        self.received_nmea_message_ct += 1

        GLib.idle_add(self.data.updateNMEA, msg)

        if self.data != None:
            self.recorder.update(self.data)

        GLib.idle_add(self.update_statusbar)

    def update_panels(self):
        # self.logger.debug("updating panels ...")
        GLib.idle_add(self.update_panels_internal)

    def update_panels_internal(self):
        self.position_info_panel.update(self.data.position)
        self.satellites_info_panel.update(self.data.position, self.data.satellites)
        self.satellites_radar_panel.update(self.data.satellites)
        self.map_panel.update(self.data.position, self.data.satellites)
        self.gnss_info_panel.update(self.data.position)
        self.recorder_panel.update()

    def updateJSON(self, jobject):
        self.data.updateJSON(jobject)
        self.received_json_message_ct += 1
        GLib.idle_add(self.update_statusbar)
        
        if self.data != None:
            self.recorder.update(self.data)

    def update_statusbar(self):
        self.main_status_text.set_label(
            "received messages: NMEA="
            + str(self.received_nmea_message_ct)
            + ", JSON="
            + str(self.received_json_message_ct)
        )

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
        self.header.pack_end(self.hamburger)

        # set app name
        GLib.set_application_name("GNSS-UI")

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
        self.logger.info("creating and starting gpsd client ...")
        if not hasattr(self, "gpsdc"):
            self.logger.info("creating new gpsd client instance")
            self.gpsdc = GpsdClient()
            self.gpsdc.set_params(
                self.config.get_param("gpsd/hostname"),
                self.config.get_param("gpsd/port"),
                self,
            )

        if not self.gpsdc.is_alive():
            self.gpsdc.start()

    def on_start_gpsd_button_pressed(self, action, param):
        self.create_and_start_gpsdc()

    def show_about_dialog(self, action, param):
        dialog = Adw.AboutWindow(transient_for=app.get_active_window())

        dialog.set_application_name("GNSS UI")
        dialog.set_version(APP_VERSION)
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

        dialog = PreferencesDialog(self.config)
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
