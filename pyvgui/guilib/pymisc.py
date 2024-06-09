#!/usr/bin/env python

''' Action Handler for open records dialog '''

# pylint: disable=C0103

import os
import sys
import datetime
import time
import threading
import queue
import qrcode

from pyvguicom import pgutils
from pyvguicom import pggui
from pyvguicom import pgtests

try:
    from playsound import playsound
except:
    print("Playsound not available, beeping only.")

    def playsound(arg):
        print("Fake playsound")
        Gdk.beep()
        pass
    #print("No sound subsystem")

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf

MAXSTATLEN = 36
IDLESTR = "Idle ..."

def anon_name(namex, slicex = 2):

    ret = ""
    sss = namex.split()
    sss2 = []

    try:
        #print("sss", sss)
        for cc, aa in enumerate(sss):
            sss2.append(sss[cc][0].upper() + sss[cc][1:slicex].lower())

        if len(sss) > 1:
            ret = sss2[0][:slicex] + '*  ' + sss2[1][:slicex] + '* '
        else:
            ret = sss2[0][:3] + '*  ' + pgtests.randupper(1) + pgtests.randlower(slicex-1) + '* '
    except:
        print(sys.exc_info())
        ret =  pgtests.randupper(1) + pgtests.randlower(slicex-1) + '* '

    return ret



class Status(Gtk.Label):

    ''' Status that disappears after a while '''

    def __init__(self):
        #super().__init__(self)
        Gtk.Label.__init__(self)
        self.set_xalign(0)
        self.set_size_request(180, -1)
        self.status_cnt = 0
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.ALWAYS, Gtk.PolicyType.NEVER)
        self.scroll.get_hscrollbar().hide()
        #self.scroll.get_vscrollbar().hide()
        self.maxlen  = MAXSTATLEN
        self.idlestr = IDLESTR
        self.set_status_text("Initial ..")

        self.scroll.add(self)

        #self.connect('size-allocate', self.sizealloc)
        GLib.timeout_add(1000, self._timer)

    def sizealloc(self, arg2, arg3):
        #print("Sizelloc", arg2, arg3)
        #lambda self, size: self.set_size_request(size.width - 1, -1))
        return True

    def set_status_text(self, *textx):
        sum = ""
        for aa in textx:
            sum += aa + " "
        #print("set_text", textx)
        self.set_tooltip_text(sum)
        if len(sum) > self.maxlen:
            sum = sum[:self.maxlen] + " .."
        self.set_text(sum)
        self.status_cnt = len(sum) // 4
        pgutils.usleep(10)

    def _timer(self):

        #self.get_window().set_resizable(False)

        #print("timer",  self.status_cnt)
        if self.status_cnt:
            self.status_cnt -= 1
            if self.status_cnt == 0:
                self.set_text(self.idlestr)
                self.set_tooltip_text("")
        return True

# These are the names that can be passed from caller:

SNAMES =  {
        "click" :    "sounds/click.ogg"  ,
        "enter" :    "sounds/enter.ogg"  ,
        "exit" :     "sounds/exit.ogg"   ,
        "plip" :     "sounds/plip.ogg"   ,
        "shutter" :  "sounds/shutter.ogg"   ,
        "trash" :    "sounds/trash.ogg"  ,
        "complete" : "sounds/complete.ogg"   ,
        "error" :    "sounds/error.ogg"   ,
        "prompt" :   "sounds/prompt.ogg"  ,
        "tictac" :   "sounds/tictac.ogg"  ,
        "wood" :     "sounds/wood.ogg"    ,
          }

class Soundx():

    def __init__(self):
        self.qqq = queue.Queue(5)
        ttt = threading.Thread(None, target=self._asynsound)
        ttt.daemon = True
        ttt.start()
        pass

    def _asynsound(self):
        while True:
            soundx = self.qqq.get()
            #print("Playing", os.path.basename(soundx))
            Gdk.beep()
            playsound(soundx)

    def play_all(self):

        ''' For tesing only '''

        for aa in SNAMES:
            self.play_sound(aa)
            time.sleep(1)

    def play_sound(self, sound):

        try:
            sname = SNAMES[sound]
        except:
            # Incoreect parameter, play someyhing neutral
            sname = SNAMES["wood"]

        me = os.path.dirname(__file__)
        sname = os.path.join(me, sname)
        #print("playing sound: '%s' '%s'" % (sound, sname))
        try:
            if not self.qqq.full():
                self.qqq.put(sname)
            else:
                #print("Sound queue full")
                pass
        except:
            print("Exc: Sound Queue:", sys.exc_info())

gl_in = 0

def  smessage(*args, **kwargs):

    ''' Decorate message with sound '''
    global gl_in;

    #print("pgmisc message", args, kwargs)

    # Protect from re-entry
    if gl_in:
        print("Ignoring smessage reentry")
        return
    gl_in = True
    sss = kwargs.get("sound")
    ccc = kwargs.get("conf")

    if ccc:
        ppp = getattr(ccc, "playsound")
        if ppp:
            ppp.play_sound(sss)
        del kwargs["conf"]               # Remove extra keyword
    if sss:
        del kwargs['sound']
    pggui.message(args[0], **kwargs)
    gl_in = False

