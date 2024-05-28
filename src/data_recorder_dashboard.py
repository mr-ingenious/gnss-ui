#! /usr/bin/python3

import logging

from panel import Panel

import gi
import time

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from data_recorder import DataRecorder, DataRecorderStatus
from data_transformer import DataTransformer

from datetime import datetime


class DataRecorderDashboard(Panel):
    def __init__(self, recorder, export_directory="./"):
        super().__init__()

        self.recorder = recorder
        self.export_directory = export_directory
        logging.config.fileConfig("gnss-ui/assets/log.ini")
        self.logger = logging.getLogger("recorder")

        self.set_css_classes(["recording_dashboard", "map_dashboard"])

        self.icons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.start_rec_button_icon = Gtk.Picture()
        self.start_rec_button_icon.set_filename(
            "gnss-ui/assets/circle_dot_round_icon.svg"
        )

        self.start_rec_button_icon_inactive = Gtk.Picture()
        self.start_rec_button_icon_inactive.set_filename(
            "gnss-ui/assets/circle_dot_round_icon_inactive.svg"
        )

        self.pause_rec_button_icon = Gtk.Picture()
        self.pause_rec_button_icon.set_filename("gnss-ui/assets/circle_pause_icon.svg")

        self.stop_rec_button_icon = Gtk.Picture()
        self.stop_rec_button_icon.set_filename("gnss-ui/assets/circle_stop_icon.svg")

        self.stop_rec_button_icon_inactive = Gtk.Picture()
        self.stop_rec_button_icon_inactive.set_filename(
            "gnss-ui/assets/circle_stop_icon_inactive.svg"
        )

        self.export_rec_button_icon = Gtk.Picture()
        self.export_rec_button_icon.set_filename(
            "gnss-ui/assets/floppy_disk_storage_icon.svg"
        )

        self.reset_button_icon = Gtk.Picture()
        self.reset_button_icon.set_filename(
            "gnss-ui/assets/trash_can_delete_remove_icon.svg"
        )

        # start_pause_button
        self.start_pause_rec_button = Gtk.Button(label="start/pause recording")
        self.start_pause_rec_button.connect(
            "clicked", self.on_start_pause_rec_button_pressed
        )
        self.start_pause_rec_button.set_tooltip_text("start / pause track recording")
        self.start_pause_rec_button.set_css_classes(
            ["recording_button", "recording_button:active", "recording_button:hover"]
        )
        self.start_pause_rec_button.set_child(self.start_rec_button_icon_inactive)
        self.icons_box.append(self.start_pause_rec_button)

        # stop button
        self.stop_rec_button = Gtk.Button(label="stop recording")
        self.stop_rec_button.connect("clicked", self.on_stop_rec_button_pressed)
        self.stop_rec_button.set_child(self.stop_rec_button_icon_inactive)
        self.stop_rec_button.set_css_classes(
            ["recording_button", "recording_button:active", "recording_button:hover"]
        )
        self.stop_rec_button.set_tooltip_text("stop track recording")

        self.icons_box.append(self.stop_rec_button)

        # reset button
        self.reset_rec_button = Gtk.Button(label="reset")
        self.reset_rec_button.connect(
            "clicked", self.on_reset_recordings_button_pressed
        )

        self.reset_rec_button.set_child(self.reset_button_icon)
        self.reset_rec_button.set_css_classes(
            ["recording_button", "recording_button:active", "recording_button:hover"]
        )
        self.reset_rec_button.set_tooltip_text("delete all recordings")
        self.icons_box.append(self.reset_rec_button)

        # export button
        self.export_rec_button = Gtk.Button(label="export")
        self.export_rec_button.connect(
            "clicked", self.on_export_recordings_button_pressed
        )
        self.export_rec_button.set_tooltip_text("export recording to file")

        self.export_rec_button.set_css_classes(
            ["recording_button", "recording_button:active", "recording_button:hover"]
        )
        self.export_rec_button.set_child(self.export_rec_button_icon)
        self.icons_box.append(self.export_rec_button)

        self.append(self.icons_box)

        self.status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.status_grid = Gtk.Grid()
        self.status_grid.insert_row(0)
        self.status_grid.insert_row(1)
        self.status_grid.insert_column(0)
        self.status_grid.insert_column(1)

        self.status_grid.set_row_spacing(10)
        self.status_grid.set_column_spacing(10)

        # recording status
        self.status_label = Gtk.Label(label="Status: ")
        self.status_label.set_css_classes(["map_dashboard_label"])
        self.status_grid.attach(self.status_label, 0, 0, 1, 1)

        self.status_value = Gtk.Label(label=self.recorder.get_status_str())
        self.status_value.set_css_classes(["map_dashboard_value"])
        self.status_grid.attach(self.status_value, 1, 0, 1, 1)

        self.current_recording_label = Gtk.Label(label="Recording: ")
        self.current_recording_label.set_css_classes(["map_dashboard_label"])
        self.status_grid.attach(self.current_recording_label, 0, 1, 1, 1)

        self.current_recording_name = Gtk.Label(label="-")
        self.current_recording_name.set_css_classes(["map_dashboard_value"])
        self.status_grid.attach(self.current_recording_name, 1, 1, 1, 1)

        self.status_box.append(self.status_grid)
        self.append(self.status_box)

    def on_start_pause_rec_button_pressed(self, button):
        self.logger.debug("[start/pause recording]")
        self.recorder.start_pause_recording()
        self.status_value.set_label(self.recorder.get_status_str())
        rec = self.recorder.get_current_recording()

        if self.recorder.get_status() == DataRecorderStatus.RECORDING_PAUSED:
            self.start_pause_rec_button.set_child(self.pause_rec_button_icon)
        else:
            self.start_pause_rec_button.set_child(self.start_rec_button_icon)

        self.stop_rec_button.set_child(self.stop_rec_button_icon)

        if rec != None:
            self.current_recording_name.set_label(rec.name)
        else:
            self.current_recording_name.set_label("-")

    def on_stop_rec_button_pressed(self, button):
        self.logger.debug("[stop recording]")
        self.recorder.stop_recording()
        self.status_value.set_label(self.recorder.get_status_str())

        self.stop_rec_button.set_child(self.stop_rec_button_icon_inactive)
        self.start_pause_rec_button.set_child(self.start_rec_button_icon_inactive)

        rec = self.recorder.get_current_recording()

        if rec != None:
            self.current_recording_name.set_label(rec.name)
        else:
            self.current_recording_name.set_label("-")

    def on_reset_recordings_button_pressed(self, button):
        self.logger.debug("[reset recordings]")
        self.status_value.set_label("recordings reset")
        self.recorder.reset()

    def on_export_recordings_button_pressed(self, button):
        self.logger.debug("[export recording]")
        recordings = self.recorder.get_recordings()

        if len(recordings) > 0:
            for recording in recordings:
                id = recording[0]

                position_data = self.recorder.get_position_data_by_id(id)
                rec = dict()
                rec = {
                    "name": recording[1],
                    "description": recording[2],
                    "ts": recording[4],
                }

                ts = datetime.fromtimestamp(rec["ts"])
                ts_str = ts.strftime("%Y-%m-%dT%H-%M-%S")

                t = DataTransformer()
                gpx = t.to_gpx(
                    rec,
                    position_data,
                    filename=self.export_directory + "/track_" + ts_str + ".gpx",
                )
                self.status_value.set_label("Export done")
        else:
            self.status_value.set_label("No export")
