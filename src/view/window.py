# window.py
#
# Copyright 2023 codenomad
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
        self._artist = artist or ""
        self._url = url or ""
        self._location = location or ""

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

    # Content Specific (maybe move to different file...)
    stitch_name_entry: Gtk.Entry = Gtk.Template.Child()
    stitch_artist_entry: Gtk.Entry = Gtk.Template.Child()
    stitch_link_entry: Gtk.Entry = Gtk.Template.Child()
    stitch_download_button: Gtk.Button = Gtk.Template.Child()

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
        self.sidebar_listview.props.single_click_activate = True
        self.sidebar_listview.connect("activate", self.update_content)

        # Set listview
        self.sidebar.append(self.sidebar_listview)

        # Add dummy data
        self.model.append(temp_object_one)
        self.update_content(self.sidebar_listview)


    def update_content(self, view, pos=None):
        model = view.get_model().get_selected_item()

        self.stitch_name_entry.set_text(model.name)
        self.stitch_artist_entry.set_text(model.artist)
        self.stitch_link_entry.set_text(model.url)


    # NOTE: This decorator is required for .blp/.ui files to setup the connections
    @Gtk.Template.Callback()
    def add_new_url(self, entry, icon_pos=None):
        if not self.sidebar_entry.get_icon_sensitive(1):
            print(f"Button not enabled yet...")
            return

        # capture the new url in entryfield
        input_buffer = entry.get_buffer()
        url = input_buffer.get_text()

        # Find the 'artist'
        pattern = r"twitter\.com\/([a-zA-Z0-9_]+)\/"
        match = re.search(pattern, url)
        detected_artist = "???"
        if match:
            detected_artist = match.group(1)

        # Add new StitchesObject to the store
        stitches_obj = StitchesObject(url=url, artist=detected_artist)
        self.model.append(stitches_obj)
        len = input_buffer.get_length()
        input_buffer.delete_text(0, len)
        print(f"yay - url added: {url}")

        # Disable button when nothing in text field
        #self.sidebar_entry.set_icon_sensitive(1, True)
        self.update_content(self.sidebar_listview)

    def get_artist_from_url(self, url):
        # Find the 'artist'
        pattern = r"twitter\.com\/([a-zA-Z0-9_]+)\/"
        match = re.search(pattern, url)
        detected_artist = "???"
        if match:
            detected_artist = match.group(1)
        return detected_artist

    # TODO: create one for each service so a custom mechanism to grab an artist/url/etc
    def is_valid_url(self, url):
        url_pattern = re.compile(r'https://(?:www\.)?(twitter\.com/([A-Za-z0-9_]+)/status/(\d+)|youtube\.com|rumble\.com)')
        if url_pattern.search(url):
            print(f"Looks like a valid url: {url}: {url_pattern.search(url)}")
            return True
        print(f"Womp womp, invalid url: {url}: {url_pattern.search(url)}")
        return False


    @Gtk.Template.Callback()
    def check_and_enable(self, entry):
        input_buffer = entry.get_buffer().get_text()
        curr_style = self.sidebar_notifier_label.get_style_context()

        if self.is_valid_url(input_buffer):
#            self.sidebar_entry.set_icon_sensitive(1, True)
#            self.sidebar_notifier_label.set_text("Looks good!")
#            curr_style.remove_class("error")
#            curr_style.add_class("success")
#            return
            pass

#        curr_style.remove_class("success")
#        curr_style.add_class("error")

