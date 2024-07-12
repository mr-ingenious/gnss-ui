#! /usr/bin/python3

import gi

import sys, os

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


class ScrolledPanel(Gtk.ScrolledWindow):
    def __init__(self):
        super().__init__()  # orientation = Gtk.Orientation.VERTICAL)


class Panel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

    def _get_resource_file(self, resource_name):
        for p in sys.path:
            if p.find("gnss-ui/assets") != -1:
                if os.path.exists(p + "/" + resource_name):
                    return p + "/" + resource_name

        print("no resource file found: " + resource_name)
        return None
