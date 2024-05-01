#!/usr/bin/env python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

class Window(Gtk.Window):

    def __init__(self):

        self.screen = Gdk.Screen.get_default()
        self.gtk_provider = Gtk.CssProvider()
        self.gtk_context = Gtk.StyleContext()
        self.gtk_context.add_provider_for_screen(self.screen, self.gtk_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


        Gtk.Window.__init__(self, title="Check Input")
        self.set_size_request(300, 80)
        self.mainbox = Gtk.VBox()
        self.add(self.mainbox)

        # entry
        self.name_entry      = Gtk.Entry()
        self.name_entry.set_name("name_entry")
        self.mainbox.pack_start(self.name_entry, True, True, 0)
        self.name_entry.connect("changed", self.check_input)

        entry_context = self.name_entry.get_style_context()
        self.entry_default_background_color = entry_context.get_background_color(Gtk.StateType.NORMAL)
        self.entry_default_background_color_str = self.entry_default_background_color.to_string()

        self.show_all()


    def check_input(self, _widget=None):
            if "red" in self.name_entry.get_text():
                self.gtk_provider.load_from_data('#name_entry { background: red; }')
            elif "green" in self.name_entry.get_text():
                self.gtk_provider.load_from_data('#name_entry { background: green; }')
            else:
                sss = b'#name_entry { background: ' + self.entry_default_background_color_str + '; }'
                print(sss)
                self.gtk_provider.load_from_data(sss)


if __name__ == '__main__':

    mainwin = Window()
    Gtk.main()

# EOF