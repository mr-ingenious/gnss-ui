#! /usr/bin/python3

import gi
import time

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from panel import Panel

import logging
import logger


class SatellitesInfoPanel(Panel):
    def __init__(self):
        super().__init__()

        self.last_update = 0
        self.satellites_shown = dict()

        self.logger = logger.get_logger("app")

        self.panel_label = Gtk.Label(label="Satellites")
        self.panel_label.set_css_classes(["panel_title"])
        self.append(self.panel_label)

        self.set_css_classes(["satellites_info_panel", "panel"])

        self.satellites_summary = Gtk.Label(label="# Satellites: -")
        self.append(self.satellites_summary)

        # satellites table
        self.list_frame = Gtk.Frame()
        self.list_frame.set_visible(True)
        self.list_frame.set_css_classes(["recording_box"])

        self.sw = Gtk.ScrolledWindow()
        self.sw.set_vexpand(True)

        self.satellites_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.sw.set_child(self.satellites_box)

        self.list_frame.set_child(self.sw)

        self.satellites_list = Gtk.ListBox()
        # self.satellites_list.set_sort_func(sort_func=self.sort_list)
        self.satellites_list.set_css_classes(["recordings_table"])
        self.satellites_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.satellites_list.set_show_separators(True)
        self.satellites_box.append(self.satellites_list)
        self.append(self.list_frame)

    def sort_list(self, row1, row2):
        # self.logger.info("list sort: %s <<===>> %s", str(row1), str(row2))
        if row1.get_child().get_name() < row2.get_child().get_name():
            return 0
        else:
            return 1

    def build_list_item(self, sat):
        satellite_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        satellite_name = sat["system"] + "-" + sat["id"]

        satellite_icon = Gtk.Picture()
        if sat["used"]:
            satellite_icon.set_filename(
                self._get_resource_file("satellite_icon2_used.svg")
            )
        else:
            satellite_icon.set_filename(self._get_resource_file("satellite_icon2.svg"))

        satellite_box.set_name(satellite_name)
        satellite_box.append(satellite_icon)

        el_text = str(sat["elevation"]) + "°"
        az_text = str(sat["azimuth"]) + "°"
        snr_text = str(sat["snr"]) + "dB"
        if el_text == "-1.0°" and az_text == "-1.0°":
            el_text = "-"
            az_text = "-"

        if snr_text == "-1.0dB" or snr_text == "0.0dB":
            snr_text = "-"

        satid_label = Gtk.Label(label=satellite_name)
        satid_label.set_css_classes(["satellites_info_satellite_name"])
        satid_label.set_xalign(0)
        satellite_box.append(satid_label)

        elevation_label = Gtk.Label(label="EL")
        elevation_label.set_css_classes(["satellites_info_label"])
        satellite_box.append(elevation_label)

        elevation_value = Gtk.Label(label=el_text)
        elevation_value.set_css_classes(["satellites_info_value"])
        elevation_value.set_xalign(1)
        satellite_box.append(elevation_value)

        azimuth_label = Gtk.Label(label="AZ")
        azimuth_label.set_css_classes(["satellites_info_label"])
        satellite_box.append(azimuth_label)

        azimuth_value = Gtk.Label(label=az_text)
        azimuth_value.set_css_classes(["satellites_info_value"])
        azimuth_value.set_xalign(1)
        satellite_box.append(azimuth_value)

        snr_label = Gtk.Label(label="SNR")
        snr_label.set_css_classes(["satellites_info_label"])
        satellite_box.append(snr_label)

        snr_value = Gtk.Label(label=snr_text)
        snr_value.set_css_classes(["satellites_info_value"])
        snr_value.set_xalign(1)
        satellite_box.append(snr_value)

        return satellite_box

    def update_row(self, sat, remove_only=False):
        sat_name = sat["system"] + "-" + sat["id"]

        for row_idx in range(0, 65):
            row_item = self.satellites_list.get_row_at_index(row_idx)
            if row_item != None:
                if row_item.get_first_child().get_name() == sat_name:
                    self.logger.debug(
                        "sat list: update: %s (row %i)", sat_name, row_idx
                    )
                    self.satellites_list.remove(row_item)

                    if not remove_only:
                        self.satellites_list.insert(self.build_list_item(sat), row_idx)
                    break
            else:
                self.logger.warn("sat list: updating %s failed - not found!", sat_name)
                break

    def __is_equal(self, sat1, sat2):
        if (
            sat1["id"] == sat2["id"]
            and sat1["system"] == sat2["system"]
            and sat1["elevation"] == sat2["elevation"]
            and sat1["azimuth"] == sat2["azimuth"]
            and sat1["snr"] == sat2["snr"]
            and sat1["used"] == sat2["used"]
        ):
            return True
        else:
            return False

    def update(self, position_info, sat_info):
        self.__update_internal2(position_info=position_info, sat_info=sat_info)

    def __update_internal1(self, position_info, sat_info):
        if self.get_visible() and time.time() - self.last_update > 1:
            self.satellites_summary.set_label(
                "# Satellites: "
                + str(len(sat_info["data"].keys()))
                + " (in use:"
                + str(position_info["data"]["satellites_in_use"])
                + ")"
            )

            for k in sorted(sat_info["data"].keys()):
                # self.logger.debug("--- satellite %s", k)

                if k not in self.satellites_shown:
                    self.logger.debug("sat list: add %s", k)
                    # self.logger.debug("sat list: %s", repr(sat_info))

                    self.satellites_list.append(
                        self.build_list_item(sat_info["data"].get(k))
                    )
                    self.satellites_shown[k] = sat_info["data"].get(k)
                else:
                    if not self.__is_equal(
                        sat_info["data"].get(k), self.satellites_shown[k]
                    ):
                        # self.logger.info("--- update: %s", k)
                        # update existing satellite data
                        self.update_row(sat_info["data"].get(k))
                        self.satellites_shown[k] = sat_info["data"].get(k)
                    else:
                        pass  # self.logger.info("--- no change: %s", k)

            for k in list(self.satellites_shown.keys()):
                if sat_info["data"].get(k) == None:
                    self.logger.debug("sat list: remove %s", k)
                    self.update_row(self.satellites_shown.get(k), True)
                    self.satellites_shown.pop(k)

            self.last_update = time.time()

    def __update_internal2(self, position_info, sat_info):
        if self.get_visible() and time.time() - self.last_update > 1:
            self.satellites_summary.set_label(
                "# Satellites: "
                + str(len(sat_info["data"].keys()))
                + " (in use:"
                + str(position_info["data"]["satellites_in_use"])
                + ")"
            )

            # self.satellites_list.insert(self.build_list_item(sat), row_idx)

            self.satellites_list.remove_all()

            sat_dict = sat_info["data"]

            for sat in sorted(
                sat_dict.keys(),
                key=lambda x: (
                    sat_dict[x]["used"],
                    sat_dict[x]["snr"],
                    sat_dict[x]["system"],
                ),
                reverse=True,
            ):
                self.logger.debug("--- satellite %s", sat)
                self.satellites_list.insert(
                    self.build_list_item(sat_info["data"][sat]), -1
                )

            self.last_update = time.time()
