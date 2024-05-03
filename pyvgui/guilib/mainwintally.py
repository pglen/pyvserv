#!/usr/bin/env python

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
#from pyvguicom import sutil
from pyvguicom import pggui

from pymenu import  *
from pgui import  *

from pyvcommon import pydata, pyservsup,  crysupp
from pydbase import twinchain

import pyvpacker

# ------------------------------------------------------------------------

class MainWin(Gtk.Window):

    def __init__(self):

        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)

        try:
            pixbuf = Gtk.IconTheme.get_default().load_icon("weather-storm", 32, 0)
            self.set_icon(pixbuf)
        except:

            icon = os.path.join(os.path.dirname(__file__), "weather-storm.png")
            ic = Gtk.Image(); ic.set_from_file(icon)
            self.set_icon(ic.get_pixbuf())

        self.start_anal = False
        self.core = None
        self.in_timer = False
        self.cnt = 0
        self.old_sss = 1
        self.status_cnt = 0
        self.set_title("PyVServer Vote Analisys")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        #ic = Gtk.Image(); ic.set_from_stock(Gtk.STOCK_DIALOG_INFO, Gtk.ICON_SIZE_BUTTON)
        #window.set_icon(ic.get_pixbuf())

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

        self.set_default_size(6*www/8, 6*hhh/8)

        #if www / hhh > 2:
        #    self.set_default_size(5*www/8, 5*hhh/8)
        #else:
        #    self.set_default_size(7*www/8, 7*hhh/8)

        self.connect("destroy", self.OnExit)
        self.connect("key-press-event", self.key_press_event)
        self.connect("button-press-event", self.button_press_event)

        self.oldtally = [0,0,0,0,0,0,0,0,0,0,0,]

        numofcols = 8
        self.tally = []
        for aa in range(numofcols):
            self.tally.append(0)

        self.untally = []
        for aa in range(numofcols):
            self.untally.append(0)

        try:
            self.set_icon_from_file("icon.png")
        except:
            pass

        vbox = Gtk.VBox(); hbox4 = Gtk.HBox()

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

        #self.mbar = merge.get_widget("/MenuBar")
        #self.mbar.show()
        #self.tbar = merge.get_widget("/ToolBar");
        #self.tbar.show()
        #bbox = Gtk.VBox()
        #bbox.pack_start(self.mbar, 0,0, 0)
        #bbox.pack_start(self.tbar, 0,0, 0)
        #vbox.pack_start(bbox, False, 0, 0)

        lab1 = Gtk.Label("   ");  hbox4.pack_start(lab1, 0, 0, 0)
        lab2a = Gtk.Label(" Initializing ");  hbox4.pack_start(lab2a, 1, 1, 0)
        lab2a.set_xalign(0)
        lab2a.set_size_request(300, -1)

        self.status = lab2a
        self.status_cnt = 1

        lab1 = Gtk.Label(" ");  hbox4.pack_start(lab1, 1, 1, 0)

        butt1 = Gtk.Button.new_with_mnemonic(" _Start ")
        butt1.connect("clicked", self.start_analize)
        hbox4.pack_start(butt1, False, 0, 4)

        butt2 = Gtk.Button.new_with_mnemonic(" E_xit ")
        butt2.connect("clicked", self.OnExit, self)
        hbox4.pack_start(butt2, False, 0, 4)

        lab2 = Gtk.Label("   ");  hbox4.pack_start(lab2, 0, 0, 0)

        hbox2 = Gtk.HBox()
        lab3 = Gtk.Label("");  hbox2.pack_start(lab3, 0, 0, 0)
        lab4 = Gtk.Label("");  hbox2.pack_start(lab4, 0, 0, 0)
        vbox.pack_start(hbox2, False, 0, 0)

        hbox3 = Gtk.HBox()
        #self.edit1 = pgsimp.SimpleEdit();

        # This is what is coming in:
        #{'Default': 'None', 'Vote': 4,
        #'UID': '64839bff-fae7-11ee-bb58-0fa03c52389e',
        #'SubVote': 6, 'TUID': '64839c00-fae7-11ee-bb58-0fa03c52389e',
        # 'Action': 'register', 'RUID': '64839c01-fae7-11ee-bb58-0fa03c52389e',
        #  'Test': 'test'}

        # Field names (set positional displays except header)
        self.fields = \
        ("Header", "Action", "Vote", "SubVote", "UID", "RUID",
            "TUID", )
        #  "Test", "Default")

        tt = type(""); fff = []
        for ccc in range(len(self.fields)):
            fff.append(tt)
        self.model = Gtk.TreeStore(*fff)

        #self.tree1s, self.tree1 = self.wrap(pgsimp.SimpleTree(["Head", "Payload", ], xalign=0))
        self.tree1s, self.tree1 = self.wrap(Gtk.TreeView(self.model))

        self.cells = []; cntf = 0
        for aa in self.fields:
            col = Gtk.TreeViewColumn(aa, self.cellx(cntf), text=cntf)
            col.set_resizable(True)
            self.tree1.append_column(col)
            cntf += 1

        hbox3.pack_start(self.tree1s, True, True, 6)
        vbox.pack_start(hbox3, True, True, 2)

        self.tallyarr = []
        hbox5 = Gtk.HBox()
        for aa in range(numofcols):
            vbox_1 = Gtk.VBox()
            vbox_1.pack_start(Gtk.Label("Tally %s" % (aa+1)), 1, 1, 2)
            self.tallyarr.append(Gtk.Label("0"))
            vbox_1.pack_start(self.tallyarr[aa], 1, 1, 2)
            hbox5.pack_start(vbox_1, 1, 1,2)
        vbox.pack_start(hbox5, False, 0, 2)

        self.untallyarr = []
        hbox6 = Gtk.HBox()
        for aa in range(numofcols):
            vbox_1 = Gtk.VBox()
            vbox_1.pack_start(Gtk.Label("Un %s" % (aa+1)), 1, 1, 2)
            self.untallyarr.append(Gtk.Label("0"))
            vbox_1.pack_start(self.untallyarr[aa], 1, 1, 2)
            hbox6.pack_start(vbox_1, 1, 1,2)
        vbox.pack_start(hbox6, False, 0, 2)

        self.sumarr = []
        hbox7 = Gtk.HBox()
        for aa in range(numofcols):
            vbox_1 = Gtk.VBox()
            vbox_1.pack_start(Gtk.Label("Sum %s" % (aa+1)), 1, 1, 2)
            self.sumarr.append(Gtk.Label("0"))
            vbox_1.pack_start(self.sumarr[aa], 1, 1, 2)
            hbox7.pack_start(vbox_1, 1, 1,2)
        vbox.pack_start(hbox7, False, 0, 2)

        vbox.pack_start(hbox4, False, 0, 6)

        self.add(vbox)
        self.show_all()

        GLib.timeout_add(500, self.timer)


    def cellx(self, idx):
        cell = Gtk.CellRendererText()

        #if centered[idx]:
        #    cell.set_property("alignment", Pango.Alignment.CENTER)
        #    cell.set_property("align-set", True)
        #    cell.set_alignment(0.5, 0.)

        #cell.connect("edited", self.text_edited, idx)
        self.cells.append(cell)
        return cell

    def sel_last(self, treex):
        #print("sel last ...")
        sel = treex.get_selection()
        xmodel, xiter = sel.get_selected()
        iter = self.model.get_iter_first()
        if not iter:
            return
        while True:
            iter2 = xmodel.iter_next(iter)
            if not iter2:
                break
            iter = iter2.copy()
        sel.select_iter(iter)
        ppp = xmodel.get_path(iter)
        treex.set_cursor(ppp, self.tree1.get_column(0), False)
        sutil.usleep(5)
        treex.scroll_to_cell(ppp, None, True, 0., 0. )
        #sel.select_path(self.treestore.get_path(iter))

    def wrap(self, cont):
        sc = Gtk.ScrolledWindow()
        sc.set_hexpand(True)
        sc.set_vexpand(True)
        sc.add(cont)
        return sc, cont

    def start_analize(self, arg1):
        #print("Analize")
        self.start_anal = True

    def timer(self):

        #print("Called timer")

        if self.in_timer:
            return True
        in_timer = True

        if self.start_anal:
            if not self.core:
                dbname = os.path.join(pyservsup.globals.chaindir, "vote", pyservsup.chainfname + ".pydb")
                self.core = twinchain.TwinChain(dbname)
                #print("opened", self.core)
            sss = self.core.getdbsize()
            #sss = 3 # test
            if sss != self.old_sss:
                cnt = 0
                # Start from one
                for aa in range(self.old_sss, sss):
                    rec = self.core.get_rec(aa)
                    if not rec:
                        continue
                    #print("Datamon", rec[1])
                    pb = pyvpacker.packbin()
                    dec = pb.decode_data(rec[1])[0]
                    #print("dec", dec)
                    decpay  = pb.decode_data(dec['payload'])[0]
                    pay = decpay['PayLoad']
                    #print("pay:", pay)
                    actstr = ["register", "unregister", "cast", "uncast", ]
                    if pay['Action'] == 'cast':
                        idx = int(decpay['PayLoad']['Vote'])
                        if idx >= numofcols:
                            print("bad vote value", idx)
                        self.tally[ idx % numofcols ] += 1

                    if pay['Action'] == 'uncast':
                        idx = int(decpay['PayLoad']['Vote'])
                        if idx >= numofcols:
                            print("bad unvote value", idx)
                        self.untally[ idx % numofcols ] += 1
                    arrx = [dec['header']]
                    for aaa in self.fields[1:]:
                        try:
                            arrx.append(str(pay[aaa]))
                        except:
                            print("Incomplete:", pay)
                    try:
                        self.model.append(None, arrx)
                    except:
                        print("Bad record:", pay)
                    #if len(self.fields) !=  len(arrx):
                    #    print("Len mismatch:", pay)

                    cnt += 1
                    if cnt % 50 == 0:
                        self.set_status_text("Getting rec: %d" % cnt)
                        sutil.usleep(2)

                self.old_sss = sss
                self.sel_last(self.tree1)
                #self.led2.set_color("00ff00")
                #GLib.timeout_add(400, self.led_off, self.led2, "#aaaaaa")

                sumstr = ""
                for aa in range(10):
                    self.tallyarr[aa].set_text(str(self.tally[aa]))
                    self.untallyarr[aa].set_text(str(self.untally[aa]))
                    diff = int(self.tally[aa]) - int(self.untally[aa])
                    self.sumarr[aa].set_text(str(diff))
                    if self.oldtally[aa]  != diff:
                        sumstr += str(aa) + "  "
                    self.oldtally[aa] = diff

                if sumstr ==  "":
                    sumstr = "None"

                self.status.set_text("Changed:  " + sumstr)
                self.status_cnt = 5

                #print("tally  ",   self.tally)
                #print("untally",   self.untally)

        self.cnt += 1
        if self.status_cnt:
            self.status_cnt -= 1
            if not self.status_cnt:
                self.status.set_text("Idle")

        in_timer = False
        return True

    def set_status_text(self, text):
        self.status.set_text(text)
        self.status_cnt = 4

    def main(self):
        Gtk.main()

    def  OnExit(self, arg, srg2 = None):
        self.exit_all()

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

# Start of program:

if __name__ == '__main__':

    mainwin = MainWin()
    Gtk.main()

# EOF
