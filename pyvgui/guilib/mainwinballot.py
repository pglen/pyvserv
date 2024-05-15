#!/usr/bin/env python

import os, sys, getopt, signal, random, time, base64
import string, warnings, uuid, datetime, struct, io

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

import recsel, pgcal, config, passdlg, pymisc

from pyvcommon import pydata, pyservsup,  pyvhash, crysupp, pyvindex

from pydbase import twincore, twinchain

import pyvpacker

from Crypto.Cipher import AES

# ------------------------------------------------------------------------

class MainWin(Gtk.Window):

    def __init__(self, globals):

        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)

        #print("globals", globals.myhome)

        self.powers     = 0
        self.conf       = globals.conf
        self.conf.iconf  = os.path.dirname(globals.conf.me) + os.sep + "pyvballot.png"
        self.conf.iconf2 = os.path.dirname(globals.conf.me) + os.sep + "pyvvote_sub.png"
        self.conf.siteid = globals.siteid
        try:
            #print("iconf", self.conf.iconf)
            ic = Gtk.Image(); ic.set_from_file(self.conf.iconf)
            self.set_icon(ic.get_pixbuf())
        except:
            pass

        self.start_anal = False
        #self.core = None
        self.in_timer = False
        self.cnt = 0
        self.old_sss = 1
        self.status_cnt = 0
        self.set_title("PyVServer Ballot Configuration")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.packer = pyvpacker.packbin()
        # We let the core carry vars; make sure they do not collide
        self.bcore = twincore.TwinCore("ballots.pydb", 0)
        self.bcore.packer = self.packer
        self.bcore.hashname  = os.path.splitext(self.bcore.fname)[0] + ".hash.id"
        self.bcore.hashname2 = os.path.splitext(self.bcore.fname)[0] + ".hash.name"

        self.acore = twincore.TwinCore("audit.pydb", 0)
        self.authcore = twincore.TwinCore("auth.pydb", 0)

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

        #self.set_default_size(6*www/8, 6*hhh/8)

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

        #butt2 = Gtk.Button.new_with_mnemonic(" Ne_w Vote ")
        #butt2.connect("clicked", self.new_data)
        #hbox4a.pack_start(butt2, False, 0, 2)

        #butt2 = Gtk.Button.new_with_mnemonic(" Dele_te entry ")
        #butt2.connect("clicked", self.del_data)
        #hbox4a.pack_start(butt2, False, 0, 2)
        #hbox4a.pack_start(Gtk.Label("   "), 0, 0, 2)

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

        hbox4 = Gtk.HBox()
        lab1 = Gtk.Label("   ");
        hbox4.pack_start(lab1, 0, 0, 0)

        #lab2a = Gtk.Label(" Initializing ");
        #hbox4.pack_start(lab2a, 1, 1, 0)
        #lab2a.set_xalign(0)
        #lab2a.set_size_request(150, -1)

        self.status = pymisc.Status()
        hbox4.pack_start(self.status.scroll, 1, 1, 0)

        lab1 = Gtk.Label(" ");
        hbox4.pack_start(lab1, 0, 0, 0)

        butt5 = Gtk.Button.new_with_mnemonic(" Ne_w Ballot ")
        butt5.connect("clicked", self.new_data)
        hbox4.pack_start(butt5, False, 0, 2)

        butt4 = Gtk.Button.new_with_mnemonic(" _Save Ballot ")
        butt4.connect("clicked", self.save_data)
        hbox4.pack_start(butt4, False, 0, 2)

        butt3 = Gtk.Button.new_with_mnemonic(" Lo_ad Ballot ")
        butt3.connect("clicked", self.load_data)
        hbox4.pack_start(butt3, False, 0, 2)

        butt2 = Gtk.Button.new_with_mnemonic("     E_xit    ")
        butt2.connect("clicked", self.OnExit, self)
        hbox4.pack_start(butt2, False, 0, 2)

        lab2 = Gtk.Label("   ");  hbox4.pack_start(lab2, 0, 0, 0)

        #sg = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
        sumx = Gtk.HBox()
        self.gridx = Gtk.Grid()
        self.gridx.set_column_spacing(6)
        self.gridx.set_row_spacing(6)

        #self.gridx.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#aaaaaa"))

        rowcnt = 0

        #self.gridx.attach(pggui.ySpacer(8), 0, rowcnt, 1, 1)
        #rowcnt += 1

        #self.gridx.attach(pggui.ySpacer(8), 0, rowcnt, 1, 1)
        #rowcnt += 1

        tp1 = ("Ballot Nam_e: ", "name", "Enter ballot name (TAB to advance)", None)
        tp2 = ("Date o_f Election: ", "dob", "Election Day, YYYY/MM/DD", None)
        lab1, lab2 = pgentry.gridquad(self.gridx, 0, rowcnt,  tp1, tp2, None)
        #lab1.set_editable(False);   lab2.set_editable(False);
        self.dat_dict['name'] = lab1
        self.dat_dict['dob']  = lab2
        rowcnt += 1

        tp3x = ("Ballot UUID: ", "uuid", "Load / Select Client ID", None)
        butt1 = Gtk.Button.new_with_mnemonic("Load")
        lab3x = pgentry.griddouble(self.gridx, 0, rowcnt, tp3x, butt1)
        butt1.connect("clicked", self.load_uuid, lab3x)
        self.dat_dict['uuid'] = lab3x
        rowcnt += 1

        #tp9b = ("Date of entry:"," ",  "Autofilled, date of entry", None)
        #tp10b = ("Entered by:", " ", "Operator, who entered this record.", None)
        #lab15, lab16 = pgentry.gridquad(self.gridx, 0, rowcnt, tp9b, tp10b, None)
        #lab15.set_editable(False);   lab16.set_editable(False);
        #self.dat_dict['now'] = lab15
        #self.dat_dict['oper'] = lab16
        #rowcnt += 1

        #tp7a = ("Phone: ", "phone", "Phone or text number. ", None)
        #tp8a = ("Email: ", "email", "Primary Email", None)
        #lab11, lab12 = pgentry.gridquad(self.gridx, 0, rowcnt, tp7a, tp8a)
        #self.dat_dict['phone'] = lab11
        #self.dat_dict['email'] = lab12
        #rowcnt += 1

        #tp6x = ("Notes: ", "", "Text for Notes. Press Shift Enter to advance", None)
        #lab6x = pgentry.gridsingle(self.gridx, 0, rowcnt, tp6x)
        #lab6x.set_editable(False);
        #self.dat_dict['notes'] = lab6x
        #rowcnt += 1

        # ----------------------------------------------------------------

        #self.gridx.attach(pggui.ySpacer(8), 0, rowcnt, 1, 1)
        #rowcnt += 1
        frame = Gtk.Frame()
        self.gridx.attach(frame, 1, rowcnt, 3, 1)
        rowcnt += 1

        tp4x = ("Site UUID: ", "guid", "Group / Site UID", None)
        butt2 = Gtk.Button.new_with_mnemonic("Load")
        lab4x = pgentry.griddouble(self.gridx, 0, rowcnt, tp4x, butt2)
        butt2.connect("clicked", self.load_site_uuid, lab4x)
        self.dat_dict['bguid'] = lab4x
        rowcnt += 1

        tp6x = ("Operator UUID: ", "ouid", "Operator UUID", None)
        butt2 = Gtk.Button.new_with_mnemonic("Load")
        lab6x = pgentry.griddouble(self.gridx, 0, rowcnt, tp6x, butt2)
        butt2.connect("clicked", self.load_op_uuid, lab6x)
        self.dat_dict['bouid'] = lab6x
        rowcnt += 1

        butt2o = Gtk.Button.new_with_mnemonic("Load")
        tp9b = ("Now: (date of entry)"," ",  "Autofilled, date of entry", None)
        tp10b = ("Operator:", " ", "Operator, who entered this record.", None)
        lab15, lab16 = pgentry.gridquad(self.gridx, 0, rowcnt, tp9b, tp10b, butt2o)
        butt2o.connect("clicked", self.load_op_name, lab16, lab15)
        rowcnt += 1

        self.dat_dict['now'] = lab15
        self.dat_dict['boper'] = lab16

        # ----------------------------------------------------------------

        frame = Gtk.Frame()
        self.gridx.attach(frame, 1, rowcnt, 3, 1)
        rowcnt += 1

        tp7 = ("Candidate _1: ", "pri", "Enter candidate, keep it less than 24 chars", None)
        tp8 = ("Candidate _2: ", "sec", "Enter candidate, keep it less than 24 chars", None)
        lab9c, lab10c = pgentry.gridquad(self.gridx, 0, rowcnt, tp7, tp8)
        self.dat_dict['can1'] = lab9c
        self.dat_dict['can2'] = lab10c
        rowcnt += 1

        tp7 = ("Candidate _3: ", "pri", "Enter candidate, keep it less than 24 chars", None)
        tp8 = ("Candidate _4: ", "sec", "Enter candidate, keep it less than 24 chars", None)
        lab9c, lab10c = pgentry.gridquad(self.gridx, 0, rowcnt, tp7, tp8)
        self.dat_dict['can3'] = lab9c
        self.dat_dict['can4'] = lab10c
        rowcnt += 1

        tp7 = ("Candidate _5: ", "pri", "Enter candidate, keep it less than 24 chars", None)
        tp8 = ("Candidate _6: ", "sec", "Enter candidate, keep it less than 24 chars", None)
        lab9c, lab10c = pgentry.gridquad(self.gridx, 0, rowcnt, tp7, tp8)
        self.dat_dict['can5'] = lab9c
        self.dat_dict['can6'] = lab10c
        rowcnt += 1

        tp7 = ("Candidate _7: ", "pri", "Enter candidate, keep it less than 24 chars", None)
        tp8 = ("Candidate _8: ", "sec", "Enter candidate, keep it less than 24 chars", None)
        lab9c, lab10c = pgentry.gridquad(self.gridx, 0, rowcnt, tp7, tp8)
        self.dat_dict['can7'] = lab9c
        self.dat_dict['can8'] = lab10c
        rowcnt += 1

        # Create table from updated fields
        self.candarr = []
        for aa in range(1, 9):
            self.candarr.append(self.dat_dict['can%d' % (aa)])

        for aa in self.candarr:
            aa.connect("focus-out-event", self.lost_focus)

        self.candstr =  [\
            "None", ]
        for aa in range(8):
            self.candstr.append("Candidate %d" % (aa + 1))
        #print("candarr:", candarr)

        hbox5 = Gtk.HBox()
        hbox5.pack_start(Gtk.Label("  "), 1, 1, 0)
        hbox5.pack_start(Gtk.Label("Ballot preview:   "), 0, 0, 0)
        self.gridx.attach(hbox5, 0, rowcnt, 1, 1)

        self.labrow = rowcnt
        rowcnt = self.preview(self.labrow)

        #lab9.set_editable(False)
        #self.dat_dict['vprim'] = lab9
        #self.dat_dict['vsec']  = lab10
        #rowcnt += 1

        rowcnt += 1

        tp6x = ("Ballot No_tes: ", "", "Text for ballot notes. Press Shift+Enter key to advance", None)
        lab6x = pgentry.gridsingle(self.gridx, 0, rowcnt, tp6x)
        self.dat_dict['vnotes'] = lab6x
        rowcnt += 1

        #self.gridx.attach(pggui.ySpacer(8), 0, rowcnt, 1, 1)
        #rowcnt += 1
        frame = Gtk.Frame()
        self.gridx.attach(frame, 1, rowcnt, 3, 1)
        rowcnt += 1
        self.gridx.attach(pggui.ySpacer(8), 0, rowcnt, 1, 1)
        rowcnt += 1

        # ----------------------------------------------------------------

        # Create snapshot
        for aa in self.dat_dict.keys():
            self.dat_dict_org[aa] = self.dat_dict[aa].get_text()

        #pggui.set_testmode(1)
        vbox.pack_start(pggui.ySpacer(4), 0, 0, 0)

        #sumx.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#aaaaaa"))
        sumx.pack_start(Gtk.Label("   "), 0, 0, 0)
        sumx.pack_start(self.gridx, 1, 1, 0)
        sumx.pack_start(Gtk.Label("   "), 0, 0, 0)

        #vbox.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#aaaaff"))

        vbox.pack_start(sumx, 1, 1, 2)
        #vbox.pack_start(frame, 0, 10, 0)
        #sumx.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#aaaa88"))

        #vbox.pack_start(hbox4a, False, 0, 2)
        vbox.pack_start(hbox4, False, 0, 2)

        if self.conf.playsound:
            self.conf.playsound.play_sound("")

        self.add(vbox)
        self.show_all()
        self.en_dis_all(False)

        GLib.timeout_add(100, self.start_pass_dlg, 0)
        GLib.timeout_add(1000, self.timer)

    def lost_focus(self, arg2, arg3):
        #print("last focus")
        # Update if label focus changes
        self.preview(self.labrow)

    def preview(self, rowcnt):

        #print("rowcnt", rowcnt)

        def _checked(arg2):
            #print("Checked", arg2.get_active(), arg2.get_label())
            if arg2.get_active():
                txtx = arg2.textx #get_label()
                # Clear it to empty
                if txtx == "None":
                    txtx = ""
                #self.dat_dict['vprim'].set_text(txtx)
                self.status.set_text("Selected: '%s'" % txtx)
                self.status_cnt = 5

        rrr = None; col = 0

        # Create the 'None' entry
        nnn = "None"
        rrr = self.gridx.get_child_at(col % 3 +  1, rowcnt)
        if not rrr:
            radiox = Gtk.RadioButton.new_with_label(None, nnn)
            rrr = radiox
            self.gridx.attach(radiox, col % 3 +  1, rowcnt, 1, 1)
        else:
            rrr.textx = nnn
            rrr.set_label(nnn)
        col += 1

        for cc in range(len(self.candarr)):
            txtx = self.candarr[cc].get_text()
            tooltip = "Click to activate selection."
            if len(txtx) > 24:
                bb = txtx[:24] + ".."
                tooltip = txtx
            else:
                if not txtx:
                    bb = "Candidate %d" % (col + 1)
                else:
                    bb = txtx

            radiox = Gtk.RadioButton.new_with_label(None, bb)
            radiox.set_tooltip_text(tooltip)
            radiox.textx = txtx
            radiox.connect("toggled", _checked)
            radiox.join_group(rrr)

            ccc = self.gridx.get_child_at(col % 3 +  1, rowcnt)
            if not ccc:
                ccc = radiox
                self.gridx.attach(radiox, col % 3 +  1, rowcnt, 1, 1)
            else:
                #print("ccc", ccc.textx)
                ccc.textx = txtx
                ccc.set_label(bb)

            if not txtx:
                ccc.set_sensitive(False)
            else:
                ccc.set_sensitive(True)

            if col % 3 == 2:
                rowcnt += 1
            col += 1

        return rowcnt

    def start_pass_dlg(self, arg2):

        authcnt = 0
        while True:
            if authcnt > 3:
                pggui.message("Too May tries, exiting.")
                sys.exit(1)
            ret = passdlg.auth_initial(self.authcore, self.packer, self.conf)
            #print("ret:", ret)
            if not ret[0]:
                authcnt += 1
                continue
            if ret[1][2] != "Enabled":
                msg = "Cannot log in, user '%s' is disbled " % ret[1][0]
                self.status.set_text(msg)
                self.status_cnt = 5
                pggui.message(msg)
                authcnt += 1
                continue
            # Success
            self.operator = ret[1][0]
            self.powers   = ret[1][4]
            self.ouid     = ret[1][5]
            self.status.set_text("Authenticated '%s'" % ret[1][0])
            self.status_cnt = 5
            self.en_dis_all(True)
            recsel.audit(self.acore, self.packer, "Successful Login", ret[1][0])
            break

        self.set_focus(self.dat_dict['name'])

    def en_dis_all(self, flag):
        for aa in self.dat_dict.keys():
            self.dat_dict[aa].set_sensitive(flag)

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

    def load_op_name(self, arg, arg2, arg3):
        if arg2.get_text() != "":
            msg = "Already has operator; Cannot set."
            pggui.message(msg)
            self.status.set_text(msg)
            self.status_cnt = 5
            return
        arg2.set_text(self.operator)
        #if arg3.get_text() == "":
        dd = datetime.datetime.now()
        dd = dd.replace(microsecond=0)
        arg3.set_text(dd.isoformat())

    def load_uuid(self, arg, arg2):
        if arg2.get_text() != "":
            msg = "Already has a UUID; Cannot set."
            pggui.message(msg)
            self.status.set_text(msg)
            self.status_cnt = 5
            return
        arg2.set_text(str(uuid.uuid1()))

    def load_op_uuid(self, arg, arg2):
        if arg2.get_text() != "":
            msg = "Already has a OUID; Cannot set."
            pggui.message(msg)
            self.status.set_text(msg)
            self.status_cnt = 5
            return
        arg2.set_text(self.ouid)

    def load_vote_uuid(self, arg, arg2):
        if arg2.get_text() != "":
            msg = "Already has a UUID; Cannot set."
            pggui.message(msg)
            self.status.set_text(msg)
            self.status_cnt = 5
            return
        arg2.set_text(str(uuid.uuid1()))

    def load_site_uuid(self, arg, arg2):
        if arg2.get_text() != "":
            msg = "Already has a Site UUID; Cannot set."
            pggui.message(msg)
            self.status.set_text(msg)
            self.status_cnt = 5
            return
        arg2.set_text(str(self.conf.siteid))

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

        ''' Delete currently active data '''

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
        ret = pggui.yes_no(msg, default="No")
        if ret != Gtk.ResponseType.YES:
            return True
        ddd = self.dat_dict['uuid'].get_text()
        # Find it via index
        ddd2 = pyvindex.search_index(self.bcore, self.bcore.hashname, ddd, pyvindex.hash_id)
        for aa in ddd2:
            #print("deleting:", ddd2)
            try:
                rrr = self.bcore.get_rec(aa)
                ret = self.bcore.del_rec(aa)
                #print(aa, "del ret:", ret)
                recsel.audit(self.acore, self.packer, "Deleted Record", rrr[1])
                self.status.set_text("Record '%s' deleted." % nnn)
                self.status_cnt = 4
            except:
                print(sys.exc_info())

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
            ret = pggui.yes_no(msg, default="No")
            if ret != Gtk.ResponseType.YES:
                return True

        # Clear, reset
        for aa in self.dat_dict.keys():
            self.dat_dict[aa].set_text("")

        # Fill in defaults
        dd = datetime.datetime.now().replace(microsecond=0)
        self.dat_dict['now'].set_text(dd.isoformat())
        self.dat_dict['uuid'].set_text(str(uuid.uuid1()))
        self.dat_dict['bguid'].set_text(str(self.conf.siteid))
        self.dat_dict['bouid'].set_text(str(self.ouid))
        self.dat_dict['boper'].set_text(str(self.operator))

        self.reset_changed()
        self.set_focus(self.dat_dict['name'])

    def load_data(self, arg):

        # See if previous one saved
        ccc = False
        for aa in self.dat_dict.keys():
            if self.dat_dict_org[aa] != self.dat_dict[aa].get_text():
                ccc = True
        if ccc:
            msg = "Unsaved data. Are you sure you want to abandon it?"
            self.status.set_text(msg)
            self.status_cnt = 4
            ret = pggui.yes_no(msg, default="No")
            if ret != Gtk.ResponseType.YES:
                return True

        heads = ["", "", "Election Date", "", ""]
        sss = recsel.RecSelDlg(self.bcore, self.acore, self.conf, headers=heads)
        if sss.response != Gtk.ResponseType.ACCEPT:
            return
        #print("sss.res:", sss.res)
        try:
            #dat = self.bcore.retrieve(sss.res[0][3])
            dat = self.bcore.get_rec(int(sss.res[0][4]))
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
        try:
            dec = self.packer.decode_data(dat[1])[0]['PayLoad']
        except:
            dec = {}
            pass
        #print("dec:", dec)
        for aa in dec.keys():
            try:
                self.dat_dict[aa].set_text(dec[aa])
            except:
                pass

        # Mark as non changed
        self.reset_changed()
        # Preview
        self.preview(self.labrow)

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
                elif aa == 'vguid':
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
            msg = "Must have a Ballot name."
            self.status.set_text(msg)
            self.status_cnt = 4
            self.set_focus(self.dat_dict['name'])
            pggui.message(msg)
            return

        dob = self.dat_dict['dob'].get_text()
        if not dob or len(dob.split("/")) < 3:
            msg = "Must have a valid Ballot date. (yyyy/mm/dd)"
            self.status.set_text(msg)
            self.status_cnt = 4
            self.set_focus(self.dat_dict['dob'])
            pggui.message(msg)
            return

        # Commemorate event by setting a fresh date
        #if  self.dat_dict['now'].get_text() == "":
        dd = datetime.datetime.now()
        dd = dd.replace(microsecond=0)
        self.dat_dict['now'].set_text(dd.isoformat())

        # Autofill what we can
        dd = datetime.datetime.now().replace(microsecond=0)
        self.dat_dict['now'].set_text(dd.isoformat())
        if self.dat_dict['uuid'].get_text() == "":
            self.dat_dict['uuid'].set_text(str(uuid.uuid1()))

        self.dat_dict['bguid'].set_text(str(self.conf.siteid))
        self.dat_dict['bouid'].set_text(str(self.ouid))
        self.dat_dict['boper'].set_text(str(self.operator))

        # Enough votes?
        cancnt = 0
        for aa in self.candarr:
            strx = aa.get_text()
            #print("strx", strx)
            if strx != "":
                cancnt += 1
        if cancnt < 2:
            msg = "Must have at least two candidates."
            self.status.set_text(msg)
            self.status_cnt = 4
            self.set_focus(self.dat_dict['can1'])
            pggui.message(msg)
            return

        # Duplicate votes?
        dupcnt = 0; dup = ""; dabs = 0; breakit = False
        for aa in self.candarr:
            if breakit:
                break
            strx = aa.get_text()
            if strx != "":
                dabs = 0; dupcnt = 0
                for bb in self.candarr:
                    stry = bb.get_text()
                    if strx == stry:
                        dupcnt += 1
                    if dupcnt > 1:
                        dup = stry
                        breakit = True
                        break
                    dabs += 1
        if dupcnt > 1:
            msg = "Duplicate candidates detected at '%s' please correct." % dup
            self.status.set_text(msg)
            self.status_cnt = 4
            self.set_focus(self.dat_dict['can%d' % (dabs+1)])
            pggui.message(msg)
            return

        # Empty gap?
        gap = False; wasempty = False; gcnt = 0
        for aa in self.candarr:
            strx = aa.get_text()
            if strx == "":
                wasempty = True
            else:
                if wasempty:
                    gap = True
                    break
            gcnt += 1
        if gap:
            msg = "Gap detected at offset '%s'. Please correct." % (gcnt)
            self.status.set_text(msg)
            self.status_cnt = 4
            self.set_focus(self.dat_dict['can%d' % (gcnt)])
            pggui.message(msg)
            return

        ddd = {}
        for aa in self.dat_dict.keys():
            ddd[aa] = self.dat_dict[aa].get_text()

        #print("Save_data", ddd)

        pvh = pyvhash.BcData()
        # We mark this as 'test' so it can stay in the chain, if desired
        pvh.addpayload({"Test": "test" ,})
        pvh.addpayload(ddd)

        pvh.hasharr()

        def callb(dlg):
            #print("callback from dlg")
            self.status.set_status_text("PROW calc, please wait ...")
            for aa in range(10):
                dlg.prog.set_fraction((aa+1) * 0.1)
                if pvh.powarr():
                    break
                self.status.set_status_text("PROW calc retry %d .." % (aa+1))
            dlg.response(Gtk.ResponseType.REJECT)
            dlg.destroy()
            self.status.set_status_text("PROW done.")
        if self.conf.weak:
            pvh.num_zeros = 1
        dlg = pymisc.progDlg(self.conf, callb, parent = self)

        if not pvh.checkpow():
            msg = "Cold not generate PROW, please retry saving record."
            pymisc.smessage(msg, conf=self.conf, sound="error")
            return

        #print("pvh", pvh.datax)

        enc = self.packer.encode_data("", pvh.datax)
        #print("enc:", enc)
        uuu = self.dat_dict['uuid'].get_text()

        # Add index indices
        def callb(c2, id2):
            # Replicate saved locally
            dddd = [uuu, enc.encode()]
            #print("dddd:", dddd)
            try:
                pyvindex.append_index(c2, c2.hashname, pyvindex.hash_id, dddd)
            except:
                print("exc save callb hash", sys.exc_info())
            try:
                pyvindex.append_index(c2, c2.hashname2, pyvindex.hash_name, dddd)
            except:
                print("exc save callb name", sys.exc_info())
        try:
            self.bcore.postexec = callb
            ret = self.bcore.save_data(uuu, enc)
        except:
            pass
            print("save", sys.exc_info())
        finally:
            self.bcore.postexec = None

        if self.conf.playsound:
            self.conf.playsound.play_sound("shutter")

        self.status.set_text("Ballot '%s' saved." % self.dat_dict['name'].get_text())
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
            ret = pggui.yes_no(msg, default="No")
            #print("yes_no:", ret)
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
