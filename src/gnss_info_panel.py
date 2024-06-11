#! /usr/bin/python3

import gi
import time

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from panel import Panel


"""

Provides an information like cgps

│ Long Err  (XDOP, EPX)   n/a ,  n/a        │
│ Lat Err   (YDOP, EPY)   n/a ,  n/a        │
│ Alt Err   (VDOP, EPV)   n/a ,  n/a        │
│ 2D Err    (HDOP, CEP)   n/a ,  n/a        │
│ 3D Err    (PDOP, SEP)   n/a ,  n/a        │
│ Time Err  (TDOP)        n/a               │
│ Geo Err   (GDOP)        n/a               │
│ Speed Err (EPS)         n/a               |
│ Track Err (EPD)         n/a               │
│ Time offset                               │
│ Grid Square             n/a               │
│ ECEF X, VX              n/a    n/a        │
│ ECEF Y, VY              n/a    n/a        │
│ ECEF Z, VZ              n/a    n/a        |


"""


class GnssInfoPanel(Panel):
    def __init__(self, as_dashboard=False):
        super().__init__()
        self.last_update = time.time()

        self.is_dashboard = as_dashboard

        self.set_css_classes(["gnss_panel", "panel"])
        self.panel_label = Gtk.Label(label="GNSS Info")
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
        # self.grid.insert_column(1)

        self.panel_frame.set_child(self.grid)
        self.append(self.panel_frame)

        self.__add_to_grid("lat_err", "Lat Err (YDOP, EPY):", 1)
        self.__add_to_grid("lon_err", "Long Err (XDOP, EPX):", 2)
        self.__add_to_grid("alt_err", "Alt Err (VDOP, EPV):", 3)

        self.__add_to_grid("2d_err", "2D Err (HDOP, CEP):", 4)
        self.__add_to_grid("3d_err", "3D Err (PDOP, SEP):", 5)

        self.__add_to_grid("time_err", "Time Err (TDOP):", 6)

        self.__add_to_grid("geo_err", "Geo Err (GDOP):", 7)
        self.__add_to_grid("speed_err", "Speed Err (EPS):", 8)
        self.__add_to_grid("track_err", "Track Err (EPD):", 9)

        self.__add_to_grid("ecef_x", "ECEF X, VX:", 10)
        self.__add_to_grid("ecef_y", "ECEF Y, VY:", 11)
        self.__add_to_grid("ecef_z", "ECEF Z, VZ:", 12)

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
        # self.grid.attach(new_value, 3, _row, 1, 1)

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
                "lon_err",
                "{:.2f}".format(position_info["data"]["dop"]["xdop"])
                + ", +/-"
                + "{:.2f}".format(position_info["data"]["gps_quality"]["error"]["epx"])
                + "m",
            )

            self.__change_value(
                "lat_err",
                "{:.2f}".format(position_info["data"]["dop"]["ydop"])
                + ", +/-"
                + "{:.2f}".format(position_info["data"]["gps_quality"]["error"]["epy"])
                + "m",
            )

            self.__change_value(
                "alt_err",
                "{:.2f}".format(position_info["data"]["dop"]["vdop"])
                + ", +/-"
                + "{:.2f}".format(position_info["data"]["gps_quality"]["error"]["epv"])
                + "m",
            )

            self.__change_value(
                "2d_err",
                "{:.2f}".format(position_info["data"]["dop"]["hdop"])
                + ", +/-"
                + "{:.1f}".format(position_info["data"]["gps_quality"]["error"]["eph"])
                + "m",
            )

            self.__change_value(
                "3d_err",
                "{:.2f}".format(position_info["data"]["dop"]["pdop"])
                + ", +/-"
                + "{:.1f}".format(position_info["data"]["gps_quality"]["error"]["sep"])
                + "m",
            )

            self.__change_value(
                "time_err", "{:.2f}".format(position_info["data"]["dop"]["tdop"])
            )

            self.__change_value(
                "geo_err", "{:.2f}".format(position_info["data"]["dop"]["gdop"])
            )

            speed_kmh = 3.6 * position_info["data"]["gps_quality"]["error"]["eps"]
            self.__change_value("speed_err", "{:.2f}".format(speed_kmh) + "km/h")

            self.__change_value(
                "track_err",
                "{:.3f}".format(position_info["data"]["gps_quality"]["error"]["epd"]),
            )

            self.__change_value(
                "ecef_x",
                "{:.2f}".format(position_info["data"]["ecef"]["x"])
                + " / "
                + "{:.3f}".format(position_info["data"]["ecef"]["vx"]),
            )

            self.__change_value(
                "ecef_y",
                "{:.2f}".format(position_info["data"]["ecef"]["y"])
                + " / "
                + "{:.3f}".format(position_info["data"]["ecef"]["vy"]),
            )

            self.__change_value(
                "ecef_z",
                "{:.2f}".format(position_info["data"]["ecef"]["z"])
                + " / "
                + "{:.3f}".format(position_info["data"]["ecef"]["vz"]),
            )
            self.last_update = time.time()
