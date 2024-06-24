#! /usr/bin/python3

import gi
import time
import math
import logging

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

        self.set_title(recording_info["name"])

        self.y_offset = 50
        self.x_offset = 40

        self.set_default_size(
            1024,
            768,
        )

        self.set_hexpand(True)
        self.set_vexpand(True)

        logging.config.fileConfig("gnss-ui/assets/log.ini")
        self.logger = logging.getLogger("app")

        self.overlay_box = Gtk.Overlay()
        self.overlay_box.set_hexpand(True)
        self.overlay_box.set_vexpand(True)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_content_height(700)
        self.drawing_area.set_content_width(len(position_data) + 100)
        self.drawing_area.set_draw_func(self.draw, None)
        self.scrolled_window.set_child(self.drawing_area)

        self.overlay_box.set_child(self.scrolled_window)

        # INFOBOX
        self.info_box = Gtk.Box()
        self.info_box.set_css_classes(["plot_info"])

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
        self.data_selection = Gtk.DropDown()
        self.select_items = Gtk.StringList()

        for f in self.fields:
            self.select_items.append(f)

        self.data_selection.set_model(self.select_items)
        self.data_selection.set_selected(self.selected_datatype)
        self.data_selection.connect("notify::selected-item", self.on_selected_datatype)

        self.controls_box.append(self.data_selection)
        self.overlay_box.add_overlay(self.controls_box)

        self.controls_box.set_hexpand(True)
        self.controls_box.set_vexpand(True)

        self.controls_box.set_halign(Gtk.Align.END)
        self.controls_box.set_valign(Gtk.Align.START)

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

    def draw(self, area, context, width, height, user_data):
        self.logger.debug("draw: width=%i, height=%i", width, height)

        context.set_source_rgb(0.8, 0.8, 0.8)
        context.paint()

        self.draw_plot_axes(context=context, width=width, height=height)

        self.draw_data(
            context=context,
            width=width,
            height=height,
            data=self.position_data,
            idx=self.selected_datatype + 1,
            label=self.fields[self.selected_datatype],
            colors=[0.5, 0.2, 0.2],
        )

    def draw_plot_axes(self, context, width, height):
        context.set_source_rgb(0.1, 0.1, 0.1)

        context.move_to(self.x_offset, height - self.y_offset)
        context.line_to(width - 40, height - self.y_offset)
        context.stroke()

        context.move_to(self.x_offset, 160)
        context.line_to(self.x_offset, height - self.y_offset)
        context.stroke()

        for x in range(self.x_offset, width - 40):
            if (x - self.x_offset) % 60 == 0:
                context.move_to(x, height - self.y_offset)
                context.line_to(x, height - self.y_offset - 5)
                context.stroke()

            if (x - self.x_offset) % 300 == 0:
                context.move_to(x, height - self.y_offset)
                context.line_to(x, height - self.y_offset + 10)
                context.stroke()
                context.move_to(x, height - self.y_offset + 20)
                context.show_text("+" + str((x - self.x_offset) / 60) + "min")

    def draw_data(
        self, context, width, height, data, idx, label="", colors=[0.1, 0.1, 0.1]
    ):
        context.set_source_rgb(colors[0], colors[1], colors[2])

        min = 0.0
        max = 0.0
        t_start = data[0][18]
        t_end = data[len(data) - 1][18]
        t_diff = t_end - t_start

        context.select_font_face("Sans")
        context.set_font_size(10)

        ts = datetime.fromtimestamp(t_start)
        ts_str = ts.strftime("%Y-%m-%d")
        context.move_to(self.x_offset, height - self.y_offset + 30)
        context.show_text(str(ts_str))

        ts_str = ts.strftime("%H:%M:%S")
        context.move_to(self.x_offset, height - self.y_offset + 40)
        context.show_text(str(ts_str))

        ts = datetime.fromtimestamp(t_end)
        ts_str = ts.strftime("%Y-%m-%d")
        context.move_to(width - 120, height - self.y_offset + 30)
        context.show_text(str(ts_str))

        ts_str = ts.strftime("%H:%M:%S")
        context.move_to(width - 120, height - self.y_offset + 40)
        context.show_text(str(ts_str))

        for s in data:
            if s[idx] < min:
                min = s[idx]

            if s[idx] > max:
                max = s[idx]

        self.logger.info("%s: length %.2f, min: %f, max: %f", label, t_diff, min, max)

        x = self.x_offset
        last = [x, height - self.y_offset]
        for s in data:
            y = height - self.y_offset - ((s[idx] / max) * (height - 200))
            context.move_to(last[0], last[1])
            context.line_to(x, y + 1)
            context.stroke()

            x = x + 1

            last = [x, y]

            if x > width - 40:
                break

    def on_selected_datatype(self, drop_down, selected_item):
        self.selected_datatype = self.data_selection.get_selected()
        
        self.logger.info(
            "another datatype selected: %s",
            self.fields[self.selected_datatype],
        )
        
        self.drawing_area.queue_draw()
