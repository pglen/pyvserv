#!/usr/bin/env python

''' Action Handler for open records dialog '''

# pylint: disable=C0103

import os
import sys
import datetime
import time
import threading
import queue

from pyvguicom import pgutils
from pyvguicom import pggui

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

MAXSTATLEN = 36

class Status(Gtk.Label):

    ''' Status that disappears after a while '''

    def __init__(self):
        #super().__init__(self)
        Gtk.Label.__init__(self)
        self.set_xalign(0)
        self.set_size_request(180, -1)
        self.status_cnt = 0
        self.set_status_text("Initial ..")
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.ALWAYS, Gtk.PolicyType.NEVER)
        self.scroll.get_hscrollbar().hide()
        #self.scroll.get_vscrollbar().hide()

        self.scroll.add(self)

        #self.connect('size-allocate', self.sizealloc)
        GLib.timeout_add(1000, self._timer)

    def sizealloc(self, arg2, arg3):
        print("Sizelloc", arg2, arg3)
        #lambda self, size: self.set_size_request(size.width - 1, -1))
        return True

    def set_status_text(self, *textx):
        sum = ""
        for aa in textx:
            sum += aa + " "
        #print("set_text", textx)
        self.set_tooltip_text(sum)
        if len(sum) > MAXSTATLEN:
            sum = sum[:MAXSTATLEN] + ".."
        self.set_text(sum)
        self.status_cnt = len(sum) // 4

    def _timer(self):

        #self.get_window().set_resizable(False)

        #print("timer",  self.status_cnt)
        if self.status_cnt:
            self.status_cnt -= 1
            if self.status_cnt == 0:
                self.set_text("Idle.")
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

# EOF
