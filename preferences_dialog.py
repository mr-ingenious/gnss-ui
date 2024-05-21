import sys
import gi

import logging

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

class PreferencesDialog(Gtk.Window):

    def __init__(self):
        super().__init__()
        logging.config.fileConfig("gnss-ui/log.ini")
        self.logger = logging.getLogger("app")

        self.set_default_size(700, 400)
        self.set_css_classes(["preferences_dialog"])
        self.set_modal(True)

        self.ok_button = Gtk.Button(label="OK")
        self.ok_button.connect("clicked", self.on_ok_button_pressed)

        self.cancel_button = Gtk.Button(label="Cancel")
        self.cancel_button.connect("clicked", self.on_cancel_button_pressed)

        self.set_title("Preferences")

        self.content_root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.buttons_box.set_hexpand(True)
        self.buttons_box.set_css_classes(["panel"])
        self.stack_box = Gtk.Box()
        self.stack_box.set_css_classes(["panel"])

        self.content_label = Gtk.Label(label="THIS IS THE CONTENT")

        # self.stack_box.append(self.content_label)

        ## PREFERENCES PAGE - GENERAL
        self.general_label = Gtk.Label(label="General")
        self.prefs_general = Gtk.Box()
        self.prefs_general.append(self.general_label)

        ## PREFERENCES PAGE - GPSD
        self.prefs_gpsd = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.prefs_gpsd_grid = Gtk.Grid()
        self.prefs_gpsd_grid.insert_column(1)
        self.prefs_gpsd_grid.insert_column(1)

        self.prefs_gpsd_grid.insert_row(0)
        self.prefs_gpsd_host_label = Gtk.Label(label="Hostname")
        self.prefs_gpsd_host_label.set_css_classes(["label"])
        self.prefs_gpsd_host_text = Gtk.EntryBuffer()
        self.prefs_gpsd_host_text.set_text("localhost", 9)
        self.prefs_gpsd_host_input = Gtk.Text()
        self.prefs_gpsd_host_input.set_name("gpsd.hostname")
        self.prefs_gpsd_host_input.connect("activate", self.on_text_input_changed)
        self.prefs_gpsd_host_input.set_buffer(self.prefs_gpsd_host_text)
        self.prefs_gpsd_host_input.set_css_classes(["value"])

        self.prefs_gpsd_port_label = Gtk.Label(label="Port")
        self.prefs_gpsd_port_label.set_css_classes(["label"])
        self.prefs_gpsd_port_text = Gtk.EntryBuffer()
        self.prefs_gpsd_port_text.set_text("2947", 4)
        self.prefs_gpsd_port_input = Gtk.Text()
        self.prefs_gpsd_port_input.set_name("gpsd.port")
        self.prefs_gpsd_port_input.connect("activate", self.on_text_input_changed)
        self.prefs_gpsd_port_input.set_buffer(self.prefs_gpsd_port_text)
        self.prefs_gpsd_port_input.set_css_classes(["value"])

        self.prefs_gpsd_grid.attach(self.prefs_gpsd_host_label, 0, 0, 1, 1)
        self.prefs_gpsd_grid.attach(self.prefs_gpsd_host_input, 1, 0, 1, 1)

        # self.prefs_gpsd_grid.insert_row(1)
        self.prefs_gpsd_grid.attach(self.prefs_gpsd_port_label, 0, 1, 1, 1)
        self.prefs_gpsd_grid.attach(self.prefs_gpsd_port_input, 1, 1, 1, 1)

        self.gpsd_label = Gtk.Label(
            label="GPSDasdf asdf asdf asdf asdf asdf asdf asdf asd f"
        )
        self.gpsd_button = Gtk.Button(label="TEST")
        self.prefs_gpsd.append(self.gpsd_label)
        self.prefs_gpsd.append(self.prefs_gpsd_grid)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        # self.stack.set_interpolate_size(True)
        self.stack.set_css_classes(["panel"])

        # self.stack.add_titled(self.prefs_general, "page_general", "General")
        # self.stack.add_titled(self.prefs_gpsd, "page_gpsd", "GPSD")

        # self.stack.set_visible_child_name("page_general")

        self.stack_sidebar = Gtk.StackSidebar()
        self.stack_sidebar.set_stack(self.stack)

        self.stack_box.append(self.stack_sidebar)
        self.stack_box.set_hexpand(True)
        self.stack_box.set_vexpand(True)

        self.buttons_box.append(self.ok_button)
        self.buttons_box.append(self.cancel_button)

        self.content_root.append(self.prefs_gpsd)
        # self.content_root.append(self.stack_box)
        self.content_root.append(self.buttons_box)

        self.set_child(self.content_root)

        self.set_visible(True)

    def save_changes(self):
        self.logger.debug("saving changes ...")
        self.logger.debug(
            "hostname: %s", self.prefs_gpsd_host_input.get_buffer().get_text()
        )
        
        self.logger.debug(
            "port: %s", self.prefs_gpsd_port_input.get_buffer().get_text()
        )

    def on_ok_button_pressed(self, *args):
        self.logger.debug("OK button clicked!")
        self.save_changes()
        self.close()

    def on_text_input_changed(self, user_data):
        self.logger.debug(
            "text input changed: %s --> %s",
            user_data.get_name(),
            repr(user_data.get_buffer().get_text()),
        )

    def on_cancel_button_pressed(self, *args):
        self.logger.debug("Cancel button clicked!")
        self.close()
