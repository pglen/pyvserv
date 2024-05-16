#!/usr/bin/env python

import os, sys, getopt, signal, random, time, base64, subprocess
import string, warnings, uuid, datetime, struct, io, threading

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
from pyvguicom import pgtests

from pymenu import  *
from pgui import  *

import recsel, pgcal, config, passdlg, pymisc

from pyvcommon import pydata, pyservsup,  pyvhash
from pyvcommon import crysupp, support, pyvindex, filedlg

from pydbase import twincore, twinchain
import pyvpacker

from Crypto.Cipher import AES

# ------------------------------------------------------------------------

class MainWin(Gtk.Window):

    def __init__(self, globals):

        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)

        #print("globals", globals.myhome)
        self.was_saved = False
        self.powers     = 0
        self.conf       = globals.conf
        self.conf.iconf  = os.path.dirname(globals.conf.me) + os.sep + "pyvvote.png"
        self.conf.iconf2 = os.path.dirname(globals.conf.me) + os.sep + "pyvvote_sub.png"
        self.conf.siteid = globals.siteid
        self.oneshot = False

        self.radioarr = {}

        try:
            #print("iconf", self.conf.iconf)
            ic = Gtk.Image(); ic.set_from_file(self.conf.iconf)
            self.set_icon(ic.get_pixbuf())
        except:
            pass

        self.start_anal = False
        self.in_timer = False
        self.cnt = 0
        self.old_sss = 1
        self.set_title("PyVServer Vote Entry")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.packer = pyvpacker.packbin()

        votename = os.path.join(pyservsup.globals.chaindir, "vote", "initial.pydb")
        self.votecore = twincore.TwinCore(votename, 0)
        self.votecore.packer = self.packer
        self.votecore.hashname  = os.path.splitext(self.votecore.fname)[0] + ".hash.id"
        self.votecore.hashname2 = os.path.splitext(self.votecore.fname)[0] + ".hash.name"

        self.acore = twincore.TwinCore("audit.pydb", 0)
        self.authcore = twincore.TwinCore("auth.pydb", 0)

        self.bcore = twincore.TwinCore("ballots.pydb", 0)
        self.bcore.packer = self.packer
        self.bcore.hashname  = os.path.splitext(self.bcore.fname)[0] + ".hash.id"
        self.bcore.hashname2 = os.path.splitext(self.bcore.fname)[0] + ".hash.name"

        # We let the core carry vars; make sure they do not collide
        self.vcore = twincore.TwinCore("voters.pydb", 0)
        self.hcore = twincore.TwinCore("ihosts.pydb", 0)
        self.vcore.packer = self.packer
        self.vcore.hashname  = os.path.splitext(self.vcore.fname)[0] + ".hash.id"
        self.vcore.hashname2 = os.path.splitext(self.vcore.fname)[0] + ".hash.name"

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

        lab1 = Gtk.Label("    ");
        hbox4.pack_start(lab1, 0, 0, 0)
        self.status = pymisc.Status()
        hbox4.pack_start(self.status.scroll, 1, 1, 0)
        lab1a = Gtk.Label("   ");
        hbox4.pack_start(lab1a, 0, 0, 0)

        if self.conf.testx:
            butt5a = Gtk.Button.new_with_mnemonic(" Te_zt ")
            butt5a.connect("clicked", self.test_data)
            hbox4.pack_start(butt5a, False, 0, 2)

        butt3 = Gtk.Button.new_with_mnemonic(" Config_ure")
        butt3.set_tooltip_text("Configure replication targets")
        butt3.connect("clicked", self.config_dlg)
        hbox4.pack_start(butt3, False, 0, 2)

        butt3 = Gtk.Button.new_with_mnemonic(" Load Li_ve")
        butt3.set_tooltip_text("Load votes from Live server directory")
        butt3.connect("clicked", self.load_live_vote)
        hbox4.pack_start(butt3, False, 0, 2)

        butt3 = Gtk.Button.new_with_mnemonic(" Lo_ad ")
        butt3.set_tooltip_text("Load votes")
        butt3.connect("clicked", self.load_vote)
        hbox4.pack_start(butt3, False, 0, 2)

        butt5 = Gtk.Button.new_with_mnemonic(" Ne_w ")
        butt5.set_tooltip_text("New Vote")
        butt5.connect("clicked", self.new_data)
        hbox4.pack_start(butt5, False, 0, 2)

        butt4 = Gtk.Button.new_with_mnemonic(" _Save ")
        butt4.set_tooltip_text("Save current vote to database")
        butt4.connect("clicked", self.save_data)
        hbox4.pack_start(butt4, False, 0, 2)

        butt3 = Gtk.Button.new_with_mnemonic(" _Delete ")
        butt3.set_tooltip_text("Delete current vote from database")
        butt3.connect("clicked", self.del_vote)
        hbox4.pack_start(butt3, False, 0, 2)

        butt2 = Gtk.Button.new_with_mnemonic(" E_xit ")
        butt2.set_tooltip_text("Exit program")
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

        tp3x = ("User / Client UUID: ", "uuid", "Load / Select Client UUID", None)
        butt1 = Gtk.Button.new_with_mnemonic("Load vote_r")
        butt2 = Gtk.Button.new_with_mnemonic("Add")
        butt2.set_tooltip_text("Open in new window")
        hbox3x = Gtk.HBox()
        hbox3x.pack_start(butt1, 1,1,2)
        hbox3x.pack_start(butt2, 0,0,2)

        lab3x = pgentry.griddouble(self.gridx, 0, rowcnt, tp3x, hbox3x)
        butt1.connect("clicked", self.load_voter)
        butt2.connect("clicked", self.new_voter)
        self.dat_dict['nuuid'] = lab3x
        rowcnt += 1

        #self.gridx.attach(pggui.ySpacer(8), 0, rowcnt, 1, 1)
        #rowcnt += 1

        tp1 = ("Full Nam_e: ", "name", "Autofilled, full name (TAB to advance)", None)
        tp2 = ("Date o_f birth: ", "ndob", "Autofilled, Date of birth, YYYY/MM/DD", None)
        lab1, lab2 = pgentry.gridquad(self.gridx, 0, rowcnt,  tp1, tp2, None)
        lab1.set_gray(True);  lab2.set_gray(True)
        self.dat_dict['name'] = lab1
        self.dat_dict['ndob'] = lab2
        rowcnt += 1

        tp9b = ("Date of entry:","nnow",  "Autofilled, date of entry", None)
        tp10b = ("Entered by:", "noper", "Autofilled, Operator, who entered this voter.", None)
        lab15, lab16 = pgentry.gridquad(self.gridx, 0, rowcnt, tp9b, tp10b, None)
        lab15.set_gray(True);  lab16.set_gray(True)

        #lab15.set_editable(False);   lab16.set_editable(False);

        self.dat_dict['nnow'] = lab15
        self.dat_dict['noper'] = lab16
        rowcnt += 1

        # ----------------------------------------------------------------

        #rowcnt += 1
        frame = Gtk.Frame()
        self.gridx.attach(frame, 1, rowcnt, 3, 1)
        rowcnt += 1

        tp4z = ("Vote UUID: ", "uuid", "Vote UID", None)
        butt2z = Gtk.Button.new_with_mnemonic("Load")
        lab4z = pgentry.griddouble(self.gridx, 0, rowcnt, tp4z, butt2z)
        butt2z.connect("clicked", self.load_vote_uuid, lab4z)
        self.dat_dict['uuid'] = lab4z
        rowcnt += 1

        tp4x = ("Site GUID: ", "guid", "Group / Site UID", None)
        butt2 = Gtk.Button.new_with_mnemonic("Load")
        lab4x = pgentry.griddouble(self.gridx, 0, rowcnt, tp4x, butt2)
        butt2.connect("clicked", self.load_site_uuid, lab4x)
        #lab4x.set_editable(False);
        self.dat_dict['vguid'] = lab4x
        rowcnt += 1

        tp6x = ("Operator UUID: ", "ouid", "Operator UUID", None)
        butt2 = Gtk.Button.new_with_mnemonic("Load")
        lab6x = pgentry.griddouble(self.gridx, 0, rowcnt, tp6x, butt2)
        butt2.connect("clicked", self.load_op_uuid, lab6x)
        #lab6x.set_editable(False);
        self.dat_dict['vouid'] = lab6x
        rowcnt += 1

        butt2o = Gtk.Button.new_with_mnemonic("Load")
        tp9b = ("Now: (date of entry)","now",  "Autofilled, date of entry", None)
        tp10b = ("Operator:", "voper", "Autofilled, Operator, who entered this record.", None)
        lab15, lab16 = pgentry.gridquad(self.gridx, 0, rowcnt, tp9b, tp10b, butt2o)
        lab15.set_gray(False);   lab16.set_gray(False);
        butt2o.connect("clicked", self.load_op_name, lab16, lab15)
        rowcnt += 1

        self.dat_dict['now'] = lab15
        self.dat_dict['voper'] = lab16

        # ----------------------------------------------------------------

        frame = Gtk.Frame()
        self.gridx.attach(frame, 1, rowcnt, 3, 1)
        rowcnt += 1

        butt1 = Gtk.Button.new_with_mnemonic("Load _Ballot")
        butt2 = Gtk.Button.new_with_mnemonic("Add")
        butt2.set_tooltip_text("Open in new window")
        hbox4x = Gtk.HBox()
        hbox4x.pack_start(butt1, 1,1,2)
        hbox4x.pack_start(butt2, 0,0,2)

        tpb = ("Ballot UUID: ", "bbuid", "Load new Ballot. (if not pre loaded)", "")
        lab3b = pgentry.griddouble(self.gridx, 0, rowcnt, tpb, hbox4x)
        butt1.connect("clicked", self.load_ballot)
        butt2.connect("clicked", self.new_ballot)
        self.dat_dict['buuid'] = lab3b
        rowcnt += 1

        tp1x = ("Ballot Name: ", "bname", "Autofilled, Ballot Name", None)
        tp2x = ("Election Date: ", "dob", "Autofilled, Election Date, YYYY/MM/DD", None)
        lab1b, lab2b = pgentry.gridquad(self.gridx, 0, rowcnt,  tp1x, tp2x, None)
        lab1b.set_gray(True);  lab2b.set_gray(True)
        self.dat_dict['bname'] = lab1b
        self.dat_dict['dob'] = lab2b   # Date of birth -- for the vote (reuse field)
        rowcnt += 1

        # Create table from updated fields
        self.cand_dict = {}
        for aa in range(9):
            candidx = "can%d" % (aa)
            self.cand_dict[candidx] = Gtk.Entry()

        #print("cand_dict", self.cand_dict.keys())
        #for aa in self.cand_dict:
        #    aa.connect("focus-out-event", self.lost_focus)

        self.candstr =  [\
            "None", ]
        for aa in range(8):
            self.candstr.append("Candidate %d" % (aa + 1))

        #print("candstr:", self.candstr)
        #print("cand_dict:", self.candstr)

        self.labrow = rowcnt
        rowcnt = self.preview()

        tp7 = ("Primary Vote: ", "pri", "Select primary vote", None)
        tp8 = ("Secondary vote: ", "sec", "Write in secondary vote. (if applicable)", None)
        lab9, lab10 = pgentry.gridquad(self.gridx, 0, rowcnt, tp7, tp8)
        lab9.set_gray(True)
        self.dat_dict['vprim'] = lab9
        self.dat_dict['vsec']  = lab10
        rowcnt += 1

        tp6x = ("Vote Notes: ", "",
            "Text for vote. Press Alt-S to save vote, Shift-Enter to advance field", None)
        lab6x = pgentry.gridsingle(self.gridx, 0, rowcnt, tp6x)
        self.dat_dict['vnotes'] = lab6x
        rowcnt += 1

        frame = Gtk.Frame()
        self.gridx.attach(frame, 1, rowcnt, 3, 1)
        rowcnt += 1

        # ----------------------------------------------------------------

        # Create snapshot
        for aa in self.dat_dict.keys():
            self.dat_dict_org[aa] = self.dat_dict[aa].get_text()

        #pggui.set_testmode(1)
        vbox.pack_start(pggui.ySpacer(4), 0, 0, 0)
        sumx.pack_start(Gtk.Label("   "), 0, 0, 0)
        sumx.pack_start(self.gridx, 1, 1, 0)
        sumx.pack_start(Gtk.Label("   "), 0, 0, 0)

        #vbox.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#aaaaff"))

        vbox.pack_start(sumx, 1, 1, 2)
        vbox.pack_start(hbox4, False, 0, 2)

        self.preload_vote()
        if self.conf.playsound:
            self.conf.playsound.play_sound("")

        self.add(vbox)
        self.show_all()
        self.en_dis_all(False)
        GLib.timeout_add(100, self.start_pass_dlg, 0)
        #GLib.timeout_add(1000, self.timer)

    def config_dlg(self, arg2):
        print("Config")


    def load_ballot(self, arg2):

        # See if previous one saved
        #if self.is_changed():
        #    msg = "Unsaved data. Are you sure you want to abandon it?"
        #    self.status.set_status_text(msg)
        #    ret = pggui.yes_no(msg)
        #    #print("yes_no:", ret)
        #    if ret != Gtk.ResponseType.YES:
        #        return True
        #    else:
        #        #print("Abandoning", self.dat_dict['name'].get_text())
        #        pass

        heads = ["Voter Name", "Entry Date", "Voter BirthDate", "Vote UUID", ""]
        sss = recsel.RecSelDlg(self.bcore, self.acore, self.conf, headers=heads)
        if sss.response != Gtk.ResponseType.ACCEPT:
            return
        try:
            #dat = self.bcore.retrieve(sss.res[0][3])
            dat = self.bcore.get_rec(int(sss.res[0][4]))
        except:
            dat = []
            print("Get rec", sys.exc_info())
            pass
        if not dat:
            msg = "No data selected."
            #print(msg)
            self.status.set_status_text(msg)
            pymisc.smessage(msg)
            return
        #print("dat:", dat)
        try:
            #dec = self.packer.decode_data(dat[0][1])[0]
            dec = self.packer.decode_data(dat[1])[0]['PayLoad']

        except:
            dec = {}
            pass
        #print("ballot dec:", dec)

        # Assign to form
        self.dat_dict['buuid'].set_text(dec['uuid'])
        self.dat_dict['bname'].set_text(dec['name'])
        self.dat_dict['dob'].set_text(dec['dob'])
        self.dat_dict['vprim'].set_text("")
        self.dat_dict['vsec'].set_text("")

        for aa in range(1, 9):
            candidx = "can%d" % (aa)
            self.cand_dict[candidx].set_text(dec[candidx])

        # Voter data changed
        #self.reset_changed()
        self.preview()
        # Select the NONE entry
        self.noneradio.set_active(True)
        self.set_focus(self.noneradio)

    def preview(self):

        rowcnt = self.labrow
        #print("rowcnt", rowcnt)

        labv = Gtk.Label.new_with_mnemonic("Vo_te:   ")
        labv.set_alignment(1, 0)
        self.gridx.attach(labv, 0, rowcnt, 1, 1)

        def _checked(arg2):
            #print("Checked", arg2.get_active(), arg2.get_label())
            if arg2.get_active():
                txtx = arg2.textx #get_label()
                # Clear it to empty
                if txtx == "None":
                    txtx = ""
                if not self.oneshot:
                    self.dat_dict['vprim'].set_text(txtx)
                self.oneshot = False
                self.status.set_status_text("Selected: '%s'" % txtx)

        col = 0

        #print("cand:", self.candstr)

        self.randarr = [-1 for _ in range(len(self.cand_dict)-1)]

        # Limit it to actual data count:
        acnt = 0
        for aa in self.cand_dict:
            if self.cand_dict[aa].get_text():
                acnt += 1
        #print("acnt:", acnt)

        # Generate matching random index for
        if acnt == 0:
            lenx = len(self.cand_dict) - 1
        else:
            lenx = acnt

        cnt = 0
        # Shuffle
        while True:
            xx = random.randint(0, lenx-1)
            # Make sure it is unique
            if self.randarr[xx] != -1:
                continue
            self.randarr[xx] = cnt + 1
            cnt += 1
            # Are we done?
            if cnt >= lenx:
                break
        #print("rarr:", self.randarr)

        # Create the 'None' entry
        nnn = "None"
        rrr = self.gridx.get_child_at(col % 3 +  1, rowcnt)
        if not rrr:
            radiox = Gtk.RadioButton.new_with_label(None, nnn)
            radiox.connect("toggled", _checked)
            self.noneradio = radiox
            self.gridx.attach(radiox, col % 3 +  1, rowcnt, 1, 1)
        else:
            self.noneradio.textx = nnn
            self.noneradio.set_label(nnn)
        col += 1

        labv.set_mnemonic_widget(self.noneradio)

        # All others
        cnt = 0
        for cc in list(self.cand_dict.keys())[1:]:
            ccc = self.randarr[cnt]
            if ccc < 0:
                txtx =  ""
            else:
                candidx = "can%d" % (ccc)
                txtx = self.cand_dict[candidx].get_text()

            tooltip = "Click to activate selection."
            if len(txtx) > 24:
                bb = txtx[:24] + ".."
                tooltip = txtx
            else:
                if not txtx:
                    bb = "Candidate %d" % (col)
                else:
                    bb = txtx
            ccc = self.gridx.get_child_at(col % 3 +  1, rowcnt)
            if not ccc:
                radiox = Gtk.RadioButton.new_with_label(None, bb)
                radiox.set_tooltip_text(tooltip)
                radiox.textx = txtx
                radiox.connect("toggled", _checked)
                radiox.join_group(self.noneradio)
                self.gridx.attach(radiox, col % 3 +  1, rowcnt, 1, 1)
                ccc = radiox

                radidx = "can%d" % (cnt)
                self.radioarr[radidx] = radiox
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
            col += 1; cnt += 1
        #print("radioarr", self.radioarr)
        return rowcnt

    def config_dlg(self, arg2):
        #print("config_dlg")
        #print("pass prow:", self.powers)
        if self.powers != "Yes":
            pymisc.smessage("Only Admin can Configure.")
        else:
            config.ConfigDlg(self.vcore, self.hcore, self.acore, self.authcore, self.conf)

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
            recsel.audit(self.acore, self.packer, "Successful Login", ret[1][0])
            break

    def en_dis_all(self, flag):
        for aa in self.dat_dict.keys():
            self.dat_dict[aa].set_sensitive(flag)

    def is_changed(self, keyx = None):

        if not keyx:
            ccc = False
            for aa in self.dat_dict.keys():
                if self.dat_dict_org[aa] != self.dat_dict[aa].get_text():
                    ccc = True
        else:
            return self.dat_dict_org[keyx] != self.dat_dict[keyx].get_text()

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
            pymisc.smessage(msg)
            self.status.set_status_text(msg)
            return
        arg2.set_text(self.operator)
        #if arg3.get_text() == "":
        dd = datetime.datetime.now()
        dd = dd.replace(microsecond=0)
        arg3.set_text(dd.isoformat())

    def load_uuid(self, arg, arg2):
        if arg2.get_text() != "":
            msg = "Already has a UUID; Cannot set, clear it first."
            pymisc.smessage(msg)
            self.status.set_status_text(msg)
            return
        arg2.set_text(str(uuid.uuid1()))

    def load_op_uuid(self, arg, arg2):
        if arg2.get_text() != "":
            msg = "Already has a OUID; Cannot set, clear it first."
            pymisc.smessage(msg)
            self.status.set_status_text(msg)
            return
        arg2.set_text(self.ouid)

    def load_vote_uuid(self, arg, arg2):
        if arg2.get_text() != "":
            msg = "Already has a Vote UUID; Cannot set, clear it first."
            pymisc.smessage(msg)
            self.status.set_status_text(msg)
            return
        arg2.set_text(str(uuid.uuid1()))

    def load_site_uuid(self, arg, arg2):
        if arg2.get_text() != "":
            msg = "Already has a Site UUID; Cannot set, clear it first."
            pymisc.smessage(msg)
            self.status.set_status_text(msg)
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

    def config(self, arg):
        print("Config")

    def new_data(self, arg):

        # See if previous one saved
        if self.is_changed():
            msg = "Unsaved data. Are you sure you want to abandon it?"
            self.status.set_status_text(msg)
            ret = pggui.yes_no(msg, default="No")
            if ret != Gtk.ResponseType.YES:
                return True

        # Clear everything except the ballot
        for aa in self.dat_dict.keys():
            if aa == 'dob':
                pass
            elif aa == 'buuid':
                pass
            elif aa == 'bname':
                pass
            else:
                self.dat_dict[aa].set_text("")

        self.was_saved = False
        self.noneradio.set_active(True)
        self.set_focus(self.noneradio)
        self.preview()

        # Fill in defaults
        #dd = datetime.datetime.now().replace(microsecond=0)
        #self.dat_dict['vnow'].set_text(dd.isoformat())
        #self.dat_dict['vuuid'].set_text(str(uuid.uuid1()))
        #self.dat_dict['vguid'].set_text(str(self.conf.siteid))
        #self.dat_dict['vouid'].set_text(str(self.ouid))
        #self.dat_dict['voper'].set_text(str(self.operator))

        self.reset_changed()
        #self.set_focus(self.dat_dict['name'])

    def preload_vote(self):

        ''' Here we preload the last record, and carry over info
            for the potencial new record
        '''

        datsize = self.votecore.getdbsize()

        try:
            dat = self.votecore.get_rec(datsize-1)
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
            dec = self.packer.decode_data(dat[1])[0]['PayLoad']
        except:
            dec = {}
            pass
        #print("preload dec:", dec)

        # Assign preview to form
        self.dat_dict['buuid'].set_text(dec['buuid'])
        self.dat_dict['bname'].set_text(dec['bname'])
        self.dat_dict['dob'].set_text(dec['dob'])

        # Load candidates
        for aa in dec.keys():
            #print("Key:", aa[:3])
            try:
                if aa[:3] == "can":
                    #print("Cand", aa)
                    self.cand_dict[aa].set_text(dec[aa])
            except:
                pass
        self.preview()
        # Mark as non changed
        self.reset_changed()

    def load_live_vote(self, arg):

        ''' Load from storage '''

        # See if previous one saved
        if self.is_changed():
            msg = "Unsaved data. Are you sure you want to abandon it?"
            self.status.set_status_text(msg)
            ret = pggui.yes_no(msg, default="No")
            #print("yes_no:", ret)
            if ret != Gtk.ResponseType.YES:
                return True
            else:
                #print("Abandoning", self.dat_dict['name'].get_text())
                pass
        #print("live vote:")
        ret = filedlg.File_Dlg()
        #print("filedlg ret:", ret)
        if not ret:
            return

        self.livecore = twincore.TwinCore(ret[0], 0)
        self.livecore.packer = self.packer
        self.livecore.hashname  = os.path.splitext(self.votecore.fname)[0] + ".hash.id"
        self.livecore.hashname2 = os.path.splitext(self.votecore.fname)[0] + ".hash.name"

        heads = ["Voter Name", "Entry Date", "Election Date", "Vote UUID", ""]
        sss = recsel.RecSelDlg(self.livecore, self.acore, self.conf, headers=heads)
        if sss.response != Gtk.ResponseType.ACCEPT:
            return

        try:
            #dat = self.votecore.retrieve(sss.res[0][3])
            dat = self.votecore.get_rec(int(sss.res[0][4]))
        except:
            dat = []
            print(sys.exc_info())
            pass
        if not dat:
            msg = "No data selected."
            #print(msg)
            self.status.set_status_text(msg)
            pymisc.smessage(msg)
            return
        #print("dat:", dat)
        try:
            dec = self.packer.decode_data(dat[1])[0]['PayLoad']
        except:
            dec = {}
            pass
        #print("dec:", dec)
        for aa in dec.keys():
            #print("Key:", aa[:3])
            try:
                if aa[:3] == "can":
                    #print("Cand", aa)
                    self.cand_dict[aa].set_text(dec[aa])
                self.dat_dict[aa].set_text(dec[aa])
            except:
                pass
        self.preview()


    def load_vote(self, arg):

        ''' Load from storage '''

        # See if previous one saved
        if self.is_changed():
            msg = "Unsaved data. Are you sure you want to abandon it?"
            self.status.set_status_text(msg)
            ret = pggui.yes_no(msg, default="No")
            #print("yes_no:", ret)
            if ret != Gtk.ResponseType.YES:
                return True
            else:
                #print("Abandoning", self.dat_dict['name'].get_text())
                pass

        heads = ["Voter Name", "Entry Date", "Election Date", "Vote UUID", ""]
        sss = recsel.RecSelDlg(self.votecore, self.acore, self.conf, headers=heads)
        if sss.response != Gtk.ResponseType.ACCEPT:
            return
        #print("sss.res:", sss.res)
        try:
            #dat = self.votecore.retrieve(sss.res[0][3])
            dat = self.votecore.get_rec(int(sss.res[0][4]))
        except:
            dat = []
            print(sys.exc_info())
            pass
        if not dat:
            msg = "No data selected."
            #print(msg)
            self.status.set_status_text(msg)
            pymisc.smessage(msg)
            return
        #print("dat:", dat)
        try:
            dec = self.packer.decode_data(dat[1])[0]['PayLoad']
        except:
            dec = {}
            pass
        #print("dec:", dec)
        for aa in dec.keys():
            #print("Key:", aa[:3])
            try:
                if aa[:3] == "can":
                    #print("Cand", aa)
                    self.cand_dict[aa].set_text(dec[aa])
                self.dat_dict[aa].set_text(dec[aa])
            except:
                pass
        self.preview()

        # Select matching entry:
        cntc = 0
        cc = self.dat_dict['vprim'].get_text()
        #print("anchor:", cc)
        for aa in range(len(self.cand_dict)-1):  #.keys():
            candidx = "can%d" % (self.randarr[cntc])
            bb = self.cand_dict[candidx].get_text()
            if bb == cc:
                #print("found bb:", bb, "ref:", aa)
                posidx = "can%d" % (aa)
                self.oneshot = True
                self.radioarr[posidx].set_active(True)
                #break
            cntc += 1

        # Mark as non changed (disabled)
        self.reset_changed()

        # Cannot change, would be duplicate upload
        self.was_saved = True

        msg = "Loaded vote: '%s'" % dec['name']
        self.status.set_status_text(msg)
        #self.status.set_status_text("Loaded:", dec['name'])

    def del_vote(self, arg):

        ''' Delete currently active data '''

        nnn = self.dat_dict['name'].get_text()
        if not nnn:
            msg = "Empty record, cannot delete."
            self.status.set_status_text(msg)
            pymisc.smessage(msg)
            return

        msg = "This will delete vote from: '%s'.\nAre you sure?" % nnn
        ret = pggui.yes_no(msg , default="No")
        if ret != Gtk.ResponseType.YES:
            return True

        ddd = self.dat_dict['uuid'].get_text().encode()
        #print("delete:", ddd)
        ddd2 = []
        # Find it via sequential
        #datasize = self.votecore.getdbsize()
        #for aa in range(datasize -1, -1, -1):
        #    rrr = self.votecore.get_rec(aa)
        #    if not rrr:
        #        continue
        #    try:
        #        dec = self.packer.decode_data(rrr[1])[0]
        #    except:
        #        #print("Cannot decode:", rrr)
        #        dec = [0]
        #    #print("dec:", rrr[0], dec['uuid'])
        #    if rrr[0] == ddd:
        #        print("Found:", rrr[0])
        #        ddd2.append(aa)

        # Find it via index
        ddd2 = recsel.search_index(self.votecore, self.votecore.hashname, ddd, recsel.hashid)

        for aa in ddd2:
            #print("deleting:", aa)
            try:
                rrr = self.votecore.get_rec(aa)
                ret = self.votecore.del_rec(aa)
                #print(aa, "del ret:", ret)
                recsel.audit(self.acore, self.packer, "Deleted Record", rrr[1])
                self.status.set_status_text("Record '%s' deleted." % nnn)
            except:
                print(sys.exc_info())

        # Clear, reset
        self.clear_data()
        self.reset_changed()

    def new_ballot(self, arg):
        exe = os.path.join(os.path.dirname(__file__), "..", "pyvballot.py")
        #print(exe)
        ret = subprocess.run([exe, ], capture_output=True)
        #print("Back to ", ret)

    def new_voter(self, arg):
        exe = os.path.join(os.path.dirname(__file__), "..", "pyvpeople.py")
        #print(exe)
        ret = subprocess.run([exe, ], capture_output=True)
        #print("Back to ", ret)

    def load_voter(self, arg):

        ''' Load new voter '''

        # See if not empty, let the user know
        if self.dat_dict['nuuid'].get_text():
            msg = "This record already has a voter. Please create a new record."
            self.status.set_status_text(msg)
            ret = pymisc.smessage(msg)
            return True

        # See if previous one saved
        if self.is_changed("nuuid"):
            msg = "Unsaved data. Are you sure you want to abandon it?"
            self.status.set_status_text(msg)
            ret = pggui.yes_no(msg, default="No")
            #print("yes_no:", ret)
            if ret != Gtk.ResponseType.YES:
                return True
            else:
                #print("Abandoning", self.dat_dict['name'].get_text())
                pass

        heads = ["Voter Name", "Date", "Voter BirthDate", "Voter UUID", ""]
        sss = recsel.RecSelDlg(self.vcore, self.acore, self.conf, headers=heads)
        if sss.response != Gtk.ResponseType.ACCEPT:
            return
        #print("sss.res:", sss.res)
        try:
            #dat = self.votecore.retrieve(sss.res[0][3])
            dat = self.vcore.get_rec(int(sss.res[0][4]))
        except:
            dat = []
            print(sys.exc_info())
            pass
        if not dat:
            msg = "No data selected."
            #print(msg)
            self.status.set_status_text(msg)
            pymisc.smessage(msg)
            return
        #print("dat:", dat)
        try:
            dec = self.packer.decode_data(dat[1])[0]['PayLoad']
        except:
            dec = {}
            pass
        #print("dec:", dec)
        #for aa in dec.keys():
        #    print("Key:", aa)

        self.was_saved = False

        # Partial fill, redirect fields
        self.dat_dict['nuuid'].set_text(dec['uuid'])
        self.dat_dict['name'].set_text(dec['name'])
        self.dat_dict['ndob'].set_text(dec['dob'])
        self.dat_dict['nnow'].set_text(dec['now'])
        self.dat_dict['noper'].set_text(dec['oper'])

        #for aa in dec.keys():
        #    try:
        #        self.dat_dict[aa].set_text(dec[aa])
        #    except:
        #        pass

        # Mark as non changed (disabled)
        #self.reset_changed()

        msg = "Loaded voter: '%s'" % dec['name']
        self.status.set_status_text(msg)
        #self.status.set_status_text("Loaded:", dec['name'])

    def test_data(self, arg1):

        buuid = self.dat_dict['buuid'].get_text()
        if not buuid:
            msg = "Must have a ballot loaded for tests."
            self.status.set_status_text(msg)
            self.set_focus(self.dat_dict['dob'])
            pymisc.smessage(msg)
            return

        # Disable sound
        sps = self.conf.playsound
        self.conf.playsound = None
        self.stop = not self.stop
        while True:
            #print("test cycle started")
            if self.exit_flag:
                self.reset_changed()
                break
            if self.stop:
                self.reset_changed()
                self.status.set_status_text("Test Stopped")
                break
            for aa in self.dat_dict.keys():
                # Handle differences in data
                if "buuid" == aa:
                    pass                # Do not change ballot fields
                elif "bname" == aa:
                    pass                # Do not change ballot fields
                elif "dob" == aa:
                    pass                # Do not change ballot fields
                elif "uid" in str(aa):
                   self.dat_dict[aa].set_text(str(uuid.uuid1()) )
                elif aa == 'name':
                   self.dat_dict[aa].set_text(pgtests.simname(random.randint(12, 22)))
                elif aa == 'dob':
                    self.dat_dict[aa].set_text(pgtests.randate())
                elif aa == 'ndob':
                    self.dat_dict[aa].set_text(pgtests.randate())
                elif aa == 'now':
                    self.dat_dict[aa].set_text(pgtests.randisodate())
                elif aa == 'vnotes':
                    self.dat_dict[aa].set_text(pgtests.randascii(random.randint(33, 66)))
                elif aa == 'vprim':
                    # Select from candidates
                    lenx = len(self.cand_dict)-1
                    # Shuffle
                    xrandarr = [-1 for _ in range(len(self.cand_dict)-1)]
                    cnt = 0
                    while True:
                        xx = random.randint(0, lenx-1)
                        # Make sure it is unique
                        if xrandarr[xx] != -1:
                            continue
                        xrandarr[xx] = cnt + 1
                        cnt += 1
                        # Are we done?
                        if cnt >= lenx:
                            break
                    rx = random.randint(0, lenx-1)

                    for bb in range(0, lenx-1):
                        candidx = "can%d" % (xrandarr[bb])
                        cc = self.cand_dict[candidx].get_text()
                        if rx == bb:
                            #print("sel:", cc)
                            self.dat_dict[aa].set_text(cc)
                            break
                    # Select matching entry:
                    cntc = 0
                    cc = self.dat_dict['vprim'].get_text()
                    for aa in range(len(self.cand_dict)-1):  #.keys():
                        candidx = "can%d" % (xrandarr[cntc])
                        bb = self.cand_dict[candidx].get_text()
                        if bb == cc:
                            #print("found bb:", bb, "candidx =",  candidx, "ref:", aa)
                            posidx = "can%d" % (aa)
                            self.oneshot = True
                            self.radioarr[posidx].set_active(True)
                            self.dat_dict['vprim'].set_text(bb)
                            #break
                        cntc += 1
                else:
                    # Just fill in something
                    self.dat_dict[aa].set_text(pgtests.randstr(random.randint(6, 22)))
            #break

            pgutils.usleep(10)
            if not self.save_data(0):
                break

            sleepx = 20
            pgutils.usleep(sleepx)

            #print("test cycle ended")

            # Do not clear, we want ballot
            #self.clear_data()

        self.conf.playsound = sps

    def save_data(self, arg1):

        ''' See if data changed, save_vote '''

        if not self.is_changed():
            msg = "Nothing changed, cannot save."
            self.status.set_status_text(msg)
            pymisc.smessage(msg, conf=self.conf, sound="error")
            return

        if self.was_saved:
            msg = "This record has been saved already, cannot duplicate.\n" \
                        "Please create a new record instead."
            self.status.set_status_text(msg)
            pymisc.smessage(msg, conf=self.conf, sound="error")
            return

        if not self.dat_dict['nuuid'].get_text():
            msg = "Must have a Voter UUID."
            self.status.set_status_text(msg)
            self.set_focus(self.dat_dict['nuuid'])
            pymisc.smessage(msg)
            return

        if not self.dat_dict['name'].get_text():
            msg = "Must have a Voter name."
            self.status.set_status_text(msg)
            self.set_focus(self.dat_dict['nuuid'])
            pymisc.smessage(msg)
            return

        ndob = self.dat_dict['ndob'].get_text()
        if not ndob or len(ndob.split("/")) < 3:
            msg = "Must have a valid Voter date of birth. (yyyy/mm/dd)"
            self.status.set_status_text(msg)
            self.set_focus(self.dat_dict['nuuid'])
            pymisc.smessage(msg)
            return

        buuid = self.dat_dict['buuid'].get_text()
        if not buuid:
            msg = "Must have a ballot loaded."
            self.status.set_status_text(msg)
            self.set_focus(self.dat_dict['buuid'])
            pymisc.smessage(msg)
            return

        # Commemorate the event by setting a fresh date
        #if  self.dat_dict['now'].get_text() == "":
        dd = datetime.datetime.now()
        dd = dd.replace(microsecond=0)
        self.dat_dict['now'].set_text(dd.isoformat())

        # Autofill what we can
        #dd = datetime.datetime.now().replace(microsecond=0)
        #self.dat_dict['vnow'].set_text(dd.isoformat())

        if self.dat_dict['uuid'].get_text() == "":
            self.dat_dict['uuid'].set_text(str(uuid.uuid1()))

        # These are constant, save them
        if self.dat_dict['vguid'].get_text() == "":
            self.dat_dict['vguid'].set_text(str(self.conf.siteid))
        if self.dat_dict['vouid'].get_text() == "":
            self.dat_dict['vouid'].set_text(str(self.ouid))
        if self.dat_dict['voper'].get_text() == "":
            self.dat_dict['voper'].set_text(str(self.operator))

        # Check if IDs are in order:
        checklist = ("nuuid", "uuid", "vguid", "vouid", "buuid")
        for aa in checklist:
            try:
                uuu = uuid.UUID(self.dat_dict[aa].get_text())
            except:
                msg = "Invalid '" + aa.upper() + "' please correct."
                self.status.set_status_text(msg)
                self.set_focus(self.dat_dict[aa])
                pymisc.smessage(msg)
                return

        if not self.dat_dict['vprim'].get_text():
            msg = "Must have at least a primary vote."
            self.status.set_status_text(msg)
            self.set_focus(self.dat_dict['vprim'])
            pymisc.smessage(msg, conf=self.conf, sound="error")
            return

        ddd = {}
        for aa in self.dat_dict.keys():
            ddd[aa] = self.dat_dict[aa].get_text()

        # Save Ballot as well:
        for aa in list(self.cand_dict.keys())[1:]:
            ddd[aa] = self.cand_dict[aa].get_text()

        pvh = pyvhash.BcData(header = self.dat_dict['uuid'].get_text())

        # We mark this as 'test' so it can stay in the chain, if desired
        #pvh.addpayload({"Test": "test" ,})
        pvh.addpayload(ddd)

        pvh.hasharr()
        if self.conf.weak:
            pvh.num_zeros = 1

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

        enc = self.packer.encode_data("", pvh.datax)

        #print("enc:", enc)
        uuu = self.dat_dict['uuid'].get_text()

        #print("Save_data", uuu, ddd)

        # Add indices
        def callb2(c2, id2):
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
                support.put_exception("save callb name")
        try:
            self.votecore.postexec = callb2
            ret = self.votecore.save_data(uuu, enc)
        except:
            print("exc save", sys.exc_info())
        finally:
            self.votecore.postexec = None

        # Save replicator
        ttt = time.time()
        dd = datetime.datetime.fromtimestamp(ttt)
        idt = dd.isoformat()
        now = dd.strftime(pyvhash.datefmt)

        #self.dat_dict['now'].get_text(),

        # Prepare data. Do strings so it can be re-written in place
        rrr = {
                'header' : uuu,
                'now' : now,
                # Human readable
                'iso' : idt,
                'stamp' : ttt,
                "processed" : "00000",
                }

        #print("replic req", rrr)

        undec2 = self.packer.encode_data("", rrr)

        votedir = os.path.join(pyservsup.globals.chaindir, "vote")
        frname = os.path.join(votedir, pyservsup.REPFNAME + ".pydb")
        #print("Saving replicator at", frname)
        repcore = twincore.TwinCore(frname, 0)

        try:
            ret = repcore.save_data(uuu, undec2)
        except:
            del repcore
            print("exc on save_data", sys.exc_info()[1])
            response = [ERR,  "Cannot save replicator.",  str(sys.exc_info()[1]) ]
            support.put_exception("save_data")
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return
        del repcore

        if self.conf.playsound:
            self.conf.playsound.play_sound("shutter")

        self.status.set_status_text("Saved '%s'" % self.dat_dict['name'].get_text())

        self.was_saved = True

        for aa in self.dat_dict.keys():
            self.dat_dict_org[aa] = self.dat_dict[aa].get_text()
        return True

    def main(self):
        Gtk.main()

    def  OnExit(self, arg, srg2 = None):

        if self.is_changed():
            msg = "Unsaved data. Are you sure you want to abandon it?"
            self.status.set_status_text(msg)
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
