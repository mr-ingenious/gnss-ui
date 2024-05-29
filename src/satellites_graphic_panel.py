#! /usr/bin/python3

import gi
import time
import math
import logging

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from panel import Panel


class SatellitesGraphicPanel(Panel):
    def __init__(self, as_dashboard=False):
        super().__init__()

        self.is_dashboard = as_dashboard

        self.last_update = time.time()

        self.satellites = dict()

        logging.config.fileConfig("gnss-ui/assets/log.ini")
        self.logger = logging.getLogger("app")

        self.panel_label = Gtk.Label(label="Satellites Radar")
        self.panel_label.set_css_classes(["panel_title"])
        self.append(self.panel_label)
        
        self.drawing_area = Gtk.DrawingArea()

        if self.is_dashboard:
            self.set_css_classes(["map_dashboard", "satellites_dashboard"])
            self.drawing_area.set_content_height(200)
            self.drawing_area.set_content_width(200)
        else:
            self.set_css_classes(["satellites_graphic_panel", "panel"])
            self.drawing_area.set_content_height(400)
            self.drawing_area.set_content_width(400)

        self.drawing_area.set_hexpand(True)
        self.drawing_area.set_vexpand(True)

        self.drawing_area.set_draw_func(self.draw, None)

        self.append(self.drawing_area)

    def draw(self, area, context, width, height, user_data):
        # self.logger.debug("draw: width=", width, ", height=", height)

        # context.set_source_rgb(0.8, 0.8, 0.8)
        # context.paint()

        # draw circles
        context.set_source_rgb(1.0, 1.0, 1.0)

        context.set_line_width(1)

        for i in range(1, 5):
            # x, y, radius, start_angle, stop_angle
            
            r = min(width, height) / 2 - 10
            if self.is_dashboard:
                r = min(width, height) / 2
            radius = r - (r / 4 * i) + 1
            context.arc(width / 2, height / 2, radius, 0, 2 * math.pi)
            context.stroke()

        # draw lines
        max_len = 0.8 * (min(width, height) / 2 - 10)

        # context.set_source_rgb(0.2, 0.2, 0.2)
        context.select_font_face("Sans")
        context.set_font_size(10)

        if width > 500 and height > 500:
            context.set_font_size(15)

        # add some value tags
        
        if not self.is_dashboard:
            self.draw_element(context, width, height, 30, 30, " 30°")
            self.draw_element(context, width, height, 30, 60, " 60°")
            self.draw_element(context, width, height, 30, 90, " 90°")

        context.set_line_width(2)

        step_range = range(0, 12)
        angle_inc = 30

        if self.is_dashboard:
            step_range = range(0, 4)
            angle_inc = 90

        for i in step_range:
            x = width / 2 + max_len * math.cos(math.radians(angle_inc * (i - 3)))
            y = height / 2 + max_len * math.sin(math.radians(angle_inc * (i - 3)))

            x_offset = (
                round(math.sin(math.radians(angle_inc * (i))), 1)
                # * math.cos(math.radians(30 * (i)))
                * (width / 30)
            )
            y_offset = (
                round(math.cos(math.radians(angle_inc * (i + 6))), 1)
                # * math.sin(math.radians(angle_inc * (i)))
                * (height / 30)
            )

            context.move_to(width / 2, height / 2)
            context.line_to(x, y)
            context.stroke()

            if not self.is_dashboard:
                context.move_to(x + x_offset, y + y_offset)
                context.show_text(str(angle_inc * i) + "°")

        if not "data" in self.satellites:
            return

        for sat, value in self.satellites["data"].items():
            if value["azimuth"] == -1 and value["elevation"] == -1:
                continue

            if value["system"] == "GP":
                context.set_source_rgb(0.5, 0.0, 0.2)
            elif value["system"] == "GA":
                context.set_source_rgb(0.2, 0.5, 0.0)
            elif value["system"] == "PQ":
                context.set_source_rgb(0.0, 0.2, 0.5)
            elif value["system"] == "GL":
                context.set_source_rgb(0.7, 0.5, 0.0)
            elif value["system"] == "GN":
                context.set_source_rgb(0.0, 0.7, 0.5)
            else:
                context.set_source_rgb(0.0, 0.0, 0.0)

            self.draw_element(
                context,
                width,
                height,
                int(value["azimuth"]),
                int(value["elevation"]),
                sat,
                ("", "-used-")[value["used"]],
            )

    def draw_element(
        self, context, width, height, azimuth, elevation, title, subtitle=""
    ):
        max_len = 0.75 * (min(width, height) / 2 - 10)

        context.select_font_face("Sans")
        context.set_font_size(11)

        if width > 500 and height > 500:
            context.set_font_size(20)

        context.set_line_width(4)

        px = width / 2 + max_len * ((90 - elevation) / 90) * math.cos(
            math.radians(azimuth - 90)
        )
        py = height / 2 + max_len * ((90 - elevation) / 90) * math.sin(
            math.radians(azimuth - 90)
        )

        context.move_to(px - 2, py - 2)
        context.line_to(px + 2, py + 2)
        context.stroke()

        context.move_to(px - 2, py + 2)
        context.line_to(px + 2, py - 2)
        context.stroke()

        if not self.is_dashboard:
            context.move_to(px, py + 15)
            context.show_text(title)

            if len(subtitle) > 0:
                context.move_to(px, py + 25)
                context.set_font_size(9)
                context.show_text(subtitle)

    def update(self, sat_info):
        if self.get_visible():
            self.satellites = sat_info
            self.drawing_area.queue_draw()
            self.last_update = time.time()
