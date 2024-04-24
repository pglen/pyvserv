#!/usr/bin/env python

import os, sys, getopt, signal, random, time
import string, warnings, uuid, datetime

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

from pyvguicom import pgutils

# Add this path to find local modules
base = os.path.dirname(pgutils.__file__)
sys.path.append(base)

from pyvguicom import pgbox
from pyvguicom import pgsimp
from pyvguicom import pggui
from pyvguicom import pgentry
from pyvguicom import pgutils

from pymenu import  *
from pgui import  *

import recsel, pgcal

from pyvcommon import pydata, pyservsup,  pyvhash, crysupp

from pydbase import twincore, twinchain

import pyvpacker

alllett =   string.ascii_lowercase + string.ascii_uppercase

def randascii(lenx):

    ''' Spew a lot of chars, simulate txt by add ' ' an '\n' '''

    strx = ""
    for aa in range(lenx):
        ridx = random.randint(0x20, 0x7d)
        rr = chr(ridx)
        strx += str(rr)
        if random.randint(0x00, 40) == 30:
            strx += "\n"
        if random.randint(0x00, 12) == 10:
            strx += " "
    return strx

def simname(lenx):
    strx = ""
    lenz = len(alllett)-1

    spidx = random.randint(0, lenx - 4)
    ridx = random.randint(0, len(string.ascii_uppercase)-1)
    strx += string.ascii_uppercase[ridx]
    for aa in range(spidx):
        ridx = random.randint(0, len(string.ascii_lowercase)-1)
        rr = string.ascii_lowercase[ridx]
        strx += str(rr)

    strx += " "
    ridx = random.randint(0, len(string.ascii_uppercase)-1)
    strx += string.ascii_uppercase[ridx]

    for aa in range(lenx - spidx):
        ridx = random.randint(0, len(string.ascii_lowercase)-1)
        rr = string.ascii_lowercase[ridx]
        strx += str(rr)

    return strx

def randisodate():
    dd = datetime.datetime.now()
    dd = dd.replace(microsecond=0)
    return dd.isoformat()