#        if len(input_buffer) > 0:
#            self.sidebar_notifier_label.set_text("Not valid url.")
#        else:
#            self.sidebar_notifier_label.set_text("")
#
#        self.sidebar_entry.set_icon_sensitive(1, False)
        # TODO, indicator for invalid url

    @Gtk.Template.Callback()
    def enter_submission_check(self, entry):

        input_buffer = entry.get_buffer().get_text()
        if len(input_buffer) == 0:
            print("You didn't enter anything...")
            return

        print(f"Somebody hit enter with:\t{input_buffer}")
        self.add_new_url(entry)


    def _update_selected_stitch(self, stitch, stitch_pos):
        """Updates the selected item in the listview by deleting and replacing the item in the
        ListStore."""
        stitch = self.sidebar_listview.get_model().get_selected_item()
        exists, stitch_pos = self.model.find(stitch)

        # Something super bonkers got us here, how could this ever not exist when
        # an item is always selected?
        if not exists:
            return

        # Remove item at the position
        self.model.remove(stitch_pos)

        # Readd item at the position
        self.model.insert(stitch_pos, stitch)


    @Gtk.Template.Callback()
    def update_model_name(self, entry):
        print("Update model name has been changed")

        buffer = entry.get_text()

        # Don't do anything until we actually have a value to change to'
        if len(buffer) == 0:
            return

        # Get the selected model
        stitch = self.sidebar_listview.get_model().get_selected_item()
        exists, stitch_pos = self.model.find(stitch)
        stitch._name = buffer
        self._update_selected_stitch(stitch, stitch_pos)

        # Now update the model at the position in the listview
        print(f"Model.name is currently set to: {stitch.name}")


    @Gtk.Template.Callback()
    def update_model_artist(self, entry, artist=None):
        print("Update model name has been changed")

        buffer = entry.get_text()

        if artist:
            buffer = artist

        # Don't do anything until we actually have a value to change to'
        if len(buffer) == 0:
            return

        # Get the selected model
        stitch = self.sidebar_listview.get_model().get_selected_item()
        exists, stitch_pos = self.model.find(stitch)
        stitch._artist = buffer

        # If we were called externally, don't do the stitch update, need abstractions'
        if not artist:
            self._update_selected_stitch(stitch, stitch_pos)

        # Now update the model at the position in the listview
        print(f"Model.artist is currently set to: {stitch.artist}")


    @Gtk.Template.Callback()
    def update_model_url(self, entry):
        buffer = entry.get_text()

        # Don't do anything until we actually have a value to change to'
        if len(buffer) == 0:
            return

        if not self.is_valid_url(buffer):
            print(f"Invalid url: {buffer}")
            return

        # Get the selected model
        stitch = self.sidebar_listview.get_model().get_selected_item()
        exists, stitch_pos = self.model.find(stitch)
        stitch._url = buffer

        # The artist should always match the url (maybe made this configurable in prefernces)
        new_artist = self.get_artist_from_url(stitch.url)
        self.update_model_artist(entry, artist=new_artist)

        self._update_selected_stitch(stitch, stitch_pos)

        # Now update the model at the position in the listview
        print(f"Model.url is currently set to: {stitch.url}")


#    @Gtk.Template.Callback()
    def update_model_file_location(self, entry):
        buffer = entry.get_text()

        # Don't do anything until we actually have a value to change to'
        if len(buffer) == 0 and not self.is_valid_url(buffer):
            return

        # Get the selected model
        stitch = self.sidebar_listview.get_model().get_selected_item()
        exists, stitch_pos = self.model.find(stitch)
        stitch._location = buffer
        self._update_selected_stitch(stitch, stitch_pos)

        # Now update the model at the position in the listview
        print(f"Model.location is currently set to: {stitch.location}")


#    @Gtk.Template.Callback()
    def save_settings(self):
        #self.settings.set_int("window-width", win_size.width)
        #self.settings.set_int("window-height", win_size.height)
        print("yay - settings saved (Not Implimented yet")


    @Gtk.Template.Callback()
    def download_url(self, clicked_button):
        print("Should attempt to download the url.")
        stitch = self.sidebar_listview.get_model().get_selected_item()

        print(f"Downloading: {stitch.url}")

        # add yt-dlp call here


    # Ref: https://pypi.org/project/yt-dlp/#embedding-examples
    def download_from_youtube(self, url):
        from yt_dlp import YoutubeDL

        with YoutubeDL() as ydl:
            download = ydl.download([url])
            print(download)

