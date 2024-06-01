#! /usr/bin/python3

import logging

from panel import Panel

import gi
import time

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gio, GLib

from data_recorder import DataRecorder, DataRecorderStatus
from data_transformer import DataTransformer

from datetime import datetime


class DataRecorderPanel(Panel):
    def __init__(self, recorder, main_window, export_directory="./"):
        super().__init__()

        self.parent_window = main_window
        self.selected_recording = None
        self.dialog = None
        self.recorder = recorder
        self.export_directory = export_directory

        logging.config.fileConfig("gnss-ui/assets/log.ini")
        self.logger = logging.getLogger("recorder")

        self.set_css_classes(["recording_panel", "panel"])

        self.panel_label = Gtk.Label(label="Recorder")
        self.panel_label.set_css_classes(["panel_title"])
        self.append(self.panel_label)

        self.controls_frame = Gtk.Frame()
        self.controls_frame.set_css_classes(["recording_box"])
        self.controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.controls_frame.set_child(self.controls_box)
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
        self.start_pause_rec_button = Gtk.Button(label="start")
        self.start_pause_rec_button.connect(
            "clicked", self.on_start_pause_rec_button_pressed
        )
        self.start_pause_rec_button.set_tooltip_text("start / pause track recording")
        self.start_pause_rec_button.set_css_classes(["button"])
        # self.start_pause_rec_button.set_css_classes(
        #    ["recording_button", "recording_button:active", "recording_button:hover"]
        # )
        # self.start_pause_rec_button.set_child(self.start_rec_button_icon_inactive)
        self.icons_box.append(self.start_pause_rec_button)

        # stop button
        self.stop_rec_button = Gtk.Button(label="stop")
        self.stop_rec_button.connect("clicked", self.on_stop_rec_button_pressed)
        self.stop_rec_button.set_css_classes(["button"])
        # self.stop_rec_button.set_child(self.stop_rec_button_icon_inactive)
        # self.stop_rec_button.set_css_classes(
        #    ["recording_button", "recording_button:active", "recording_button:hover"]
        # )
        self.stop_rec_button.set_tooltip_text("stop track recording")

        self.icons_box.append(self.stop_rec_button)
        self.controls_box.append(self.icons_box)

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
        # self.status_value.set_css_classes(["map_dashboard_value"])
        self.status_grid.attach(self.status_value, 1, 0, 1, 1)

        self.current_recording_label = Gtk.Label(label="Recording: ")
        self.current_recording_label.set_css_classes(["map_dashboard_label"])
        self.status_grid.attach(self.current_recording_label, 0, 1, 1, 1)

        self.current_recording_name = Gtk.Label(label="-")
        # self.current_recording_name.set_css_classes(["map_dashboard_value"])
        self.status_grid.attach(self.current_recording_name, 1, 1, 1, 1)

        self.status_box.append(self.status_grid)
        self.controls_box.append(self.status_box)

        self.append(self.controls_frame)

        # self.set_hexpand(True)
        self.set_vexpand(True)

        # recordings table
        self.list_frame = Gtk.Frame()
        self.list_frame.set_visible(True)
        self.list_frame.set_css_classes(["recording_box"])
        self.recordings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.list_frame.set_child(self.recordings_box)

        self.recordings_table_box = Gtk.ListBox()
        self.recordings_table_box.set_css_classes(["recordings_table"])
        self.placeholder = Gtk.Label(label="-")
        self.placeholder.set_hexpand(True)
        self.placeholder.set_vexpand(True)
        self.recordings_table_box.set_placeholder(self.placeholder)
        self.recordings_table_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.recordings_table_box.set_show_separators(True)
        self.recordings_table_box.connect(
            "row-selected", self.on_recordings_list_row_selected
        )
        self.recordings_title = Gtk.Label(label="Recordings")
        self.recordings_title.set_css_classes(["map_dashboard_label"])

        self.recordings_box.append(self.recordings_title)
        self.update_recordings_table()
        self.recordings_list_scrolled_window = Gtk.ScrolledWindow()
        self.recordings_list_scrolled_window.set_css_classes(["recording_list_sw"])

        self.recordings_list_scrolled_window.set_child(self.recordings_table_box)
        self.recordings_box.append(self.recordings_list_scrolled_window)
        self.append(self.list_frame)

        # Recording details
        self.recording_details_frame = Gtk.Frame()
        self.recording_details_frame.set_css_classes(["recording_box"])
        self.recording_details_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.recording_details_frame.set_child(self.recording_details_box)
        self.recording_details_controls_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL
        )
        self.recording_details_info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.recordings_details = Gtk.Label(label="")
        self.recordings_details.set_css_classes(["recording_details"])

        self.recording_details_info_box.append(self.recordings_details)

        # reset button
        self.delete_rec_button = Gtk.Button(label="reset")
        self.delete_rec_button.connect(
            "clicked", self.on_delete_recording_button_pressed
        )

        self.delete_rec_button.set_child(self.reset_button_icon)
        self.delete_rec_button.set_css_classes(
            ["recording_button", "recording_button:active", "recording_button:hover"]
        )
        self.delete_rec_button.set_tooltip_text("delete recording")
        self.recording_details_controls_box.append(self.delete_rec_button)

        # export button
        self.export_rec_button = Gtk.Button(label="export")
        self.export_rec_button.connect(
            "clicked", self.on_export_recording_button_pressed
        )
        self.export_rec_button.set_tooltip_text("export recording to file")

        self.export_rec_button.set_css_classes(
            ["recording_button", "recording_button:active", "recording_button:hover"]
        )
        self.export_rec_button.set_child(self.export_rec_button_icon)
        self.recording_details_controls_box.append(self.export_rec_button)

        self.recording_details_box.append(self.recording_details_info_box)
        self.recording_details_box.append(self.recording_details_controls_box)

        self.recording_details_frame.set_visible(False)

        self.append(self.recording_details_frame)

    def on_start_pause_rec_button_pressed(self, button):
        self.logger.debug("[start/pause recording]")
        self.recording_details_frame.set_visible(False)
        self.recorder.start_pause_recording()
        self.status_value.set_label(self.recorder.get_status_str())
        rec = self.recorder.get_current_recording()

        if self.recorder.get_status() == DataRecorderStatus.RECORDING_PAUSED:
            # self.start_pause_rec_button.set_child(self.pause_rec_button_icon)
            self.start_pause_rec_button.set_label("pause")
        else:
            # self.start_pause_rec_button.set_child(self.start_rec_button_icon)
            self.start_pause_rec_button.set_label("start")

        # self.stop_rec_button.set_child(self.stop_rec_button_icon)

        if rec != None:
            self.current_recording_name.set_label(rec.name)
        else:
            self.current_recording_name.set_label("-")

    def on_stop_rec_button_pressed(self, button):
        self.logger.debug("[stop recording]")
        self.recording_details_frame.set_visible(False)
        self.recorder.stop_recording()
        self.status_value.set_label(self.recorder.get_status_str())

        # self.stop_rec_button.set_child(self.stop_rec_button_icon_inactive)
        # self.start_pause_rec_button.set_child(self.start_rec_button_icon_inactive)

        rec = self.recorder.get_current_recording()

        if rec != None:
            self.current_recording_name.set_label(rec.name)
        else:
            self.current_recording_name.set_label("-")

        self.update_recordings_table()

    def on_delete_recording_button_pressed(self, button):
        self.logger.debug("[delete recording]")

        self.dialog = Gtk.AlertDialog()
        self.dialog.set_buttons(["Delete", "Cancel"])
        self.dialog.set_detail(
            "Do you want to delete recording " + self.selected_recording["name"] + "?"
        )

        self.dialog.set_modal(False)
        self.dialog.choose(
            parent=self.parent_window,
            callback=self.on_delete_recording_confirmed,
            user_data=self.selected_recording["name"],
        )

    def on_delete_recording_confirmed(self, source_object, result, user_data):
        choice = source_object.choose_finish(result)

        if choice == 0:
            self.logger.debug("delete recording confirmed: %s", repr(user_data))

            if self.selected_recording != None:
                self.recordings_details.set_label(
                    "\nDeleted recording\n" + self.selected_recording["name"] + "\n"
                )
                self.recorder.delete_recording_by_id(int(self.selected_recording["id"]))
                self.recording_details_controls_box.set_visible(False)
                self.selected_recording = None
                self.update_recordings_table()
        else:
            self.logger.debug("delete recording cancelled.")

    def on_export_recording_button_pressed(self, button):
        self.logger.debug("[export recording]")
        if self.selected_recording != None:
            position_data = self.recorder.get_position_data_by_id(
                int(self.selected_recording["id"])
            )

            ts = datetime.fromtimestamp(self.selected_recording["ts_start"])
            ts_str = ts.strftime("%Y-%m-%dT%H-%M-%S")

            filename_str = "track_" + ts_str + ".gpx"
            t = DataTransformer()
            gpx = t.to_gpx(
                self.selected_recording,
                position_data,
                filename=self.export_directory + "/" + filename_str,
            )
            self.recordings_details.set_label(
                "\nExport done to file\n" + filename_str + "\n"
            )
        else:
            self.recordings_details.set_label("\nNo export.\n")

    def update_recordings_table(self):
        recordings = self.recorder.get_recordings()
        self.recordings_table_box.remove_all()

        # if len(recordings) == 0:
        #    self.list_frame.set_visible(False)
        # else:
        #    self.list_frame.set_visible(True)
        #
        for recording in recordings:
            recording_icon = Gtk.Picture()
            recording_icon.set_filename("gnss-ui/assets/map_icon.svg")
            recording_icon.set_css_classes(["recording_icon"])

            recording_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            recording_box.set_name(str(recording[0]))
            recording_box.set_css_classes("[recording_list_item]")
            recording_box.append(recording_icon)

            ts = datetime.fromtimestamp(recording[4])
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")

            pos_count = self.recorder.get_position_data_count_by_id(recording[0])
            sat_count = self.recorder.get_satellite_data_count_by_id(recording[0])
            recording_box.append(
                Gtk.Label(
                    label="Recording "
                    + ts_str
                    + "\nposition data: "
                    + str(pos_count)
                    + "\nsatellite data:"
                    + str(sat_count)
                )
            )
            self.recordings_table_box.append(recording_box)

    def on_recordings_list_row_selected(self, row, data):
        if data != None:
            self.recording_details_frame.set_visible(True)
            self.recording_details_controls_box.set_visible(True)
            self.logger.debug(
                "recordings list row selected: " + repr(data.get_child().get_name())
            )
            self.selected_recording = self.recorder.get_recording_by_id(
                int(data.get_child().get_name())
            )
            self.logger.debug("selected recording: %s", repr(self.selected_recording))

            ts = datetime.fromtimestamp(self.selected_recording["ts_start"])
            ts_start_str = ts.strftime("%Y-%m-%d %H:%M:%S")

            ts = datetime.fromtimestamp(self.selected_recording["ts_end"])
            ts_end_str = ts.strftime("%Y-%m-%d %H:%M:%S")

            self.recordings_details.set_label(
                self.selected_recording["name"]
                + "\n\n"
                + self.selected_recording["description"]
                + "\n\nstart: "
                + ts_start_str
                + "\nend: "
                + ts_end_str
            )

    def update(self):
        pass  # self.update_recordings_table()
