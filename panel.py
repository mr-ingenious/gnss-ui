#! /usr/bin/python3

import gi

gi.require_version('Gtk', '4.0')

from gi.repository import Gtk

class ScrolledPanel(Gtk.ScrolledWindow):
    def __init__ (self):
        super().__init__() #orientation = Gtk.Orientation.VERTICAL)

class Panel(Gtk.Box):
    def __init__ (self):
        super().__init__(orientation = Gtk.Orientation.VERTICAL)