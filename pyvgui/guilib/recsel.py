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
import random
import array
from io import BytesIO

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

# Make even and odd flags for obfuscation. This way boolean desision
# is made on an integer instead of 0 and 1

for aa in range(6):
    r1 = random.randint(0, 100000); FLAG_ON  =  (r1 // 2) * 2
    r2 = random.randint(0, 100000); FLAG_OFF =  (r2 // 2) * 2 + 1
    # Unlikely, but catch it
    if FLAG_ON != FLAG_OFF:
        break

def search_index(vcore, hashname, textx, hashfunc, ccc = None):

    if ccc:
        ccc.rec_cnt = 0
    try:
        ifp = open(hashname, "rb")
    except:
        print("cannot open hash", hashname)
        return
        if ccc:
            ccc.gen_index(0)
        ifp = open(hashname, "rb")

    buffsize = vcore.getsize(ifp)
    ifp.seek(twincore.HEADSIZE, io.SEEK_SET)
    datasize = vcore.getdbsize()
    fakedict = {}
    fakedict['name'] = textx
    enc = vcore.packer.encode_data("", fakedict)
    # We populate all indexed entries, as they are the only significant field
    hhh = hashfunc(vcore, [textx, enc])
    #hhh = struct.unpack("I", hhh)[0]
    # reverse
    hhh2  = hhh.to_bytes(4, 'little')
    #print("hhh2",  hhh2)

    #ttt = time.time()
    cnt = 0
    ddd3 = []

    # Tried it ... 140 ms
    #while True:
    #    if ccc:
    #        if ccc.stop:
    #            break
    #    val = ifp.read(4)
    #    if not val:
    #        break;
    #    val2 = struct.unpack("I", val)[0]
    #    if hhh == val2:
    #        ddd3.append(cnt)
    #    cnt += 1

    # Tried it .... 7 seconds
    #arr4 = array.array('i')
    #arr4.frombytes(data)
    #buf = arr4.buffer()
    #arr4.byteswap()
    #for aa in range(len(arr4)):
    #   if val == hhh:
    #       print("found", aa)
    #       ddd3.append(cnt)

    # Tried it ... 80 ms
    while True:
        if ccc:
            if ccc.stop:
                break
        data = ifp.read(10000)
        if not data:
            break;
        cnt2 = 0
        fp = BytesIO(data)
        while True:
            val = fp.read(4)
            if not val:
                break
            #if cnt2 < 3:
            #    print(val)
            if val == hhh2:
                ddd3.append(cnt + cnt2)
                #print("Found", cnt2 + cnt)
            cnt2 += 1
        cnt += 10000 // 4

    ifp.close()

    #print("search delta %.2f ms" % (1000 * (time.time() - ttt)) )
    return ddd3

# ---------------------------------------------------------------

def   append_index(vcore, idxname,  hashx, rrr):

    ''' append hashx to index file.
        generate / re - index if not there. If no hash passed,
        just regenerate '
    '''

    #print("append_index", rrr)

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
        #print("re-hash:", ddiff)
        ddd2 = []
        for aa in range(bsize, datasize):
            rrrr = vcore.get_rec(aa)
            #print("rrrr:", rrrr)
            if not rrrr:
                # Deleted record has empty hash, keeps offset correct
                rrrr[0] = ""
            try:
                hhh = hashx(vcore, rrrr)
            except:
                hhh = 0
            # print last entry for test
            #if aa == datasize - 1:
            #print("hhh gen", hex(hhh))
            pp = struct.pack("I", hhh)
            ifp.write(pp)
        #print("gen_index done %.2fs" % (time.time() - ttt) )
    else:
        if rrr:
            hhh = hashx(vcore, rrr)
            print("append hashx", hex(hhh))
            pp = struct.pack("I", hhh)
            ifp.write(pp)
    ifp.close()

def hashid(vcore, rrr):

    ''' Produce a hash of ID from record '''

    if type(rrr[0]) != type(b""):
        rrr[0] = rrr[0].encode()

    hhh = vcore.hash32(rrr[0])
    return hhh

def hashname(vcore, rrr):

    ''' Produce a hash of name from record '''

    if type(rrr[0]) != type(b""):
        rrr[0] = rrr[0].encode()

    dec = vcore.packer.decode_data(rrr[1])[0]
    sss = dec['name'].upper().replace(" ", "")
    #print("sss:", sss)
    hhh = vcore.hash32(sss.encode())
    return hhh

def audit(acore, packer, eventstr, rrr):

    auditx = {};
    auditx['header'] = str(uuid.uuid1())
    auditx['event'] = eventstr
    dd = datetime.datetime.now()
    auditx['now'] = dd.isoformat()
    try:
        auditx['rec'] = packer.decode_data(rrr)[0]
    except:
        #print("exc audit decode:", sys.exc_info())
        #auditx['rec'] = "Could not decode"
        # Was not data, just add
        auditx['rec'] = rrr

    rrrr = packer.encode_data("", auditx)
    acore.save_data(auditx['header'], rrrr)

class RecSel(Gtk.Dialog):

    ''' Open record selection dialog. We attach state vars to the class,
    it was attached to the dialog in the original incarnation.
    '''

    def __init__(self, vcore, acore):
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
        self.acore = acore
        self.packer = pyvpacker.packbin()
        self.rec_cnt = 0
        self.scan_cnt = 0
        self.stop = False
        self.w_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self.sort_cnt = 0
        #self.vbox = self.get_content_area()

        try:
            ic = Gtk.Image(); ic.set_from_file("pyvvote_sub.png")
            self.set_icon(ic.get_pixbuf())
        except:
            pass

        self.connect("key-press-event", self.area_key)
        self.connect("key-release-event", self.area_key)

        #self.pbox = Gtk.HBox()
        #self.vbox.pack_start(self.pbox, 0, 0, 0)

        simp = pgsel.LetterNumberSel(self.lettersel, "Mono 16", " ")
        simp.set_tooltip_text("Click on selection or navigate " \
                " to selection, press space / enter to select")

        self.vbox.pack_start(simp, 0, 0, 0)

        gridx = Gtk.Grid()
        gridx.set_column_spacing(6)
        gridx.set_row_spacing(6)
        rowcnt = 0
        hbox4 = Gtk.HBox()

        butt4 = Gtk.Button.new_with_mnemonic("  Fin_d Name   ")
        tp6x = ("Find Full N_ame:", "get", "Search for record by full name. Case insesitive.", None)
        lab6x = pgentry.griddouble(gridx, 0, rowcnt, tp6x, butt4)
        butt4.connect("clicked", self.search_idx, lab6x, self.vcore.hashname2, hashname)
        rowcnt += 1

        butt3 = Gtk.Button.new_with_mnemonic("  Find ID   ")
        tp5x = ("_Find ID:", "get", "Search for record ID. Must be valid UUID", None)
        lab5x = pgentry.griddouble(gridx, 0, rowcnt, tp5x, butt3)
        butt3.connect("clicked", self.search_id, lab5x, self.vcore.hashname, hashid)
        rowcnt += 1

        butt2 = Gtk.Button.new_with_mnemonic("  Sea_rch   ")
        tp4x = ("_Search for name (slow):", "find", "Search for partial record match. Slow", None)
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
        self.tview.connect("button-press-event",  self.tree_butt, self.tview)
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
        label13 = Gtk.Label.new("Select Filter or Search criteria. On the list, double click to select an entry.")

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
        if self.response == (Gtk.ResponseType.ACCEPT):
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
        #print("Search:", entry.get_text())
        self.populate("", entry.get_text())

    def search_idx(self, arg2, entry, hashname, hashfunc):

        ''' Search Name Index. Fast '''

        textx = entry.get_text()
        #print("Search for:", textx)
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

        ddd3 =  search_index(self.vcore, hashname, textx, hashfunc, self)

        # Fill in results
        self.stopbutt.set_sensitive( False )

        ddd2 = []
        for aa in ddd3:
            #print("Found", hex(val2), cnt)
                rrr = self.vcore.get_rec(aa)
                if not rrr:
                    continue
                try:
                    uuu = rrr[0].decode()
                except:
                    uuu = 0
                    pass
                try:
                    dec = self.packer.decode_data(rrr[1])[0]
                except:
                    # This way the user knows
                    print("Damaged:", cnt, sys.exc_info(), rrr)
                    continue
                    #dec = {}       # Was a fake record ... now just print
                    #dec['name'] = "Damaged record:", cnt
                    #dec['now'] = ""
                    #dec['dob'] = ""
                ddd2.append((dec['name'], dec['now'], dec['dob'],  uuu))

        ddd_dup = []
        for aa in ddd2:
            if aa[3] not in ddd_dup:
                ddd_dup.append(aa[3])
                try:
                    piter = self.ts.append(row=None)
                    #print("row", aa)
                    for cc in range(4):
                        self.ts.set(piter, cc, aa[cc])
                except:
                    print("Malformed record:", aa)

        delta = (time.time() - ttt)
        self.labsss.set_text("%s records. (%.2fs)" % (self.rec_cnt, delta))
        self.get_window().set_cursor()

    def search_id(self, arg2, entry, hashname, hashfunc):
        ttt = entry.get_text()
        #print("Search ID:", ttt)
        try:
            uuu = uuid.UUID(ttt)
        except:
            msg = "Must be a valid UUID"
            print(msg)
            pggui.message(msg)
            return
        self.search_idx(arg2, entry, hashname, hashfunc)

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

    def dec_rec(self, rrr):

        ''' Decode record, handle excptions by returning empty data '''
        try:
            dec = self.packer.decode_data(rrr[1])[0]
        except:
            dec = {}
        try:
            uuu = rrr[0].decode()
        except:
            uuu = ""
        return uuu, dec

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
            try:
                dec = self.packer.decode_data(rrr[1])[0]
            #print("dec:", dec)
            #print("dec:", dec['name'], dec['dob'], dec['uuid'])
            except:
                dec = {}
                dec['name'] = "Invalid / Damaged data."
                dec['now'] = dec['dob'] =  dec['uuid'] = ""
                continue

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
            try:
                ddd2.append((dec['name'], dec['now'], dec['dob'],  uuu))
            except:
                print("Exc Cannot append rec", dec)
                print(sys.exc_info())
                pass

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

    def create_menuitem(self, string, action, arg = None):
        rclick_menu = Gtk.MenuItem(string)
        if action:
            rclick_menu.connect("activate", action, string, arg)
        rclick_menu.show()
        return rclick_menu

    def popmenu(self, event, xstr):

        self.menu3.append(self.create_menuitem("Open Selected Record",
                            self.open_rec, xstr))
        self.menu3.append(self.create_menuitem("Delete Selected Record",
                            self.del_rec, xstr))
        self.menu3.popup(None, None, None, None, event.button, event.time)

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
                        self.popmenu(event, xstr)
                        break

    def del_rec(self, arg2, arg3, textx):

        ''' Delete record driven by menu interface '''

        #print("Del rec", arg2, arg3, textx)

        ddd2 = search_index(self.vcore, self.vcore.hashname, textx, hashid)
        for aa in ddd2:
            #print("deleting:", ddd2)
            try:
                rrr = self.vcore.get_rec(aa)
                self.vcore.del_rec(aa)
                #print("del rrr", rrr)
                audit(self.acore, self.packer, "Deleted Record (from Menu)", rrr[1])
            except:
                print("delrec,", sys.exc_info())
                pgutils.put_exception("delrec")

            # Remove from displayed list
            iterx = self.ts.get_iter_first()
            while True:
                if not iterx:
                    break
                xstr = self.ts.get_value(iterx, 3)
                #print("xstr:", xstr)
                if xstr == textx:
                    try:
                        self.ts.remove(iterx)
                    except:
                        print("Exception on del from tree", sys.exc_info())
                    break
                iterx = self.ts.iter_next(iterx)

    def open_rec(self, arg2, arg3, arg4):
        #print("open rec", arg2, arg3, arg4)
        self.response(Gtk.ResponseType.ACCEPT)

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
