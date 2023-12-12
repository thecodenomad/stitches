import os
import re

from gi.repository import Adw
from gi.repository import Gtk, GObject, Gio


@Gtk.Template(resource_path='/org/codenomad/stitches/stitch_content.ui')
class StitchesWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'StitchContent'

    sidebar: Gtk.Box = Gtk.Template.Child()
    # sidebar_listview: Gtk.ListView = Gtk.Template.Child()
    sidebar_entry: Gtk.Entry = Gtk.Template.Child()
    # sidebar_notifier_label: Gtk.Label = Gtk.Template.Child()
    sidebar_window: Gtk.ScrolledWindow = Gtk.Template.Child()

