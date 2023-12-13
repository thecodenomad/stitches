import os
import re

from gi.repository import Adw
from gi.repository import Gtk, GObject, Gio

from stitches import common

# 3rd party imports
from yt_dlp import YoutubeDL

BASE_DL_LOC = "$HOME/Videos/python"
YT_DLP_OPTIONS = {"outtmpl": f"{BASE_DL_LOC}/%(title)s.%(ext)s"}



@Gtk.Template(resource_path='/org/codenomad/stitches/stitch_content.ui')
class StitchContent(Adw.NavigationPage):
    __gtype_name__ = 'StitchContent'

    stitch_name_entry: Adw.EntryRow = Gtk.Template.Child()
    stitch_artist_entry: Adw.EntryRow = Gtk.Template.Child()
    stitch_link_entry: Adw.EntryRow = Gtk.Template.Child()
    stitch_file_location: Gtk.Entry = Gtk.Template.Child()
    stitch_video: Gtk.Video = Gtk.Template.Child()
    stitches_toast: Adw.ToastOverlay = Gtk.Template.Child()

    def __init__(self, stitch_listview, model, **kwargs):
        super().__init__(**kwargs)
        self.stitch_listview = stitch_listview
        self.model = model

    @Gtk.Template.Callback()
    def update_model_name(self, entry):
        print("Update model name has been changed")

        buffer = entry.get_text()

        # Don't do anything until we actually have a value to change to'
        if len(buffer) == 0:
            return

        # Get the selected model
        stitch = self.stitch_listview.get_model().get_selected_item()
        exists, stitch_pos = self.model.find(stitch)
        stitch._name = buffer
        stitch.update_location()

        self.stitch_file_location.set_text(f"{stitch.artist}/{stitch.name}")
        #self.stitch_download_button.set_sensitive(not os.path.exists(stitch.location))

        self._update_selected_stitch(stitch, stitch_pos)

        # Now update the model at the position in the listview
        # print(f"Model.name is currently set to: {stitch.artist}/{stitch.name}")

        # Url Entry should receive focus
        #self.sidebar_entry.grab_focus_without_selecting()
        if not os.path.exists(stitch.location):
            self.update_secondary_icon(self.stitch_file_location, "document-save")


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
        stitch = self.stitch_listview.get_model().get_selected_item()
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

        if not common.is_valid_url(buffer):
            print(f"Invalid url: {buffer}")
            return

        # Get the selected model
        stitch = self.stitch_listview.get_model().get_selected_item()
        exists, stitch_pos = self.model.find(stitch)
        stitch._url = buffer

        # The artist should always match the url (maybe made this configurable in prefernces)
        new_artist = common.get_artist_from_url(stitch.url)
        self.update_model_artist(entry, artist=new_artist)
        self._update_selected_stitch(stitch, stitch_pos)

        # Now update the model at the position in the listview
        print(f"Model.url is currently set to: {stitch.url}")


    @Gtk.Template.Callback()
    def stitch_file_location_click(self, clicked_button, pos=None):

        # Get the selected stitch
        stitch = self.stitch_listview.get_model().get_selected_item()

        # We already have the file, open up a folder location
        if os.path.exists(stitch.location):
            open_folder(stitch.location)
            return

        # TODO: Catch exceptions and throw in a toast for debug
        # add yt-dlp call here
        result = self.download_from_youtube(stitch.url, name=stitch.name, artist=stitch.artist)

        # If it was downloaded, then change the icon to be open folder
        # self.stitch_file_location.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "folder-download")
        self.update_secondary_icon(self.stitch_file_location, "folder-download")

    def update_secondary_icon(self, entry, icon_name):
        try:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, icon_name)
            print(f"Icon has been set: {icon_name}")
        except Exception as e:
            print("Failed updating icon")
            print(e)

    # Ref: https://pypi.org/project/yt-dlp/#embedding-examples
    def download_from_youtube(self, url, name=None, artist=None):

        yt_dl_options = YT_DLP_OPTIONS
        if name:
            yt_dl_options = {
#                "outtmpl": f"$HOME/Videos/python/{name}"
                "outtmpl": f"/var/home/codenomad/Videos/python/{artist}/{name}",
                "format": "best",
                "merge_output_format": "mkv"
        }

        with YoutubeDL(yt_dl_options) as ydl:
            download = ydl.download([url])

        message = Adw.Toast.new(f"{name or url} has been downloaded")
        self.stitches_toast.add_toast(message)
        self.stitch_video.set_filename(yt_dl_options["outtmpl"]["default"])

        print(f'Filename: {yt_dl_options["outtmpl"]["default"]}')


    def update_content(self):
        print("Updating content")

        model = self.stitch_listview.get_model().get_selected_item()
        if not model:
            print(f"Couldn't find model in: {self.stitch_listview}")
            self.stitch_video.set_file(None)
            return

        print("Model is not null")
        print(f"Name: {model.name} - Artist: {model.artist} - URL: {model.url}")

        self.stitch_name_entry.set_text(model.name)
        self.stitch_artist_entry.set_text(model.artist)
        self.stitch_link_entry.set_text(model.url)
        self.stitch_file_location.set_text(f"{model.artist}/{model.name}")

        print(f"Checking for folder existence: {model.location}")
        if os.path.exists(model.location):
            self.stitch_video.set_filename(model.location)
            # self.stitch_file_location.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "folder-download")
            self.update_secondary_icon(self.stitch_file_location, "folder-download")
        else:
            # self.stitch_file_location.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "document-save")
            self.update_secondary_icon(self.stitch_file_location, "document-save")
            self.stitch_video.set_file(None)

    def _update_selected_stitch(self, stitch, stitch_pos):
        """Updates the selected item in the listview by deleting and replacing the item in the
        ListStore."""
        stitch = self.stitch_listview.get_model().get_selected_item()
        exists, stitch_pos = self.model.find(stitch)

        # Something super bonkers got us here, how could this ever not exist when
        # an item is always selected?
        if not exists:
            return

        # Remove item at the position
        self.model.remove(stitch_pos)

        # Readd item at the position
        self.model.insert(stitch_pos, stitch)

        if stitch.location is not None:
            self.stitch_video.set_filename(stitch.location)

