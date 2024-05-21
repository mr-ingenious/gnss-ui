#! /usr/bin/python3

import gi
import time
import math

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from panel import Panel


class SatellitesGraphicPanel(Panel):
    def __init__(self):
        super().__init__()

        self.drawing_area = Gtk.DrawingArea()

        self.satellites = dict()

        self.set_css_classes(["satellites_graphic_panel", "panel"])

        self.drawing_area.set_hexpand(True)
        self.drawing_area.set_vexpand(True)

        self.drawing_area.set_content_height(400)
        self.drawing_area.set_content_width(400)

        self.drawing_area.set_draw_func(self.draw, None)

        self.append(self.drawing_area)

        self.last_update = time.time()

    def draw(self, area, context, width, height, user_data):
        print("draw: width=", width, ", height=", height)

        # context.set_source_rgb(0.8, 0.8, 0.8)
        # context.paint()

        # arcs

        context.set_source_rgb(0.5, 0.5, 0.5)
        context.set_line_width(1)

        for i in range(1, 5):
            # x, y, radius, start_angle, stop_angle
            r = min(width, height) / 2 - 10
            radius = r - (r / 4 * i) + 1
            context.arc(width / 2, height / 2, radius, 0, 2 * math.pi)
            context.stroke()

        # draw lines
        max_len = 0.8 * (min(width, height) / 2 - 10)

        context.set_source_rgb(0.2, 0.2, 0.2)
        context.select_font_face("Sans")
        context.set_font_size(10)
        
        if width > 500 and height > 500:
            context.set_font_size(15)

        self.draw_element(context, width, height, 30, 30, "30°")
        self.draw_element(context, width, height, 30, 60, "60°")
        self.draw_element(context, width, height, 30, 90, "90°")

        context.set_line_width(1)

        for i in range(0, 12):
            x = width / 2 + max_len * math.cos(math.radians(30 * (i - 3)))
            y = height / 2 + max_len * math.sin(math.radians(30 * (i - 3)))

            context.move_to(width / 2, height / 2)
            context.line_to(x, y)
            context.stroke()
            context.move_to(x, y)
            context.show_text(str(30 * i) + "°")

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

        context.move_to(px, py + 15)
        context.show_text(title)

        if len(subtitle) > 0:
            context.move_to(px, py + 25)
            context.set_font_size(9)
            context.show_text(subtitle)

    def update(self, sat_info):
        if time.time() - self.last_update > 2:
            self.satellites = sat_info
            self.drawing_area.queue_draw()
            self.last_update = time.time()
