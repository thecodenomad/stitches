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

import json
import os
import re


from gi.repository import Adw
from gi.repository import Gtk, GObject, Gio

from threading import Lock

# Stitch Modules
from stitches import common, constants
from stitches.stitch_content import StitchContent

class StitchesObject(GObject.GObject):
    __gtype_name__ = 'StitchesObject'

    def __init__(self, name=None, artist=None, url=None, location=None):
        super().__init__()

        # By default grab the url for the name if it's not set. The user controls the name
        # of the object when they decide on the right hand side of the app'
        self._name = name
        self._artist = artist
        self._url = url or ""
        self._location = location

        if not self._artist:
            self._artist = common.get_artist_from_url(self._url)

        if not self._name:
            status_id = common.get_twitter_status_id(self._url)
            self._name = f"status_{status_id}.mkv"

        if not self._location:
            artist_dir = f"{constants.BASE_DL_LOC}/{self._artist}"
            artist_dir = os.path.expandvars(artist_dir)
            if not os.path.exists(artist_dir):
                os.mkdir(artist_dir)

            self._location = f"{constants.BASE_DL_LOC}/{self._artist}/{self._name}"
            self._location = os.path.expandvars(self._location)

    def update_location(self):
        self._location = f"{constants.BASE_DL_LOC}/{self._artist}/{self._name}"
        self._location = os.path.expandvars(self._location)

        artist_dir = f"{constants.BASE_DL_LOC}/{self._artist}"
        artist_dir = os.path.expandvars(artist_dir)
        if not os.path.exists(artist_dir):
            os.mkdir(artist_dir)

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

    # The entry field for URLs
    sidebar_entry: Gtk.Entry = Gtk.Template.Child()
    #sidebar_header: Adw.HeaderBar = Gtk.Template.Child()
    sidebar_save_button: Gtk.Button = Gtk.Template.Child()

    # The container for the list
    sidebar_window: Gtk.ScrolledWindow = Gtk.Template.Child()

    # The container page for the content panel
    # TODO: 'Add ability to embed exif data either on download, or after. Is there a way to
    #        embed a diff?
    adw_navigation_split_view: Adw.NavigationSplitView = Gtk.Template.Child()

    # Main content panel that shows the individual stitch and it's details
    stitch_content: StitchContent = Gtk.Template.Child()


    # TODO: Add logging to the config folder

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # self.settings = Gio.Settings.new("org.codenomad.stitches")
        temp_object_one = StitchesObject(
            name="Twitter1.mp4",
            artist="",
            url="https://twitter.com/Thekeksociety/status/1733473570343289235",
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

        # Add headerbar
        #StitchSidebarHeader(self.model)
        #print("Instantiated fine...\n\n\n")
        #self.sidebar_header = StitchSidebarHeader(self.model)

        # Set listview
        self.sidebar_window.set_child(self.sidebar_listview)

        # Add main content page
        print("Adding Stitch Content")
        self.stitch_content = StitchContent(self.sidebar_listview, self.model)
        self.adw_navigation_split_view.set_content(self.stitch_content)

        # Entry on the left should only accept URLs.
        self.sidebar_entry.set_input_purpose(Gtk.InputPurpose.URL)

        # TODO: Add ability to load from JSON
        # Add dummy data
        # self.model.append(temp_object_one)
        # self.stitch_content.update_content()

        #self.sidebar_save_button.connect("activate", self.save_list)

    def toggle_changes(self, *args, **kwargs):
        # TODO: Limit this when it's just a sorting change
        print("Changes have been made, enable save button")
        self.sidebar_save_button.set_sensitive(True)

    #    @Gtk.Template.Callback()
    def save_settings(self):
        # TODO: Add preferences panel:
        #       - Folder location to store stitches in.
        #       - Ability to save current list into a .json / .yaml file
        #       - Ability to load current list from .json / .yaml file
        #self.settings.set_int("window-width", win_size.width)
        #self.settings.set_int("window-height", win_size.height)
        print("yay - settings saved (Not Implimented yet")


    @Gtk.Template.Callback()
    def save_list(self, button):
        """ Saves the currently activated list """

        # Iterate over the store and save each item to dict for export to json
        out_doc = {}

        # Want O(1) lookup
        for stitch in self.model:
            out_doc[stitch.url] =  {
                "name": stitch.name,
                "artist": stitch.artist,
                "url": stitch.url,
                "location": stitch.location
            }

        filepath = f"{constants.BASE_DL_LOC}/{constants.DEFAULT_DB_FILENAME}"

        # Expand OS vars
        filepath = os.path.expandvars(filepath)

        try:
            with open(filepath, "w") as f:
                json.dump(out_doc, f)
            self.stitch_content.send_toast(f"Saved DB: {filepath}")

            # Reset after save
            self.sidebar_save_button.set_sensitive(False)
        except Exception as e:
            self.stitch_content.send_toast(f"Failed to save DB: {e}")
            self.sidebar_save_button.set_sensitive(True)


    # NOTE: This decorator is required for .blp/.ui files to setup the connections
    @Gtk.Template.Callback()
    def add_new_url(self, entry, icon_pos=None):
        """ Bound to the click action on the Gtk.EntryIconPosition.SECONDARY """

        # capture the new url in entryfield
        url = entry.get_text()

        # Do nothing
        if not common.is_valid_url(url):
            return

        # Add new StitchesObject to the store
        stitches_obj = StitchesObject(url=url)
        self.model.append(stitches_obj)
        entry.set_text("")

        selection_model = self.sidebar_listview.get_model()

        # Make sure the entry made is what is focused/selected
        _, stitch_pos = self.model.find(stitches_obj)
        selection_model.select_item(stitch_pos, True)

        # Disable button when nothing in text field
        self.stitch_content.update_content()

        # Remove the icon after the file was added
        common.update_secondary_icon(self.sidebar_entry, None)
        self.sidebar_save_button.set_sensitive(True)


    @Gtk.Template.Callback()
    def check_and_enable(self, entry):
        """ Called whenever there is a change in the Sidebar Entry """
        input_buffer = entry.get_text()

        # Default to no behavior
        icon_to_set = None
        if common.is_valid_url(input_buffer):
            icon_to_set = "document-save"
            self.sidebar_entry.set_icon_sensitive(Gtk.EntryIconPosition.SECONDARY, True)
        elif len(input_buffer) > 0:
            icon_to_set = "face-cryping"

        self.sidebar_entry.set_icon_sensitive(Gtk.EntryIconPosition.SECONDARY, False)
        common.update_secondary_icon(self.sidebar_entry, icon_to_set)



    @Gtk.Template.Callback()
    def enter_submission_check(self, entry):
        """ Called when user hits enter. """
        input_buffer = entry.get_text()
        if len(input_buffer) == 0:
            print("You didn't enter anything...")
            return

        self.add_new_url(entry)

