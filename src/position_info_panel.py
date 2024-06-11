#! /usr/bin/python3

import gi
import time

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from panel import Panel


class PositionInfoPanel(Panel):
    def __init__(self, as_dashboard=False):
        super().__init__()
        self.last_update = time.time()
        self.is_dashboard = as_dashboard

        if self.is_dashboard:
            self.set_css_classes(["position_dashboard", "map_dashboard"])
        else:
            self.set_css_classes(["position_panel", "panel"])
            self.panel_label = Gtk.Label(label="Position")
            self.panel_label.set_css_classes(["panel_title"])
            self.append(self.panel_label)

            self.panel_frame = Gtk.Frame()
            self.panel_frame.set_visible(True)
            self.panel_frame.set_css_classes(["recording_box"])

        self.grid = Gtk.Grid()

        self.grid.set_row_spacing(10)
        self.grid.set_column_spacing(10)

        self.grid.insert_column(1)
        self.grid.insert_column(1)

        if self.is_dashboard:
            self.append(self.grid)
        else:
            self.panel_frame.set_child(self.grid)
            self.append(self.panel_frame)

        self.__add_to_grid("latitude", "Latitude:", 1)
        self.__add_to_grid("longitude", "Longitude:", 2)
        self.__add_to_grid("altitude", "Altitude [m]:", 3)

        self.__add_to_grid("cog", "COG [°]:", 4)
        self.__add_to_grid("mag_var", "Magn. var. [°]", 5)

        self.__add_to_grid("sog_kph", "SOG [kph]:", 6)

        # if not self.is_dashboard:
        #    self.__add_to_grid("sog_kts", "SOG [kts]:", 7)

        self.__add_to_grid("status", "Status:", 8)
        self.__add_to_grid("gps_quality", "GPS quality:", 9)

        self.__add_to_grid("hdop", "HDOP:", 10)
        self.__add_to_grid("pdop", "PDOP:", 11)
        self.__add_to_grid("vdop", "VDOP:", 12)

        self.set_vexpand(True)

    def __add_to_grid(self, _name, _label, _row):
        self.grid.insert_row(_row)

        new_label = Gtk.Label(name=_name + "_label", label=_label)
        new_label.set_xalign(0)

        if self.is_dashboard:
            new_label.set_css_classes(["map_dashboard_label"])
        else:
            new_label.set_css_classes(["label"])

        self.grid.attach(new_label, 1, _row, 1, 1)

        new_value = Gtk.Label(name=_name + "_value", label="---")

        if self.is_dashboard:
            new_value.set_css_classes(["map_dashboard_value"])
        else:
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

    def update(self, position_info):
        if self.get_visible():
            self.__change_value(
                "latitude",
                "{:.6f}".format(position_info["data"]["latitude"]["decimal"])
                + " "
                + position_info["data"]["latitude"]["direction"],
            )
            self.__change_value(
                "longitude",
                "{:.6f}".format(position_info["data"]["longitude"]["decimal"])
                + " "
                + position_info["data"]["longitude"]["direction"],
            )

            self.__change_value("cog", str(position_info["data"]["cog"]["deg"]))
            self.__change_value(
                "mag_var", "{:.2f}".format(position_info["data"]["cog"]["magvar_deg"])
            )

            self.__change_value("hdop", str(position_info["data"]["dop"]["hdop"]))
            self.__change_value("pdop", str(position_info["data"]["dop"]["pdop"]))
            self.__change_value("vdop", str(position_info["data"]["dop"]["vdop"]))
            self.__change_value(
                "altitude", str(position_info["data"]["altitude"]["msl"])
            )
            self.__change_value(
                "sog_kph", "{:.2f}".format(position_info["data"]["sog"]["kph"])
            )

            # if not self.is_dashboard:
            #    self.__change_value("sog_kts", str(position_info["data"]["sog"]["kts"]))
            self.__change_value("status", str(position_info["data"]["status"]))
            self.__change_value(
                "gps_quality", str(position_info["data"]["gps_quality"]["description"])
            )
            self.last_update = time.time()