def randate():

    ''' Give us a random date in str '''

    dd = datetime.datetime.now()
    dd = dd.replace(year=random.randint(1980, 2024),
                        month=random.randint(1, 12),
                           day=random.randint(1, 28),
                             hour=0, minute=0, second=0, microsecond=0)

    return dd.strftime("%Y/%m/%d")

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
        self.set_title("PyVServer Voter Entry")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.packer = pyvpacker.packbin()
        self.vcore = twincore.TwinCore("voters.pydb", 0)
        self.exit_flag = 0
        self.stop = True
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
        #self.connect("key-press-event", self.key_press_event)
        #self.connect("button-press-event", self.button_press_event)

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

        lab2 = Gtk.Label(" | ");
        hbox4.pack_start(lab2, 0, 0, 0)

        butt2 = Gtk.Button.new_with_mnemonic(" Te_zt ")
        butt2.connect("clicked", self.test_data)
        hbox4.pack_start(butt2, False, 0, 4)

        lab3 = Gtk.Label(" | ");
        hbox4.pack_start(lab3, 0, 0, 0)

        butt2 = Gtk.Button.new_with_mnemonic(" Dele_te entry ")
        butt2.connect("clicked", self.del_data)
        hbox4.pack_start(butt2, False, 0, 4)

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

        buttx2 = Gtk.Button.new_with_mnemonic("Sele_ct Date")
        tp1 =("Full Nam_e: ", "name", "Enter full name (TAB to advance)", None)
        tp2 = ("Date o_f birth: ", "dob", "Date of birth, YYYY/MM/DD", None)
        lab1, lab2 = pgentry.gridquad(gridx, rowcnt, 0, tp1, tp2, buttx2)
        buttx2.connect("clicked", self.pressed_dob, lab2)
        self.dat_dict['name'] = lab1
        self.dat_dict['dob'] = lab2
        rowcnt += 1

        tp3 = ("Location of birth: ", "lob", "Location: City / Country", None)
        tp4 = ("Nick Name: ", "nick", "Enter nick name / Alias if available", None)
        lab3, lab4 = pgentry.gridquad(gridx, 0, rowcnt, tp3, tp4)
        self.dat_dict['lob'] = lab3
        self.dat_dict['nick'] = lab4
        rowcnt += 1

        gridx.attach(self.vspacer(8), 0, rowcnt, 1, 1)
        rowcnt += 1

        tp3x = ("UUID: ", "uuid", "Generate VOTER UID by pressing button", None)
        butt1 = Gtk.Button.new_with_mnemonic("Gene_rate")
        lab3x = pgentry.griddouble(gridx, 0, rowcnt, tp3x, butt1)
        butt1.connect("clicked", self.pressed_uuid, lab3x)
        self.dat_dict['uuid'] = lab3x
        rowcnt += 1

        tp4x = ("GUID: ", "guid", "Load GROUP UID by pressing button", None)
        butt2 = Gtk.Button.new_with_mnemonic("Loa_d")
        lab4x = pgentry.griddouble(gridx, 0, rowcnt, tp4x, butt2)
        butt2.connect("clicked", self.load_uuid, lab4x)
        self.dat_dict['guid'] = lab4x
        rowcnt += 1
        gridx.attach(self.vspacer(8), 0, rowcnt, 1, 1)
        rowcnt += 1

        tp3a = ("Address Line 1: ", "addr1", "Address line one. (Number, Street)", None)
        tp4a = ("Address Line 2: ", "addr2", "Addressline two. (if applicable)", None)
        lab5, lab6 = pgentry.gridquad(gridx, 0, rowcnt, tp3a, tp4a)
        self.dat_dict['addr1'] = lab5
        self.dat_dict['addr2'] = lab6
        rowcnt += 1

        tp5 = ("City: ", "city", "City or Township", None)
        tp6 = ("State / Territory: ", "county", "County or Teritory or Borough", None)
        lab7, lab8 = pgentry.gridquad(gridx, 0, rowcnt, tp5, tp6)
        self.dat_dict['city'] = lab7
        self.dat_dict['terr'] = lab8
        rowcnt += 1

        tp7 = ("Zip: ", "zip", "Zip code or Postal code", None)
        tp8 = ("Country: ", "country", "Coutry of residence", None)
        lab9, lab10 = pgentry.gridquad(gridx, 0, rowcnt, tp7, tp8)
        self.dat_dict['zip'] = lab9
        self.dat_dict['country'] = lab10
        rowcnt += 1

        tp7a = ("Phone: ", "phone", "Phone or text number. ", None)
        tp8a = ("Email: ", "email", "Primary Email", None)
        lab11, lab12 = pgentry.gridquad(gridx, 0, rowcnt, tp7a, tp8a)
        self.dat_dict['phone'] = lab11
        self.dat_dict['email'] = lab12
        rowcnt += 1

        tp7b = ("Phone: (secondary)", "phone2", "Secondary phone or text number. ", None)
        tp8b = ("Email: (Secondary)", "email2", "Secondary Email, if available: Ex: whatsapp", None)
        lab13, lab14 = pgentry.gridquad(gridx, 0, rowcnt, tp7b, tp8b)
        self.dat_dict['phone2'] = lab13
        self.dat_dict['email2'] = lab14
        rowcnt += 1

        tp9b = ("Now: (date of entry)"," ",  "Autofilled, date of entry", None)
        tp10b = ("Operator:", " ", "Operator, who entered this record.", None)
        lab15, lab16 = pgentry.gridquad(gridx, 0, rowcnt, tp9b, tp10b)
        self.dat_dict['now'] = lab15
        self.dat_dict['oper'] = lab16
        rowcnt += 1

        tp6x = ("Notes: ", "", "Text for Notes. Press Shift Enter to advance", None)
        lab6x = pgentry.gridsingle(gridx, 0, rowcnt, tp6x)
        self.dat_dict['notes'] = lab6x
        rowcnt += 1

        gridx.attach(self.vspacer(8), 0, rowcnt, 1, 1)
        rowcnt += 1

        #tp7b = ("Vote:" , "", "Voting entity. ", None)
        #tp8b = ("Secondary Vote", "", "Secondary Entity", None)
        #lab13, lab14 = gridquad(gridx, 0, rowcnt, tp7b, tp8b, butt)
        #self.dat_dict['vote'] = lab13
        #self.dat_dict['vote2'] = lab14
        #rowcnt += 1

        # ----------------------------------------------------------------

        # Create snapshot
        for aa in self.dat_dict.keys():
            self.dat_dict_org[aa] = self.dat_dict[aa].get_text()

        #hboxtop = Gtk.HBox()
        #hboxtop.pack_start(Gtk.Label(" "),  0, 0, 2)
        #hboxtop.pack_start(Gtk.Label("Not all enrties are required: "),  0, 0, 6)
        #hboxtop.pack_start(Gtk.Label(" "),  1, 1, 2)
        ##hboxtop.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#aaaa44"))
        #vbox.pack_start(hboxtop, 0, 0, 0)

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

        GLib.timeout_add(1000, self.timer)

    def vspacer(self, sp):
        hbox = Gtk.HBox()
        hbox.set_size_request(sp, sp)
        return hbox

    def is_changed(self):
        ccc = False
        for aa in self.dat_dict.keys():
            if self.dat_dict_org[aa] != self.dat_dict[aa].get_text():
                ccc = True
        return ccc

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

        result = pgcal.PopCal(org)

        if result[0] != Gtk.ResponseType.ACCEPT:
            return
        #print("res:", result)

        #result[1][1] += 1

        arg2.set_text(str(result[1][0]) + "/" + str(result[1][1]) + \
                            "/" + str(result[1][2]))

    def pressed_uuid(self, arg, arg2):
        if arg2.get_text() != "":
            msg = "Already has a UUID; Cannot set."
            pggui.message(msg)
            self.status.set_text(msg)
            self.status_cnt = 5
            return
        arg2.set_text(str(uuid.uuid1()))

    def load_uuid(self, arg, arg2):
        if arg2.get_text() != "":
            msg = "Already has a GUID; Cannot set."
            pggui.message(msg)
            self.status.set_text(msg)
            self.status_cnt = 5
            return
        arg2.set_text(str(uuid.uuid1()))


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
        pgutils.usleep(5)
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

    def  clear_data(self):

        ''' Clar out data '''

        for aa in self.dat_dict.keys():
            self.dat_dict[aa].set_text("")

    def  reset_changed(self):

        ''' Reset flags for changed dict '''

        for aa in self.dat_dict.keys():
            self.dat_dict_org[aa] = self.dat_dict[aa].get_text()

    def del_data(self, arg):

        nnn = self.dat_dict['name'].get_text()
        if not nnn:
            msg = "Empty record, cannot delete."
            self.status.set_text(msg)
            self.status_cnt = 4
            pggui.message(msg)
            return
        msg = "This will delete: '%s'. \nAre you sure?" % nnn
        self.status.set_text(msg)
        self.status_cnt = 4
        ret = self.yesno(msg)
        if ret != Gtk.ResponseType.YES:
            return True
        ddd = self.dat_dict['uuid'].get_text()
        #print("deleting:", ddd)
        try:
            dat = self.vcore.del_rec_bykey(ddd)
            #print("dat:", dat)
        except:
            dat = []
            print(sys.exc_info())
            pass
        self.status.set_text("Record '%s' deleted." % nnn)
        self.status_cnt = 4
        # Clear, reset
        self.clear_data()
        self.reset_changed()

    def new_data(self, arg):

        # See if previous one saved
        ccc = False
        for aa in self.dat_dict.keys():
            if self.dat_dict_org[aa] != self.dat_dict[aa].get_text():
                ccc = True
        if ccc:
            msg = "Unsaved data. Are you sure you want to abandon it?"
            self.status.set_text(msg)
            self.status_cnt = 4
            ret = self.yesno(msg)
            if ret != Gtk.ResponseType.YES:
                return True

        # Clear, reset
        for aa in self.dat_dict.keys():
            self.dat_dict[aa].set_text("")

        # Fill in defaults
        dd = datetime.datetime.now()
        dd = dd.replace(microsecond=0)
        self.dat_dict['now'].set_text(dd.isoformat())
        self.dat_dict['uuid'].set_text(str(uuid.uuid1()))

        self.reset_changed()

    def load_data(self, arg):

        # See if previous one saved
        ccc = False
        for aa in self.dat_dict.keys():
            if self.dat_dict_org[aa] != self.dat_dict[aa].get_text():
                ccc = True
        if ccc:
            msg = "Please save current data before loading a new one."
            self.status.set_text(msg)
            self.status_cnt = 4
            pggui.message(msg)
            return

        # Clear, reset
        for aa in self.dat_dict.keys():
            self.dat_dict[aa].set_text("")

        self.reset_changed()

        sss = recsel.RecSel(self.vcore)
        if sss.response != Gtk.ResponseType.ACCEPT:
            return

        print("sss.res:", sss.res)

        try:
            dat = self.vcore.retrieve(sss.res[0][3])
        except:
            dat = []
            print(sys.exc_info())
            pass
        if not dat:
            msg = "No data selected."
            #print(msg)
            self.status.set_text(msg)
            self.status_cnt = 5
            pggui.message(msg)
            return

        #print("dat:", dat)
        dec = self.packer.decode_data(dat[0][1])[0]
        #print("dec:", dec)
        for aa in dec.keys():
            self.dat_dict[aa].set_text(dec[aa])

        # Mark as non changed
        self.reset_changed()

    def test_data(self, arg1):

        #print("test started")
        self.stop = not self.stop
        while True:
            if self.exit_flag:
                self.reset_changed()
                break
            if self.stop:
                self.reset_changed()
                self.status.set_text("Test Stopped")
                self.status_cnt = 4
                break
            for aa in self.dat_dict.keys():
                # Handle differences
                if aa == 'uuid':
                   self.dat_dict[aa].set_text(str(uuid.uuid1()) )
                elif aa == 'name':
                   self.dat_dict[aa].set_text(simname(random.randint(12, 22)))
                elif aa == 'guid':
                   self.dat_dict[aa].set_text(str(uuid.uuid1()) )
                elif aa == 'dob':
                    self.dat_dict[aa].set_text(randate())
                elif aa == 'now':
                    self.dat_dict[aa].set_text(randisodate())
                elif aa == 'notes':
                    self.dat_dict[aa].set_text(randascii(random.randint(33, 66)))
                else:
                    self.dat_dict[aa].set_text(pgutils.randstr(random.randint(6, 22)))
            sleepx = 20
            pgutils.usleep(sleepx)
            self.save_data(0)
            self.clear_data()

    def save_data(self, arg1):

        # See if changed
        if not self.is_changed():
            msg = "Nothing changed, cannot save."
            self.status.set_text(msg)
            self.status_cnt = 4
            pggui.message(msg)
            return

        if not self.dat_dict['name'].get_text():
            msg = "Must have a voter name."
            self.status.set_text(msg)
            self.status_cnt = 4
            self.set_focus(self.dat_dict['name'])
            pggui.message(msg)
            return

        if not self.dat_dict['dob'].get_text():
            msg = "Must have a voter date of birth."
            self.status.set_text(msg)
            self.status_cnt = 4
            self.set_focus(self.dat_dict['dob'])
            pggui.message(msg)
            return

        try:
            uuu = uuid.UUID(self.dat_dict['uuid'].get_text())
        except:
            #print("Gen UUID", sys.exc_info())
            msg = "Cannot save without a valid UUID"
            self.status.set_text(msg)
            self.status_cnt = 4
            pggui.message(msg)
            return

        ddd = {}
        for aa in self.dat_dict.keys():
            ddd[aa] = self.dat_dict[aa].get_text()

        #print("Save_data", ddd)
        enc = self.packer.encode_data("", ddd)
        #print("enc:", enc)

        try:
            ret = self.vcore.save_data(self.dat_dict['uuid'].get_text(), enc)
        except:
            pass
            print("save", sys.exc_info())

        self.status.set_text("Entry '%s' saved." % self.dat_dict['name'].get_text())
        self.status_cnt = 4

        for aa in self.dat_dict.keys():
            self.dat_dict_org[aa] = self.dat_dict[aa].get_text()

    def timer(self):

        #print("Called timer")
        if self.in_timer:
            return True
        in_timer = True
        self.cnt += 1
        if self.status_cnt:
            self.status_cnt -= 1
            if not self.status_cnt:
                self.status.set_text("Idle.")
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
                #print("Abandoning", self.dat_dict['name'].get_text())
                pass

        self.exit_all()

    def exit_all(self):
        self.exit_flag = 1
        Gtk.main_quit()

    def key_press_event(self, win, event):
        #print( "key_press_event", event.string, event.state)
        pass

    def button_press_event(self, win, event):
        #print( "button_press_event", win, event)
        pass

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
