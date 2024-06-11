#!/usr/bin/env python

#from __future__ import absolute_import
#from __future__ import print_function

import os, sys, getopt, signal, random, time, warnings

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

from pyvguicom import pgbox
from pyvguicom import pgsimp
from pyvguicom import pggui
from pyvguicom import pgutils

from pymenu import  *
from pgui import  *

from pyvcommon import pydata, pyservsup,  crysupp
from pydbase import twinchain

import pyvpacker

# ------------------------------------------------------------------------

class MainWin(Gtk.Window):

    def __init__(self):

        self.cnt = 0
        self.led1_cnt = 0
        self.in_timer = False
        self.datamon_ena = False
        self.repmon_ena = False
        self.status_cnt = 0
        self.core = None
        self.replog_fp = 0
        self.log_fp = None
        self.log_ena = False
        self.old_sss = 1        # Remember, cnnot use record one

        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)

        self.set_title("PyVserv Control Panel")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        try:
            pixbuf = Gtk.IconTheme.get_default().load_icon("weather-storm", 32, 0)
            self.set_icon(pixbuf)
        except:

            icon = os.path.join(os.path.dirname(__file__), "weather-storm.png")
            ic = Gtk.Image(); ic.set_from_file(icon)
            self.set_icon(ic.get_pixbuf())

        www = Gdk.Screen.width(); hhh = Gdk.Screen.height();

        disp2 = Gdk.Display()
        disp = disp2.get_default()
        #print( disp)
        scr = disp.get_default_screen()
        ptr = disp.get_pointer()
        mon = scr.get_monitor_at_point(ptr[1], ptr[2])
        geo = scr.get_monitor_geometry(mon)
        www = geo.width; hhh = geo.height
        xxx = geo.x;     yyy = geo.y

        # Resort to old means of getting screen w / h
        if www == 0 or hhh == 0:
            www = Gdk.screen_width(); hhh = Gdk.screen_height();

        if www / hhh > 2:
            self.set_default_size(5*www/8, 7*hhh/8)
        else:
            self.set_default_size(7*www/8, 7*hhh/8)
        self.connect("destroy", self.OnExit)
        self.connect("key-press-event", self.key_press_event)
        self.connect("button-press-event", self.button_press_event)

        try:
            self.set_icon_from_file("icon.png")
        except:
            pass

        vbox = Gtk.VBox();

        merge = Gtk.UIManager()
        #self.mywin.set_data("ui-manager", merge)

        aa = create_action_group(self)
        merge.insert_action_group(aa, 0)
        self.add_accel_group(merge.get_accel_group())

        merge_id = merge.new_merge_id()

        try:
            mergeid = merge.add_ui_from_string(ui_info)
        except GLib.GError as msg:
            print("Building menus failed: %s" % msg)

        self.mbar = merge.get_widget("/MenuBar")
        #self.mbar.show()

        self.tbar = merge.get_widget("/ToolBar");
        #self.tbar.show()

        #bbox = Gtk.VBox()
        #bbox.pack_start(self.mbar, 0, 0, 0)
        #bbox.pack_start(self.tbar, 0, 0, 0)
        #vbox.pack_start(bbox, 0, 0, 0)

        #hbox2 = Gtk.HBox()
        #lab3 = Gtk.Label(" 1 ");  hbox2.pack_start(lab3, 0, 0, 0)
        #lab4 = Gtk.Label("Top");  hbox2.pack_start(lab4, 1, 1, 0)
        #lab5 = Gtk.Label(" 2 ");  hbox2.pack_start(lab5, 0, 0, 0)
        #vbox.pack_start(hbox2, False, 0, 0)

        hbox4t = Gtk.HBox()
        lab1 = Gtk.Label("   ");  hbox4t.pack_start(lab1, 1, 1, 0)

        self.led1 = pggui.Led("#aaaaaa")
        hbox4t.pack_start(self.led1, 0, 0, 0)
        lab1 = Gtk.Label(" Server Activity ");  hbox4t.pack_start(lab1, 0, 0, 0)

        lab1 = Gtk.Label("      ");  hbox4t.pack_start(lab1, 0, 0, 0)

        self.led2 = pggui.Led("#aaaaaa")
        hbox4t.pack_start(self.led2, 0, 0, 0)
        lab1 = Gtk.Label(" Data Activity ");  hbox4t.pack_start(lab1, 0, 0, 0)

        lab1 = Gtk.Label("      ");  hbox4t.pack_start(lab1, 0, 0, 0)

        self.led3 = pggui.Led("#aaaaaa")
        hbox4t.pack_start(self.led3, 0, 0, 0)
        lab1 = Gtk.Label(" Replication Activity");  hbox4t.pack_start(lab1, 0, 0, 0)

        lab1 = Gtk.Label("   ");  hbox4t.pack_end(lab1, 1, 1, 0)

        vbox.pack_start(hbox4t, False, 0, 4)

        vbox3 = Gtk.VBox()
        hbox3 = Gtk.HBox()
        hbox4 = Gtk.HBox()

        self.tree1s, self.tree1 = self.wrap(pgsimp.SimpleTree(["Date", "Time", "Level", "Entry"], xalign=0))
        self.tree2s, self.tree2 = self.wrap(pgsimp.SimpleTree(["Date", "Time", "Level", "Entry"], xalign=0))
        self.tree3s, self.tree3 = self.wrap(pgsimp.SimpleTree(["Head", "Payload",]))
        #self.tree4s, self.tree4 = self.wrap(pgsimp.SimpleTree([" Main4 "]))

        hbox3.pack_start(self.tree1s, True, True, 6)
        hbox3.pack_start(self.tree2s, True, True, 6)

        hbox4.pack_start(self.tree3s, True, True, 6)
        #hbox4.pack_start(self.tree4s, True, True, 6)

        vbox.pack_start(hbox3, True, True, 2)
        vbox.pack_start(hbox4, True, True, 2)

        hbox4p = Gtk.HBox()
        lab1 = Gtk.Label("   ");  hbox4p.pack_start(lab1, 1, 1, 0)

        #butt1 = Gtk.Button.new_with_mnemonic("    Placeholder  ")
        ##butt1.connect("clicked", self.show_new, window)
        #hbox4p.pack_start(butt1, False, 0, 2)

        butt1 = Gtk.Button.new_with_mnemonic("    _Start Log Mon.  ")
        butt1.connect("clicked", self.mon_log)
        hbox4p.pack_start(butt1, False, 0, 2)

        butt1 = Gtk.Button.new_with_mnemonic("    Stop Log Mon.  ")
        butt1.connect("clicked", self.mon_log_off)
        hbox4p.pack_start(butt1, False, 0, 2)

        butt1 = Gtk.Button.new_with_mnemonic("    Start _Replic. Mon.  ")
        butt1.connect("clicked", self.enable_replic)
        hbox4p.pack_start(butt1, False, 0, 2)

        butt1 = Gtk.Button.new_with_mnemonic("    Stop Replic. Mon. ")
        butt1.connect("clicked", self.disable_replic)
        hbox4p.pack_start(butt1, False, 0, 2)

        hbox4 = Gtk.HBox()
        lab1 = Gtk.Label("   ");  hbox4p.pack_start(lab1, 0, 0, 0)

        # Buttom row
        lab1 = Gtk.Label("  ");  hbox4.pack_start(lab1, 0, 0, 0)
        lab2a = Gtk.Label(" buttom ");  hbox4.pack_start(lab2a, 1, 1, 0)
        lab2a.set_xalign(0)
        lab2a.set_size_request(300, -1)
        self.status = lab2a

        lab1 = Gtk.Label("  ");  hbox4.pack_start(lab1, 1, 1, 0)

        butt1 = Gtk.Button.new_with_mnemonic("    Start _Data Mon.  ")
        butt1.connect("clicked", self.datamon_on)
        hbox4.pack_start(butt1, False, 0, 2)

        butt1 = Gtk.Button.new_with_mnemonic("    S_top Data Mon.   ")
        butt1.connect("clicked", self.datamon_off)
        hbox4.pack_start(butt1, False, 0, 2)

        #butt1 = Gtk.Button.new_with_mnemonic("    _Last Hour    ")
        ##butt1.connect("clicked", self.show_new, window)
        #hbox4.pack_start(butt1, False, 0, 2)
        #
        #butt1 = Gtk.Button.new_with_mnemonic("    _Last Day    ")
        ##butt1.connect("clicked", self.show_new, window)
        #hbox4.pack_start(butt1, False, 0, 2)

        #butt1 = Gtk.Button.new_with_mnemonic("    _New    ")
        ##butt1.connect("clicked", self.show_new, window)
        #hbox4.pack_start(butt1, False, 0, 2)

        butt2 = Gtk.Button.new_with_mnemonic("    E_xit    ")
        butt2.connect("clicked", self.OnExit, self)
        hbox4.pack_start(butt2, False, 0, 2)

        lab2b = Gtk.Label("   ");  hbox4.pack_start(lab2b, 0, 0, 0)

        vbox.pack_start(hbox4p, False, 0, 2)
        vbox.pack_start(hbox4, False, 0, 2)

        self.add(vbox)
        self.show_all()

        GLib.timeout_add(200, self.load)
        GLib.timeout_add(1000, self.timer)

    def set_status_text(self, text):
        self.status.set_text(text)
        self.status_cnt = 4

    def datamon_on(self, aarg1):
        self.datamon_ena = True
        self.status.set_text("Enabled DATA monitoring")

    def datamon_off(self, aarg1):
        self.datamon_ena = False
        self.set_status_text("Disabled DATA monitoring")
        self.status_cnt = 4

    def mon_log(self, arg1):
        self.log_ena = True
        self.set_status_text("Enabled LOG monitoring")
        self.status_cnt = 4

    def enable_replic(self, arg1):
        self.repmon_ena = True
        self.set_status_text("Enabled REPLIC monitoring")
        self.status_cnt = 4

    def disable_replic(self, arg1):
        self.repmon_ena = False
        self.set_status_text("Disabled REPLIC monitoring")
        self.status_cnt = 4

    def mon_log_off(self, arg1):
        self.log_ena = False
        self.set_status_text("Disabled LOG monitoring")
        self.status_cnt = 4

    def  OnExit(self, arg, srg2 = None):
        self.exit_all()

    def wrap(self, cont):
        sc = Gtk.ScrolledWindow()
        sc.set_hexpand(True)
        sc.set_vexpand(True)
        sc.add(cont)
        return sc, cont

    def exit_all(self):
        Gtk.main_quit()

    def key_press_event(self, win, event):
        #print( "key_press_event", win, event)
        pass

    def button_press_event(self, win, event):
        #print( "button_press_event", win, event)
        pass

    def activate_action(self, action):

        #dialog = Gtk.MessageDialog(None, Gtk.DIALOG_DESTROY_WITH_PARENT,
        #    Gtk.MESSAGE_INFO, Gtk.BUTTONS_CLOSE,
        #    'Action: "%s" of type "%s"' % (action.get_name(), type(action)))
        # Close dialog on user response
        #dialog.connect ("response", lambda d, r: d.destroy())
        #dialog.show()

        warnings.simplefilter("ignore")
        strx = action.get_name()
        warnings.simplefilter("default")

        print ("activate_action", strx)

    def activate_quit(self, action):
        print( "activate_quit called")
        self.OnExit(False)

    def activate_exit(self, action):
        print( "activate_exit called" )
        self.OnExit(False)

    def activate_about(self, action):
        print( "activate_about called")
        pass

    def main(self):
        Gtk.main()

    def load(self):
        #print("Called load")
        self.set_status_text("Status text for load")
        self.status_cnt = 4

    def timer(self):

        #print("Called timer")

        if self.in_timer:
            return True
        in_timer = True

        if self.repmon_ena:
            if not self.replog_fp:
                rlogfile = os.path.join(pyservsup.globals.logdir, pyservsup.repfname +".log")
                print("log", rlogfile)
                if not self.replog_fp:
                    self.replog_fp = open(rlogfile, "rt")
                    self.replog_fp.seek(0, os.SEEK_END)
                    sss = max(0, self.replog_fp.tell() - 1000)
                    self.replog_fp.seek(sss, os.SEEK_SET)
                if sss:
                    while True:
                        rrr =  self.replog_fp.read(1)
                        if not rrr:
                            break
                        if rrr == '\n':
                            break
            got = False
            while True:
                aa = self.replog_fp.readline()
                if not aa:
                    break
                aa = aa.strip()
                #print(aa)
                bb = aa.split()
                self.tree2.append([bb[0], bb[1], bb[2], " ".join(bb[3:]) ])
                pgutils.usleep(10)
                got = True

            if got:
                self.tree2.sel_last()
                self.led3.set_color("00ff00")
                GLib.timeout_add(400, self.led_off, self.led3, "#888888")

        if self.log_ena:
            if not self.log_fp:
                slogfile = os.path.join(pyservsup.globals.logdir, pyservsup.logfname + ".log")
                self.log_fp = open(slogfile, "rt")
                self.log_fp.seek(0, os.SEEK_END)
                sss = max(0, self.log_fp.tell() - 1000)
                self.log_fp.seek(sss, os.SEEK_SET)
                if sss:
                    while True:
                        rrr =  self.log_fp.read(1)
                        if not rrr:
                            break
                        if rrr == '\n':
                            break
            got = False
            while True:
                aa = self.log_fp.readline()
                if not aa:
                    break
                aa = aa.strip()
                #print(aa)
                bb = aa.split()
                self.tree1.append([bb[0], bb[1], bb[2], " ".join(bb[3:]) ])
                pgutils.usleep(10)
                got = True

            if got:
                self.tree1.sel_last()
                self.led1.set_color("00ff00")
                GLib.timeout_add(400, self.led_off, self.led1, "#888888")

        if self.datamon_ena:
            if not self.core:
                dbname = os.path.join(pyservsup.globals.chaindir, "vote",
                                    pyservsup.chainfname + ".pydb")
                self.core = twinchain.TwinChain(dbname)
                #print("opened", self.core)
            sss = self.core.getdbsize()
            if sss != self.old_sss:
                # Start from one
                for aa in range(self.old_sss, sss):
                    rec = self.core.get_rec(aa)
                    if not rec:
                        continue
                    #print("Datamon", rec)
                    pb = pyvpacker.packbin()
                    dec = pb.decode_data(rec[1])[0]
                    #print("dec", dec)
                    decpay   = pb.decode_data(dec['payload'])[0]
                    #print("decpay", decpay)
                    strx = ""
                    for bb in sorted(decpay['PayLoad'].keys()):
                        if 1: #bb[0] != "_":
                            strx += bb + " : " + str(decpay['PayLoad'][bb]) + "  "
                    #print("append:", strx)
                    self.tree3.append([dec['header'], strx])
                self.old_sss = sss
                self.tree3.sel_last()
                self.led2.set_color("00ff00")
                GLib.timeout_add(400, self.led_off, self.led2, "#aaaaaa")

        self.cnt += 1
        if self.status_cnt:
            self.status_cnt -= 1
            if not self.status_cnt:
                self.status.set_text("Idle")

        self.in_timer = False
        return True

    def led_off(self, ledx, color):
        ledx.set_color(color)

# Start of program:

if __name__ == '__main__':

    mainwin = MainWin()
    Gtk.main()

# EOF
