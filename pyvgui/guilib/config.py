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

import passdlg

class Blank(): pass


class ConfigDlg(Gtk.Dialog):

    '''
        The config dialog.
    '''

    def __init__(self, vcore, acore, authcore, conf):
        super().__init__(self)

        self.set_title("Configuration")
        self.set_modal(True)

        self.add_buttons(   Gtk.STOCK_CLOSE, Gtk.ResponseType.ACCEPT)
        self.set_size_request(800, 600)
        self.conf = conf
        self.alt = False
        self.xmulti = []
        self.vcore = vcore
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
        hbox4.pack_start(Gtk.Label("Edit user / admin entries on tree control. Tab key to advance."), 0, 0, 2)
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
        butt5 = Gtk.Button.new_with_mnemonic(" _Delete Selected User ")
        hbox3.pack_start(butt5, 0, 0, 2)
        hbox3.pack_start(pggui.xSpacer(), 1, 1, 4)
        self.vbox3.pack_start(hbox3, 0, 0, 4)
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

    def loaddata(self):
        ddd2 = []
        datasize = self.authcore.getdbsize()
        for aa in range(datasize -1, -1, -1):
            rrr = self.authcore.get_rec(aa)
            if not rrr:
                pass
            try:
                dec = self.packer.decode_data(rrr[1])[0]
            except:
                dec = {}

            if not dec[0] in ddd2:
                ddd2.append(dec[0])
                #print("dec", dec)
                # Check:
                hhh = SHA256.new();
                hhh.update(bytes(str(dec[:-1]), "utf-8"))
                #print("sums:", hhh.hexdigest(), dec[-1])
                if hhh.hexdigest() != dec[-1]:
                    print("Bad sum on:", dec[0])
                else:
                    self.model.append(None, dec[:-1])

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
                    pgutils.message("Duplicate user, cannot add.")
                    return
            ddd = passdlg.gen_def_data(userx, passx, flag)
            self.model.append(None, ddd[:-1])
            passdlg.addauth(self.authcore, self.packer, userx, passx, flag)

            #try:
            #    enc = packer.encode_data("", ddd)
            #except:
            #    enc = {}
            #self.authcore.save_data(ddd[5], enc)

    def add_admin(self, arg2):
        self.add_user_admin("Yes")

    def add_user(self, arg2):
        #print("Add admin")
        self.add_user_admin("No")

    def tree_butt(self, arg2, event, arg4):
        #print("tree_but:", arg3)
        if event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == 3:
                sel = self.tview.get_selection()
                xmodel, xpath = sel.get_selected_rows()
                if xpath:
                    for aa in xpath:
                        xiter2 = xmodel.get_iter(aa)
                        xstr = xmodel.get_value(xiter2, 3)
                        #print("Tree sel right click:", xstr)
                        self.menu3 = Gtk.Menu()
                        self.menu3.append(self.create_menuitem("Open Selected Record", self.open_rec, xstr))
                        self.menu3.append(self.create_menuitem("Delete Selected Record", self.del_rec, xstr))
                        self.menu3.popup(None, None, None, None, event.button, event.time)
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

    def text_edited(self, widget, path, text, idx):

        # Changed?
        if  self.model[path][idx] == text:
            #print("No change", text)
            return

        # Commit to field, save it.
        try:
            self.model[path][idx] = text
            print("Commit", text)
            self.save_row(self.model[path])
        except:
            print("Cannot commit field to tree.")

    def save_row(self, row):
        print("save_row", *row)

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
        cell.connect("edited", self.text_edited, row_cnt)
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
        cell.set_property("editable", True)
        cell.connect("edited", self.text_edited, row_cnt)
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
        tvcolumn2.set_min_width(100)
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

    def tree_sel_row(self, xtree):
        pass


# EOF
