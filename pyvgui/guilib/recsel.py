#!/usr/bin/env python

''' Action Handler for open records dialog '''

# pylint: disable=C0103

import os
import sys
import datetime
import time
import uuid
import io
import struct

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk

import pyvpacker
from pydbase import twincore, twinchain

from pyvguicom import pggui
from pyvguicom import pgsel
from pyvguicom import pgutils
from pyvguicom import pgentry

from pyvcommon import pyvhash

# ---------------------------------------------------------------

def   append_index(vcore, idxname,  hashx, rrr):

    ''' append hashx to index file.
        generate / re - index if not there. If no hash passed,
        just regenerate '
    '''
    ttt = time.time()
    ifp = vcore.softcreate(idxname)
    buffsize = vcore.getsize(ifp)
    if buffsize < twincore.HEADSIZE:
        vcore.create_data(ifp)
        ifp.seek(twincore.HEADSIZE, io.SEEK_SET)
        buffsize = vcore.getsize(ifp)

    ifp.seek(0, io.SEEK_END)
    bsize = (buffsize - twincore.HEADSIZE) // 4
    datasize = vcore.getdbsize()
    #print("bsize", bsize, "datasize:", datasize)
    ddiff = datasize - bsize
    if ddiff:
        ddd2 = []
        for aa in range(bsize, datasize):
            rrr = vcore.get_rec(aa)
            if not rrr:
                # Deleted record has empty hash, keeps offset correct
                rrr[0] = ""
            hhh = hashx(vcore, rrr)
            # print last entry for test
            #if aa == datasize - 1:
            print("hhh", hex(hhh))
            pp = struct.pack("I", hhh)
            ifp.write(pp)
    else:
        if rrr:
            hhh = hashx(vcore, rrr)
            print("append hashx", hex(hhh))
            pp = struct.pack("I", hashx)
            ifp.write(pp)
    ifp.close()

    print("gen_index done %.2fs" % (time.time() - ttt) )

def hashid(vcore, rrr):

    if type(rrr[0]) != type(b""):
        rrr[0] = rrr[0].encode()
    hhh = vcore.hash32(rrr[0])
    return hhh

def hashname(vcore, rrr):

    dec = vcore.packer.decode_data(rrr[1])[0]
    sss = dec['name'].upper().replace(" ", "")
    print("sss:", sss)
    hhh = vcore.hash32(sss.encode())
    return hhh

''' Open voter dialog. We attach state vars to the class,
    it was attached to the dialog in the original incarnation.
'''

