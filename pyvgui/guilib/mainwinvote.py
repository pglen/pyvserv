#!/usr/bin/env python

import os, sys, getopt, signal, random, time, warnings, uuid, datetime

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

from pyvguicom import pgbox
from pyvguicom import pgsimp
from pyvguicom import sutil
from pyvguicom import pggui

from pymenu import  *
from pgui import  *

import recsel, pgcal

from pyvcommon import pydata, pyservsup,  crysupp

from pydbase import twincore, twinchain

import pyvpacker

class   TextViewx(Gtk.TextView):

    def __init__(self):
        super(TextViewx).__init__()
        GObject.GObject.__init__(self)
        self.buffer = Gtk.TextBuffer()
        self.set_buffer(self.buffer)
        self.single_line = False

    def get_text(self):
        startt = self.buffer.get_start_iter()
        endd = self.buffer.get_end_iter()
        return self.buffer.get_text(startt, endd, False)

    def set_text(self, txt, eventx = False):
        if eventx:
            self.check_saved()
        startt = self.buffer.get_start_iter()
        endd = self.buffer.get_end_iter()
        self.buffer.delete(startt, endd)
        self.buffer.insert(startt, txt)
        self.buffer.set_modified(True)

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
        self.set_title("PyVServer Vote Entry")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.packer = pyvpacker.packbin()
        self.vcore = twincore.TwinCore("voters.pydb", 0)

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

        self.dat_dict = {}
        self.dat_dict_org = {}

        #if www / hhh > 2:
        #    self.set_default_size(5*www/8, 5*hhh/8)
        #else:
        #    self.set_default_size(7*www/8, 7*hhh/8)

        self.connect("delete-event", self.OnExit)
        self.connect("destroy", self.OnExit)
        self.connect("key-press-event", self.key_press_event)
        self.connect("button-press-event", self.button_press_event)

        try:
            self.set_icon_from_file("icon.png")
        except:
            pass

        vbox = Gtk.VBox()
        hbox4 = Gtk.HBox()

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

        lab1 = Gtk.Label("   ");
        hbox4.pack_start(lab1, 0, 0, 0)
        lab2a = Gtk.Label(" Initializing ");
        hbox4.pack_start(lab2a, 1, 1, 0)
        lab2a.set_xalign(0)
        lab2a.set_size_request(300, -1)

        self.status = lab2a
        self.status_cnt = 1

        lab1 = Gtk.Label(" ");
        hbox4.pack_start(lab1, 1, 1, 0)

        butt2 = Gtk.Button.new_with_mnemonic(" Ne_w entry ")
        butt2.connect("clicked", self.new_data)
        hbox4.pack_start(butt2, False, 0, 4)

        butt3 = Gtk.Button.new_with_mnemonic(" Lo_ad entry ")
        butt3.connect("clicked", self.load_data)
        hbox4.pack_start(butt3, False, 0, 4)

        butt1 = Gtk.Button.new_with_mnemonic(" _Save entry ")
        butt1.connect("clicked", self.save_data)
        hbox4.pack_start(butt1, False, 0, 4)

        butt2 = Gtk.Button.new_with_mnemonic(" E_xit ")
        butt2.connect("clicked", self.OnExit, self)
        hbox4.pack_start(butt2, False, 0, 4)

        lab2 = Gtk.Label("   ");  hbox4.pack_start(lab2, 0, 0, 0)

        #hbox2 = Gtk.HBox()
        #lab3 = Gtk.Label("");  hbox2.pack_start(lab3, 0, 0, 0)
        #lab4 = Gtk.Label("");  hbox2.pack_start(lab4, 0, 0, 0)
        #vbox.pack_start(hbox2, False, 0, 0)

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

        #self.tree1s, self.tree1 = self.wrap(Gtk.TreeView(self.model))
        #self.cells = []; cntf = 0
        #for aa in self.fields:
        #    col = Gtk.TreeViewColumn(aa, self.cellx(cntf), text=cntf)
        #    col.set_resizable(True)
        #    self.tree1.append_column(col)
        #    cntf += 1
        #hbox3.pack_start(self.tree1s, True, True, 6)

        #sg = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
        gridx = Gtk.Grid()
        gridx.set_column_spacing(6)
        gridx.set_row_spacing(6)

        #gridx.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#aaaaaa"))

        rowcnt = 0
        sumx = Gtk.HBox()

        # ----------------------------------------------------------------

        tp1 =("Full Name: ", "name", "Enter full name (TAB to advance)", None)
        tp2 = ("Nick Name: ", "nick", "Enter nick name / Alias if available", None)
        lab1, lab2 = self.gridquad(gridx, rowcnt, 0, tp1, tp2)
        self.dat_dict['name'] = lab1
        self.dat_dict['nick'] = lab2
        rowcnt += 1

        tp3 = ("Location of birth: ", "lob", "Location: City / Country", None)
        tp4 = ("Date of birth: ", "dob", "Date of birth, YYYY/MM/DD", None)
        buttx2 = Gtk.Button.new_with_mnemonic("Sele_ct Date")
        lab3, lab4 = self.gridquad(gridx, 0, rowcnt, tp3, tp4, buttx2)
        buttx2.connect("clicked", self.pressed_dob, lab4)
        self.dat_dict['dob'] = lab3
        self.dat_dict['lob'] = lab4
        rowcnt += 1

        gridx.attach(self.vspacer(8), 0, rowcnt, 1, 1)
        rowcnt += 1

        tp3x = ("UUID: ", "uuid", "Generate VOTER UID by pressing button", None)
        butt1 = Gtk.Button.new_with_mnemonic("G_enerate")
        lab3x = self.griddouble(gridx, 0, rowcnt, tp3x, butt1)
        butt1.connect("clicked", self.pressed_uuid, lab3x)
        self.dat_dict['uuid'] = lab3x
        rowcnt += 1

        tp4x = ("GUID: ", "guid", "Load GROUP UID by pressing button", None)
        butt2 = Gtk.Button.new_with_mnemonic("Loa_d")
        lab4x = self.griddouble(gridx, 0, rowcnt, tp4x, butt2)
        butt2.connect("clicked", self.load_uuid, lab4x)
        self.dat_dict['guid'] = lab4x
        rowcnt += 1
        gridx.attach(self.vspacer(8), 0, rowcnt, 1, 1)
        rowcnt += 1

        tp3a = ("Address Line 1: ", "addr1", "Address line one. (Number, Street)", None)
        tp4a = ("Address Line 2: ", "addr2", "Addressline two. (if applicable)", None)
        lab5, lab6 = self.gridquad(gridx, 0, rowcnt, tp3a, tp4a)
        self.dat_dict['addr1'] = lab5
        self.dat_dict['addr2'] = lab6
        rowcnt += 1

        tp5 = ("City: ", "city", "City or Township", None)
        tp6 = ("State / Territory: ", "county", "County or Teritory or Borough", None)
        lab7, lab8 = self.gridquad(gridx, 0, rowcnt, tp5, tp6)
        self.dat_dict['city'] = lab7
        self.dat_dict['terr'] = lab8
        rowcnt += 1

        tp7 = ("Zip: ", "zip", "Zip code or Postal code", None)
        tp8 = ("Country: ", "country", "Coutry of residence", None)
        lab9, lab10 = self.gridquad(gridx, 0, rowcnt, tp7, tp8)
        self.dat_dict['zip'] = lab9
        self.dat_dict['country'] = lab10
        rowcnt += 1

        tp7a = ("Phone: ", "phone", "Phone or text number. ", None)
        tp8a = ("Email: ", "email", "Primary Email", None)
        lab11, lab12 = self.gridquad(gridx, 0, rowcnt, tp7a, tp8a)
        self.dat_dict['phone'] = lab11
        self.dat_dict['email'] = lab12
        rowcnt += 1

        tp7b = ("Phone: (secondary)", "phone2", "Secondary phone or text number. ", None)
        tp8b = ("Email: (Secondary)", "email2", "Secondary Email", None)
        lab13, lab14 = self.gridquad(gridx, 0, rowcnt, tp7b, tp8b)
        self.dat_dict['phone2'] = lab13
        self.dat_dict['email2'] = lab14
        rowcnt += 1

        tp6x = ("Notes: ", "", "Load GROUP UID by pressing button", None)
        lab6x = self.gridsingle(gridx, 0, rowcnt, tp6x)
        self.dat_dict['Notes'] = lab6x
        rowcnt += 1

        gridx.attach(self.vspacer(8), 0, rowcnt, 1, 1)
        rowcnt += 1

        #tp7b = ("Vote:" , "", "Voting entity. ", None)
        #tp8b = ("Secondary Vote", "", "Secondary Entity", None)
        #lab13, lab14 = self.gridquad(gridx, 0, rowcnt, tp7b, tp8b, butt)
        #self.dat_dict['vote'] = lab13
        #self.dat_dict['vote2'] = lab14
        #rowcnt += 1

        # ----------------------------------------------------------------

        # Create snapshot
        for aa in self.dat_dict.keys():
            self.dat_dict_org[aa] = self.dat_dict[aa].get_text()

        hboxtop = Gtk.HBox()
        hboxtop.pack_start(Gtk.Label(" "),  0, 0, 2)
        hboxtop.pack_start(Gtk.Label("Not all enrties are required: "),  0, 0, 6)
        hboxtop.pack_start(Gtk.Label(" "),  1, 1, 2)
        #hboxtop.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#aaaa44"))
        vbox.pack_start(hboxtop, 0, 0, 0)

        sumx.pack_start(Gtk.Label("   "), 0, 0, 0)
        sumx.pack_start(gridx, 0, 0, 0)
        sumx.pack_start(Gtk.Label("   "), 1, 1, 0)

        vbox.pack_start(sumx, 1, 1, 2)
        #sumx.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#aaaa88"))

        #fill = Gtk.VBox()
        #vbox.pack_start(fill, 0, 0, 2)

        #hbox3 = Gtk.HBox()
        #hbox3.pack_start(Gtk.Label("q"),1,1,0)
        #hbox3.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#aaaaaa"))
        #vbox.pack_start(hbox3, 0, 0, 2)

        vbox.pack_start(hbox4, False, 0, 4)

        self.add(vbox)
        self.show_all()

        #GLib.timeout_add(500, self.timer)

    def vspacer(self, sp):
        hbox = Gtk.HBox()
        hbox.set_size_request(sp, sp)
        return hbox

    def pressed_dob(self, arg, arg2):
        #arg2.set_text("Developing")

        dd = datetime.datetime.now()

        org = arg2.get_text().split("/")
        #print("org:", org)

        if len(org) == 0:
            org.append(dd.year)
            org.append(dd.month)
            org.append(dd.day)
        elif len(org) == 1:
            if not org[0]:
                org[0] = dd.year
            org.append(dd.month)
            org.append(dd.day)

        result = pgcal.popcal(org)

        if result[0] != Gtk.ResponseType.ACCEPT:
            return
        #print("res:", result)

        #result[1][1] += 1

        arg2.set_text(str(result[1][0]) + "/" + str(result[1][1]) + \
                            "/" + str(result[1][2]))

    def pressed_uuid(self, arg, arg2):
        if arg2.get_text() != "":
            msg = "Already has a UUID; Cannot set."
            self.message(msg)
            self.status.set_text(msg)
            self.status_cnt = 5
            return
        arg2.set_text(str(uuid.uuid1()))

    def load_uuid(self, arg, arg2):
        if arg2.get_text() != "":
            msg = "Already has a GUID; Cannot set."
            self.message(msg)
            self.status.set_text(msg)
            self.status_cnt = 5
            return
        arg2.set_text(str(uuid.uuid1()))

    def gridquad(self, gridx, left, top, entry1, entry2, butt = None):
        lab1 = Gtk.Label(entry1[0] + "   ")
        lab1.set_alignment(1, 0)
        lab1.set_tooltip_text(entry1[2])
        gridx.attach(lab1, left, top, 1, 1)

        headx = Gtk.Entry();
        headx.set_width_chars(20)
        if entry1[3] != None:
            headx.set_text(entry1[3])
        gridx.attach(headx, left+1, top, 1, 1)

        lab2 = Gtk.Label("    " + entry2[0] + "   ")
        lab2.set_alignment(1, 0)
        lab2.set_tooltip_text(entry2[2])
        gridx.attach(lab2, left+2, top, 1, 1)

        headx2 = Gtk.Entry();
        headx2.set_width_chars(20)
        if entry2[3] != None:
            headx2.set_text(entry2[3])
        gridx.attach(headx2, left+3, top, 1, 1)
        if butt:
            gridx.attach(butt, left+4, top, 1, 1)
        return headx, headx2

    def griddouble(self, gridx, left, top, entry1, buttx = None):
        lab1 = Gtk.Label(entry1[0] + "   ")
        lab1.set_alignment(1, 0)
        lab1.set_tooltip_text(entry1[2])
        gridx.attach(lab1, left, top, 1, 1)

        headx = Gtk.Entry();
        headx.set_width_chars(40)
        if entry1[3] != None:
            headx.set_text(entry1[3])
        gridx.attach(headx, left+1, top, 2, 1)
        if buttx:
            gridx.attach(buttx, left+3, top, 1, 1)
        return headx

    def gridsingle(self, gridx, left, top, entry1):
        lab1 = Gtk.Label(entry1[0] + "   ")
        lab1.set_alignment(1, 0)
        lab1.set_tooltip_text(entry1[2])
        gridx.attach(lab1, left, top, 1, 1)

        headx, cont = self.wrap(TextViewx())
        if entry1[3] != None:
             headx.set_text(entry1[3])
        gridx.attach(headx, left+1, top, 3, 1)

        return cont

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
        iter = xmodel.get_iter_first()
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
        fr = Gtk.Frame()
        sc = Gtk.ScrolledWindow()
        sc.set_hexpand(True)
        sc.set_vexpand(True)
        sc.add(cont)
        fr.add(sc)
        return fr, cont

    def  non_changed(self):

        ''' Mark as non changed '''
        for aa in self.dat_dict.keys():
            self.dat_dict_org[aa] = self.dat_dict[aa].get_text()

    def  reset_changed(self):

        ''' Reset flags for changed dict '''

        for aa in self.dat_dict.keys():
            self.dat_dict_org[aa] = self.dat_dict[aa].get_text()

    def new_data(self, arg):

        # See if previous one saved
        ccc = False
        for aa in self.dat_dict.keys():
            if self.dat_dict_org[aa] != self.dat_dict[aa].get_text():
                ccc = True
        if ccc:
            msg = "Please save data before creating a new one."
            self.status.set_text(msg)
            self.status_cnt = 4
            self.message(msg)
            return

        # Clear, reset
        for aa in self.dat_dict.keys():
            self.dat_dict[aa].set_text("")

        self.reset_changed()


    def load_data(self, arg):

        # See if previous one saved
        ccc = False
        for aa in self.dat_dict.keys():
            if self.dat_dict_org[aa] != self.dat_dict[aa].get_text():
                ccc = True
        if ccc:
            msg = "Please save data before loading new one."
            self.status.set_text(msg)
            self.status_cnt = 4
            self.message(msg)
            return

        # Clear, reset
        for aa in self.dat_dict.keys():
            self.dat_dict[aa].set_text("")

        self.reset_changed()

        result, loadid = recsel.ovd(self.vcore)

        if result != Gtk.ResponseType.ACCEPT:
            return

        print("loadid:", loadid)

        try:
            dat = self.vcore.retrieve(loadid[0][2])
        except:
            dat = []
            print(sys.exc_info())
            pass
        if not dat:
            msg = "No data"
            print(msg)
            self.status.set_text(msg)
            self.status_cnt = 5
            return

        #print("dat:", dat)
        dec = self.packer.decode_data(dat[0][1])[0]
        print("dec:", dec)
        for aa in dec.keys():
            self.dat_dict[aa].set_text(dec[aa])

        # Mark as non changed
        for aa in self.dat_dict.keys():
            self.dat_dict_org[aa] = self.dat_dict[aa].get_text()

    def save_data(self, arg1):
        for aa in self.dat_dict.keys():
            print(aa, "=", "'" + self.dat_dict[aa].get_text() + "'")
        ddd = {}
        for aa in self.dat_dict.keys():
            ddd[aa] = self.dat_dict[aa].get_text()

        print("Save_data", ddd)

        enc = self.packer.encode_data("", ddd)
        print("enc:", enc)

        try:
            ret = self.vcore.save_data(self.dat_dict['uuid'].get_text(), enc)
        except:
            pass
            print("save", sys.exc_info())

        for aa in self.dat_dict.keys():
            self.dat_dict_org[aa] = self.dat_dict[aa].get_text()

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
                        if idx >= 11:
                            print("bad vote value", idx)
                        self.tally[ idx % 11 ] += 1

                    if pay['Action'] == 'uncast':
                        idx = int(decpay['PayLoad']['Vote'])
                        if idx >= 11:
                            print("bad unvote value", idx)
                        self.untally[ idx % 11 ] += 1
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

        ccc = False
        for aa in self.dat_dict.keys():
            if self.dat_dict_org[aa] != self.dat_dict[aa].get_text():
                ccc = True
        if ccc:
            msg = "Unsaved data. Are you sure you want to abandon it?"
            self.status.set_text(msg)
            self.status_cnt = 4
            ret = self.yesno(msg)
            #print("yesno:", ret)
            if ret != Gtk.ResponseType.YES:
                return True
            else:
                print("Abandoning", self.dat_dict['name'].get_text())

        self.exit_all()

    def exit_all(self):
        Gtk.main_quit()

    def key_press_event(self, win, event):
        #print( "key_press_event", win, event)
        pass

    def button_press_event(self, win, event):
        #print( "button_press_event", win, event)
        pass

    def message(self, msg):
        dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE, msg)

        #    'Action: "%s" of type "%s"' % (action.get_name(), type(action)))

        # Close dialog on user response
        dialog.connect ("response", lambda d, r: d.destroy())
        return dialog.run()

    def yesno(self, msg):
        dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.INFO, Gtk.ButtonsType.YES_NO, msg)

        #    'Action: "%s" of type "%s"' % (action.get_name(), type(action)))

        # Close dialog on user response
        #dialog.connect ("response", lambda d, r: d.destroy())
        ret = dialog.run()
        dialog.destroy()
        return  ret

    def activate_action(self, action):

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
