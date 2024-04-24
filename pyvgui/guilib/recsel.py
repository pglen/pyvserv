#!/usr/bin/env python

''' Action Handler self for open records self '''

# pylint: disable=C0103

import os
import sys
import datetime

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk

import pyvpacker

from pyvguicom import pggui
from pyvguicom import pgsel
from pyvguicom import pgutils

from pyvcommon import pyvhash

''' Open voter self. We attach state vars to the self class
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
                " to selection, press space to select")

        self.vbox.pack_start(simp, 0, 0, 0)

        self.vbox.pack_start(pggui.xSpacer(), 0, 0, 0)
        label13 = Gtk.Label.new("Double click to select an entry.")
        self.vbox.pack_start(label13, 0, 0, 0)
        self.vbox.pack_start(pggui.xSpacer(), 0, 0, 0)

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

        label3  = Gtk.Label("  ")
        self.vbox.pack_start(label3, 0, 0, 0)

        self.abox = self.get_action_area()

        self.stopbutt = Gtk.Button("Stop Loading")
        self.stopbutt.set_sensitive( False )
        self.stopbutt.connect("clicked", self.stopload)

        self.abox.pack_start(self.stopbutt, 1, 1, 0)
        self.abox.reorder_child(self.stopbutt, 0)

        self.labsss = Gtk.Label("Awaiting filter selection ...")
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
        self.ts.set(piter, 0, "Select Appropriate filter.")
        self.ts.set(piter, 1, "From TOP row")
        self.ts.set(piter, 2, "Selecting 'All' may take a long time to load")

    # ------------------------------------------------------------------------

    def populate(self, filterx = ""):

        ''' populate tree '''

        if len(filterx):
            filterx = filterx.upper()
        #print("pop", filterx)

        self.stop = False

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
        sss = self.vcore.getdbsize()

        ddd2 = []
        for aa in range(sss-1, -1, -1):
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
                self.labsss.set_text("Scanning:  %d/%d Loading: %d" %
                            (sss, self.scan_cnt, self.rec_cnt))
                self.get_window().set_cursor(self.w_cursor)
                pgutils.usleep(5)

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
            #    if aaa[2] == uuu:
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
            if filterx == "All":
                if self.rec_cnt >= 10000:
                    sig = True
            else:
                if self.rec_cnt >= 1000:
                    sig = True
            if sig:
                msg = "Loaded 10000 records, stopping. \n" \
                        "If your intended record is not included, please narrow filter."
                pggui.message(msg)
                self.set_focus(self.tview)
                break

        self.stopbutt.set_sensitive( False )

        for aa in ddd2:
            piter = self.ts.append(row=None)
            #print("row", aa)
            self.ts.set(piter, 0, aa[0])
            self.ts.set(piter, 1, aa[1])
            self.ts.set(piter, 2, aa[2])
            self.ts.set(piter, 3, aa[3])

        self.labsss.set_text("%s records." % self.rec_cnt)

        self.get_window().set_cursor()

        # --------------------------------------------------------------------

    def compare(self, model, row1, row2, user_data):

        ''' compare fields for sort '''

        self.sort_cnt += 1
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
        ts.set_sort_func(1, self.dcompare, None)
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
            selfx.response(Gtk.ResponseType.ACCEPT)

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
