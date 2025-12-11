#!/usr/bin/env python

#from __future__ import absolute_import
#from __future__ import print_function

import os, sys, getopt, signal, random, time, warnings, subprocess

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

from pyvcommon import pydata, pyservsup,  crysupp, pyvindex
from pydbase import twinchain

import pymisc, pyvcores, pyvrecsel, passdlg

from pydbase import twincore, twinchain

import pyvpacker

# ------------------------------------------------------------------------

class MainWin(Gtk.Window):

    def __init__(self, globals):

        self.cnt = 0
        self.led1_cnt = 0
        self.in_timer = False
        self.datamon_ena = False
        self.repmon_ena = False
        self.conf       = globals.conf
        self.conf.iconf  = os.path.dirname(globals.conf.me) + \
                                    os.sep + "images/pyvvote.png"
        self.conf.iconf2 = os.path.dirname(globals.conf.me) + \
                                    os.sep + "images/pyvvote_sub.png"
        self.conf.siteid = globals.siteid

        self.core = None
        self.replog_fp = 0
        self.log_fp = None
        self.log_ena = False
        self.old_sss = 1        # Remember, cnnot use record one
        self.w_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self.packer = pyvpacker.packbin()

        votename = os.path.join(pyservsup.globals.chaindir, "vote", "initial.pydb")
        #print("Checking:", votename)
        self.votecore = pyvcores.votecore(votename)
        self.votecore.packer = pyvpacker.packbin()

        self.acore = twincore.TwinCore("audit.pydb", 0)
        self.authcore = twincore.TwinCore("auth.pydb", 0)

        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)

        self.set_title("PyVserv Check Utility")
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

        #self.led1 = pggui.Led("#aaaaaa")
        #hbox4t.pack_start(self.led1, 0, 0, 0)
        #lab1 = Gtk.Label(" Server Activity ");  hbox4t.pack_start(lab1, 0, 0, 0)
        #lab1 = Gtk.Label("      ");  hbox4t.pack_start(lab1, 0, 0, 0)

        self.tree1s, self.tree1 = self.wrap(pgsimp.SimpleTree(["Vuuid", "Name / Vote", "Time", "Ballot"], xalign=0))
        self.tree1.connect("button-press-event",  self.tree_butt, self.tree1)

        hbox3 = Gtk.VBox()
        hbox4 = Gtk.HBox()
        #hbox3.pack_start(Gtk.Label(label="Main Area"), 1, 1, 1)
        hbox3.pack_start(self.tree1s, 1, 1, 1)
        vbox.pack_start(hbox3, True, True, 2)
        hbox4 = Gtk.HBox()

        # Buttom row:
        lab1 = Gtk.Label("  ");
        hbox4.pack_start(lab1, 0, 0, 0)
        self.status = pymisc.Status()
        hbox4.pack_start(self.status.scroll, 1, 1, 0)
        lab1 = Gtk.Label("  ");  hbox4.pack_start(lab1, 0, 0, 0)

        butt1 = Gtk.Button.new_with_mnemonic("   Check _duplicate Voter  ")
        butt1.connect("clicked", self.duplicate_check)
        hbox4.pack_start(butt1, False, 0, 2)

        butt1 = Gtk.Button.new_with_mnemonic("   Check Data Integrity  ")
        butt1.connect("clicked", self.datamon_off)
        hbox4.pack_start(butt1, False, 0, 2)

        #butt1 = Gtk.Button.new_with_mnemonic("   Button_s here  ")
        #butt1.connect("clicked", self.datamon_off)
        #hbox4.pack_start(butt1, False, 0, 2)

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

        vbox.pack_start(hbox4, False, 0, 2)

        self.add(vbox)
        self.show_all()

        #GLib.timeout_add(200, self.load)
        GLib.timeout_add(1000, self.timer)
        GLib.timeout_add(200, self.start_pass_dlg, 0)

    def en_dis_all(self, flag):
        pass

    def start_pass_dlg(self, arg2):

        authcnt = 0
        while True:
            if authcnt > 3:
                pymisc.smessage("Too May tries, exiting.")
                self.exit_all()
                break

            ret = passdlg.auth_initial(self.authcore, self.packer, self.conf)
            #print("ret:", ret)
            if ret[0] < 0:
                # Cancel
                self.exit_all()
                break

            if not ret[0]:
                authcnt += 1
                continue

            if ret[1][2] != "Enabled":
                authcnt += 1
                msg = "Cannot log in, user '%s' is disbled " % ret[1][0]
                self.status.set_status_text(msg)
                pymisc.smessage(msg)
                continue

            # Success
            self.operator = ret[1][0]
            self.powers   = ret[1][4]
            self.ouid     = ret[1][5]
            #print("pow", self.powers, self.operator, self.ouid)
            self.status.set_status_text("Authenticated '%s'" % ret[1][0])
            self.en_dis_all(True)
            pyvrecsel.audit(self.acore, self.packer, "Successful Login", ret[1][0])
            break
        #self.set_focus(self.dat_dict['nuuid'])

    def open_rec(self, arg2, arg3, arg4):
        #print("open rec", arg2, arg3, arg4)
        sel =  self.tree1.get_selection()
        xmodel, xpath = sel.get_selected_rows()
        if xpath:
            for aa in xpath:
                xiter2 = xmodel.get_iter(aa)
                xstr = xmodel.get_value(xiter2, 0)
                print("Tree sel menu click:", xstr)
                zzz = xstr.split()
                if len(zzz) < 2:
                    msg = "Please click on the expanded record, not the header."
                    pggui.message(msg, parent=self)
                    break
                #print("show:", zzz)
                self.status.set_text("Opening in new window ... exit view to continue.")

                exe = os.path.join(os.path.dirname(__file__), "..", "pyvvote.py")
                ret = subprocess.run([exe, "-c", zzz[0], ])
                break

    def del_rec(self, arg2, arg3, arg4):
        print("del rec", arg2, arg3, arg4)
        pass

    def create_menuitem(self, string, action, arg = None):
        rclick_menu = Gtk.MenuItem(string)
        if action:
            rclick_menu.connect("activate", action, string, arg)
        rclick_menu.show()
        return rclick_menu

    def tree_butt(self, arg2, event, arg4):
        #print("tree_but:", arg2)
        if event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == 3:
                sel = arg2.get_selection()
                xmodel, xpath = sel.get_selected_rows()
                if xpath:
                    for aa in xpath:
                        xiter2 = xmodel.get_iter(aa)
                        xstr = xmodel.get_value(xiter2, 3)
                        #print("Tree sel right click:", xstr)
                        self.menu3 = Gtk.Menu()
                        self.popmenu(event, xstr)
                        break

    def popmenu(self, event, xstr):
        self.menu3.append(self.create_menuitem("Show Selected Record",
                            self.open_rec, xstr))
        self.menu3.append(self.create_menuitem("Delete Selected Record",
                            self.del_rec, xstr))
        self.menu3.popup(None, None, None, None, event.button, event.time)

    def wrap(self, cont):
        sc = Gtk.ScrolledWindow()
        sc.set_hexpand(True)
        sc.set_vexpand(True)
        sc.add(cont)
        return sc, cont

    def set_status_text(self, *text):
        self.status.set_text(*text)

    def datamon_on(self, aarg1):
        self.datamon_ena = True
        self.status.set_text("Enabled DATA monitoring")

    def datamon_off(self, aarg1):
        self.datamon_ena = False
        self.set_status_text("Disabled DATA monitoring", "Hello")

    def duplicate_check(self, aarg1):
        self.set_status_text("Started duplicate check")
        self.get_window().set_cursor(self.w_cursor)
        self.tree1.clear()
        pgutils.usleep(15)

        datsize = self.votecore.getdbsize()

        cnt = 0; was = []; found = 0
        for aa in range(datsize-1, -1, -1):
            try:
                dat = self.votecore.get_rec(aa)
            except:
                dat = []
                print(sys.exc_info())
                pass
            if not dat:
                msg = "No data selected."
                #print(msg)
                return
            #print("preload dat:", dat)
            try:
                dec = self.votecore.packer.decode_data(dat[1])[0]['PayLoad']
            except:
                dec = {}
                pass
            #print("dec:", dec)
            #print("voter id", dec['nuuid'])

            if dec['nuuid'] in was:
                continue

            was.append(dec['nuuid'])
            ddd3 = pyvindex.search_index(dec['nuuid'], self.votecore,
                            self.votecore.hashname2,
                                    pyvindex.hash_nuuid, "nuuid")
            cnt += 1
            if cnt % 1000 == 0:
                self.set_status_text("Duplicate check %d" % cnt)
                pgutils.usleep(5)
            if len(ddd3) <= 1:
                continue
            found += 1
            par = self.tree1.append([dec['nuuid'], dec['name'], dec['uuid'], ""])
            #print("dup", ddd3)
            for bb in ddd3:
                try:
                    dat2 = self.votecore.get_rec(bb)
                except:
                    dat2 = []
                    print(sys.exc_info())
                    pass
                if not dat2:
                    continue
                #print("preload dat2:", dat2)
                try:
                    dec2 = self.votecore.packer.decode_data(dat2[1])[0]['PayLoad']
                except:
                    dec2 = {}
                self.tree1.append([str(bb) + " " + dec2['uuid'], dec2['vprim'],
                                        dec2['now'], dec2['bname']], par)
        self.get_window().set_cursor()
        self.set_status_text("%d records %d duplicates" % (cnt, found))

    def mon_log(self, arg1):
        self.log_ena = True
        self.set_status_text("Enabled LOG monitoring")

    def enable_replic(self, arg1):
        self.repmon_ena = True
        self.set_status_text("Enabled REPLIC monitoring")

    def disable_replic(self, arg1):
        self.repmon_ena = False
        self.set_status_text("Disabled REPLIC monitoring")

    def mon_log_off(self, arg1):
        self.log_ena = False
        self.set_status_text("Disabled LOG monitoring")

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
        self.in_timer = False
        return True

    def led_off(self, ledx, color):
        ledx.set_color(color)

# Start of program:

if __name__ == '__main__':

    mainwin = MainWin()
    Gtk.main()

# EOF
