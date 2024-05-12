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
from Crypto.Hash import SHA256
from Crypto import Random

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

import pymisc

COMMONKEY =  b"1234567890" * 4

def     dbsalt(upass):

    rstr = Random.new().read(4)
    hstr = ""
    for aa in rstr:
        hstr += "%02x" % aa
    hhh = SHA256.new();
    hhh.update(bytes(upass, "utf-8") + bytes(hstr, "utf-8"))
    #print(hstr)
    ddd = hhh.hexdigest()
    upass2 = ddd  + hstr
    return upass2

def    dbunsalt(upass, oldhash):

    hstr = oldhash[-8:]
    hhh = SHA256.new();
    hhh.update(bytes(upass, "utf-8") + bytes(hstr, "utf-8"))
    #print(hstr)
    upass2 = hhh.hexdigest()  + hstr
    return upass2

def gen_def_data(uname, passx, flag):

    dd = datetime.datetime.now().replace(microsecond=0)
    uuuu = str(uuid.uuid1())
    salt = dbsalt(passx)
    ddd = [uname, "Full_Name",  "Enabled", dd.isoformat(), flag, uuuu, salt]

    # Make sure it is not tempered with
    hhh = SHA256.new();
    hhh.update(bytes(str(ddd), "utf-8"))
    ddd.append(hhh.hexdigest())

    return ddd

def auth_initial(authcore, packer, conf):

    ret = [0, ]
    datasize = authcore.getdbsize()
    if datasize > 0:
        # Check if pre-auth
        if conf.prompt:
            ret = auth(authcore, packer, conf.user, conf.apass)
            if ret[0] == 1:
                return ret
            else:
                pymisc.smessage("Invalid user / pass from command line prompt.")

    dlg = PassDlg(datasize == 0, conf)
    #print(dlg.res)
    if dlg.res[0] == Gtk.ResponseType.ACCEPT:
        cipher = AES.new(COMMONKEY[:32], AES.MODE_CTR,
                        use_aesni=True, nonce = COMMONKEY[-8:])
        userx = cipher.decrypt(dlg.res[1]).decode()
        cipher = AES.new(COMMONKEY[:32], AES.MODE_CTR,
                        use_aesni=True, nonce = COMMONKEY[-8:])
        decr = cipher.decrypt(dlg.res[2]).decode()
        #print("userx", userx, "decr", decr)
        if datasize == 0:
            ret = addauth(authcore, packer, userx, decr, "Yes")
        else:
            ret = auth(authcore, packer, userx, decr)
        if ret[0] != 1:
            pymisc.smessage("Bad user or password", conf=conf, sound="error")
    else:
        dret = pggui.yes_no("Must authenticate. Cancel login process?")
        if dret == Gtk.ResponseType.YES:
            ret = [-1]

    #print("auth ret:", ret)
    return ret

def addauth(authcore, packer, uname, passx, flag):

    ''' Replicate what the UI does, no tree update '''

    #print("AddAuth:", "'" + uname + "'" , "'" + passx + "'")

    # Assumng success in creation
    ret = [1,]

    salt = dbsalt(passx)
    ddd = gen_def_data(uname, passx, flag)
    try:
        enc = packer.encode_data("", ddd)
    except:
        print("packer", sys.exc_info())
        enc = ""
        pass
    authcore.save_data(ddd[5], enc)
    ret.append(ddd)
    return ret

def auth(authcore, packer, uname, passx):

    #print("Auth:", "'" + uname + "'" , "'" + passx + "'")

    ret = [0,]
    ddd2 = []; dec = {}
    datasize = authcore.getdbsize()
    for aa in range(datasize -1, -1, -1):
        rrr = authcore.get_rec(aa)
        if not rrr:
            continue
        try:
            dec = packer.decode_data(rrr[1])[0]
        except:
            #print("Cannot decode:", rrr)
            dec = [0]
        try:
            #print("dec:", dec)
            if not dec[0] in ddd2:
                ddd2.append(dec[0])
                #print("dec", dec)
                if uname == dec[0]:
                    # Check:
                    hhh = SHA256.new();
                    hhh.update(bytes(str(dec[:-1]), "utf-8"))
                    #print("sums:", hhh.hexdigest(), dec[-1])
                    if hhh.hexdigest() != dec[-1]:
                        print("Bad sum on:", dec[0], dec[6])
                        continue
                    unsaltx = dbunsalt(passx, dec[6])
                    #print("auth", dec[0], dec[6], unsaltx)
                    if unsaltx == dec[6]:
                        ret[0] = 1
                        ret.append(dec)
                        break
        except:
            print("exc dec rec", dec)

    return(ret)

