#! /usr/bin/python3

import gi
import time

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from panel import ScrolledPanel


class DyndataPanel(ScrolledPanel):
    def __init__(self):
        super().__init__()
        self.last_vtg_update = time.time()

        self.set_css_classes(["dyndata_panel", "panel"])

        self.grid = Gtk.Grid()

        self.grid.set_row_spacing(10)
        self.grid.set_column_spacing(10)

        self.grid.insert_column(1)
        self.grid.insert_column(1)

        self.panel_label = Gtk.Label(label="Dynamic Data")
        self.panel_label.set_css_classes(["panel_title"])
        self.set_child(self.panel_label)
        self.set_child(self.grid)

        self.__add_to_grid("vtg.track_true_north", "Track:", 1)
        self.__add_to_grid("vtg.track_mag", "Track mag.:", 2)
        self.__add_to_grid("vtg.speed_knots", "Speed (kn):", 3)
        self.__add_to_grid("vtg.speed_kph", "Speed (kph):", 4)
        self.__add_to_grid("vtg.faa_mode", "Mode:", 5)

        self.set_vexpand(True)

    def __add_to_grid(self, _name, _label, _row):
        self.grid.insert_row(_row)

        new_label = Gtk.Label(name=_name + "_label", label=_label)
        new_label.set_css_classes(["label"])
        self.grid.attach(new_label, 1, _row, 1, 1)

        new_value = Gtk.Label(name=_name + "_value", label="---")
        new_value.set_css_classes(["value"])
        self.grid.attach(new_value, 2, _row, 1, 1)

    def __change_value(self, name, value):
        next_element = self.grid.get_first_child()

        while next_element != None:
            if next_element.get_name() == name + "_value":
                next_element.set_label(value)
                break
            else:
                next_element = next_element.get_next_sibling()

    def update(self, msg):
        if msg["type"] == "VTG":
            self.__change_value(
                "vtg.track_true_north", msg["track_deg"] + " " + msg["true_north"]
            )
            self.__change_value(
                "vtg.track_mag",
                msg["track_mag"] + " " + msg["track_mag_relative_north"],
            )
            self.__change_value(
                "vtg.speed_knots", msg["speed_knots"] + " " + msg["unit_knots"]
            )
            self.__change_value(
                "vtg.speed_kps", msg["speed_kph"] + " " + msg["unit_kph"]
            )
            self.__change_value("vtg.faa_mode", msg["mode"])
