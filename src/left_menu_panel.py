#! /usr/bin/python3

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from panel import Panel

class LeftMenuPanel(Panel):
    def __init__(self, button_event_listener):
        super().__init__()

        self.event_listener = button_event_listener

        self.set_css_classes(["panel", "sidepanel"])
        self.position_button = Gtk.Button(label="Position")
        self.position_button.set_css_classes(["sidepanel_button"])
        self.position_button.connect("clicked", self.on_position_button_pressed)
        self.append(self.position_button)

        self.satellites_button = Gtk.Button(label="Satellites")
        self.satellites_button.set_css_classes(["sidepanel_button"])
        self.satellites_button.connect("clicked", self.on_satellites_button_pressed)
        self.append(self.satellites_button)

        self.satellites_graphic_button = Gtk.Button(label="Satellites2")
        self.satellites_graphic_button.set_css_classes(["sidepanel_button"])
        self.satellites_graphic_button.connect(
            "clicked", self.on_satellites_graphic_button_pressed
        )
        self.append(self.satellites_graphic_button)

        self.map_button = Gtk.Button(label="Map")
        self.map_button.set_css_classes(["sidepanel_button"])
        self.map_button.connect("clicked", self.on_map_button_pressed)
        self.append(self.map_button)

    def on_position_button_pressed(self, button):
        self.event_listener.on_position_button_pressed(button)

    def on_satellites_button_pressed(self, button):
        self.event_listener.on_satellites_button_pressed(button)

    def on_satellites_graphic_button_pressed(self, button):
        self.event_listener.on_satellites_graphic_button_pressed(button)

    def on_map_button_pressed(self, button):
        self.event_listener.on_map_button_pressed(button)
