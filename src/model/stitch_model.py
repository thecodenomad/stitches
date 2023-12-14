import os

from gi.repository import Gtk, GObject, Gio
from stitches import common, constants

class StitchObject(GObject.GObject):
    __gtype_name__ = 'StitchObject'

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

