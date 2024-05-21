#! /usr/bin/python3

import gi

gi.require_version('Gtk', '4.0')

from gi.repository import Gtk

from panel import Panel

class GpsdPanel (Panel):
    def __init__(self, event_listener, hostname = "localhost", port = 2947):
        super().__init__()

        self.button_event_listener = event_listener
        self.hostname = hostname
        self.port = port

        self.set_css_classes (['gpsd_panel', 'panel'])

        self.grid = Gtk.Grid()

        self.grid.set_row_spacing (10)
        self.grid.set_column_spacing (10)

        self.grid.insert_column(1)
        self.grid.insert_column(1)

        self.panel_label = Gtk.Label (label = "GPSD")
        self.panel_label.set_css_classes (['panel_title'])
        self.append (self.panel_label)
        self.append (self.grid)

        self.__add_to_grid ("host", "Hostname:", 1)
        self.__add_to_grid ("port", "Port:", 2)

        self.connect_button = Gtk.Button (label = "connect")
        self.connect_button.set_css_classes (['button'])
        self.connect_button.connect ("clicked", self.button_event_listener.on_connect_button)
        self.append (self.connect_button)

        self.disconnect_button = Gtk.Button(label = "disconnect")
        self.disconnect_button.set_css_classes (['button'])
        self.disconnect_button.connect ("clicked", self.button_event_listener.on_disconnect_button)
        self.append (self.disconnect_button)

        self.status = Gtk.Label ()
        self.append (self.status)

        self.update_parameter (self.hostname, self.port)

    def __add_to_grid (self, _name, _label, _row):
        self.grid.insert_row (_row)

        new_label = Gtk.Label (name = _name + "_label", label = _label)
        new_label.set_css_classes (['label'])
        self.grid.attach (new_label, 1, _row, 1, 1)

        new_value = Gtk.Label (name = _name + "_value", label = "---")
        new_value.set_css_classes (['value'])
        self.grid.attach (new_value, 2, _row, 1, 1)

    def __change_value (self, name, value):
        next_element = self.grid.get_first_child();

        while next_element != None:
            if next_element.get_name () == name + "_value":
                next_element.set_label (value)
                break
            else:
                next_element = next_element.get_next_sibling()

    def update_parameter (self, hostname, port):
        self.hostname = hostname
        self.port = port

        self.__change_value ("host", self.hostname)
        self.__change_value ("port", str(self.port))

    def update_info (self, json_object):
        pass
