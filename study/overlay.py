#!/usr/bin/env python

''' Login and configure dialogs '''

# pylint: disable=C0103

import os
import sys
import datetime
import time
import uuid
import io
import struct
import base64

from Crypto.Cipher import AES

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GLib


BACKGROUND_IMAGE  = "../pyvvote.png"
BACKGROUND_IMAGE2 = "../pyvvote_sub.png"

class DlgImg(Gtk.Dialog):
    def __init__(self):

        Gtk.Dialog.__init__(self)

        self.set_title("Open Record(s)")
        self.add_buttons(   Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                            Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)

        self.overlay = Gtk.Overlay()

        self.vbox.pack_start(self.overlay, 1, 1, 1)

        self.bg = Gtk.Image()
        # Load file. Optionally scale it for window
        self.bg.set_from_file(BACKGROUND_IMAGE)
        pix = self.bg.get_pixbuf()
        #pix.saturate_and_pixelate(pix, 0.5, False)
        #pix = pix.add_alpha(True, 0xFF, 0xFF, 0xFF)

        www = pix.get_width();   hhh = pix.get_height()
        #print("www", www, "hhh", hhh)

        # Water mark it
        self.pix2 = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB,
                               True, 8, www, hhh)
        pix.composite(self.pix2, 0, 0, www, hhh, 0, 0, 1, 1,
                                GdkPixbuf.InterpType.NEAREST, 30)
        self.bg.set_from_pixbuf(self.pix2)

        # Wrapping in the Scrollable make it resizable.
        scrollable_wrapper = Gtk.ScrolledWindow()
        scrollable_wrapper.add(self.bg)
        scrollable_wrapper.set_size_request(300, 400)

        self.overlay.add(scrollable_wrapper)
        vvv = Gtk.VBox()
        text = Gtk.Label(label="Test Placed here")
        vvv.pack_start(text, 0,0,0)
        text2 = Gtk.Label(label="Test Placed here2")
        vvv.pack_start(text2, 1, 1, 0)

        self.overlay.add_overlay(vvv)

        self.connect('destroy', lambda w: Gtk.main_quit())
        self.show_all()
        self.offs = 0

        GLib.timeout_add(1000, self.timer)

    def timer(self):
        #print("Timer")
        #pix = self.bg.get_pixbuf()
        www =   self.pix2.get_width();   hhh = self.pix2.get_height()

        self.offs += 1
        self.offs = self.offs % 10
        pix3 = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB,
                               True, 8, www + self.offs, hhh + self.offs)

        #pix3.fill(0xffffffff)
        self.pix2.composite(pix3, + self.offs, + self.offs, www, hhh, self.offs, self.offs, 1, 1,
                                GdkPixbuf.InterpType.NEAREST, 255)
        self.bg.set_from_pixbuf(pix3)

        return True


DlgImg()
Gtk.main()
