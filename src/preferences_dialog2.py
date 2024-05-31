import sys
import gi

import logging

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

xml = """\
<interface>
    <template class="preferences_window" parent="GtkWindow">
        <child>
            <object class="GtkBox" id="window_area">
                <property name="orientation">vertical</property>
                <child>
                    <object class="GtkBox" id="content_area">
                        <property name="orientation">vertical</property>
                        <child>
                            <object class="GtkBox" id="preferences_area">
                                <property name="orientation">vertical</property>
                                <child>
                                    <object class="GtkLabel" id="title">
                                        <property name="label">Preferences</property>
                                    </object>
                                </child>
                            </object>
                        </child>
                        <child>
                            <object class="GtkBox" id="buttons_area">
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
    preferences_area = Gtk.Template.Child()
    title = Gtk.Template.Child()
    buttons_area = Gtk.Template.Child()

    def __init__(self, config_provider):
        super().__init__()
        self.config = config_provider

        logging.config.fileConfig("gnss-ui/assets/log.ini")
        self.logger = logging.getLogger("preferences")

        self.title.set_css_classes(["panel_title"])
        self.buttons_area.set_css_classes(["preferences_buttons_area"])
        self.ok_button.set_css_classes(["button"])
        self.cancel_button.set_css_classes(["button"])

        self.set_css_classes(["preferences_dialog"])
        self.set_modal(True)
        self.set_visible(True)

        self.transform_config()

    def transform_config(self):
        self.logger.debug("transform_config ...")
        result = []
        self.get_ppart(self.config.get_all_params(), "", result)

        self.params_listbox = Gtk.ListBox()
        self.params_listbox.set_css_classes(["preferences_row"])
        self.params_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        # self.params_listbox.set_show_separators(True)
        self.params_listbox.connect("row-selected", self.on_param_selected)

        for t in result:
            if not "config" in t[0]:
                continue

            param_name = t[0].replace("config/", "")

            self.logger.debug("list: " + repr(t))
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            box.set_css_classes(["preferences_row"])
            box.set_name(t[0])
            label = Gtk.Label(label=param_name)
            label.set_name(t[0])
            label.set_css_classes(["preferences_label"])
            label.set_xalign(0)

            value_buffer = Gtk.EntryBuffer()
            value_buffer.set_text(str(t[1]), 60)

            value = Gtk.Entry()
            value.set_buffer(value_buffer)
            value.set_name(param_name + "_value")
            value.set_css_classes(["preferences_value"])

            # value = Gtk.Label(label=t[1])
            # value.set_name(param_name + "_value")
            # value.set_css_classes(["preferences_value"])

            box.append(label)
            box.append(value)

            self.params_listbox.append(box)

        self.preferences_area.append(self.params_listbox)

    def on_param_selected(self, row, data):
        self.logger.debug("param selected: " + repr(data.get_child().get_name()))

    def get_ppart(self, params, base, result):
        for key in params.keys():
            if isinstance(params.get(key), dict):
                if base == "":
                    sep = ""
                else:
                    sep = "/"
                self.get_ppart(params.get(key), base + sep + key, result)
            elif params.get(key) != None:
                if base == "":
                    sep = ""
                else:
                    sep = "/"
                result.append((base + sep + key, params.get(key)))

    def save_changes(self):
        self.logger.debug("saving changes ...")
        child = self.params_listbox.get_row_at_index(0)
        i = 1
        while child != None:
            self.logger.debug(
                " ---> "
                + child.get_child().get_first_child().get_name()
                + ": "
                + child.get_child().get_first_child().get_next_sibling().get_text()
            )
            child = self.params_listbox.get_row_at_index(i)
            i = i + 1

    @Gtk.Template.Callback()
    def ok_button_clicked(self, *args):
        self.logger.debug("OK button clicked!")
        self.save_changes()
        self.close()

    @Gtk.Template.Callback()
    def cancel_button_clicked(self, *args):
        self.logger.debug("Cancel button clicked!")
        self.close()
