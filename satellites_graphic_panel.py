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

        self.last_gsa_update = time.time()
        self.last_gsv_update = time.time()

    def draw(self, area, context, width, height, user_data):
        print("draw: width=", width, ", height=", height)

        context.set_source_rgb(0.8, 0.8, 0.8)
        context.paint()

        # Draw a line
        # context.set_source_rgb(0.5, 0.0, 0.5)
        # context.set_line_width(3)
        # context.move_to(10, 10)
        # context.line_to(width - 10, height - 10)
        # context.stroke()

        # Draw a rectangle
        # context.set_source_rgb(0.8, 0.8, 0.1)
        # context.move_to(10, 10)
        # context.rectangle(20, 20, 50, 20)
        # context.fill()

        # Draw some text
        # c.set_source_rgb(0.1, 0.1, 0.1)
        # c.select_font_face("Sans")
        # c.set_font_size(13)
        # c.move_to(25, 35)
        # c.show_text("Test")

        # arcs

        context.set_source_rgb(0.5, 0.5, 0.5)
        context.set_line_width(1)

        for i in range(1, 5):
            # x, y, radius, start_angle, stop_angle
            r = min(width, height) / 2 - 10
            radius = r - (r / 4 * i) + 1
            # print("radius: ", radius)
            context.arc(width / 2, height / 2, radius, 0, 2 * math.pi)
            # context.fill_preserve()
            context.stroke()

        # draw lines

        max_len = 0.8 * (min(width, height) / 2 - 10)

        context.set_source_rgb(0.2, 0.2, 0.2)
        context.select_font_face("Sans")
        context.set_font_size(10)

        self.draw_element(context, width, height, 30, 30, "30°")
        self.draw_element(context, width, height, 30, 60, "60°")
        self.draw_element(context, width, height, 30, 90, "90°")

        context.set_line_width(1)

        for i in range(0, 12):
            x = width / 2 + max_len * math.cos(math.radians(30 * (i - 3)))
            y = height / 2 + max_len * math.sin(math.radians(30 * (i - 3)))
            # print(30 * i, ": x=", x, ", y=", y)

            context.move_to(width / 2, height / 2)
            context.line_to(x, y)
            context.stroke()
            context.move_to(x, y)
            context.show_text(str(30 * i) + "°")

        for sat, value in self.satellites.items():
            if value["tlk"] == "GP":
                context.set_source_rgb(0.5, 0.0, 0.2)
            elif value["tlk"] == "GA":
                context.set_source_rgb(0.2, 0.5, 0.0)
            elif value["tlk"] == "PQ":
                context.set_source_rgb(0.0, 0.2, 0.5)
            elif value["tlk"] == "GL":
                context.set_source_rgb(0.7, 0.5, 0.0)
            elif value["tlk"] == "GN":
                context.set_source_rgb(0.0, 0.7, 0.5)
            else:
                context.set_source_rgb(0.0, 0.0, 0.0)

            self.draw_element(
                context,
                width,
                height,
                int(value["az"]),
                int(value["el"]),
                sat,
                ("", "-used-")[value["used"]],
            )

        # self.draw_element(context, width, height, 270, 30, "Sat 2")
        # self.draw_element(context, width, height, 170, 20, "Sat 3")
        # self.draw_element(context, width, height, 270, 90, "Sat 4")
        # self.draw_element(context, width, height, 270, 0, "Sat 5")

    def draw_element(
        self, context, width, height, azimuth, elevation, title, subtitle=""
    ):
        max_len = 0.75 * (min(width, height) / 2 - 10)

        # context.set_source_rgb(0.4, 0.0, 0.2)
        context.select_font_face("Sans")
        context.set_font_size(11)

        context.set_line_width(4)

        px = width / 2 + max_len * ((90 - elevation) / 90) * math.cos(
            math.radians(azimuth - 90)
        )
        py = height / 2 + max_len * ((90 - elevation) / 90) * math.sin(
            math.radians(azimuth - 90)
        )
        # print(
        #    "item: (az=",
        #    azimuth,
        #   ", el=",
        #   elevation,
        #   "): px=",
        #   px,
        #   ", py=",
        #   py,
        #   sep="",
        # )

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

    def update(self, msg):
        if msg["type"] == "GSA" and (time.time() - self.last_gsa_update >= 1):
            self.last_gsa_update = time.time()
            # print("satellites --- got GSA:", repr(msg))

            for i in range(1, 13):
                sat_id = msg["id_" + str(i)]
                if sat_id != "":
                    key = msg["talker"] + "-" + sat_id
                    # print("GSA: updating sat: ", key)
                    if self.satellites.get(key) != None:
                        self.satellites.get(key).update({"used": True})
                        print("GSA: updated satellite info:", self.satellites.get(key))

        if msg["type"] == "GSV":
            # print("satellites --- got GSV:", repr(msg))
            if time.time() - self.last_gsv_update > 5:
                for key in list(self.satellites.keys()):
                    if time.time() - self.satellites.get(key)["last_update"] > 5:
                        print("GSV: satellites: removing ", key)
                        self.satellites.pop(key)

                self.drawing_area.queue_draw()
                self.last_gsv_update = time.time()

            for i in range(1, int(msg["num_sat_info_in_msg"]) + 1):
                if (
                    msg["sat_" + str(i) + "_elevation_deg"] != ""
                    and msg["sat_" + str(i) + "_azimuth_deg"] != ""
                    and msg["sat_" + str(i) + "_num"] != ""
                ):
                    sat_key = msg["talker"] + "-" + msg["sat_" + str(i) + "_num"]
                    if self.satellites.get(sat_key) == None:
                        self.satellites[
                            msg["talker"] + "-" + msg["sat_" + str(i) + "_num"]
                        ] = {
                            "tlk": msg["talker"],
                            "el": msg["sat_" + str(i) + "_elevation_deg"],
                            "az": msg["sat_" + str(i) + "_azimuth_deg"],
                            "snr": msg["sat_" + str(i) + "_snr_db"],
                            "used": False,
                            "last_update": time.time(),
                        }

                        print(
                            "GSV: added new satellite info:",
                            self.satellites.get(sat_key),
                        )
                    else:
                        self.satellites.get(sat_key).update(
                            {
                                "tlk": msg["talker"],
                                "el": msg["sat_" + str(i) + "_elevation_deg"],
                                "az": msg["sat_" + str(i) + "_azimuth_deg"],
                                "snr": msg["sat_" + str(i) + "_snr_db"],
                                "last_update": time.time(),
                            }
                        )
                        # print("GSV: updated satellite info:", self.satellites.get(sat_key))
            # print("satellites:", repr(self.satellites))
