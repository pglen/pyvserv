#!/usr/bin/env python

''' Action Handler for simple open file dialog '''

# pylint disable=C0103

import os
import sys
import datetime

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk

import pyvpacker

#from pyvguicom import sutil
from pyvguicom import pgbox

def ovd(vcore = ""):

    ''' open voter dialog. While technically thisis not a class,
        we attach state vers to the dialog class ...
    '''

    dialog = Gtk.Dialog("Open Record",
                   None,
                   Gtk.DialogFlags.MODAL | \
                   Gtk.DialogFlags.DESTROY_WITH_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                    Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))


    dialog.set_default_response(Gtk.ResponseType.ACCEPT)
    #dialog.set_position(Gtk.WindowPosition.CENTER)
    dialog.set_size_request(800, 600)
    dialog.set_default_size(800, 600)
    dialog.xmulti = []
    dialog.vcore = vcore
    dialog.packer = pyvpacker.packbin()

    #dialog.set_transient_for(pyedlib.pedconfig.conf.pe.mywin);

    dialog.connect("key-press-event", area_key, dialog)
    dialog.connect("key-release-event", area_key, dialog)

    # Spacers
    label1  = Gtk.Label("   ")
    label2 = Gtk.Label("   ")
    label3  = Gtk.Label("   ")
    label4 = Gtk.Label("   ")
    dialog.label11 = Gtk.Label("   ")
    dialog.label12 = Gtk.Label("   ")

    dialog.pbox = Gtk.HBox()
    #fill_path(dialog)

    dialog.vbox.pack_start(label4, 0, 0, 0)
    dialog.vbox.pack_start(dialog.pbox, 0, 0, 0)

    dialog.vbox.pack_start(pgbox.xSpacer(), 0, 0, 0)
    label13 = Gtk.Label.new(" Double click to select an entry.")
    dialog.vbox.pack_start(label13, 0, 0, 0)
    dialog.vbox.pack_start(pgbox.xSpacer(), 0, 0, 0)

    dialog.ts = Gtk.ListStore(str, str, str, str)
    tview = create_ftree(dialog.ts)

    scroll = Gtk.ScrolledWindow()

    tview.connect("row-activated",  tree_sel, dialog)
    tview.connect("cursor-changed",  tree_sel_row, dialog)
    dialog.tview = tview

    scroll.add(tview)

    frame2 = Gtk.Frame()
    frame2.add(scroll)

    hbox3 = Gtk.HBox()
    hbox3.pack_start(label1, 0, 0, 0)
    hbox3.pack_start(frame2, True, True, 0)
    hbox3.pack_start(label2, 0, 0, 0)

    dialog.vbox.pack_start(hbox3, True, True, 0)
    dialog.vbox.pack_start(label3, 0, 0, 0)

    dialog.show_all()
    populate(dialog)
    dialog.set_focus(tview)
    #dialog.set_focus(dialog.entry)

    response = dialog.run()

    res = []
    if response == Gtk.ResponseType.ACCEPT:
        xmodel = dialog.ts
        sel = tview.get_selection()
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
                res.append((xstr, xstr2, xstr3))
            iterx = xmodel.iter_next(iterx)

    #print ("response", response, "result", res  )
    dialog.destroy()
    #del dialog
    return response, res

# ------------------------------------------------------------------------

def populate(dialog):

    # Clear old contents:
    while True:
        root = dialog.ts.get_iter_first()
        if not root:
            break
        try:
            dialog.ts.remove(root)
        except:
            print("Exception on rm ts", sys.exc_info())

    sss = dialog.vcore.getdbsize()

    ddd2 = []
    for aa in range(sss-1, -1, -1):
        rrr = dialog.vcore.get_rec(aa)
        if not rrr:
            continue
        #print("rrr:", rrr)
        dec = dialog.packer.decode_data(rrr[1])[0]
        #print("dec:", dec)
        #print("dec", dec['name'], dec['dob'], dec['uuid'])
        uuu = rrr[0].decode()
        # See if we have this already
        found = False
        for aaa in ddd2:
            if aaa[2] == uuu:
                found = True
        if not found:
            #print("append")
            ddd2.append((dec['name'], dec['dob'],  uuu))

    for aa in ddd2:
        piter = dialog.ts.append(row=None)
        dialog.ts.set(piter, 0, aa[0])
        dialog.ts.set(piter, 1, aa[1])
        dialog.ts.set(piter, 2, aa[2])

    # --------------------------------------------------------------------

