#! /usr/bin/python3

import gi

import logging

import logger

from datetime import datetime

gi.require_version("Gtk", "4.0")
gi.require_version("Shumate", "1.0")

from gi.repository import Gtk, Shumate


class RecordingMapWindow(Gtk.Window):
    def __init__(self, recording_info, points):
        super().__init__()

        self.set_default_size(
            1024,
            600,
        )

        self.set_title(recording_info["name"])

        self.logger = logger.get_logger("app")

        self.set_hexpand(True)
        self.set_vexpand(True)

        self.content_box = Gtk.Overlay()
        self.content_box.set_css_classes(["panel", "map_panel"])

        self.panel_label = Gtk.Label(label="Map")
        self.panel_label.set_css_classes(["panel_title"])
        # self.append(self.panel_label)

        self.map_widget = Shumate.SimpleMap()
        self.map_widget.get_map().set_go_to_duration(100)

        self.map_widget.set_hexpand(True)
        self.map_widget.set_vexpand(True)
        self.registry = Shumate.MapSourceRegistry.new_with_defaults()

        # Use OpenStreetMap as the source
        # Alternatives: https://gitlab.gnome.org/GNOME/libshumate/-/blob/main/shumate/shumate-map-source-registry.h?ref_type=heads

        self.map_source = self.registry.get_by_id(Shumate.MAP_SOURCE_OSM_MAPNIK)
        self.viewport = self.map_widget.get_viewport()

        self.map_widget.set_map_source(self.map_source)
        # self.map_widget.get_map().center_on(self.last_latitude, self.last_longitude)

        # Reference map source used by MarkerLayer
        self.viewport.set_reference_map_source(self.map_source)
        self.viewport.set_max_zoom_level(20)
        # self.viewport.set_zoom_level(self.initial_zoom)

        self.recorded_track_layer = Shumate.PathLayer(viewport=self.viewport)
        self.recorded_track_layer.set_stroke_width(6)

        self.viewport.set_zoom_level(18)

        lat_start = 0.0
        lon_start = 0.0

        point_ct = 0
        for pt in points:
            lat = pt[1]
            lon = pt[2]

            if lat != 0.0 and lon != 0.0:
                if lat_start == 0.0 and lon_start == 0.0:
                    lat_start = lat
                    lon_start = lon

                coord = Shumate.Coordinate()
                coord.set_location(lat, lon)
                self.recorded_track_layer.add_node(coord)

                point_ct += 1

        self.map_widget.get_map().go_to(lat_start, lon_start)
        self.map_widget.get_map().add_layer(self.recorded_track_layer)
        self.map_widget.set_visible(True)

        self.content_box.set_child(self.map_widget)

        # INFOBOX
        self.info_box = Gtk.Box()
        self.info_box.set_css_classes(["map_dashboard"])
        self.info_box.set_halign(Gtk.Align.START)
        self.info_box.set_valign(Gtk.Align.START)

        self.info_grid = Gtk.Grid()

        self.info_grid.set_row_spacing(10)
        self.info_grid.set_column_spacing(10)

        self.info_grid.insert_column(1)
        self.info_grid.insert_column(1)

        # name
        name_label = Gtk.Label(label="Name: ")
        name_label.set_xalign(0)
        name_label.set_css_classes(["map_dashboard_label"])
        self.info_grid.attach(name_label, 1, 1, 1, 1)

        name_value = Gtk.Label(label=recording_info["name"])
        name_value.set_xalign(0)
        name_value.set_css_classes(["map_dashboard_value"])
        self.info_grid.attach(name_value, 2, 1, 1, 1)

        # description
        description_label = Gtk.Label(label="Description: ")
        description_label.set_xalign(0)
        description_label.set_css_classes(["map_dashboard_label"])
        self.info_grid.attach(description_label, 1, 2, 1, 1)

        description_value = Gtk.Label(label=recording_info["description"])
        description_value.set_xalign(0)
        description_value.set_css_classes(["map_dashboard_value"])
        self.info_grid.attach(description_value, 2, 2, 1, 1)

        # start timestamp
        ts_start_label = Gtk.Label(label="Start: ")
        ts_start_label.set_xalign(0)
        ts_start_label.set_css_classes(["map_dashboard_label"])
        self.info_grid.attach(ts_start_label, 1, 3, 1, 1)

        ts = datetime.fromtimestamp(recording_info["ts_start"])
        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
        ts_start_value = Gtk.Label(label=ts_str)
        ts_start_value.set_xalign(0)
        ts_start_value.set_css_classes(["map_dashboard_value"])
        self.info_grid.attach(ts_start_value, 2, 3, 1, 1)

        # end timestamp
        ts_end_label = Gtk.Label(label="End: ")
        ts_end_label.set_xalign(0)
        ts_end_label.set_css_classes(["map_dashboard_label"])
        self.info_grid.attach(ts_end_label, 1, 4, 1, 1)

        ts = datetime.fromtimestamp(recording_info["ts_end"])
        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
        ts_end_value = Gtk.Label(label=ts_str)
        ts_end_value.set_xalign(0)
        ts_end_value.set_css_classes(["map_dashboard_value"])
        self.info_grid.attach(ts_end_value, 2, 4, 1, 1)

        # number of points
        points_label = Gtk.Label(label="Points: ")
        points_label.set_xalign(0)
        points_label.set_css_classes(["map_dashboard_label"])
        self.info_grid.attach(points_label, 1, 5, 1, 1)

        points_value = Gtk.Label(label=str(point_ct))
        points_value.set_xalign(0)
        points_value.set_css_classes(["map_dashboard_value"])
        self.info_grid.attach(points_value, 2, 5, 1, 1)

        self.info_box.append(self.info_grid)

        self.content_box.add_overlay(self.info_box)

        self.set_child(self.content_box)
