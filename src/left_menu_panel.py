#! /usr/bin/python3

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from panel import Panel


class LeftMenuPanel(Panel):
    def __init__(
        self,
        position_info_panel,
        satellites_info_panel,
        satellites_radar_panel,
        map_panel,
        recorder_panel,
    ):
        super().__init__()

        self.position_info_panel = position_info_panel
        self.satellites_info_panel = satellites_info_panel
        self.satellites_radar_panel = satellites_radar_panel
        self.map_panel = map_panel
        self.recorder_panel = recorder_panel

        self.set_css_classes(["panel", "sidepanel"])

        self.position_icon = Gtk.Picture()

        self.__set_icon(
            self.position_info_panel,
            self.position_icon,
            "gnss-ui/assets/panel_icon_position_info(!).svg",
        )

        self.position_button = Gtk.Button(label="Position")
        self.position_button.set_tooltip_text("Toggle Position Panel")
        self.position_button.set_css_classes(["sidepanel_button"])
        self.position_button.set_child(self.position_icon)

        self.position_button.connect("clicked", self.on_position_info_button_pressed)
        self.append(self.position_button)

        self.satellites_icon = Gtk.Picture()
        self.__set_icon(
            self.satellites_info_panel,
            self.satellites_icon,
            "gnss-ui/assets/panel_icon_satellites_info2(!).svg",
        )
        self.satellites_button = Gtk.Button(label="Satellites")
        self.satellites_button.set_tooltip_text("Toggle Satellites Panel")
        self.satellites_button.set_css_classes(["sidepanel_button"])
        self.satellites_button.set_child(self.satellites_icon)
        self.satellites_button.connect(
            "clicked", self.on_satellites_info_button_pressed
        )
        self.append(self.satellites_button)

        self.satellites_radar_icon = Gtk.Picture()
        self.__set_icon(
            self.satellites_radar_panel,
            self.satellites_radar_icon,
            "gnss-ui/assets/panel_icon_satellites_radar(!).svg",
        )
        self.satellites_radar_button = Gtk.Button(label="Satellites Radar")
        self.satellites_radar_button.set_tooltip_text("Toggle Satellites Radar Panel")
        self.satellites_radar_button.set_child(self.satellites_radar_icon)
        self.satellites_radar_button.set_css_classes(["sidepanel_button"])
        self.satellites_radar_button.connect(
            "clicked", self.on_satellites_radar_button_pressed
        )
        self.append(self.satellites_radar_button)

        self.map_icon = Gtk.Picture()
        self.__set_icon(
            self.map_panel,
            self.map_icon,
            "gnss-ui/assets/panel_icon_map(!).svg",
        )
        self.map_button = Gtk.Button(label="Map")
        self.map_button.set_tooltip_text("Toggle Map Panel")
        self.map_button.set_child(self.map_icon)
        self.map_button.set_css_classes(["sidepanel_button"])
        self.map_button.connect("clicked", self.on_map_button_pressed)
        self.append(self.map_button)

        self.recorder_icon = Gtk.Picture()
        self.__set_icon(
            self.recorder_panel,
            self.recorder_icon,
            "gnss-ui/assets/panel_icon_recorder(!).svg",
        )

        self.recorder_button = Gtk.Button(label="Recorder")
        self.recorder_button.set_css_classes(["sidepanel_button"])
        self.recorder_button.set_tooltip_text("Toggle Recorder Panel")
        self.recorder_button.set_child(self.recorder_icon)
        self.recorder_button.connect("clicked", self.on_recorder_button_pressed)
        self.append(self.recorder_button)

    def __set_icon(self, panel, icon, filename_pattern):
        if panel.get_visible():
            icon.set_filename(filename_pattern.replace("(!)", ""))
        else:
            icon.set_filename(filename_pattern.replace("(!)", "_inactive"))

    def on_position_info_button_pressed(self, button):
        self.position_info_panel.set_visible(not self.position_info_panel.get_visible())
        self.__set_icon(
            self.position_info_panel,
            self.position_icon,
            "gnss-ui/assets/panel_icon_position_info(!).svg",
        )

    def on_satellites_info_button_pressed(self, button):
        self.satellites_info_panel.set_visible(
            not self.satellites_info_panel.get_visible()
        )
        self.__set_icon(
            self.satellites_info_panel,
            self.satellites_icon,
            "gnss-ui/assets/panel_icon_satellites_info2(!).svg",
        )

    def on_satellites_radar_button_pressed(self, button):
        self.satellites_radar_panel.set_visible(
            not self.satellites_radar_panel.get_visible()
        )
        self.__set_icon(
            self.satellites_radar_panel,
            self.satellites_radar_icon,
            "gnss-ui/assets/panel_icon_satellites_radar(!).svg",
        )

    def on_map_button_pressed(self, button):
        self.map_panel.set_visible(not self.map_panel.get_visible())
        self.__set_icon(
            self.map_panel,
            self.map_icon,
            "gnss-ui/assets/panel_icon_map(!).svg",
        )

    def on_recorder_button_pressed(self, button):
        self.recorder_panel.set_visible(not self.recorder_panel.get_visible())
        self.__set_icon(
            self.recorder_panel,
            self.recorder_icon,
            "gnss-ui/assets/panel_icon_recorder(!).svg",
        )