def compare(model, row1, row2, user_data):

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

def ncompare(model, row1, row2, user_data):
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

def create_ftree(ts):

    # create the tview using ts
    tv = Gtk.TreeView(model=ts)

    tv.set_search_column(0)
    tv.set_headers_clickable(True)
    #tv.set_enable_search(True)
    ts.set_sort_func(0, compare, None)
    ts.set_sort_func(1, ncompare, None)

    # create a CellRendererText to render the data
    cell = Gtk.CellRendererText()

    tvcolumn = Gtk.TreeViewColumn('Name')
    tvcolumn.set_min_width(240)
    tvcolumn.pack_start(cell, True)
    tvcolumn.add_attribute(cell, 'text', 0)
    tvcolumn.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
    tvcolumn.set_sort_column_id(0)
    tv.append_column(tvcolumn)

    tvcolumn = Gtk.TreeViewColumn('Date of Birth')
    tvcolumn.set_min_width(240)
    tvcolumn.pack_start(cell, True)
    tvcolumn.add_attribute(cell, 'text', 1)
    tvcolumn.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
    tvcolumn.set_sort_column_id(1)
    tv.append_column(tvcolumn)

    cell2 = Gtk.CellRendererText()
    tvcolumn2 = Gtk.TreeViewColumn('UUID')
    tvcolumn2.set_min_width(100)
    tvcolumn2.set_sort_column_id(2)
    tvcolumn2.pack_start(cell2, True)
    tvcolumn2.add_attribute(cell2, 'text', 2)
    tv.append_column(tvcolumn2)

    #tv.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

    return tv

    #sel.get_selected()

def tree_sel_row(xtree, dialog):

    #print("tree_sel_row", xtree)
    #sel = xtree.get_selection()
    #xmodel, xpath = sel.get_selected_rows()
    #if sel:
    #    try:
    #        #xiter2 = xmodel.get_iter(xpath)
    #        #xstr = xmodel.get_value(xiter2, 0)
    #        #xstr2 = xmodel.get_value(xiter2, 1)
    #        #print("tree_sel_row", xstr, xstr2)
    #        #dialog.entry.set_text(xstr)
    #        pass
    #    except:
    #        pass
    #        #print("sel row", sys.exc_info())
    #else:
    #    pass
    #    #dialog.entry.set_text("")
    pass

def tree_sel(xtree, xiter, xpath, dialog):

    #print ("tree_sel", xtree, xiter, xpath)
    sel = xtree.get_selection()
    xmodel, xpath = sel.get_selected_rows()
    if xpath:
        #for aa in xpath:
        #    xiter2 = xmodel.get_iter(aa)
        #    xstr = xmodel.get_value(xiter2, 0)
        #    xstr2 = xmodel.get_value(xiter2, 1)
        #    print("mul selstr: ", "'" + xstr + "'" )
        dialog.response(Gtk.ResponseType.ACCEPT)

# If directory, change to it
def click_dir_action(xstr):
    if xstr[0] == "[":
        xstr = xstr[1:len(xstr)-1]
    if os.path.isdir(xstr):
        #print ("dir", xstr)
        os.chdir(xstr)
        return True
    return False

# Call key handler
def area_key(area, event, self):

    #print "area_key", event
    # Do key down:
    if  event.type == Gdk.EventType.KEY_PRESS:

        if event.keyval == Gdk.KEY_Escape:
            #print "Esc"
            self.response(Gtk.ResponseType.CANCEL)

        if event.keyval == Gdk.KEY_Return:
            #print("Ret")
            self.response(Gtk.ResponseType.ACCEPT)

        if event.keyval == Gdk.KEY_Alt_L or \
                event.keyval == Gdk.KEY_Alt_R:
            self.alt = True

        if event.keyval == Gdk.KEY_x or \
                event.keyval == Gdk.KEY_X:
            if self.alt:
                self.response(Gtk.ResponseType.CANCEL)

    elif  event.type == Gdk.EventType.KEY_RELEASE:
        if event.keyval == Gdk.KEY_Alt_L or \
              event.keyval == Gdk.KEY_Alt_R:
            self.alt = False

    return None

# eof
