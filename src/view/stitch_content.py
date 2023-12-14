import os
import re

from gi.repository import Adw
from gi.repository import Gtk, GObject, Gio

from stitches import common, constants
from threading import Thread


# 3rd party imports
from yt_dlp import YoutubeDL

YT_DLP_OPTIONS = {"outtmpl": f"{constants.BASE_DL_LOC}/%(title)s.%(ext)s"}


@Gtk.Template(resource_path='/org/codenomad/stitches/stitch_content.ui')
class StitchContent(Adw.NavigationPage):
    __gtype_name__ = 'StitchContent'

    stitch_name_entry: Adw.EntryRow = Gtk.Template.Child()
    stitch_artist_entry: Adw.EntryRow = Gtk.Template.Child()
    stitch_link_entry: Adw.EntryRow = Gtk.Template.Child()
    stitch_file_location: Gtk.Entry = Gtk.Template.Child()
    stitch_video: Gtk.Video = Gtk.Template.Child()
    stitches_toast: Adw.ToastOverlay = Gtk.Template.Child()

    def __init__(self, stitch_listview=None, model=None, **kwargs):
        super().__init__(**kwargs)
        self.stitch_listview = stitch_listview
        self.model = model

        # Whenever the listview changes, update the content
        if self.stitch_listview:
            self.stitch_listview.connect("activate", self.update_content)


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

        # BASEDIR/{artist}/{name} -- TODO: Make this configurable
        self.stitch_file_location.set_text(f"{stitch.artist}/{stitch.name}")

        icon_name = "document-save"
        if os.path.exists(stitch.location):
            icon_name = "folder-download"
        common.update_secondary_icon(self.stitch_file_location, icon_name)

        # Now update the model at the position in the listview
        self._update_selected_stitch(stitch, stitch_pos)


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
            common.open_folder(stitch.location)
            return

        # TODO: Catch exceptions and throw in a toast for debug
        # add yt-dlp call here
        result = self.download_from_youtube(stitch)

        # If it was downloaded, then change the icon to be open folder
        common.update_secondary_icon(self.stitch_file_location, "folder-download")


    def _download_wrapper(self, stitch, yt_dl_options):

        # TODO: Turn this into a threadpool or something
        # TODO: Do a size check, files can get crazy big

        message = Adw.Toast.new(f"{stitch.name or stitch.url} has been downloaded")
        try:
            with YoutubeDL(yt_dl_options) as ydl:
                ydl.download([stitch.url])

            # If the currently selected stitch is this stitch then update the video
            if self.stitch_listview.get_model().get_selected_item() == stitch:
                print("Currently selected item is the stitch we are downloading vid for")
                self.stitch_video.set_filename(yt_dl_options["outtmpl"]["default"])
            else:
                print("Download isn't occuring on currently selected stitch")
                self.stitch_video.set_filename(None)

        except Exception as e:
            message = Adw.Toast.new(f"Failed downloading {stitch.url}: {e}")
            print(f"Failed downloading: {stitch.url}: {e}")

        # Send a toast to show downloded
        self.stitches_toast.add_toast(message)


    # Ref: https://pypi.org/project/yt-dlp/#embedding-examples
    def download_from_youtube(self, stitch):

        yt_dl_options = YT_DLP_OPTIONS
        if stitch.name:
            yt_dl_options = {
#                "outtmpl": f"$HOME/Videos/python/{name}"
                "outtmpl": f"/var/home/codenomad/Videos/python/{stitch.artist}/{stitch.name}",
                "format": "best",
                "merge_output_format": "mkv"
        }

        self.send_toast(f"Downloading: {stitch.url}")

        with YoutubeDL(yt_dl_options) as ydl:
            thread = Thread(target=self._download_wrapper, args=[stitch, yt_dl_options], daemon=False)
            thread.start()
            # TODO: Any clean up that needs to occur here?

        print(f'Filename: {yt_dl_options["outtmpl"]["default"]}')


    def send_toast(self, message, timeout=constants.DEFAULT_TOAST_TIMEOUT):
        print(f"Trying to send toast: {message}")
        if not message:
            return

        toast_msg = Adw.Toast.new(message)
        toast_msg.set_timeout(timeout)
        self.stitches_toast.add_toast(toast_msg)


    def update_content(self, *args, **kwargs):

        # Get the SelectionModel
        model = self.stitch_listview.get_model().get_selected_item()
        if not model:
            print(f"Couldn't find model in: {self.stitch_listview}")
            self.stitch_video.set_file(None)
            return

        # Update all Stitch Content EntryRows and Entry with model values
        self.stitch_name_entry.set_text(model.name)
        self.stitch_artist_entry.set_text(model.artist)
        self.stitch_link_entry.set_text(model.url)
        self.stitch_file_location.set_text(f"{model.artist}/{model.name}")

        icon_name = "document-save"
        # TODO: Have a default image for this at least...
        self.stitch_video.set_file(None)

        # Load the video if it exists
        if os.path.exists(model.location):
            icon_name = "folder-download"
            self.stitch_video.set_filename(model.location)

        # Update the icon. If the file is downloaded, this button should just take the
        # user to the location of the file.
        # TODO: Configurable, it could do an xdg-open ./filename
        common.update_secondary_icon(self.stitch_file_location, icon_name)


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