class RecSel(Gtk.Dialog):

    def __init__(self, vcore):
        super().__init__(self)

        self.set_title("Open Record(s)")
        self.add_buttons(   Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                            Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)

        #self.set_default_response(Gtk.ResponseType.ACCEPT)
        #self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(800, 600)
        self.alt = False
        self.xmulti = []
        self.vcore = vcore
        self.packer = pyvpacker.packbin()
        self.rec_cnt = 0
        self.scan_cnt = 0
        self.stop = False
        self.w_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self.sort_cnt = 0

        self.connect("key-press-event", self.area_key)
        self.connect("key-release-event", self.area_key)

        self.pbox = Gtk.HBox()
        self.vbox.pack_start(self.pbox, 0, 0, 0)

        simp = pgsel.LetterNumberSel(self.lettersel, "Mono 16", " ")
        simp.set_tooltip_text("Click on selection or navigate " \
                " to selection, press space / enter to select")

        self.vbox.pack_start(simp, 0, 0, 0)

        gridx = Gtk.Grid()
        gridx.set_column_spacing(6)
        gridx.set_row_spacing(6)
        rowcnt = 0
        hbox4 = Gtk.HBox()

        butt3 = Gtk.Button.new_with_mnemonic("  _Find ID   ")
        tp5x = ("Find ID:", "get", "Search for record ID", None)
        lab5x = pgentry.griddouble(gridx, 0, rowcnt, tp5x, butt3)
        butt3.connect("clicked", self.search_id, lab5x)
        rowcnt += 1

        butt4 = Gtk.Button.new_with_mnemonic("  _Find Full Name   ")
        tp6x = ("Find Name:", "get", "Search for record by full name", None)
        lab6x = pgentry.griddouble(gridx, 0, rowcnt, tp6x, butt4)
        butt4.connect("clicked", self.search_nameidx, lab6x)
        rowcnt += 1

        butt2 = Gtk.Button.new_with_mnemonic("  _Search For Partial Nane   ")
        tp4x = ("Search for entry (slow):", "find", "Search for partial record", None)
        lab4x = pgentry.griddouble(gridx, 0, rowcnt, tp4x, butt2)
        butt2.connect("clicked", self.search_entry, lab4x)
        rowcnt += 1


        hbox4.pack_start(pggui.xSpacer(), 0, 0, 4)
        hbox4.pack_start(gridx, 0, 0, 4)
        hbox4.pack_start(pggui.xSpacer(), 0, 0, 4)

        self.vbox.pack_start(hbox4, 0, 0, 4)

        #self.vbox.pack_start(pggui.xSpacer(), 0, 0, 0)
        hbox3 = Gtk.HBox()

        #label13 = Gtk.Label.new("   Find an entry containing:   ")
        #hbox3.pack_start(label13, 0, 0, 0)
        #self.entry = Gtk.Entry()
        #hbox3.pack_start(self.entry, 1, 1, 0)
        #hbox3.pack_start(butt, 0, 0, 4)
        #self.vbox.pack_start(hbox3, 0, 0, 4)

        self.ts = Gtk.ListStore(str, str, str, str)
        self.tview = self.create_ftree(self.ts)

        scroll = Gtk.ScrolledWindow()
        self.tview.connect("row-activated",  self.tree_sel)
        scroll.add(self.tview)

        frame2 = Gtk.Frame()
        frame2.add(scroll)

        hbox3 = Gtk.HBox()
        label1 = Gtk.Label("   ")
        hbox3.pack_start(label1, 0, 0, 0)
        hbox3.pack_start(frame2, True, True, 0)
        label2 = Gtk.Label("   ")
        hbox3.pack_start(label2, 0, 0, 0)

        self.vbox.pack_start(hbox3, True, True, 0)

        #label5  = Gtk.Label("  ")
        #self.vbox.pack_start(label5, 0, 0, 0)
        label13 = Gtk.Label.new("Select Filter or Search criteria. When done, double click to select an entry.")

        self.vbox.pack_start(label13, 0, 0, 0)
        #self.vbox.pack_start(pggui.xSpacer(), 0, 0, 0)

        self.abox = self.get_action_area()

        self.stopbutt = Gtk.Button.new_with_mnemonic("Stop Lo_ading")
        self.stopbutt.set_sensitive( False )
        self.stopbutt.connect("clicked", self.stopload)

        self.abox.pack_start(self.stopbutt, 1, 1, 0)
        self.abox.reorder_child(self.stopbutt, 0)

        self.labsss = Gtk.Label("Awaiting filter or seach selection ...")
        self.abox.pack_start(self.labsss, 1, 1, 0)
        self.abox.reorder_child(self.labsss, 0)

        self.show_all()
        self.initial_pop()
        #self.set_focus(self.tview)
        self.response = self.run()

        self.res = []
        if self.response == Gtk.ResponseType.ACCEPT:
            xmodel = self.ts
            sel = self.tview.get_selection()
            if not sel:
                return
            # Is multi selection?
            iterx = xmodel.get_iter_first()
            while True:
                #print("iterate", xmodel.get_value(iterx, 0))
                if not iterx:
                    break
                if sel.iter_is_selected(iterx):
                    xstr = xmodel.get_value(iterx, 0)
                    xstr2 = xmodel.get_value(iterx, 1)
                    xstr3 = xmodel.get_value(iterx, 2)
                    xstr4 = xmodel.get_value(iterx, 3)
                    self.res.append((xstr, xstr2, xstr3, xstr4))
                iterx = xmodel.iter_next(iterx)

        #print ("response", self.response, "result", self.res)
        self.destroy()

    def search_entry(self, butt, entry):
        print("Search:", entry.get_text())
        self.populate("", entry.get_text())

    def search_nameidx(self, arg2, arg3):

        ''' Search Name Index. Fast '''

        xxx = arg3.get_text()
        #print("Search for:", xxx)
        #print("search_index:", self.vcore.hashname2)

        self.stop = False
        ttt = time.time()
        self.labsss.set_text("Loading ...")
        self.stopbutt.set_sensitive(True)
        self.get_window().set_cursor(self.w_cursor)
        pgutils.usleep(5)

        # Clear old contents:
        while True:
            root = self.ts.get_iter_first()
            if not root:
                break
            try:
                self.ts.remove(root)
            except:
                print("Exception on rm ts", sys.exc_info())

        self.rec_cnt = 0

        try:
            ifp = open(self.vcore.hashname2, "rb")
        except:
            self.gen_index(0)
            ifp = open(self.hashname2, "rb")
            #return
        ttt = time.time()
        buffsize = self.vcore.getsize(ifp)
        ifp.seek(twincore.HEADSIZE, io.SEEK_SET)
        datasize = self.vcore.getdbsize()
        sss = xxx.upper().replace(" ", "")
        #print("sss:", sss)
        hhh = self.vcore.hash32(sss.encode())
        cnt = 0
        ddd2 = []
        while True:
            if self.stop:
                break
            val = ifp.read(4)
            if not val:
                break;
            val2 = struct.unpack("I", val)[0]
            if hhh == val2:
                #print("Found", hex(val2), cnt)
                rrr = self.vcore.get_rec(cnt)
                dec = self.packer.decode_data(rrr[1])[0]
                uuu = rrr[0].decode()
                ddd2.append((dec['name'], dec['now'], dec['dob'],  uuu))

            cnt += 1
        ifp.close()
        #print("delta %.3f" % (time.time() - ttt) )

        # Fill in results
        self.stopbutt.set_sensitive( False )
        for aa in ddd2:
            piter = self.ts.append(row=None)
            #print("row", aa)
            for cc in range(4):
                self.ts.set(piter, cc, aa[cc])
        delta = (time.time() - ttt)
        self.labsss.set_text("%s records. (%.2fs)" % (self.rec_cnt, delta))
        self.get_window().set_cursor()

    def search_id(self, butt, entry):
        ttt = entry.get_text()
        #print("Search ID:", ttt)
        try:
            uuu = uuid.UUID(ttt)
        except:
            msg = "Must be a valid UUID"
            print(msg)
            pggui.message(msg)
            return

        self.populateid(ttt)

    def stopload(self, butt):

        ''' Flag stop '''
        self.stop = True

    def lettersel(self, letterx):

        ''' Selection callback '''

        #print(letterx)
        pgutils.usleep(10)
        self.populate(letterx)
        pgutils.usleep(10)

    def initial_pop(self):

        ''' Fill in use instructions '''

        piter = self.ts.append(row=None)
        self.ts.set(piter, 0, "Select Appropriate filter")
        self.ts.set(piter, 1, "From top row")
        self.ts.set(piter, 2, "Selecting 'All' may take a long time to load")

    # ------------------------------------------------------------------------

    def populateid(self, idval):

        ''' populate tree with ID'''

        #print("pop", idval)

        self.stop = False
        ttt = time.time()
        self.labsss.set_text("Loading ...")
        self.stopbutt.set_sensitive(True)
        self.get_window().set_cursor(self.w_cursor)
        pgutils.usleep(5)

        # Clear old contents:
        while True:
            root = self.ts.get_iter_first()
            if not root:
                break
            try:
                self.ts.remove(root)
            except:
                print("Exception on rm ts", sys.exc_info())

        self.rec_cnt = 0
        datasize = self.vcore.getdbsize()

        ddd2 = []
        lll = self.vcore.find_key(idval)
        print("lll", lll)
        for aa in lll:
            rrr = self.vcore.get_rec_byoffs(aa)
            dec = self.packer.decode_data(rrr[1])[0]
            uuu = rrr[0].decode()
            ddd2.append((dec['name'], dec['now'], dec['dob'],  uuu))

        # Fill in results
        self.stopbutt.set_sensitive( False )
        for aa in ddd2:
            piter = self.ts.append(row=None)
            #print("row", aa)
            for cc in range(4):
                self.ts.set(piter, cc, aa[cc])

        #print("index %.1fs" % (time.time() - ttt) )
        #for aa in range(datasize -1, -1, -1):
        #    rrr = self.vcore.get_rec(aa)
        #    pass
        #print("read %.1fs" % (time.time() - ttt) )

        delta = (time.time() - ttt)
        self.labsss.set_text("%s records. (%.1fs)" % (self.rec_cnt, delta))
        self.get_window().set_cursor()

    def populate(self, filterx = "", searchx = ""):

        ''' populate tree '''

        if len(filterx):
            filterx = filterx.upper()

        #if len(searchx):
        #    searchx = searchx.upper()

        #print("pop", filterx, searchx)

        self.stop = False
        ttt = time.time()
        self.labsss.set_text("Loading ...")
        self.stopbutt.set_sensitive(True)
        self.get_window().set_cursor(self.w_cursor)
        pgutils.usleep(5)

        # Clear old contents:
        while True:
            root = self.ts.get_iter_first()
            if not root:
                break
            try:
                self.ts.remove(root)
            except:
                print("Exception on rm ts", sys.exc_info())

        self.rec_cnt = 0
        datasize = self.vcore.getdbsize()

        ddd2 = []
        for aa in range(datasize -1, -1, -1):
            rrr = self.vcore.get_rec(aa)
            if not rrr:
                continue
            #print("rrr:", rrr)
            dec = self.packer.decode_data(rrr[1])[0]
            #print("dec:", dec)
            #print("dec:", dec['name'], dec['dob'], dec['uuid'])

            if self.stop:
                break

            self.scan_cnt += 1
            if self.scan_cnt % 1000 == 0:
                self.labsss.set_text("Scanning:  %d of %d Loading: %d" %
                            (self.scan_cnt, datasize, self.rec_cnt))
                self.get_window().set_cursor(self.w_cursor)
                pgutils.usleep(5)

            # See if search requested:
            if searchx:
                if len(dec['name']):
                    #if dec['name'].upper().find(searchx) < 0:
                    if dec['name'].find(searchx) < 0:
                        continue
            else:
                # See if it is filtered:
                if filterx != "ALL":
                    if filterx != "":
                        if len(dec['name']):
                            if filterx[0] != dec['name'][0].upper():
                                #print("Filtered", dec['name'])
                                continue

            uuu = rrr[0].decode()

            # Wed 24.Apr.2024 load all, include history
            # See if we have this already
            #found = False
            #for aaa in ddd2:
            #    if aaa[3] == uuu:
            #        found = True
            #        break
            #if found:
            #    continue

            #print("append:", dec)
            ddd2.append((dec['name'], dec['now'], dec['dob'],  uuu))
            self.rec_cnt += 1
            if self.rec_cnt % 100 == 0:
                if self.stop:
                    break
            sig = False
            if filterx == "ALL":
                if self.rec_cnt >= 5000:
                    sig = True
            else:
                if self.rec_cnt >= 1000:
                    sig = True
            if sig:
                msg = "Loaded %d records, stopping. \n" \
                        "If your intended record is not included, " \
                        "please narrow the filter condition." % (self.rec_cnt)
                pggui.message(msg)
                self.set_focus(self.tview)
                break

        # Fill in results
        self.stopbutt.set_sensitive( False )
        for aa in ddd2:
            piter = self.ts.append(row=None)
            #print("row", aa)
            for cc in range(4):
                self.ts.set(piter, cc, aa[cc])

        delta = (time.time() - ttt)
        self.labsss.set_text("%s records. (%.1fs)" % (self.rec_cnt, delta))
        self.get_window().set_cursor()

        # --------------------------------------------------------------------

    def compare(self, model, row1, row2, user_data):

        ''' compare fields for sort '''

        #self.sort_cnt += 1
        #if self.sort_cnt % 1000 == 0:
        #    self.get_window().set_cursor(self.w_cursor)
        #    pgutils.usleep(5)

        sort_column, _ = model.get_sort_column_id()
        value1 = model.get_value(row1, sort_column)
        value2 = model.get_value(row2, sort_column)
        #print(sort_column, value1, value2)
        if value1 < value2:
            return -1
        elif value1 == value2:
            return 0
        else:
            return 1

    def ncompare(self, model, row1, row2, user_data):

        ''' compare fields for sort '''

        self.sort_cnt += 1
        sort_column, _ = model.get_sort_column_id()
        value1 = model.get_value(row1, sort_column)
        value2 = model.get_value(row2, sort_column)
        #print("n", sort_column, value1, value2, type(value1))

        dd = datetime.datetime.now()
        try:
            dd2 = dd.strptime(value1, "%Y/%m/%d").timestamp()
        except:
            dd2 = 0
        try:
            dd3 = dd.strptime(value2, "%Y/%m/%d").timestamp()
        except:
            dd3 = 0

        if int(dd2) < int(dd3):
            return -1
        elif int(dd2) == int(dd3):
            return 0
        else:
            return 1

    def dcompare(self, model, row1, row2, user_data):

        ''' compare fields for sort '''

        self.sort_cnt += 1

        sort_column, _ = model.get_sort_column_id()
        value1 = model.get_value(row1, sort_column)
        value2 = model.get_value(row2, sort_column)
        #print("n", sort_column, value1, value2, type(value1))
        dd = datetime.datetime.now()
        #YYYY-MM-DDTHH:MM
        try:
            dd2 = dd.strptime(value1, pyvhash.isostr).timestamp()
        except:
            print(sys.exc_info())
            dd2 = 0
        try:
            dd3 = dd.strptime(value2, isostr).timestamp()
        except:
            dd3 = 0

        #print("dd 2/3", dd2, dd3)

        if int(dd2) < int(dd3):
            return -1
        elif int(dd2) == int(dd3):
            return 0
        else:
            return 1

    def create_ftree(self, ts):

        ''' worker function for tree creation '''

        # create the tview using ts
        tv = Gtk.TreeView(model=ts)

        tv.set_search_column(0)
        tv.set_headers_clickable(True)
        #tv.set_enable_search(True)
        ts.set_sort_func(0, self.compare, None)
        ts.set_sort_func(1, self.compare, None)
        #ts.set_sort_func(1, self.dcompare, None)
        ts.set_sort_func(2, self.ncompare, None)

        # create a CellRendererText to render the data
        cell = Gtk.CellRendererText()
        tvcolumn = Gtk.TreeViewColumn('Name')
        tvcolumn.set_min_width(240)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 0)
        tvcolumn.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        tvcolumn.set_sort_column_id(0)
        tv.append_column(tvcolumn)

        celld = Gtk.CellRendererText()
        tvcolumn2 = Gtk.TreeViewColumn('Date of Entry')
        tvcolumn2.set_min_width(100)
        tvcolumn2.pack_start(celld, True)
        tvcolumn2.add_attribute(celld, 'text', 1)
        tvcolumn2.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        tvcolumn2.set_sort_column_id(1)
        tv.append_column(tvcolumn2)

        cellx = Gtk.CellRendererText()
        tvcolumn3 = Gtk.TreeViewColumn('Date of Birth')
        tvcolumn3.set_min_width(100)
        tvcolumn3.pack_start(cellx, True)
        tvcolumn3.add_attribute(cellx, 'text', 2)
        tvcolumn3.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        tvcolumn3.set_sort_column_id(2)
        tv.append_column(tvcolumn3)

        cell2 = Gtk.CellRendererText()
        tvcolumn2 = Gtk.TreeViewColumn('UUID')
        tvcolumn2.set_min_width(100)
        tvcolumn2.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        tvcolumn2.set_sort_column_id(3)
        tvcolumn2.pack_start(cell2, True)
        tvcolumn2.add_attribute(cell2, 'text', 3)
        tv.append_column(tvcolumn2)

        #tv.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

        return tv

    def tree_sel_row(self, xtree):
        pass

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

    # If directory, change to it
    def click_dir_action(self, xstr):
        if xstr[0] == "[":
            xstr = xstr[1:len(xstr)-1]
        if os.path.isdir(xstr):
            #print ("dir", xstr)
            os.chdir(xstr)
            return True

        return False

    # Call key handler

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

# EOF
