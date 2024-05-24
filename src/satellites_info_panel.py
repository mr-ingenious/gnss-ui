#! /usr/bin/python3

import gi
import time

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from panel import Panel

import logging


class SatellitesInfoPanel(Panel):
    def __init__(self):
        super().__init__()

        self.last_update = 0

        logging.config.fileConfig("gnss-ui/assets/log.ini")

        self.logger = logging.getLogger("app")

        self.sw = Gtk.ScrolledWindow()

        self.content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.content.set_vexpand(True)
        self.sw.set_child(self.content)

        self.set_css_classes(["satellites_info_panel", "panel"])

        self.sv_grid = Gtk.Grid()
        self.sv_grid.set_css_classes(["sv_grid"])
        self.sv_grid.set_row_spacing(5)
        self.sv_grid.set_column_spacing(10)

        self.sv_grid.insert_column(1)
        self.sv_grid.insert_column(1)
        self.sv_grid.insert_column(1)
        self.sv_grid.insert_column(1)
        self.sv_grid.insert_column(1)
        self.sv_grid.insert_column(1)

        self.panel_label = Gtk.Label(label="Satellites")
        self.panel_label.set_css_classes(["panel_title"])
        self.content.append(self.panel_label)
        self.content.append(self.sv_grid)
        self.append(self.sw)

        self.sv_grid_h0 = Gtk.Label(name="_sv_list_h0", label="SAT")
        self.sv_grid_h0.set_css_classes(["label"])
        self.sv_grid.attach(self.sv_grid_h0, 1, 1, 1, 1)

        self.sv_grid_h0 = Gtk.Label(name="_sv_list_h1", label="U")
        self.sv_grid_h0.set_css_classes(["label"])
        self.sv_grid.attach(self.sv_grid_h0, 2, 1, 1, 1)

        self.sv_grid_h1 = Gtk.Label(name="_sv_list_h2", label="PRN")
        self.sv_grid_h1.set_css_classes(["label"])
        self.sv_grid.attach(self.sv_grid_h1, 3, 1, 1, 1)

        self.sv_grid_h2 = Gtk.Label(name="_sv_list_h3", label="EL")
        self.sv_grid_h2.set_css_classes(["label"])
        self.sv_grid.attach(self.sv_grid_h2, 4, 1, 1, 1)

        self.sv_grid_h3 = Gtk.Label(name="_sv_list_h4", label="AZ")
        self.sv_grid_h3.set_css_classes(["label"])
        self.sv_grid.attach(self.sv_grid_h3, 5, 1, 1, 1)

        self.sv_grid_h4 = Gtk.Label(name="_sv_list_h5", label="SNR")
        self.sv_grid_h4.set_css_classes(["label"])
        self.sv_grid.attach(self.sv_grid_h4, 6, 1, 1, 1)

        for x in range(
            2, 66
        ):  # 16 satellites per 4 systems (GPS, Galileo, Beidou, Glonass)
            self.__add_to_sv_grid(
                "gsv.sat_info_" + str(x - 1), "#" + str(x - 1) + ":", (x)
            )

    def __add_to_sv_grid(self, _name, _label, _row):
        self.sv_grid.insert_row(_row)

        new_label = Gtk.Label(name=_name + "_label", label=_label)
        new_label.set_css_classes(["label"])
        self.sv_grid.attach(new_label, 1, _row, 1, 1)

        new_label = Gtk.Label(name=_name + "_value_used", label="")
        new_label.set_css_classes(["sv_value"])
        self.sv_grid.attach(new_label, 2, _row, 1, 1)

        new_value = Gtk.Label(name=_name + "_value_prn", label="")
        new_value.set_css_classes(["sv_value"])
        self.sv_grid.attach(new_value, 3, _row, 1, 1)

        new_value = Gtk.Label(name=_name + "_value_elevation", label="")
        new_value.set_css_classes(["sv_value"])
        self.sv_grid.attach(new_value, 4, _row, 1, 1)

        new_value = Gtk.Label(name=_name + "_value_azimuth", label="")
        new_value.set_css_classes(["sv_value"])
        self.sv_grid.attach(new_value, 5, _row, 1, 1)

        new_value = Gtk.Label(name=_name + "_value_snr", label="")
        new_value.set_css_classes(["sv_value"])
        self.sv_grid.attach(new_value, 6, _row, 1, 1)

    def __change_sv_value(self, num, used, prn, elevation, azimuth, snr):
        next_element = self.sv_grid.get_first_child()

        prefix = "gsv.sat_info_" + str(num)

        while next_element != None:
            if next_element.get_name() == prefix + "_value_used":
                next_element.set_label(used)
                next_element = next_element.get_next_sibling()
                continue

            if next_element.get_name() == prefix + "_value_prn":
                next_element.set_label(prn)
                next_element = next_element.get_next_sibling()
                continue

            if next_element.get_name() == prefix + "_value_elevation":
                next_element.set_label(elevation)
                next_element = next_element.get_next_sibling()
                continue

            if next_element.get_name() == prefix + "_value_azimuth":
                next_element.set_label(azimuth)
                next_element = next_element.get_next_sibling()
                continue

            if next_element.get_name() == prefix + "_value_snr":
                next_element.set_label(snr)
                next_element = next_element.get_next_sibling()
                continue

            else:
                next_element = next_element.get_next_sibling()

    def update(self, sat_info):
        if self.get_visible() and time.time() - self.last_update > 2:
            idx = 1

            keys = sorted(sat_info["data"].keys())

            for k in keys:
                # self.logger.debug("--- satellite %s", k)
                currsat = sat_info["data"].get(k)

                used = ""
                if currsat["used"]:
                    used = "U"

                el_text = str(currsat["elevation"]) + "°"
                az_text = str(currsat["azimuth"]) + "°"
                snr_text = str(currsat["snr"]) + "dB"
                if el_text == "-1°" and az_text == "-1°":
                    el_text = "-"
                    az_text = "-"

                if snr_text == "-1dB":
                    snr_text = "-"

                self.__change_sv_value(
                    idx,
                    used,
                    k,
                    el_text,
                    az_text,
                    snr_text,
                )

                idx += 1

            for i in range(idx, 65):
                self.__change_sv_value(
                    i,
                    "",
                    "",
                    "",
                    "",
                    "",
                )

            self.last_update = time.time()
