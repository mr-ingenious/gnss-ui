#! /usr/bin/python3

import gi
import time

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from panel import Panel


class SatellitesInfoPanel(Panel):
    def __init__(self, gnss_name, talker_id):
        super().__init__()
        # self.box = Gtk.Box()
        self.gnss_name = gnss_name
        self.talker_id = talker_id
        self.sat_in_view1 = {}
        self.sat_in_view2 = {}
        self.sat_in_view3 = {}

        self.last_gsa_update = time.time()
        self.last_gsv_update = time.time()

        self.set_css_classes(["satellites_info_panel", "panel"])

        self.grid = Gtk.Grid()

        self.grid.set_row_spacing(10)
        self.grid.set_column_spacing(10)

        self.grid.insert_column(1)
        self.grid.insert_column(1)

        self.sv_grid = Gtk.Grid()
        self.sv_grid.set_css_classes(["sv_grid"])
        self.sv_grid.set_row_spacing(5)
        self.sv_grid.set_column_spacing(10)

        self.sv_grid.insert_column(1)
        self.sv_grid.insert_column(1)
        self.sv_grid.insert_column(1)
        self.sv_grid.insert_column(1)
        self.sv_grid.insert_column(1)

        self.panel_label = Gtk.Label(label=self.gnss_name + " Satellites")
        self.panel_label.set_css_classes(["panel_title"])
        self.append(self.panel_label)
        self.append(self.grid)
        self.append(self.sv_grid)
        ### GSA data
        self.__add_to_grid("gsa.mode", "GSA selection mode:", 1)
        self.__add_to_grid("gsa.mode_fix_type", "GSA fix type:", 2)

        self.sv_grid_h0 = Gtk.Label(name="_sv_list_h0", label="SAT")
        self.sv_grid_h0.set_css_classes(["label"])
        self.sv_grid.attach(self.sv_grid_h0, 1, 1, 1, 1)

        self.sv_grid_h1 = Gtk.Label(name="_sv_list_h1", label="PRN")
        self.sv_grid_h1.set_css_classes(["label"])
        self.sv_grid.attach(self.sv_grid_h1, 2, 1, 1, 1)

        self.sv_grid_h2 = Gtk.Label(name="_sv_list_h2", label="EL")
        self.sv_grid_h2.set_css_classes(["label"])
        self.sv_grid.attach(self.sv_grid_h2, 3, 1, 1, 1)

        self.sv_grid_h3 = Gtk.Label(name="_sv_list_h3", label="AZ")
        self.sv_grid_h3.set_css_classes(["label"])
        self.sv_grid.attach(self.sv_grid_h3, 4, 1, 1, 1)

        self.sv_grid_h4 = Gtk.Label(name="_sv_list_h4", label="SNR")
        self.sv_grid_h4.set_css_classes(["label"])
        self.sv_grid.attach(self.sv_grid_h4, 5, 1, 1, 1)

        for x in range(2, 18):
            self.__add_to_sv_grid(
                "gsv.sat_info_" + str(x - 1), "#" + str(x - 1) + ":", (x)
            )

    def __add_to_grid(self, _name, _label, _row):
        self.grid.insert_row(_row)

        new_label = Gtk.Label(name=_name + "_label", label=_label)
        new_label.set_css_classes(["label"])
        self.grid.attach(new_label, 1, _row, 1, 1)

        new_value = Gtk.Label(name=_name + "_value", label="---")
        new_value.set_css_classes(["value"])
        self.grid.attach(new_value, 2, _row, 1, 1)

    def __add_to_sv_grid(self, _name, _label, _row):
        self.sv_grid.insert_row(_row)

        new_label = Gtk.Label(name=_name + "_label", label=_label)
        new_label.set_css_classes(["label"])
        self.sv_grid.attach(new_label, 1, _row, 1, 1)

        new_value = Gtk.Label(name=_name + "_value_prn", label="")
        new_value.set_css_classes(["sv_value"])
        self.sv_grid.attach(new_value, 2, _row, 1, 1)

        new_value = Gtk.Label(name=_name + "_value_elevation", label="")
        new_value.set_css_classes(["sv_value"])
        self.sv_grid.attach(new_value, 3, _row, 1, 1)

        new_value = Gtk.Label(name=_name + "_value_azimuth", label="")
        new_value.set_css_classes(["sv_value"])
        self.sv_grid.attach(new_value, 4, _row, 1, 1)

        new_value = Gtk.Label(name=_name + "_value_snr", label="")
        new_value.set_css_classes(["sv_value"])
        self.sv_grid.attach(new_value, 5, _row, 1, 1)

    def __change_value(self, name, value):
        next_element = self.grid.get_first_child()

        while next_element != None:
            if next_element.get_name() == name + "_value":
                next_element.set_label(value)
                break
            else:
                next_element = next_element.get_next_sibling()

    def __change_sv_value(self, num, prn, elevation, azimuth, snr):
        next_element = self.sv_grid.get_first_child()

        prefix = "gsv.sat_info_" + str(num)

        while next_element != None:
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

    def update(self, msg):
        if msg["talker"] != self.talker_id:
            return

        if msg["type"] == "GSA" and (time.time() - self.last_gsa_update >= 1):
            self.last_gsa_update = time.time()

            self.__change_value("gsa.mode", msg["smode"])
            self.__change_value("gsa.mode_fix_type", msg["mode"])

        if msg["type"] == "GSV":
            self.last_gsv_update = time.time()

            idx = (int(msg["msg_num"]) - 1) * 4

            self.__change_sv_value(
                idx + 1,
                msg["sat_1_num"],
                msg["sat_1_elevation_deg"] + "°",
                msg["sat_1_azimuth_deg"] + "°",
                msg["sat_1_snr_db"] + " dB",
            )
            if int(msg["num_sat_info_in_msg"]) >= 2:
                self.__change_sv_value(
                    idx + 2,
                    msg["sat_2_num"],
                    msg["sat_2_elevation_deg"] + "°",
                    msg["sat_2_azimuth_deg"] + "°",
                    msg["sat_2_snr_db"] + " dB",
                )
            if int(msg["num_sat_info_in_msg"]) >= 3:
                self.__change_sv_value(
                    idx + 3,
                    msg["sat_3_num"],
                    msg["sat_3_elevation_deg"] + "°",
                    msg["sat_3_azimuth_deg"] + "°",
                    msg["sat_3_snr_db"] + " dB",
                )
            if int(msg["num_sat_info_in_msg"]) == 4:
                self.__change_sv_value(
                    idx + 4,
                    msg["sat_4_num"],
                    msg["sat_4_elevation_deg"] + "°",
                    msg["sat_4_azimuth_deg"] + "°",
                    msg["sat_4_snr_db"] + " dB",
                )

            if msg["num_msg"] == msg["msg_num"]:
                for idx in range(int(msg["num_msg"]), 4):
                    for sat in range(1, 5):
                        self.__change_sv_value(
                            (idx * 4) + sat,
                            "",
                            "",
                            "",
                            "",
                        )
