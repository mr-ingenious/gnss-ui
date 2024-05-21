import sys
import gi

import logging

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

xml = """\
<interface>
    <template class="preferences_window" parent="GtkWindow">
        <child>
            <object class="GtkBox" id="content_area">
                <child>
                    <object class="GtkButton" id="ok_button">
                        <property name="label">OK</property>
                        <signal name="clicked" handler="ok_button_clicked" swapped="no" />
                    </object>
                </child>
                <child>
                    <object class="GtkButton" id="cancel_button">
                        <property name="label">Cancel</property>
                        <signal name="clicked" handler="cancel_button_clicked" swapped="no" />
                    </object>
                </child>
            </object>
        </child>
    </template>
</interface>
"""


@Gtk.Template(string=xml)
class PreferencesDialog(Gtk.Window):
    __gtype_name__ = "preferences_window"

    ok_button = Gtk.Template.Child()
    cancel_button = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        logging.config.fileConfig("gnss-ui/log.ini")
        self.logger = logging.getLogger("app")

    @Gtk.Template.Callback()
    def ok_button_clicked(self, *args):
        self.logger.debug("OK button clicked!")

    @Gtk.Template.Callback()
    def cancel_button_clicked(self, *args):
        self.logger.debug("Cancel button clicked!")