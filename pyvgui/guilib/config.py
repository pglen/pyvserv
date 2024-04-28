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
from gi.repository import GLib
from gi.repository import GdkPixbuf

import pyvpacker
from pydbase import twincore, twinchain

from pyvguicom import pggui
from pyvguicom import pgsel
from pyvguicom import pgutils
from pyvguicom import pgentry

from pyvcommon import pyvhash

class ConfigDlg(Gtk.Dialog):

    ''' Open record selection dialog. We attach state vars to the class,
    it was attached to the dialog in the original incarnation.
    '''

    def __init__(self, vcore, acore):
        super().__init__(self)

        self.set_title("Configuration")
        self.add_buttons(   Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                            Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)

        #self.set_default_response(Gtk.ResponseType.ACCEPT)
        #self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(800, 600)
        self.alt = False
        self.xmulti = []
        self.vcore = vcore
        self.acore = acore
        self.packer = pyvpacker.packbin()
        self.rec_cnt = 0
        self.scan_cnt = 0
        self.stop = False
        self.w_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self.sort_cnt = 0
        #self.vbox = self.get_content_area()

        self.vbox3 = Gtk.VBox()

        try:
            ic = Gtk.Image(); ic.set_from_file("pyvvote_sub.png")
            self.set_icon(ic.get_pixbuf())
        except:
            pass

        self.connect("key-press-event", self.area_key)
        self.connect("key-release-event", self.area_key)

        self.pbox = Gtk.HBox()
        self.vbox3.pack_start(self.pbox, 0, 0, 0)

        gridx = Gtk.Grid()
        gridx.set_column_spacing(6)
        gridx.set_row_spacing(6)
        rowcnt = 0
        hbox4 = Gtk.HBox()

        buttx2 = Gtk.Button.new_with_mnemonic("Save")
        tp1 =("Admin Nam_e: ", "name", "Enter full name (TAB to advance)", None)
        tp2 = ("Password:: ", "dob", "Date of birth, YYYY/MM/DD", None)
        lab1, lab2 = pgentry.gridquad(gridx, rowcnt, 0, tp1, tp2, buttx2)

        #buttx2.connect("clicked", self.pressed_dob, lab2)
        #self.dat_dict['name'] = lab1
        #self.dat_dict['dob'] = lab2
        rowcnt += 1

        hbox4.pack_start(pggui.xSpacer(), 1, 1, 4)
        hbox4.pack_start(gridx, 0, 0, 4)
        hbox4.pack_start(pggui.xSpacer(), 1, 1, 4)

        self.vbox3.pack_start(hbox4, 0, 0, 4)

        self.abox = self.get_action_area()

        self.stopbutt = Gtk.Button.new_with_mnemonic("Stop Lo_ading")
        self.stopbutt.set_sensitive( False )
        #self.stopbutt.connect("clicked", self.stopload)

        self.abox.pack_start(self.stopbutt, 1, 1, 0)
        self.abox.reorder_child(self.stopbutt, 0)

        self.show_all()
        self.response = self.run()

        self.res = []
        if self.response == Gtk.ResponseType.ACCEPT:
            pass

        self.destroy()

    def area_key(self, area, event):

        #print("area_key", event.keyval)

        # Do key down:
        if  event.type == Gdk.EventType.KEY_PRESS:

            if event.keyval in  (Gdk.KEY_Alt_L, Gdk.KEY_Alt_R):
                self.alt = True

            if event.keyval in (Gdk.KEY_x, Gdk.KEY_X):
                if self.alt:
                    self.response(Gtk.ResponseType.CANCEL)

        elif  event.type == Gdk.EventType.KEY_RELEASE:
            if event.keyval in (Gdk.KEY_Alt_L, Gdk.KEY_Alt_R):
                self.alt = False

BACKGROUND_IMAGE  = "pyvvote.png"