class progDlg(Gtk.Dialog):

    '''
        Pop up a progress dialog.
    '''

    def __init__(self, conf, callb, parent = None):

        Gtk.Window.__init__(self)

        self.callb = callb
        self.set_title("PPROW")
        self.set_modal(False)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        #self.set_focus_on_map(False)
        #self.set_focus_visible(False)

        #self.add_buttons(   Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)

        self.w_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        try:
            ic = Gtk.Image(); ic.set_from_file(conf.iconf2)
            self.set_icon(ic.get_pixbuf())
        except:
            pass

        if parent:
            self.set_transient_for(parent)

        self.set_size_request(300, 80)

        self.prog = Gtk.ProgressBar()
        #self.prog.set_fraction(1.1)
        hbox = Gtk.HBox()
        hbox.pack_start(Gtk.Label(label="  "), 0, 0, 0)
        hbox.pack_start(self.prog, 1, 1, 4)
        hbox.pack_start(Gtk.Label(label="  "), 0, 0, 0)

        #self.vbox = Gtk.VBox()
        self.vbox.pack_start(hbox, 1, 1, 4)
        self.vbox.pack_start(Gtk.Label("Calculating Proof of Work"), 1, 1, 4)

        #self.connect("destroy", self.destroy_sig)

        #self.add(self.vbox)
        self.show_all()
        self.get_window().set_cursor(self.w_cursor)
        pgutils.usleep(5)
        GLib.timeout_add(100, self._timer)

        #while True:
        #    Gtk.main_iteration_do(False)
        #Gtk.main()

        self.response = self.run()
        #print("main ended")
        #self.destroy()

    def response(self, res):
        pass

    #def destroy_sig(self, arg2):
    #    print("destroy", self, arg2)
    #    #self.get_window().set_cursor()

    def _timer(self):
        self.callb(self)

class ihostDlg(Gtk.Dialog):

    '''
        Pop up a progress dialog.
    '''

    def __init__(self, conf, callb, parent = None):

        super().__init__(self)

        self.callb = callb
        self.set_title("PPROW")

        self.add_buttons(   Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                            Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)

        self.w_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        try:
            ic = Gtk.Image(); ic.set_from_file(conf.iconf2)
            self.set_icon(ic.get_pixbuf())
        except:
            pass

        if parent:
            self.set_transient_for(parent)

        self.set_size_request(300, 80)

        self.prog = Gtk.ProgressBar()
        #self.prog.set_fraction(1.1)
        hbox = Gtk.HBox()
        hbox.pack_start(Gtk.Label(label="  "), 0, 0, 0)
        hbox.pack_start(self.prog, 1, 1, 4)
        hbox.pack_start(Gtk.Label(label="  "), 0, 0, 0)

        self.vbox.pack_start(hbox, 1, 1, 4)
        self.vbox.pack_start(Gtk.Label("Calculating Proof of Work"), 1, 1, 4)

        #self.connect("destroy", self.destroy_sig)

        self.show_all()
        self.get_window().set_cursor(self.w_cursor)
        pgutils.usleep(5)
        GLib.timeout_add(100, self._timer)

        self.response = self.run()

    #def destroy_sig(self, arg2):
    #    print("destroy", self, arg2)
    #    #self.get_window().set_cursor()

    def _timer(self):
        self.callb(self)

class QrDlg(Gtk.Dialog):

    '''
        Pop up a QR dialog.
    '''

    def __init__(self, uuu, nnn, conf, parent = None):

        super().__init__(self)

        self.set_title("QR code")

        self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)

        self.w_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        try:
            ic = Gtk.Image(); ic.set_from_file(conf.iconf2)
            self.set_icon(ic.get_pixbuf())
        except:
            pass

        if parent:
            self.set_transient_for(parent)

        self.set_size_request(400, 400)

        self.edit = Gtk.Image()
        hbox = Gtk.HBox()
        hbox.pack_start(Gtk.Label(label="  "), 0, 0, 0)
        hbox.pack_start(self.edit, 1, 1, 4)
        hbox.pack_start(Gtk.Label(label="  "), 0, 0, 0)

        qq =  qrcode.make(uuu, version=1)
        dd =  self.image2pixbuf(qq)
        self.edit.set_from_pixbuf(dd)

        self.vbox.pack_start(hbox, 1, 1, 4)

        lab = Gtk.Label(label="%s" % uuu)
        hbox2 = Gtk.HBox()
        hbox2.pack_start(Gtk.Label(label="  "), 0, 0, 0)
        hbox2.pack_start(lab, 1, 1, 4)
        hbox2.pack_start(Gtk.Label(label="  "), 0, 0, 0)
        self.vbox.pack_start(hbox2, 0, 0, 4)

        lab2 = Gtk.Label(label="%s" % nnn)
        hbox3 = Gtk.HBox()
        hbox3.pack_start(Gtk.Label(label="  "), 0, 0, 0)
        hbox3.pack_start(lab2, 1, 1, 4)
        hbox3.pack_start(Gtk.Label(label="  "), 0, 0, 0)
        self.vbox.pack_start(hbox3, 0, 0, 4)

        #self.connect("destroy", self.destroy_sig)

        self.show_all()
        self.response = self.run()
        self.destroy()

    def image2pixbuf(self, im):
        """Convert Pillow image to GdkPixbuf"""
        qqq = im.convert("RGB")
        data = qqq.tobytes()
        ww, hh = qqq.size
        data2 = GLib.Bytes.new(data)
        pix = GdkPixbuf.Pixbuf.new_from_bytes(
                                    data2, GdkPixbuf.Colorspace.RGB,
                                                      False, 8, ww, hh, ww*3 )
        return pix

# EOF
