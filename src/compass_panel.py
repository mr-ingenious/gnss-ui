#! /usr/bin/python3

import gi
import time
import math
import logging
import random

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib

from panel import Panel


class CompassPanel(Panel):
    def __init__(self, as_dashboard=False):
        super().__init__()

        self.position = dict()

        self.is_dashboard = as_dashboard

        self.last_update = time.time()

        logging.config.fileConfig("gnss-ui/assets/log.ini")
        self.logger = logging.getLogger("app")

        self.logger.info("compass panel created")

        self.overlay_box = Gtk.Overlay()
        self.overlay_box.set_hexpand(True)
        self.overlay_box.set_vexpand(True)

        self.drawing_area = Gtk.DrawingArea()
        self.overlay_box.set_child(self.drawing_area)

        self.values_box = Gtk.Box()
        # self.values_box.set_hexpand(True)
        # self.values_box.set_vexpand(True)
        self.values_box.set_halign(Gtk.Align.CENTER)
        self.values_box.set_valign(Gtk.Align.CENTER)
        self.overlay_box.add_overlay(self.values_box)

        self.value_label = Gtk.Label(label="---")
        self.value_label.set_css_classes(["compass_value"])
        self.values_box.append(self.value_label)

        if self.is_dashboard:
            self.set_css_classes(["map_dashboard", "compass_dashboard"])
            self.drawing_area.set_content_height(150)
            self.drawing_area.set_content_width(150)
        else:
            self.panel_label = Gtk.Label(label="Compass")
            self.panel_label.set_css_classes(["panel_title"])
            self.append(self.panel_label)
            self.set_css_classes(["compass_panel", "panel"])
            self.drawing_area.set_content_height(400)
            self.drawing_area.set_content_width(400)

        # self.drawing_area.set_hexpand(True)
        # self.drawing_area.set_vexpand(True)

        self.drawing_area.set_draw_func(self.draw, None)

        self.append(self.overlay_box)

    def draw(self, area, context, width, height, user_data):
        # self.logger.debug("draw: width=", width, ", height=", height)

        # context.set_source_rgb(0.8, 0.8, 0.8)
        # context.paint()

        # draw circles
        context.set_source_rgb(0.85, 0.85, 0.85)

        context.set_line_width(1)

        # if self.is_dashboard:
        #    for i in range(1, 5):
        #        # x, y, radius, start_angle, stop_angle

        #        r = min(width, height) / 2 - 10
        #        if self.is_dashboard:
        #            r = min(width, height) / 2
        #        radius = r - (r / 4 * i) + 1
        #        context.arc(width / 2, height / 2, radius, 0, 2 * math.pi)
        #        context.stroke()

        # draw lines
        max_len = 0.8 * (min(width, height) / 2 - 10)

        context.select_font_face("Sans")
        context.set_font_size(15)

        if width > 500 and height > 500:
            context.set_font_size(20)

        context.set_line_width(1)

        step_range = range(0, 4)
        angle_inc = 90

        context.set_source_rgb(1.0, 1.0, 1.0)

        dir_txt = ["N", "E", "S", "W"]

        for i in step_range:
            x = width / 2 + max_len * math.cos(math.radians(angle_inc * (i - 1)))
            y = height / 2 + max_len * math.sin(math.radians(angle_inc * (i - 1)))

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
                # context.show_text(str(angle_inc * (i)) + "°")
                context.show_text(dir_txt[i])

        context.set_source_rgb(0.9, 0.9, 0.9)

        if "data" in self.position:
            cog = self.position["data"]["cog"]["deg"]
            sog = self.position["data"]["sog"]["kph"]

            if (
                self.position["data"]["latitude"]["decimal"] != 0.0
                and self.position["data"]["longitude"]["decimal"] != 0.0
            ):
                self.draw_arrow(context, width, height, cog)
            # self.draw_arrow(context, width, height, self.position["data"]["cog"]["mag_deg"])

            GLib.idle_add(self.update_value, cog, sog)

    def update_value(self, cog, sog):
        if (
            self.position["data"]["latitude"]["decimal"] == 0.0
            and self.position["data"]["longitude"]["decimal"] == 0.0
        ):
            self.value_label.set_label("---")
        else:
            if self.is_dashboard:
                self.value_label.set_label(str(cog) + "°\n" + str(sog) + "kph")
            else:
                self.value_label.set_label(
                    "course: " + str(cog) + "°\nspeed: " + str(sog) + "kph"
                )

    def draw_arrow(self, context, width, height, cog):
        max_len = 0.9 * (min(width, height) / 2 - 10)

        context.select_font_face("Sans")
        context.set_font_size(15)

        # cog = random.randrange(0, 359, 1)

        context.set_source_rgb(0.9, 9.0, 0.2)

        if width > 500 and height > 500:
            context.set_font_size(20)

        if self.is_dashboard:
            context.set_line_width(3)
        else:
            context.set_line_width(5)

        p1 = (
            (width / 2 + (1 * max_len) * math.cos(math.radians(cog - 90))),
            (height / 2 + (1 * max_len) * math.sin(math.radians(cog - 90))),
        )

        p2 = (
            (width / 2 + (0.70 * max_len) * math.cos(math.radians(cog + 4 - 90))),
            (height / 2 + (0.70 * max_len) * math.sin(math.radians(cog + 4 - 90))),
        )

        p3 = (
            (width / 2 + (0.70 * max_len) * math.cos(math.radians(cog - 4 - 90))),
            (height / 2 + (0.70 * max_len) * math.sin(math.radians(cog - 4 - 90))),
        )

        p4 = (
            (width / 2 + (0.65 * max_len) * math.cos(math.radians(cog - 90))),
            (height / 2 + (0.65 * max_len) * math.sin(math.radians(cog - 90))),
        )

        p5 = (
            (width / 2 + (0.25 * max_len) * math.cos(math.radians(cog - 90))),
            (height / 2 + (0.25 * max_len) * math.sin(math.radians(cog - 90))),
        )

        context.move_to(p1[0], p1[1])
        context.line_to(p2[0], p2[1])
        context.stroke()

        context.move_to(p1[0], p1[1])
        context.line_to(p3[0], p3[1])
        context.stroke()

        context.move_to(p2[0], p2[1])
        context.line_to(p3[0], p3[1])
        context.stroke()

        context.move_to(p4[0], p4[1])
        context.line_to(p5[0], p5[1])
        context.stroke()

        x_offset = (
            round(math.sin(math.radians(cog)), 1)
            # * math.cos(math.radians(30 * (i)))
            * (width / 10)
        )
        y_offset = (
            round(math.cos(math.radians(cog)), 1)
            # * math.sin(math.radians(angle_inc * (i)))
            * (height / 10)
        )

        # context.move_to(p1[0] + x_offset, p1[1] + y_offset)
        # context.set_source_rgb(1.0, 1.0, 1.0)
        # context.move_to(width / 2 - (width / 30), height / 2 + 5)
        # context.show_text(str(cog) + "°")

    def update(self, position_info):
        if self.get_visible():
            self.position = position_info
            self.drawing_area.queue_draw()
            self.last_update = time.time()
