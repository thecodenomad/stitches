# window.py
#
# Copyright 2023 Ray Gomez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from gi.repository import Adw
from gi.repository import Gtk, GObject, Gio


class StitchesObject(GObject.GObject):
    __gtype_name__ = 'StitchesObject'

    def __init__(self, name=None, artist=None, url=None, location=None):
        super().__init__()

        # By default grab the url for the name if it's not set. The user controls the name
        # of the object when they decide on the right hand side of the app'
        self._name = name or url
        self._artist = artist
        self._url = url
        self._location = location

    @GObject.Property(type=str)
    def name(self):
        return self._name

    @GObject.Property(type=str)
    def artist(self):
        return self._artist

    @GObject.Property(type=str)
    def url(self):
        return self._url

    @GObject.Property(type=str)
    def location(self):
        return self._location


@Gtk.Template(resource_path='/org/codenomad/stitches/window.ui')
class StitchesWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'StitchesWindow'

    sidebar: Gtk.Box = Gtk.Template.Child()
    sidebar_listview: Gtk.ListView = Gtk.Template.Child()
    sidebar_entry: Gtk.Entry = Gtk.Template.Child()
    sidebar_notifier_label: Gtk.Label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # self.settings = Gio.Settings.new("org.codenomad.stitches")
        temp_object_one = StitchesObject(
            name="Twitter 1",
            artist="LauraLoomer",
            url="https://twitter.com/LauraLoomer/status/1732853903941624275",
            location=None
        )

        self.model = Gio.ListStore.new(StitchesObject)
        #self.model.append(temp_object_two)

        # Setup the selected value
        self.selection = Gtk.SingleSelection.new(self.model)

        # Setup the Factory to build the ListView
        self.factory = Gtk.BuilderListItemFactory.new_from_resource(None, '/org/codenomad/stitches/listitem.ui')

        # Create the listview
        self.sidebar_listview = Gtk.ListView(model=self.selection, factory=self.factory)
        self.sidebar_listview.props.show_separators = True
        self.sidebar_listview.props.single_click_activate = False

        # Set listview
        self.sidebar.append(self.sidebar_listview)

        self.model.append(temp_object_one)

        # If empty, disable button (note: 0: start, 1: end of entrybox):
        self.sidebar_entry.set_icon_sensitive(1, False)

        # Connect entry icon to signal:
        # Gtk.Entry.signals.icon_press(entry, icon_pos)

        self.sidebar_entry.connect("icon-press", self.add_new_url)
        self.sidebar_entry.connect("changed", self.check_and_enable)
        self.sidebar_entry.connect("activate", self.enter_submission_check)


    def add_new_url(self, entry, icon_pos=None):

        print(f"Sensitivity: {self.sidebar_entry.get_icon_sensitive(1)}")
        if not self.sidebar_entry.get_icon_sensitive(1):
            print(f"Button not enabled yet...")
            return

        # capture the new url in entryfield
        input_buffer = entry.get_buffer()
        url = input_buffer.get_text()

        # Add new StitchesObject to the store
        stitches_obj = StitchesObject(url=url)
        self.model.append(stitches_obj)
        len = input_buffer.get_length()
        input_buffer.delete_text(0, len)
        print(f"yay - url added: {url}")

        # Disable button when nothing in text field
        self.sidebar_entry.set_icon_sensitive(1, False)

    def check_and_enable(self, entry):
        input_buffer = entry.get_buffer().get_text()
        url_pattern = re.compile(r'https?://(?:www\.)?(twitter\.com/([A-Za-z0-9_]+)/status/(\d+)|youtube\.com|rumble\.com)')

        if url_pattern.search(input_buffer):
            self.sidebar_entry.set_icon_sensitive(1, True)
            self.sidebar_notifier_label.set_text("Valid!")
            return

        self.sidebar_notifier_label.set_text("Not valid yet.")
        self.sidebar_entry.set_icon_sensitive(1, False)
        # TODO, indicator for invalid url

    def enter_submission_check(self, entry):

        input_buffer = entry.get_buffer().get_text()
        if len(input_buffer) == 0:
            print("You didn't enter anything...")
            return

        print(f"Somebody hit enter with:\t{input_buffer}")
        self.add_new_url(entry)

        # Check if the pressed key is Enter (keyval=65293)
#        if event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_KP_Enter:
            # Handle Enter key press
#            entered_text = widget.get_text()
#            print(f"Enter key pressed. Entered Text: {entered_text}")

    def save_settings(self):
        #self.settings.set_int("window-width", win_size.width)
        #self.settings.set_int("window-height", win_size.height)
        print("yay - settings saved (Not Implimented yet")

