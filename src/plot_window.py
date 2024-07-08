#! /usr/bin/python3

import gi
import time
import math
import logging

import logger

from datetime import datetime


gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


class PlotWindow(Gtk.Window):
    def __init__(self, recording_info, position_data, satellites_data):
        super().__init__()

        self.selected_datatype = 2  # set to altitude

        self.fields = [
            # "id",
            "latitude",
            "longitude",
            "altitude",
            "speed over ground",
            "course over ground",
            "course over ground (mag.)",
            "mag. variation",
            "satellites in use",
            "hdop",
            "pdop",
            "vdop",
            "gdop",
            "xdop",
            "ydop",
            "tdop",
            "gps quality",
            "geoid separation",
        ]

        self.recording_info = recording_info
        self.position_data = position_data
        self.satellites_data = satellites_data

        self.bin_size = 1  # data bin size in seconds

        self.set_title(recording_info["name"])

        self.y_offset = 50

        self.set_default_size(
            1024,
            768,
        )

        self.set_hexpand(True)
        self.set_vexpand(True)

        self.logger = logger.get_logger("app")

        self.overlay_box = Gtk.Overlay()
        self.overlay_box.set_hexpand(True)
        self.overlay_box.set_vexpand(True)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)

        self.yaxis_drawing_area = Gtk.DrawingArea()
        self.yaxis_drawing_area.set_content_height(700)
        self.yaxis_drawing_area.set_content_width(72)
        self.yaxis_drawing_area.set_draw_func(self.draw_yaxis, None)

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_content_height(700)
        self.drawing_area.set_content_width(len(position_data) + 100)
        self.drawing_area.set_draw_func(self.draw, None)
        self.scrolled_window.set_child(self.drawing_area)

        self.plot_content_box = Gtk.Box()
        self.plot_content_box.set_css_classes(["panel"])
        self.plot_content_box.set_hexpand(True)
        self.plot_content_box.set_vexpand(True)

        self.plot_content_box.append(self.yaxis_drawing_area)
        self.plot_content_box.append(self.scrolled_window)

        self.overlay_box.set_child(self.plot_content_box)

        # INFOBOX
        self.info_box = Gtk.Box()
        self.info_box.set_css_classes(["panel", "plot_info"])

        self.overlay_box.add_overlay(self.info_box)

        self.info_box.set_hexpand(True)
        self.info_box.set_vexpand(True)

        self.info_box.set_halign(Gtk.Align.START)
        self.info_box.set_valign(Gtk.Align.START)

        self.info_grid = Gtk.Grid()

        self.info_grid.set_row_spacing(10)
        self.info_grid.set_column_spacing(10)

        self.info_grid.insert_column(1)
        self.info_grid.insert_column(1)

        self.controls_box = Gtk.Box()
        self.controls_box.set_css_classes(["plot_controls"])
        self.data_selection = Gtk.DropDown()
        self.select_items = Gtk.StringList()

        for f in self.fields:
            self.select_items.append(f)

        self.data_selection.set_model(self.select_items)
        self.data_selection.set_selected(self.selected_datatype)
        self.data_selection.connect(
            "notify::selected-item", self.__on_selected_datatype
        )

        self.controls_box.append(self.data_selection)
        self.overlay_box.add_overlay(self.controls_box)

        self.controls_box.set_hexpand(True)
        self.controls_box.set_vexpand(True)

        self.controls_box.set_halign(Gtk.Align.END)
        self.controls_box.set_valign(Gtk.Align.START)

        # Zoom in button
        self.x_zoom_in_button = Gtk.Button(label="zoom in")
        self.x_zoom_in_button.connect("clicked", self.__on_x_zoom_in_button_pressed)
        self.x_zoom_in_button.set_css_classes(["button"])

        self.controls_box.append(self.x_zoom_in_button)

        # Zoom out button
        self.x_zoom_out_button = Gtk.Button(label="zoom out")
        self.x_zoom_out_button.connect("clicked", self.__on_x_zoom_out_button_pressed)
        self.x_zoom_out_button.set_css_classes(["button"])

        self.controls_box.append(self.x_zoom_out_button)

        # name
        name_label = Gtk.Label(label="Name: ")
        name_label.set_xalign(0)
        name_label.set_css_classes(["plot_info_label"])
        self.info_grid.attach(name_label, 1, 1, 1, 1)

        name_value = Gtk.Label(label=recording_info["name"])
        name_value.set_xalign(0)
        name_value.set_css_classes(["plot_info_value"])
        self.info_grid.attach(name_value, 2, 1, 1, 1)

        # description
        description_label = Gtk.Label(label="Description: ")
        description_label.set_xalign(0)
        description_label.set_css_classes(["plot_info_label"])
        self.info_grid.attach(description_label, 1, 2, 1, 1)

        description_value = Gtk.Label(label=recording_info["description"])
        description_value.set_xalign(0)
        description_value.set_css_classes(["plot_info_value"])
        self.info_grid.attach(description_value, 2, 2, 1, 1)

        # start timestamp
        ts_start_label = Gtk.Label(label="Start: ")
        ts_start_label.set_xalign(0)
        ts_start_label.set_css_classes(["plot_info_label"])
        self.info_grid.attach(ts_start_label, 1, 3, 1, 1)

        ts = datetime.fromtimestamp(recording_info["ts_start"])
        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
        ts_start_value = Gtk.Label(label=ts_str)
        ts_start_value.set_xalign(0)
        ts_start_value.set_css_classes(["plot_info_value"])
        self.info_grid.attach(ts_start_value, 2, 3, 1, 1)

        # end timestamp
        ts_end_label = Gtk.Label(label="End: ")
        ts_end_label.set_xalign(0)
        ts_end_label.set_css_classes(["plot_info_label"])
        self.info_grid.attach(ts_end_label, 1, 4, 1, 1)

        ts = datetime.fromtimestamp(recording_info["ts_end"])
        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
        ts_end_value = Gtk.Label(label=ts_str)
        ts_end_value.set_xalign(0)
        ts_end_value.set_css_classes(["plot_info_value"])
        self.info_grid.attach(ts_end_value, 2, 4, 1, 1)

        self.info_box.append(self.info_grid)

        self.set_child(self.overlay_box)

    def draw_yaxis(self, area, context, width, height, user_data):
        context.set_source_rgb(1.0, 1.0, 1.0)
        context.paint()

        metadata = self.__get_data_metadata(
            data=self.position_data, idx=self.selected_datatype + 1
        )

        self.__draw_plot_yaxis(
            context=context, width=width, height=height, metadata=metadata
        )

    def draw(self, area, context, width, height, user_data):
        self.logger.debug("draw: width=%i, height=%i", width, height)

        context.set_source_rgb(1.0, 1.0, 1.0)
        context.paint()

        metadata = self.__get_data_metadata(
            data=self.position_data, idx=self.selected_datatype + 1
        )

        self.drawing_area.set_content_width(metadata["bins"] + 100)

        self.__draw_plot_xaxis(
            context=context, width=width, height=height, metadata=metadata
        )

        self.__draw_data(
            context=context,
            width=width,
            height=height,
            data=self.position_data,
            idx=self.selected_datatype + 1,
            metadata=metadata,
            label=self.fields[self.selected_datatype],
            colors=[0.3, 0.3, 0.7],
        )

    def __draw_plot_yaxis(self, context, width, height, metadata):
        context.set_source_rgb(0.1, 0.1, 0.1)

        context.move_to(70, 160)
        context.line_to(70, height - self.y_offset)
        context.stroke()

        # y axis ticks
        if metadata["max"]["value"] > 0.0:
            context.move_to(10, 160 - 10)
            context.show_text(str(metadata["max"]["value"]))

            dist_per_tick = metadata["max"]["value"] / 10

            for i in range(0, 10):
                y = (
                    height
                    - self.y_offset
                    - (
                        ((i * dist_per_tick) / metadata["max"]["value"])
                        * (height - 200)
                    )
                )
                context.move_to(65, y)
                context.line_to(70, y)
                context.stroke()

                context.move_to(10, y)
                context.show_text("{:.2f}".format(i * dist_per_tick))

    def __draw_plot_xaxis(self, context, width, height, metadata):
        context.set_source_rgb(0.1, 0.1, 0.1)

        # x axis
        context.move_to(0, height - self.y_offset)
        context.line_to(metadata["bins"] + 50, height - self.y_offset)
        context.stroke()

        # x axis tickscontext.move_to(metadata["bins"], height - self.y_offset + 30)
        for x in range(0, metadata["bins"] + 50):
            if x % int(60 / self.bin_size) == 0:
                context.move_to(x, height - self.y_offset)
                context.line_to(x, height - self.y_offset - 5)
                context.stroke()

            if x % int(300 / self.bin_size) == 0:
                context.move_to(x, height - self.y_offset)
                context.line_to(x, height - self.y_offset + 10)
                context.stroke()
                context.move_to(x, height - self.y_offset + 20)
                context.show_text(
                    "+" + "{:.0f}".format(x / int(60 / self.bin_size)) + "min"
                )

        context.set_source_rgb(0.3, 0.0, 0.0)

        ts = datetime.fromtimestamp(metadata["t_start"])
        ts_str = ts.strftime("%Y-%m-%d")
        context.move_to(0, height - self.y_offset + 30)
        context.show_text(str(ts_str))

        ts_str = ts.strftime("%H:%M:%S")
        context.move_to(0, height - self.y_offset + 40)
        context.show_text(str(ts_str))

        x = metadata["bins"]

        if x < 80:
            x = 80
        ts = datetime.fromtimestamp(metadata["t_end"])
        ts_str = ts.strftime("%Y-%m-%d")
        context.move_to(x, height - self.y_offset + 30)
        context.show_text(str(ts_str))

        ts_str = ts.strftime("%H:%M:%S")
        context.move_to(x, height - self.y_offset + 40)
        context.show_text(str(ts_str))

    def __get_data_metadata(self, data, idx):
        min = 0.0
        min_idx = 0
        max = 0.0
        max_idx = 0

        t_start = data[0][18]
        t_end = data[len(data) - 1][18]
        t_diff = t_end - t_start

        i = 0
        for s in data:
            if s[idx] < min:
                min = s[idx]
                min_idx = i

            if s[idx] > max:
                max = s[idx]
                max_idx = i

            i = i + 1

        num_bins = int(t_diff / self.bin_size)

        self.logger.debug(
            "length %.2f secs, min: %.2f, max: %.2f, bin_size: %i, bins: %i",
            t_diff,
            min,
            max,
            self.bin_size,
            num_bins,
        )

        return {
            "min": {"value": min, "idx": min_idx},
            "max": {"value": max, "idx": max_idx},
            "t_start": t_start,
            "t_end": t_end,
            "t_diff": t_diff,
            "bins": num_bins,
        }

    def __draw_data(
        self,
        context,
        width,
        height,
        data,
        idx,
        metadata,
        label="",
        colors=[0.1, 0.1, 0.1],
    ):
        context.set_source_rgb(colors[0], colors[1], colors[2])

        context.select_font_face("Sans")
        context.set_font_size(10)

        if metadata["max"]["value"] != 0.0:
            bin_val_idx = 0
            bin_mean_val = 0.0
            bin_min_val = 1e100
            bin_max_val = 0.0

            bins = list()

            for s in data:
                bin_val_idx = bin_val_idx + 1
                bin_mean_val = bin_mean_val + s[idx]

                if s[idx] < bin_min_val:
                    bin_min_val = s[idx]

                if s[idx] > bin_max_val:
                    bin_max_val = s[idx]

                if bin_val_idx == self.bin_size:
                    bins.append(
                        {
                            "mean": bin_mean_val / self.bin_size,
                            "min": bin_min_val,
                            "max": bin_max_val,
                        }
                    )
                    bin_mean_val = 0.0
                    bin_val_idx = 0
                    bin_min_val = 1e100
                    bin_max_val = 0.0

            x = 0
            last = [x, height - self.y_offset]
            for s in bins:
                if self.bin_size > 1:
                    context.set_source_rgb(0.9, 0.5, 0.5)
                    y_min = (
                        height
                        - self.y_offset
                        - ((s["min"] / metadata["max"]["value"]) * (height - 200))
                    )

                    y_max = (
                        height
                        - self.y_offset
                        - ((s["max"] / metadata["max"]["value"]) * (height - 200))
                    )
                    context.move_to(x, y_min)
                    context.line_to(x, y_max)
                    context.stroke()

                    context.set_source_rgb(colors[0], colors[1], colors[2])

                y = (
                    height
                    - self.y_offset
                    - ((s["mean"] / metadata["max"]["value"]) * (height - 200))
                )
                context.move_to(last[0], last[1])
                context.line_to(x, y + 1)
                context.stroke()

                x = x + 1

                last = [x, y]

                if x > width - 40:
                    break

    def __on_selected_datatype(self, drop_down, selected_item):
        self.selected_datatype = self.data_selection.get_selected()

        self.logger.debug(
            "another datatype selected: <%s>",
            self.fields[self.selected_datatype],
        )

        self.drawing_area.queue_draw()
        self.yaxis_drawing_area.queue_draw()

    def __on_x_zoom_in_button_pressed(self, button):
        self.logger.debug("[zoom in] pressed")
        if self.bin_size >= 2:
            self.bin_size = self.bin_size - 1

        self.drawing_area.queue_draw()

    def __on_x_zoom_out_button_pressed(self, button):
        self.logger.debug("[zoom out] pressed")

        if self.bin_size < 5:
            self.bin_size = self.bin_size + 1

        self.drawing_area.queue_draw()
