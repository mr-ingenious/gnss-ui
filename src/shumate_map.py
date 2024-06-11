#! /usr/bin/python3

import gi
from panel import Panel
import math

import time

import logging

gi.require_version("Gtk", "4.0")
gi.require_version("Shumate", "1.0")

from gi.repository import Gtk, Shumate

from position_info_panel import PositionInfoPanel
from satellites_graphic_panel import SatellitesGraphicPanel
from data_recorder_dashboard import DataRecorderDashboard

# Code inspired by GNOME Workbench


class ShumateMapPanel(Panel):
    def __init__(
        self,
        with_title=True,
        autocenter_map=True,
        start_latitude=48.78,
        start_longitude=9.17,
        initial_zoom_level=10,
        show_satellites_radar_dashboard=True,
        show_position_dashboard=True,
        recorder=None,
        export_directory="./",
    ):
        super().__init__()

        self.track_points = list()
        self.last_map_update = 0
        self.last_latitude = start_latitude
        self.last_longitude = start_longitude
        self.initial_zoom = initial_zoom_level
        self.export_directory = export_directory

        logging.config.fileConfig("gnss-ui/assets/log.ini")
        self.logger = logging.getLogger("app")

        self.set_css_classes(["panel", "map_panel"])

        self.set_hexpand(True)
        self.set_vexpand(True)

        if with_title:
            self.panel_label = Gtk.Label(label="Map")
            self.panel_label.set_css_classes(["panel_title"])
            self.append(self.panel_label)

        # Position Dashboard
        self.position_dashboard = PositionInfoPanel(as_dashboard=True)
        self.position_dashboard.set_halign(Gtk.Align.END)
        self.position_dashboard.set_valign(Gtk.Align.END)
        self.position_dashboard.set_visible(show_position_dashboard)

        # Satellites Radar Dashboard
        self.satellites_radar_dashboard = SatellitesGraphicPanel(as_dashboard=True)
        self.satellites_radar_dashboard.set_halign(Gtk.Align.START)
        self.satellites_radar_dashboard.set_valign(Gtk.Align.END)
        self.satellites_radar_dashboard.set_visible(show_satellites_radar_dashboard)

        # Recorder Control
        self.recorder_dashboard = None
        if recorder != None:
            self.recorder_dashboard = DataRecorderDashboard(
                recorder, self.export_directory
            )
            self.recorder_dashboard.set_halign(Gtk.Align.CENTER)
            self.recorder_dashboard.set_valign(Gtk.Align.END)
            self.recorder_dashboard.set_visible(True)

        self.is_valid_location = True
        self.overlay = Gtk.Overlay()
        self.hint = Gtk.Label(label="NO CURRENT / VALID POSITION")
        self.hint.set_halign(Gtk.Align.CENTER)
        self.hint.set_valign(Gtk.Align.START)
        self.hint.set_css_classes(["map_hint"])

        self.b1_icon = Gtk.Picture()
        self.b1_icon.set_filename("gnss-ui/assets/center_icon.svg")

        self.autocenter_map = autocenter_map
        self.b1 = Gtk.Button(label="Toggle Auto center")
        self.b1.set_child(self.b1_icon)
        self.b1.set_halign(Gtk.Align.END)
        self.b1.set_valign(Gtk.Align.START)
        self.b1.set_tooltip_text("Toggle map auto center")
        self.b1.set_css_classes(
            ["autocenter_button", "autocenter_button:active", "autocenter_button:hover"]
        )
        self.b1.connect("clicked", self.on_autocenter_button_pressed)

        self.map_widget = Shumate.SimpleMap()
        self.map_widget.get_map().set_go_to_duration(1000)

        self.map_widget.set_hexpand(True)
        self.map_widget.set_vexpand(True)
        self.registry = Shumate.MapSourceRegistry.new_with_defaults()

        # Use OpenStreetMap as the source
        # Alternatives: https://gitlab.gnome.org/GNOME/libshumate/-/blob/main/shumate/shumate-map-source-registry.h?ref_type=heads

        self.map_source = self.registry.get_by_id(Shumate.MAP_SOURCE_OSM_MAPNIK)
        self.viewport = self.map_widget.get_viewport()

        self.map_widget.set_map_source(self.map_source)
        self.map_widget.get_map().center_on(self.last_latitude, self.last_longitude)

        # Reference map source used by MarkerLayer
        self.viewport.set_reference_map_source(self.map_source)
        self.viewport.set_zoom_level(self.initial_zoom)

        self.marker_layer = Shumate.MarkerLayer(
            viewport=self.viewport,
            selection_mode=Gtk.SelectionMode.SINGLE,
        )

        self.track_layer = Shumate.MarkerLayer(
            viewport=self.viewport,
            selection_mode=Gtk.SelectionMode.SINGLE,
        )

        self.marker = Shumate.Marker()
        self.marker.set_location(self.last_latitude, self.last_longitude)
        self.marker_icon = Gtk.Image()
        self.marker_icon.set_css_classes(["map_marker"])
        self.marker_icon.set_from_file("gnss-ui/assets/marker_icon_large.png")
        self.marker.set_child(self.marker_icon)

        self.marker_layer.add_marker(self.marker)
        self.map_widget.get_map().add_layer(self.marker_layer)
        self.map_widget.get_map().add_layer(self.track_layer)
        self.map_widget.set_visible(True)

        self.overlay.set_child(self.map_widget)
        self.overlay.add_overlay(self.position_dashboard)
        self.overlay.add_overlay(self.satellites_radar_dashboard)

        if self.recorder_dashboard != None:
            self.overlay.add_overlay(self.recorder_dashboard)

        self.overlay.add_overlay(self.hint)
        self.overlay.add_overlay(self.b1)

        self.append(self.overlay)

    def on_autocenter_button_pressed(self, button):
        self.logger.debug("toggle autocenter pressed")
        self.autocenter_map = not self.autocenter_map

        if self.autocenter_map == True:
            self.b1_icon.set_filename("gnss-ui/assets/center_icon.svg")
            self.go_to_location(self.last_latitude, self.last_longitude)
        else:
            self.b1_icon.set_filename("gnss-ui/assets/center_icon_inactive.svg")

    def go_to_location(self, latitude, longitude):
        if math.isnan(latitude) or math.isnan(longitude):
            self.logger.warn("map panel: no valid coordinates!")
            return

        if latitude > Shumate.MAX_LATITUDE or latitude < Shumate.MIN_LATITUDE:
            self.logger.warn(
                f"map panel: latitudes must be between {Shumate.MIN_LATITUDE} and {Shumate.MAX_LATITUDE}",
            )
            return

        if longitude > Shumate.MAX_LONGITUDE or longitude < Shumate.MIN_LONGITUDE:
            self.logger.warn(
                f"map panel: longitudes must be between {Shumate.MIN_LONGITUDE} and {Shumate.MAX_LONGITUDE}",
            )
            return

        self.logger.debug(
            "map panel: going to location lat: %f, lon: %f", latitude, longitude
        )

        if self.initial_zoom == 4:
            self.viewport.set_zoom_level(15)
            self.initial_zoom = -1
        # self.viewport.set_zoom_level(15)

        if self.autocenter_map:
            self.map_widget.get_map().go_to(latitude, longitude)

        self.marker.set_location(latitude, longitude)

    def update(self, position_info, satellites_info):
        if self.get_visible():
            self.position_dashboard.update(position_info)
            self.satellites_radar_dashboard.update(satellites_info)

            if (
                position_info["data"]["latitude"]["decimal"] != 0.0
                and position_info["data"]["longitude"]["decimal"] != 0.0
            ):
                if self.is_valid_location == True:
                    self.overlay.remove_overlay(self.hint)
                    self.is_valid_location = False

                self.last_latitude = position_info["data"]["latitude"]["decimal"]
                self.last_longitude = position_info["data"]["longitude"]["decimal"]

                self.go_to_location(self.last_latitude, self.last_longitude)

                self.track_points.append((self.last_latitude, self.last_longitude))
                if len(self.track_points) > 100:
                    self.track_points.pop(0)

            else:
                if self.is_valid_location == False:
                    self.overlay.add_overlay(self.hint)
                    self.is_valid_location = True

            self.last_map_update = time.time()
