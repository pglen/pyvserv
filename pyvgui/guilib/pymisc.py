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
        self.set_size_request(150, -1)
        self.status_cnt = 0
        self.set_status_text("Initial ..")
        GLib.timeout_add(1000, self._timer)

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
        self.qqq = queue.Queue(10)
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
        self.qqq.put(sname)

def  message(*args, **kwargs):

    ''' Decorate message with sound '''

    #print("pgmisc message", args, kwargs)

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

# EOF
