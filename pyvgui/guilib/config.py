#!/usr/bin/env python

''' Login and configure dialogs '''

# pylint: disable=C0103

import os
import sys
import datetime
import time
import uuid
import io
import struct
import base64

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GdkPixbuf

import pyvpacker
from pydbase import twincore, twinchain

from pyvguicom import pggui
from pyvguicom import pgsel
from pyvguicom import pgutils
from pyvguicom import pgentry

from pyvcommon import pyvhash

import passdlg, recsel, pymisc

class Blank(): pass

class ConfigDlg(Gtk.Dialog):

    '''
        The config dialog.
    '''

    def __init__(self, vcore, repcore, acore, authcore, conf):
        super().__init__(self)

        self.set_title("Configuration")
        self.set_modal(True)

        self.add_buttons(Gtk.STOCK_CLOSE, Gtk.ResponseType.ACCEPT)
        self.set_size_request(800, 600)
        self.conf = conf
        self.alt = False
        self.xmulti = []
        self.vcore = vcore
        self.repcore = repcore
        self.acore = acore
        self.authcore = authcore
        self.packer = pyvpacker.packbin()
        self.rec_cnt = 0
        self.scan_cnt = 0
        self.stop = False
        self.w_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self.sort_cnt = 0
        #self.vbox = self.get_content_area()
        self.cells = []

        self.model = Gtk.TreeStore(str, str, str, str, str, str, str)
        self.tview = self.create_ftree(self.model)
        scroll = Gtk.ScrolledWindow()
        self.tview.connect("row-activated",  self.tree_sel)
        self.tview.connect("button-press-event",  self.tree_butt, self.tview)
        self.tview.connect("key-press-event", self.onTreeNavigateKeyPress)

        scroll.add(self.tview)

        frame2 = Gtk.Frame()
        frame2.add(scroll)

        self.vbox3 = Gtk.VBox()

        try:
            ic = Gtk.Image(); ic.set_from_file(conf.iconf2) #"pyvvote_sub.png")
            self.set_icon(ic.get_pixbuf())
        except:
            pass

        self.connect("key-press-event", self.area_key)
        self.connect("key-release-event", self.area_key)

        pbox = Gtk.HBox()
        pbox.pack_start(pggui.xSpacer(), 1, 1, 4)
        pbox.pack_start(Gtk.Label(" Site ID: "), 0, 0, 4)
        pbox.pack_start(Gtk.Label(conf.siteid), 0, 0, 4)
        pbox.pack_start(pggui.xSpacer(), 1, 1, 4)
        self.vbox3.pack_start(pbox, 0, 0, 0)

        hbox4 = Gtk.HBox()
        hbox4.pack_start(pggui.xSpacer(), 1, 1, 2)
        hbox4.pack_start(Gtk.Label("Edit user / admin entries on tree control below. Tab key to advance."), 0, 0, 2)
        hbox4.pack_start(pggui.xSpacer(), 1, 1, 2)
        self.vbox3.pack_start(hbox4, 0, 0, 4)

        gridx = Gtk.Grid()
        gridx.set_column_spacing(6)
        gridx.set_row_spacing(6)
        rowcnt = 0
        hbox4 = Gtk.HBox()

        self.vbox3.pack_start(hbox4, 0, 0, 4)
        self.vbox3.pack_start(frame2, 1, 1, 4)

        hbox3 = Gtk.HBox()

        hbox3.pack_start(pggui.xSpacer(), 1, 1, 2)
        butt2 = Gtk.Button.new_with_mnemonic(" _Add new Admin ")
        butt2.connect("clicked", self.add_admin)
        hbox3.pack_start(butt2, 0, 0, 2)
        butt3 = Gtk.Button.new_with_mnemonic(" Add ne_w User ")
        hbox3.pack_start(butt3, 0, 0, 2)
        butt3.connect("clicked", self.add_user)
        butt5 = Gtk.Button.new_with_mnemonic(" _Toggle Enable flag ")
        butt5.connect("clicked", self.toggle_enable)
        hbox3.pack_start(butt5, 0, 0, 2)
        butt6 = Gtk.Button.new_with_mnemonic(" Delete Selected User ")
        butt6.connect("clicked", self.del_user)
        hbox3.pack_start(butt6, 0, 0, 2)
        hbox3.pack_start(pggui.xSpacer(), 1, 1, 4)
        self.vbox3.pack_start(hbox3, 0, 0, 4)
        self.vbox.pack_start(self.vbox3, 1, 1, 4)
        self.abox = self.get_action_area()

        hbox4 = Gtk.HBox()
        hbox4.pack_start(pggui.xSpacer(), 1, 1, 2)
        lab3 = Gtk.Label.new_with_mnemonic(\
                        "_Edit replication Host / Port on the tree control below. Tab key to advance.")
        hbox4.pack_start(lab3, 0, 0, 2)

        hbox4.pack_start(pggui.xSpacer(), 1, 1, 2)
        self.vbox3.pack_start(hbox4, 0, 0, 4)

        self.model2 = Gtk.TreeStore(str, str, str, str)
        self.tview2 = self.create_ftree2(self.model2)
        lab3.set_mnemonic_widget(self.tview2)

        scroll2 = Gtk.ScrolledWindow()
        self.tview2.connect("row-activated",  self.tree_sel)
        self.tview2.connect("button-press-event",  self.tree_butt, self.tview2)
        self.tview2.connect("key-press-event", self.onTreeNavigateKeyPress)

        scroll2.add(self.tview2)
        frame22 = Gtk.Frame()
        frame22.add(scroll2)

        hbox32 = Gtk.HBox()

        hbox32.pack_start(pggui.xSpacer(), 1, 1, 2)
        butt2 = Gtk.Button.new_with_mnemonic(" Add new Ho_st ")
        butt2.connect("clicked", self.add_host)
        hbox32.pack_start(butt2, 0, 0, 2)

        butt6 = Gtk.Button.new_with_mnemonic(" Delete Host ")
        butt6.connect("clicked", self.del_host)
        hbox32.pack_start(butt6, 0, 0, 2)
        hbox32.pack_start(pggui.xSpacer(), 1, 1, 4)

        self.vbox3.pack_start(frame22, 1, 1, 4)
        self.vbox3.pack_start(hbox32, 0, 0, 4)

        self.vbox.pack_start(self.vbox3, 1, 1, 4)
        self.abox = self.get_action_area()


        # Load date after presenting
        GLib.timeout_add(100, self.loaddata)
        self.show_all()
        self.response = self.run()
        # No return value processed
        self.res = [Gtk.ResponseType.ACCEPT, "", ""]
        if self.response == Gtk.ResponseType.ACCEPT:
            pass
        self.destroy()

    def toggle_enable(self, arg2):
        #print("toggle_enable")
        sel = self.tview.get_selection()
        xmodel, xpath = sel.get_selected_rows()
        if not xpath:
            return
        for aa in xpath:
            xiter2 = xmodel.get_iter(aa)
            xstr = xmodel.get_value(xiter2, 0)
            xid = xmodel.get_value(xiter2, 5)
            #print("Toggle", xstr, xid)
            lll = self.authcore.find_key(xid)
            #print("lll", lll)
            for aa in lll:
                rrr = self.authcore.get_rec_byoffs(aa)
                dec = self.packer.decode_data(rrr[1])[0]
                if dec[2] == "Enabled":
                    dec[2] = "Disabled"
                else:
                    dec[2] = "Enabled"

                dd = datetime.datetime.now().replace(microsecond=0)
                dec[3] = dd.isoformat()
                # Make sure it is not tempered with
                dec = dec[:-1]
                hhh = SHA256.new();
                hhh.update(bytes(str(dec), "utf-8"))
                dec.append(hhh.hexdigest())
                #print("toggled rrr", dec)
                try:
                    enc = self.packer.encode_data("", dec)
                except:
                    print("packer", sys.exc_info())
                    enc = ""
                    pass
                self.authcore.save_data(rrr[0], enc)
                recsel.audit(self.acore, self.packer, "Toggled Enable flag to:", rrr[1])
                break
            # Relaad screen
            iters = []
            iterx = self.model.get_iter_first()
            while True:
                if not iterx:
                    break
                iters.append(iterx)
                iterx = self.model.iter_next(iterx)
            for aa in iters:
                self.model.remove(aa)
            self.loaddata()
            break

    def del_user(self, arg2):
        #print("Del user")
        sel = self.tview.get_selection()
        xmodel, xpath = sel.get_selected_rows()
        if not xpath:
            return

        for aa in xpath:
            xiter2 = xmodel.get_iter(aa)
            xstr = xmodel.get_value(xiter2, 0)
            xid = xmodel.get_value(xiter2, 5)
            #print("Delete", xstr, xid)
            msg = "About to delete user: '%s' \nAre you sure?" % xstr
            ret = pggui.yes_no(msg, default="No")
            if ret != Gtk.ResponseType.YES:
                return True
            try:
                lll = self.authcore.find_key(xid)
                #print("lll", lll)
                # Delete all occurances
                for aa in lll:
                    rrr = self.authcore.get_rec_byoffs(aa)
                    dec = self.packer.decode_data(rrr[1])[0]
                    uuu = rrr[0].decode()
                    self.authcore.del_rec_offs(aa)
                    #print("del rrr", rrr)
                    recsel.audit(self.acore, self.packer, "Deleted User", rrr[1])

            except:
                print("exc on delrec,", sys.exc_info())
                pgutils.put_exception("del_user")

            # Remove from displayed list
            iterx = self.model.get_iter_first()
            while True:
                if not iterx:
                    break
                xstr = self.model.get_value(iterx, 5)
                #print("xstr:", xstr)
                if xstr == xid:
                    try:
                        self.model.remove(iterx)
                    except:
                        print("Exception on del from tree", sys.exc_info())
                    break
                iterx = self.model.iter_next(iterx)
            break

    def del_host(self, arg2):
        #print("Del host")
        sel = self.tview2.get_selection()
        xmodel, xpath = sel.get_selected_rows()
        if not xpath:
            return

        for aa in xpath:
            xiter2 = xmodel.get_iter(aa)
            xstr = xmodel.get_value(xiter2, 0) + ":" + \
                        xmodel.get_value(xiter2, 1)
            xid = xmodel.get_value(xiter2, 3)
            print("Delete", xstr, xid)

            msg = "About to delete host: '%s' \nAre you sure?" % xstr
            ret = pggui.yes_no(msg, default="No")
            if ret != Gtk.ResponseType.YES:
                return True
            try:
                lll = self.repcore.find_key(xid)
                #print("lll", lll)
                # Delete all occurances
                for aa in lll:
                    rrr = self.repcore.get_rec_byoffs(aa)
                    #print("rrr:", rrr)
                    try:
                        dec = self.packer.decode_data(rrr[1])[0]['PayLoad']
                    except:
                        dec = {}
                    #print("dec", dec)
                    ret = self.repcore.del_rec_offs(aa)
                    #print("del host",  ret, dec['host'])
                    recsel.audit(self.acore, self.packer, "Deleted Host", dec['host'])
            except:
                print("exc on delhost,", sys.exc_info())
                pgutils.put_exception("del_host")

            # Remove from displayed list
            iterx = self.model2.get_iter_first()
            while True:
                if not iterx:
                    break
                xstr = self.model2.get_value(iterx, 3)
                #print("xstr:", xstr)
                if xstr == xid:
                    try:
                        self.model2.remove(iterx)
                    except:
                        print("Exception on del from tree", sys.exc_info())
                    break
                iterx = self.model2.iter_next(iterx)
            break

    def create_menuitem(self, string, action, arg = None):
        rclick_menu = Gtk.MenuItem(string)
        if action:
            rclick_menu.connect("activate", action, string, arg)
        rclick_menu.show()
        return rclick_menu

    def toggle_rec(self, arg2, arg3, textx):

        #print("Toggle rec", arg2, arg3, textx)
        self.toggle_enable(0)

    def del_rec(self, arg2, arg3, textx):

        ''' Delete record driven by menu interface '''
        #print("Del rec", arg2, arg3, textx)
        self.del_user(0)

    def loaddata(self):
        ddd2 = []
        datasize = self.authcore.getdbsize()
        for aa in range(datasize -1, -1, -1):
            rrr = self.authcore.get_rec(aa)
            if not rrr:
                continue
            try:
                dec = self.packer.decode_data(rrr[1])[0]
            except:
                print("Cannot read", sys.exc_info(), rrr)
                dec = [0]
            try:
                if not dec[0] in ddd2:
                    #print("dec", dec)
                    # Check:
                    hhh = SHA256.new();
                    hhh.update(bytes(str(dec[:-1]), "utf-8"))
                    #print("sums:", hhh.hexdigest(), dec[-1])
                    if hhh.hexdigest() != dec[-1]:
                        print("Bad sum on:", dec[0], aa)
                    else:
                        self.model.append(None, dec[:-1])
                        ddd2.append(dec[0])
            except:
                pass

        # load host data as well
        ddd3 = []
        repsize = self.repcore.getdbsize()
        # Load
        for aa in range(repsize-1, -1, -1):
            rec = self.repcore.get_rec(aa)
            if not rec:
                continue
            #print("rec:", rec)
            try:
                dec = self.packer.decode_data(rec[1])[0]['PayLoad']
            except:
                dec['host'] = ""
                dec['now'] = ""
            #print("dec", dec)
            if rec[0] in ddd3:
                continue
            ddd3.append(rec[0])

            hhh = dec['host'].split(":")
            if len(hhh) < 2:
                hhh.append("")
            arr = (hhh[0], hhh[1], dec['now'], rec[0].decode())
            self.model2.append(None, arr)

    def nextfield(self, treeview, path, next_column):

        #print("nextfield()", path, next_column)
        try:
            #ret = treeview.set_cursor(path, next_column, True)
            ret = treeview.set_cursor_on_cell(path, next_column, None, True)
            #print("ret:", ret)
            usleep(50)
            #ret2 = treeview.scroll_to_cell(path, next_column, False, 0.5, 0.5)
            #print("ret2:", ret2)
        except:
            pass

    def onTreeNavigateKeyPress(self, treeview, event):
        keyname = Gdk.keyval_name(event.keyval)
        path, col = treeview.get_cursor()
        columns = [c for c in treeview.get_columns()]
        try:
            colnum = columns.index(col)
        except:
            pass
            return
        #print("colnum", colnum, "columns", columns)
        #print("event", event.state, keyname)

        if keyname == 'Tab': # or keyname == 'Shift_L':
            # Walk to next editable
            newcol = colnum + 1
            while True:
                if newcol < len(columns):
                    next_column = columns[newcol]
                    ed = self.cells[newcol].get_property("editable")
                    if ed:
                        #print("ed", ed)
                        break
                else:
                    next_column = columns[0]
                    break
                newcol += 1

            GLib.timeout_add(50, self.nextfield, treeview, path, next_column)

        elif keyname == 'Return':

            model = treeview.get_model()
            #Check if currently in last row of Treeview
            if path.get_indices()[0] + 1 == len(model):
                path = treeview.get_path_at_pos(0,0)[0]
                #treeview.set_cursor(path, columns[colnum], True)
                GLib.timeout_add(50,
                             treeview.set_cursor,
                             path, columns[colnum], True)
            else:
                path.next()
                #treeview.set_cursor(path, columns[colnum], True)
                GLib.timeout_add(50,
                             treeview.set_cursor,
                             path, columns[colnum], True)
        else:
            pass

    def add_user_admin(self, flag):

        #print("Add user admin")
        dd = datetime.datetime.now().replace(microsecond=0)
        # Relicate conf for a blank sheet
        conf = Blank();
        conf.iconf  = self.conf.iconf;
        conf.iconf2 = self.conf.iconf2;
        conf.user   = ""; conf.apass = ""
        if flag == "Yes":
            mode = 3
        else:
            mode = 2
        dlg = passdlg.PassDlg(mode, conf)
        if dlg.res[0] == Gtk.ResponseType.ACCEPT:
            cipher = AES.new(passdlg.COMMONKEY[:32], AES.MODE_CTR,
                                use_aesni=True, nonce = passdlg.COMMONKEY[-8:])
            userx = cipher.decrypt(dlg.res[1]).decode()
            cipher = AES.new(passdlg.COMMONKEY[:32], AES.MODE_CTR,
                                use_aesni=True, nonce = passdlg.COMMONKEY[-8:])
            passx = cipher.decrypt(dlg.res[2]).decode()
            #print("userx:", userx, "passx", passx)
            # Is this a duplicate user?
            for aa in self.model:
                if aa[0] == userx:
                    pggui.message("Duplicate user, cannot add.", parent=self)
                    return
            ddd = passdlg.gen_def_data(userx, passx, flag)
            self.model.append(None, ddd[:-1])
            passdlg.addauth(self.authcore, self.packer, userx, passx, flag)

            #try:
            #    enc = packer.encode_data("", ddd)
            #except:
            #    enc = {}
            #self.authcore.save_data(ddd[5], enc)


    def sel_last(self, tviewx):
        #print("sel last ...")
        sel = tviewx.get_selection()
        xmodel, xiter = sel.get_selected()
        iterx = xmodel.get_iter_first()
        if not iterx:
            return
        while True:
            iter2 = xmodel.iter_next(iterx)
            if not iter2:
                break
            iterx = iter2.copy()
        sel.select_iter(iterx)
        ppp = xmodel.get_path(iterx)
        tviewx.set_cursor(ppp, tviewx.get_column(0), False)
        pgutils.usleep(5)
        tviewx.scroll_to_cell(ppp, None, True, 0., 0. )
        #sel.select_path(self.treestore.get_path(iterx))

    def add_host(self, arg2):
        #print("Add host")
        dd = datetime.datetime.now().replace(microsecond=0).isoformat()
        self.model2.append(None, ("Host", "Port", dd, str(uuid.uuid1()) ) )
        # Sel last (new) row
        self.sel_last(self.tview2)
        self.set_focus(self.tview2)

    def add_admin(self, arg2):
        self.add_user_admin("Yes")

    def add_user(self, arg2):
        #print("Add admin")
        self.add_user_admin("No")

    def popmenu(self, event, xstr):

        self.menu3.append(self.create_menuitem("Toggle Enable / Disable User",
                            self.toggle_rec, xstr))
        self.menu3.append(self.create_menuitem("Delete Selected User",
                            self.del_rec, xstr))
        self.menu3.popup(None, None, None, None, event.button, event.time)

    def tree_butt(self, arg2, event, arg4):
        #print("tree_but:", arg3)
        if event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == 3:
                sel = arg4.get_selection()
                xmodel, xpath = sel.get_selected_rows()
                if xpath:
                    for aa in xpath:
                        xiter2 = xmodel.get_iter(aa)
                        xstr = xmodel.get_value(xiter2, 5)
                        #print("Tree sel right click:", xstr)
                        self.menu3 = Gtk.Menu()
                        self.popmenu(event, xstr)
                        break

    def tree_sel(self, xtree, xiter, xpath):

        #print ("tree_sel", xtree, xiter, xpath)
        sel = xtree.get_selection()
        xmodel, xpath = sel.get_selected_rows()
        if xpath:
            #for aa in xpath:
            #    xiter2 = xmodel.get_iter(aa)
            #    xstr = xmodel.get_value(xiter2, 0)
            #    xstr2 = xmodel.get_value(xiter2, 1)
            #    print("mul selstr: ", "'" + xstr + "'" )
            self.response(Gtk.ResponseType.ACCEPT)

    def host_edited(self, widget, path, text, idx):

        # Changed?
        if  self.model2[path][idx] == text:
            print("No change", text)
            return

        # Commit to field, save it.
        try:
            self.model2[path][idx] = text
            print("Commit", text, idx)
            self.save_host_row(self.model2[path])

        except:
            print("Cannot commit field to db.", sys.exc_info())


    def text_edited(self, widget, path, text, idx):

        # Changed?
        if  self.model[path][idx] == text:
            #print("No change", text)
            return

        # Commit to field, save it.
        try:
            self.model[path][idx] = text
            #print("Commit", text)
            self.save_row(self.model[path])
        except:
            print("Cannot commit field to tree.", sys.exc_info())

    def save_row(self, row):
        #print("save_row", *row)
        pass

    def save_host_row(self, row):

        hhh = row[0] + ":" + row[1]
        #print("save_host_row", hhh, self.conf.user)

        repsize = self.repcore.getdbsize()
        # Check duplicate
        for aa in range(repsize-1, -1, -1):
            rec = self.repcore.get_rec(aa)
            if not rec:
                continue
            #print("rec:", rec)
            try:
                dec = self.packer.decode_data(rec[1])[0]['PayLoad']
            except:
                dec['host'] = ""
            #print("dec", dec)
            if dec['host'] == hhh:
                msg = "This host/port already exists. Not saved."
                pymisc.smessage(msg, conf=self.conf, sound="error")
                return

        uuu = row[3]
        now = datetime.datetime.now().replace(microsecond=0).isoformat()
        undec = {"host" : hhh , "header" : uuu,
                  "now": now, "oper": self.conf.user }
        #print("undec", undec)
        pvh = pyvhash.BcData()
        pvh.addpayload(undec)
        pvh.hasharr()
        #while not pvh.powarr():
        #    pass
        ddd = self.packer.encode_data("", pvh.datax)
        ret = self.repcore.save_data(uuu, ddd)

    def area_key(self, area, event):

        #print("area_key", event.keyval)
        # Do key down:
        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval in  (Gdk.KEY_Alt_L, Gdk.KEY_Alt_R):
                self.alt = True
            if event.keyval in (Gdk.KEY_x, Gdk.KEY_X):
                if self.alt:
                    self.response(Gtk.ResponseType.CANCEL)

        elif  event.type == Gdk.EventType.KEY_RELEASE:
            if event.keyval in (Gdk.KEY_Alt_L, Gdk.KEY_Alt_R):
                self.alt = False

    def create_ftree(self, ts):

        ''' worker function for tree creation '''
        # create the tview using ts
        tv = Gtk.TreeView(model=ts)

        tv.set_search_column(0)
        tv.set_headers_clickable(True)

        #tv.set_enable_search(True)
        #ts.set_sort_func(0, self.compare, None)
        #ts.set_sort_func(1, self.compare, None)
        ##ts.set_sort_func(1, self.dcompare, None)
        #ts.set_sort_func(2, self.ncompare, None)

        row_cnt = 0
        # Create a CellRendererText to render the data
        cell = Gtk.CellRendererText()
        #cell.set_property("editable", True)
        self.cells.append(cell)
        tvcolumn = Gtk.TreeViewColumn('Name')
        tvcolumn.set_min_width(200)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', row_cnt)
        tvcolumn.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        tvcolumn.set_sort_column_id(row_cnt)
        tv.append_column(tvcolumn)
        row_cnt += 1

        cell = Gtk.CellRendererText()
        cell.set_property("editable", True)
        cell.connect("edited", self.text_edited, row_cnt)
        self.cells.append(cell)
        tvcolumn2 = Gtk.TreeViewColumn('Full Name')
        tvcolumn2.set_min_width(100)
        tvcolumn2.pack_start(cell, True)
        tvcolumn2.add_attribute(cell, 'text', row_cnt)
        tvcolumn2.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        tvcolumn2.set_sort_column_id(row_cnt)
        tv.append_column(tvcolumn2)
        row_cnt += 1

        cell = Gtk.CellRendererText()
        #cell.set_property("editable", True)
        self.cells.append(cell)
        tvcolumn3 = Gtk.TreeViewColumn('Status')
        tvcolumn3.set_min_width(100)
        tvcolumn3.pack_start(cell, True)
        tvcolumn3.add_attribute(cell, 'text', row_cnt)
        tvcolumn3.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        tvcolumn3.set_sort_column_id(row_cnt)
        tv.append_column(tvcolumn3)
        row_cnt += 1

        cell = Gtk.CellRendererText()
        #celld.set_property("editable", True)
        self.cells.append(cell)
        tvcolumn2 = Gtk.TreeViewColumn('Date Created')
        tvcolumn2.set_min_width(180)
        tvcolumn2.pack_start(cell, True)
        tvcolumn2.add_attribute(cell, 'text', row_cnt)
        tvcolumn2.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        tvcolumn2.set_sort_column_id(row_cnt)
        tv.append_column(tvcolumn2)
        row_cnt += 1

        cell = Gtk.CellRendererText()
        cell.set_alignment(0.5, 0.)
        self.cells.append(cell)
        #celly.set_property("editable", True)
        tvcolumn3 = Gtk.TreeViewColumn('Admin')
        tvcolumn3.set_min_width(100)
        tvcolumn3.pack_start(cell, True)
        tvcolumn3.add_attribute(cell, 'text', row_cnt)
        tvcolumn3.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        tvcolumn3.set_sort_column_id(row_cnt)
        tv.append_column(tvcolumn3)
        row_cnt += 1

        cell = Gtk.CellRendererText()
        #cell.set_property("editable", True)
        self.cells.append(cell)
        tvcolumn2 = Gtk.TreeViewColumn('UUID')
        tvcolumn2.set_min_width(100)
        tvcolumn2.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        tvcolumn2.set_sort_column_id(row_cnt)
        tvcolumn2.pack_start(cell, True)
        tvcolumn2.add_attribute(cell, 'text', row_cnt)
        tv.append_column(tvcolumn2)
        row_cnt += 1

        cell = Gtk.CellRendererText()
        #cell.set_property("editable", True)
        self.cells.append(cell)
        tvcolumn2 = Gtk.TreeViewColumn('Hash')
        tvcolumn2.set_min_width(100)
        tvcolumn2.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        tvcolumn2.set_sort_column_id(row_cnt)
        tvcolumn2.pack_start(cell, True)
        tvcolumn2.add_attribute(cell, 'text', row_cnt)
        tv.append_column(tvcolumn2)
        row_cnt += 1

        #tv.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

        return tv

    def create_ftree2(self, ts):

        ''' worker function for tree creation '''
        # create the tview using ts
        tv = Gtk.TreeView(model=ts)

        tv.set_search_column(0)
        tv.set_headers_clickable(True)

        row_cnt = 0
        # Create a CellRendererText to render the data
        cell = Gtk.CellRendererText()
        self.cells.append(cell)
        cell.set_property("editable", True)
        cell.connect("edited", self.host_edited, row_cnt)
        tvcolumn = Gtk.TreeViewColumn('Host Name:')
        tvcolumn.set_min_width(150)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', row_cnt)
        tvcolumn.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        tvcolumn.set_sort_column_id(row_cnt)
        tv.append_column(tvcolumn)
        row_cnt += 1

        cell = Gtk.CellRendererText()
        self.cells.append(cell)
        cell.set_property("editable", True)
        cell.connect("edited", self.host_edited, row_cnt)
        tvcolumn = Gtk.TreeViewColumn('Host Port')
        tvcolumn.set_min_width(100)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', row_cnt)
        tvcolumn.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        tvcolumn.set_sort_column_id(row_cnt)
        tv.append_column(tvcolumn)
        row_cnt += 1

        cell = Gtk.CellRendererText()
        self.cells.append(cell)
        tvcolumn2 = Gtk.TreeViewColumn('Date Created')
        tvcolumn2.set_min_width(180)
        tvcolumn2.pack_start(cell, True)
        tvcolumn2.add_attribute(cell, 'text', row_cnt)
        tvcolumn2.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        tvcolumn2.set_sort_column_id(row_cnt)
        tv.append_column(tvcolumn2)
        row_cnt += 1

        cell = Gtk.CellRendererText()
        self.cells.append(cell)
        tvcolumn2 = Gtk.TreeViewColumn('UUID')
        tvcolumn2.set_min_width(100)
        tvcolumn2.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        tvcolumn2.set_sort_column_id(row_cnt)
        tvcolumn2.pack_start(cell, True)
        tvcolumn2.add_attribute(cell, 'text', row_cnt)
        tv.append_column(tvcolumn2)
        row_cnt += 1

        return tv

    def tree_sel_row(self, xtree):
        pass

# EOF