class PassDlg(Gtk.Dialog):

    ''' Open password dialog.  '''

    def __init__(self, firsttime, conf):

        super().__init__(self)

        self.set_title("Password prompt")
        self.add_buttons(   Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,
                            Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)

        self.set_modal(True)
        self.set_skip_pager_hint(False)
        self.set_skip_taskbar_hint(False)

        ic = Gtk.Image(); ic.set_from_file(conf.iconf2)
        self.set_icon(ic.get_pixbuf())

        self.offs = 0
        self.dirx = 1
        self.overlay = Gtk.Overlay()
        self.bg = Gtk.Image()
        # Load file. Optionally scale it for window
        self.bg.set_from_file(conf.iconf2)
        try:
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
        except:
            #print("Exc on load wartemark", sys.exc_info())
            pass

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
        self.connect("key-press-event", self.area_key)
        self.connect("key-release-event", self.area_key)
        self.connect("response", self.response_pre)

        self.vbox3 = Gtk.VBox()
        self.vbox3.pack_start(pggui.ySpacer(8), 0, 0, 0)

        pbox = Gtk.HBox()

        if self.firsttime == 1:
            vbox2 = Gtk.VBox()
            lab1 = Gtk.Label.new("Please Enter Administrator password.")
            pbox.pack_start(lab1, 1, 1, 0)
            vbox2.pack_start(pbox, 0, 0, 0)

            pbox2 = Gtk.HBox()
            lab2 = Gtk.Label.new("After successful entry, this will be the master password ")
            pbox2.pack_start(lab2, 1, 1, 0)
            vbox2.pack_start(pbox2, 0, 0, 0)

            pbox3 = Gtk.HBox()
            lab3 = Gtk.Label.new("for administering the program. Please Make a note of this password.")
            pbox3.pack_start(lab3, 1, 1, 0)
            vbox2.pack_start(pbox3, 0, 0, 0)
            self.vbox3.pack_start(vbox2, 0, 0, 0)

        elif self.firsttime == 3:
            vbox2 = Gtk.VBox()
            lab1 = Gtk.Label.new("Please Enter New Admin password.")
            pbox.pack_start(lab1, 1, 1, 0)
            vbox2.pack_start(pbox, 0, 0, 0)

        elif self.firsttime == 2:
            vbox2 = Gtk.VBox()
            lab1 = Gtk.Label.new("Please Enter New User password.")
            pbox.pack_start(lab1, 1, 1, 0)
            vbox2.pack_start(pbox, 0, 0, 0)
        else:
            lab1 = Gtk.Label.new("Please Enter User or Admin password.")
            pbox.pack_start(lab1, 1, 1, 0)
            self.vbox3.pack_start(pbox, 0, 0, 0)

        self.vbox3.pack_start(pggui.ySpacer(8), 0, 0, 0)

        gridx = Gtk.Grid()
        gridx.set_column_spacing(6)
        gridx.set_row_spacing(6)
        rowcnt = 0
        hbox4 = Gtk.HBox()

        if self.firsttime == 3:
            tp3x = ("New Admin Name: ", "name", "Enter admin name", None)
        elif self.firsttime == 2:
            tp3x = ("New User Name: ", "name", "Enter user name", None)
        elif self.firsttime == 1:
            tp3x = ("Master Admin Name: ", "name", "Enter admin name", None)
        else:
            tp3x = ("User Name: ", "name", "Enter user or admin name", None)

        self.uname = pgentry.griddouble(gridx, 0, rowcnt, tp3x, None)
        if conf.user:
            self.uname.set_text(conf.user)
        rowcnt += 1

        tp4x = ("Password: ", "pass", "Enter Password", None)
        self.passx = pgentry.griddouble(gridx, 0, rowcnt, tp4x, None)
        self.passx.set_visibility(False)
        if not self.firsttime:
            self.passx.set_activates_default(True)
            self.passx.noemit = True
            if conf.apass:
                self.passx.set_text(conf.apass)
                self.set_focus(self.passx)
        rowcnt += 1
        if self.firsttime > 0:
            tp5x = (" Veriy: ", "pass", "Enter Password to verify", None)
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
            # Transmittted encrypted from dialog
            cipher = AES.new(COMMONKEY[:32], AES.MODE_CTR,
                            use_aesni=True, nonce = COMMONKEY[-8:])
            userx = cipher.encrypt(self.uname.get_text().encode())
            self.res.append(userx)
            cipher = AES.new(COMMONKEY[:32], AES.MODE_CTR,
                            use_aesni=True, nonce = COMMONKEY[-8:])
            cyph = cipher.encrypt(self.passx.get_text().encode())
            self.res.append(cyph)
        else:
            self.res.append("")
        self.destroy()

    def timer(self):

        ''' Animate watermark '''

        if self.offs > 10:
            self.dirx = -1
        if self.offs == 0:
            self.dirx = 1
        self.offs += self.dirx
        try:
            www =   self.pix2.get_width();   hhh = self.pix2.get_height()
            pix3 = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB,
                                   True, 8, www + self.offs, hhh + self.offs)
            self.pix2.composite(pix3, + self.offs, + self.offs, www, hhh, self.offs, self.offs, 1, 1,
                                    GdkPixbuf.InterpType.NEAREST, 255)
            self.bg.set_from_pixbuf(pix3)
        except:
            pass
        return True

    # Evaluate respoonse
    def response_pre(self, arg2, arg3):
        #print("response", arg2, arg3)
        if arg3 == Gtk.ResponseType.ACCEPT:
            if self.uname.get_text() == "":
                self.set_focus(self.uname)
                pymisc.smessage("User name cannot be empty.")
                self.stop_emission_by_name ("response")
                return True
            if self.passx.get_text() == "":
                self.set_focus(self.passx)
                pymisc.smessage("Password name cannot be empty.")
                self.stop_emission_by_name ("response")
                return True
            if self.firsttime:
                if self.passx.get_text() != self.lab5x.get_text():
                    self.set_focus(self.lab5x)
                    pymisc.smessage("Passwords must match.")
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
