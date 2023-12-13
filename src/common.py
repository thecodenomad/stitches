import json
import os
import re
import subprocess

from gi.repository import Gtk

from stitches import constants

def open_folder(location):
    """Open a given location with the OS"""

    # TODO: Only works on Linux, need to use 'open' for MacOS, who knows what for Windoze
    parent_folder = os.path.dirname(location)
    subprocess.run(["xdg-open", parent_folder])


def get_artist_from_url(url):
    """Retrieves a username or artist given a url"""

    # Support for Twitter
    pattern = r"twitter\.com\/([a-zA-Z0-9_]+)\/"
    match = re.search(pattern, url)
    detected_artist = "???"
    if match:
        detected_artist = match.group(1)
    return detected_artist

    # TODO: Support for Youtube and rumble needed


def get_twitter_status_id(url):
    """Retrieves the status ID for a given tweet"""

    pattern = re.compile(r"(?<=status/)\d+")
    match = re.search(pattern, url)
    status_id = "unknown"
    if match:
        status_id = match.group()
    return status_id


# TODO: create one for each service so a custom mechanism to grab an artist/url/etc
def is_valid_url(url):
    url_pattern = re.compile(r'https://(?:www\.)?(twitter\.com/([A-Za-z0-9_]+)/status/(\d+)|youtube\.com|rumble\.com)')
    if url and url_pattern.search(url):
        return True
    return False


def update_secondary_icon(entry, icon_name):
    try:
        entry.set_icon_from_icon_name(constants.DEFAULT_ENTRY_ICON_POS, icon_name)
    except Exception as e:
        print(f"Hit an exception: {e}")