class PassDlg(Gtk.Dialog):

    ''' Open password dialog.  '''

    def __init__(self, firsttime = False):

        super().__init__(self)

        self.set_title("Password prompt")
        self.add_buttons(   Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                            Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)

        #self.set_skip_pager_hint(False)
        #self.set_skip_taskbar_hint(False)

        self.overlay = Gtk.Overlay()
        self.bg = Gtk.Image()
        # Load file. Optionally scale it for window
        self.bg.set_from_file(BACKGROUND_IMAGE)

        self.offs = 0
        self.dirx = 1
        pix = self.bg.get_pixbuf()
        #print("image", self.bg, pix)

        www = pix.get_width();   hhh = pix.get_height()
        #print("www", www, "hhh", hhh)

        # Water mark it
        self.pix2 = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB,
                               True, 8, www, hhh)
        pix.composite(self.pix2, 0, 0, www, hhh, 0, 0, 1, 1,
                                GdkPixbuf.InterpType.NEAREST, 30)
        self.bg.set_from_pixbuf(self.pix2)

         # Wrapping in the Scrollable make it resizable.
        #scrollable_wrapper = Gtk.ScrolledWindow()
        #scrollable_wrapper.add(self.bg)
        #scrollable_wrapper.set_size_request(300, 400)
        #self.overlay.add(scrollable_wrapper)
        self.overlay.add_overlay(self.bg)

        self.set_default_response(Gtk.ResponseType.ACCEPT)

        self.firsttime = firsttime
        self.alt = False
        self.xmulti = []
        self.packer = pyvpacker.packbin()
        self.rec_cnt = 0
        self.scan_cnt = 0
        self.stop = False
        self.w_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self.sort_cnt = 0
        #self.vbox3 = self.get_content_area()

        try:
            ic = Gtk.Image(); ic.set_from_file("pyvvote_sub.png")
            self.set_icon(ic.get_pixbuf())
        except:
            pass

        self.connect("key-press-event", self.area_key)
        self.connect("key-release-event", self.area_key)
        self.connect("response", self.response_pre)

        self.vbox3 = Gtk.VBox()

        self.vbox3.pack_start(pggui.ySpacer(8), 0, 0, 0)

        pbox = Gtk.HBox()

        if self.firsttime:
            vbox2 = Gtk.VBox()
            lab1 = Gtk.Label.new("Please Enter Administrator password.")
            pbox.pack_start(lab1, 1, 1, 0)
            vbox2.pack_start(pbox, 0, 0, 0)

            pbox2 = Gtk.HBox()
            lab2 = Gtk.Label.new("After successful entry, this will be the")
            pbox2.pack_start(lab2, 1, 1, 0)
            vbox2.pack_start(pbox2, 0, 0, 0)

            pbox3 = Gtk.HBox()
            lab3 = Gtk.Label.new("master password for administering this entry system. ")
            pbox3.pack_start(lab3, 1, 1, 0)
            vbox2.pack_start(pbox3, 0, 0, 0)

            self.vbox3.pack_start(vbox2, 0, 0, 0)

        else:
            lab1 = Gtk.Label.new("Please Enter User or Administrator password.")
            pbox.pack_start(lab1, 1, 1, 0)
            self.vbox3.pack_start(pbox, 0, 0, 0)

        self.vbox3.pack_start(pggui.ySpacer(8), 0, 0, 0)

        gridx = Gtk.Grid()
        gridx.set_column_spacing(6)
        gridx.set_row_spacing(6)
        rowcnt = 0
        hbox4 = Gtk.HBox()

        tp3x = ("User Name: ", "name", "Enter user or admin name", None)
        self.uname = pgentry.griddouble(gridx, 0, rowcnt, tp3x, None)
        rowcnt += 1

        tp4x = ("Password: ", "pass", "Enter Password", None)
        self.passx = pgentry.griddouble(gridx, 0, rowcnt, tp4x, None)
        self.passx.set_visibility(False)
        if not self.firsttime:
            self.passx.set_activates_default(True)
            self.passx.noemit = True
        rowcnt += 1

        if self.firsttime:
            tp5x = ("Veriy: ", "pass", "Enter Password to verify", None)
            self.lab5x = pgentry.griddouble(gridx, 0, rowcnt, tp5x, None)
            self.lab5x.set_activates_default(True)
            self.lab5x.noemit = True
            self.lab5x.set_visibility(False)
        rowcnt += 1

        #gridx.attach(pggui.ySpacer(8), 0, rowcnt, 1, 1)
        #rowcnt += 1

        hbox4.pack_start(pggui.xSpacer(), 1, 1, 4)
        hbox4.pack_start(gridx, 0, 0, 4)
        #hbox4.pack_start(pggui.xSpacer(), 1, 1, 4)

        self.vbox3.pack_start(hbox4, 0, 0, 4)
        self.vbox3.pack_start(\
            Gtk.Label("Watermark animation is to assure authenticity."), 0, 0, 4)

        self.overlay.add(self.vbox3)
        self.vbox.pack_start(self.overlay, 1, 1, 1)

        #self.set_size_request(640, 280)

        #self.abox = self.get_action_area()
        self.show_all()
        self.overlay.reorder_overlay(self.bg, 0)

        self.res = []
        GLib.timeout_add(1000, self.timer)

        response = self.run()
        self.res.append(response)
        if response == Gtk.ResponseType.ACCEPT:
            key =  b"1234567890" * 4
            cipher = AES.new(key[:32], AES.MODE_CTR,
                            use_aesni=True, nonce = key[-8:])
            cyph = cipher.encrypt(self.passx.get_text().encode())
            self.res.append(base64.b64encode(self.uname.get_text().encode()))
            self.res.append(cyph)
        self.destroy()

    def timer(self):

        www =   self.pix2.get_width();   hhh = self.pix2.get_height()

        if self.offs > 10:
            self.dirx = -1
        if self.offs == 0:
            self.dirx = 1
        self.offs += self.dirx
        pix3 = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB,
                               True, 8, www + self.offs, hhh + self.offs)
        self.pix2.composite(pix3, + self.offs, + self.offs, www, hhh, self.offs, self.offs, 1, 1,
                                GdkPixbuf.InterpType.NEAREST, 255)
        self.bg.set_from_pixbuf(pix3)
        return True

    # Evaluate respoonse
    def response_pre(self, arg2, arg3):
        #print("response", arg2, arg3)
        if arg3 == Gtk.ResponseType.ACCEPT:
            if self.uname.get_text() == "":
                self.set_focus(self.uname)
                pggui.message("User name cannot be empty.")
                self.stop_emission_by_name ("response")
                return True
            if self.passx.get_text() == "":
                self.set_focus(self.passx)
                pggui.message("Password name cannot be empty.")
                self.stop_emission_by_name ("response")
                return True
            if self.firsttime:
                if self.passx.get_text() != self.lab5x.get_text():
                    self.set_focus(self.lab5x)
                    pggui.message("Passwords must match.")
                    self.stop_emission_by_name ("response")
                    return True

    def area_key(self, area, event):

        #print("area_key", event.keyval)

        # Do key down:
        if  event.type == Gdk.EventType.KEY_PRESS:

            if event.keyval in  (Gdk.KEY_Alt_L, Gdk.KEY_Alt_R):
                self.alt = True

            if event.keyval in (Gdk.KEY_x, Gdk.KEY_X):
                if self.alt:
                    self.response(Gtk.ResponseType.CANCEL)

        elif  event.type == Gdk.EventType.KEY_RELEASE:
            if event.keyval in (Gdk.KEY_Alt_L, Gdk.KEY_Alt_R):
                self.alt = False

# EOF
