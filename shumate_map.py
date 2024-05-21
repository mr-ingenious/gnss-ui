#! /usr/bin/python3

import gi
from panel import Panel
import math

import time

import logging

gi.require_version("Gtk", "4.0")
gi.require_version("Shumate", "1.0")

from gi.repository import Gtk, Shumate

# Code inspired by GNOME Workbench


class ShumateMapPanel(Panel):
    def __init__(self):
        super().__init__()

        self.last_map_update = 0
        self.last_latitude = 0.0
        self.last_longitude = 0.0

        logging.config.fileConfig("gnss-ui/log.ini")
        self.logger = logging.getLogger("app")

        self.set_css_classes(["panel", "map_panel"])

        self.set_hexpand(True)
        self.set_vexpand(True)

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
        self.map_widget.get_map().center_on(0, 0)

        # Reference map source used by MarkerLayer
        self.viewport.set_reference_map_source(self.map_source)
        self.viewport.set_zoom_level(12)

        self.marker_layer = Shumate.MarkerLayer(
            viewport=self.viewport,
            selection_mode=Gtk.SelectionMode.SINGLE,
        )

        self.marker = Shumate.Marker()
        self.marker.set_location(0, 0)
        self.marker.set_css_classes(["map_marker"])
        self.marker_icon = Gtk.Image()
        self.marker_icon.set_from_file("gnss-ui/marker_icon_large.png")
        self.marker.set_child(self.marker_icon)

        self.marker_layer.add_marker(self.marker)
        self.map_widget.get_map().add_layer(self.marker_layer)

        self.append(self.map_widget)

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
        # self.viewport.set_zoom_level(15)
        self.map_widget.get_map().go_to(latitude, longitude)
        self.marker.set_location(latitude, longitude)

    def update(self, position_info):
        if (self.get_visible()) and time.time() - self.last_map_update > 5:
            if (
                position_info["data"]["latitude"]["decimal"] != 0.0
                and position_info["data"]["longitude"]["decimal"] != 0.0
            ):
                self.last_latitude = position_info["data"]["latitude"]["decimal"]
                self.last_longitude = position_info["data"]["longitude"]["decimal"]
                
            self.go_to_location(self.last_latitude, self.last_longitude)
            self.last_map_update = time.time()
