#! /usr/bin/python3

import sys
import gi

from left_menu_panel import LeftMenuPanel
from gpsd_client import GpsdClient
from observer import Observer

from position_info_panel import PositionInfoPanel
from satellites_info_panel import SatellitesInfoPanel

from satellites_graphic_panel import SatellitesGraphicPanel

from dyndata_panel import DyndataPanel
from gpsd_panel import GpsdPanel

from map_panel import MapPanel

from datamodel import DataModel

import json

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

        self.gpsd_hostname = "localhost"
        self.gpsd_port = 2947
        self.received_nmea_message_ct = 0
        self.received_json_message_ct = 0

        super().__init__(*args, **kwargs)

        self.set_default_size(1024, 768)
        self.set_title("GNSS UI")

        self.add_header_menu()
        self.data = DataModel()

        self.rootbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.mainbox = Gtk.Box()
        self.mainbox.set_hexpand(True)
        self.mainbox.set_vexpand(True)
        # Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

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

        self.dyndata_info_panel = DyndataPanel()
        self.mainbox.append(self.dyndata_info_panel)

        self.satellites_info_panel_gps = SatellitesInfoPanel("GPS", "GP")
        self.satellites_info_panel_gps.set_visible(False)
        self.mainbox.append(self.satellites_info_panel_gps)

        self.satellites_info_panel_glonass = SatellitesInfoPanel("Glonass", "GL")
        self.satellites_info_panel_glonass.set_visible(False)
        self.mainbox.append(self.satellites_info_panel_glonass)

        self.satellites_info_panel_galileo = SatellitesInfoPanel("Galileo", "GA")
        self.satellites_info_panel_galileo.set_visible(False)
        self.mainbox.append(self.satellites_info_panel_galileo)

        self.satellites_info_panel_beidou = SatellitesInfoPanel("Beidou", "PQ")
        self.satellites_info_panel_beidou.set_visible(False)
        self.mainbox.append(self.satellites_info_panel_beidou)

        self.satellites_graphic_panel = SatellitesGraphicPanel()
        # self.satellites_graphic_panel.set_visible(False)
        self.mainbox.append(self.satellites_graphic_panel)

        self.map_panel = MapPanel()
        self.map_panel.set_visible(False)
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
        print("AW: close-request")
        self.gpsdc.signalize_stop()

    def add_value_item_to_grid(self, _name, _label, _grid, _row):
        _grid.insert_row(_row)

        new_label = Gtk.Label(name=_name + "_label", label=_label)
        new_label.set_css_classes(["label"])
        _grid.attach(new_label, 1, _row, 1, 1)

        new_value = Gtk.Label(name=_name + "_value", label="---")
        new_value.set_css_classes(["value"])
        _grid.attach(new_value, 2, _row, 1, 1)

        self.gps_values_box.append(self.gps_values_grid)
        self.gps_values_box.set_vexpand(True)
        self.mainbox.append(self.gps_values_box)

    def change_gps_value(self, base_element, name, value):
        next_element = base_element.get_first_child()

        while next_element != None:
            # print ("> element: ", next_element.get_name(), ", label: ", next_element.get_label())

            if next_element.get_name() == name + "_value":
                next_element.set_label(value)
                # print ("> found element: ", next_element.get_name(), ", value: ", next_element.get_label())
                break
            else:
                next_element = next_element.get_next_sibling()

        # value_element.set_label = value;

    def add_gps_quality_panel(self):
        self.gps_quality_box = Gtk.DrawingArea()

        # Make it fill the available space (It will stretch with the window)
        self.gps_quality_box.set_hexpand(True)
        self.gps_quality_box.set_vexpand(True)

        # Instead, If we didn't want it to fill the available space but wanted a fixed size
        # self.gps_quality_box.set_content_width(100)
        # self.gps_quality_box.set_content_height(100)

        self.gps_quality_box.set_draw_func(self.draw_quality_info, None)
        self.mainbox.append(self.gps_quality_box)

    def draw_quality_info(self, area, c, w, h, data):
        # c is a Cairo context

        # Fill background with a colour
        c.set_source_rgb(0, 0, 0)
        c.paint()

        # Draw a line
        c.set_source_rgb(0.5, 0.0, 0.5)
        c.set_line_width(3)
        c.move_to(10, 10)
        c.line_to(w - 10, h - 10)
        c.stroke()

        # Draw a rectangle
        c.set_source_rgb(0.8, 0.8, 0.0)
        c.rectangle(20, 20, 50, 20)
        c.fill()

        # Draw some text
        c.set_source_rgb(0.1, 0.1, 0.1)
        c.select_font_face("Sans")
        c.set_font_size(13)
        c.move_to(25, 35)
        c.show_text("Test")

    def add_map_panel(self):
        self.map_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.map_box.set_css_classes(["map_panel", "panel"])

        self.map_panel_label = Gtk.Label(label="Map")
        self.map_panel_label.set_css_classes(["panel_title"])
        self.map_box.append(self.map_panel_label)

        network_session = WebKit.NetworkSession(
            data_directory="/tmp/gps-ui/data", cache_directory="/tmp/gps-ui/cache"
        )

        self.map_view = WebKit.WebView(network_session=network_session)
        self.map_view.get_network_session().get_cookie_manager().set_persistent_storage(
            "/tmp/gps-ui/cookies.sqlite", WebKit.CookiePersistentStorage.SQLITE
        )

        self.map_box.append(self.map_view)

        self.map_view.set_hexpand(True)
        self.map_view.set_vexpand(True)
        self.map_view.load_uri("https://www.heise.de")

        self.mainbox.append(self.map_box)

        self.connect("destroy", lambda *args: self.map_view.try_close())

    def handle_exit(self):
        print("stopping gpsd client")
        self.gpsdc.signalize_stop()
        self.gpsdc.join(5)

    def updateNmea(self, msg):
        # print (">> NMEA UPDATE (", msg["type"], "):", repr (msg))
        self.received_nmea_message_ct += 1

        GLib.idle_add(self.update_panels, msg)
        GLib.idle_add(self.update_statusbar)

    def update_panels(self, msg):
        self.data.updateNMEA(msg)

        self.position_info_panel.update(msg)
        self.satellites_info_panel_gps.update(msg)
        self.satellites_info_panel_glonass.update(msg)
        self.satellites_info_panel_galileo.update(msg)
        self.satellites_info_panel_beidou.update(msg)

        self.satellites_graphic_panel.update(msg)
        self.dyndata_info_panel.update(msg)
        self.map_panel.update(msg)

    def updateJSON(self, jobject):
        self.data.updateJSON(jobject)
        self.received_json_message_ct += 1
        GLib.idle_add(self.update_statusbar)
        # print(">> JSON UPDATE:", json.dumps(jobject, indent=4))
        # selfGPSDC.gpsd_panel.update_info(jobject)

    def update_statusbar(self):
        self.main_status_text.set_label(
            "received messages: NMEA="
            + str(self.received_nmea_message_ct)
            + ", JSON="
            + str(self.received_json_message_ct)
        )

    def on_position_button_pressed(self, button):
        self.position_info_panel.set_visible(not self.position_info_panel.get_visible())
        self.dyndata_info_panel.set_visible(not self.dyndata_info_panel.get_visible())

    def on_satellites_button_pressed(self, button):
        self.satellites_info_panel_gps.set_visible(
            not self.satellites_info_panel_gps.get_visible()
        )
        self.satellites_info_panel_glonass.set_visible(
            not self.satellites_info_panel_glonass.get_visible()
        )
        self.satellites_info_panel_galileo.set_visible(
            not self.satellites_info_panel_galileo.get_visible()
        )
        self.satellites_info_panel_beidou.set_visible(
            not self.satellites_info_panel_beidou.get_visible()
        )

    def on_satellites_graphic_button_pressed(self, button):
        self.satellites_graphic_panel.set_visible(
            not self.satellites_graphic_panel.get_visible()
        )

    def on_map_button_pressed(self, button):
        self.map_panel.set_visible(not self.map_panel.get_visible())

        if self.map_panel.get_visible():
            self.map_panel.show_map()

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
        self.hamburger.set_icon_name("open-menu-symbolic")  # Give it a nice icon

        # Add menu button to the header bar
        self.header.pack_start(self.hamburger)

        # set app name
        GLib.set_application_name("My App")

        action = Gio.SimpleAction.new("start-gpsd", None)
        action.connect("activate", self.on_start_gpsd_button_pressed)
        self.add_action(action)
        menu.append("start gpsd", "win.start-gpsd")

        # Add an about dialog
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.show_about_dialog)
        self.add_action(action)
        menu.append("About", "win.about")

    def create_and_start_gpsdc(self):
        print("creating and starting GPSD ...")
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


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)
        self.connect("window-removed", self.on_exit)
        self.connect("shutdown", self.on_shutdown)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

    def on_exit(self, window, data):
        # print("exiting ...")
        # self.win.handle_exit()
        pass

    def on_shutdown(self, data):
        # print("shutting down ...")
        # self.win.handle_exit()
        pass


app = MyApp(application_id="mr-ingenious.gnss-ui")
try:
    app.run(sys.argv)
except Exception as e:
    print(f"Unexpected: {e=}, {type(e)=}")
    exit(0)
