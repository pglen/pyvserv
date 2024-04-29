#!/usr/bin/env python

''' Action Handler for simple open file dialog '''

import datetime

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk

from pyvguicom import pgbox
from pyvguicom import pggui

def PopCal(ddd):

    ''' Open calendar dialog. While technically this is not a class,
        we attach state vars to the dialog class, pretending it is.
    '''

    dialog = Gtk.Dialog("Get Date",
                   None,
                   Gtk.DialogFlags.MODAL | \
                   Gtk.DialogFlags.DESTROY_WITH_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                    Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))

    dialog.set_default_response(Gtk.ResponseType.ACCEPT)

    dialog.set_position(Gtk.WindowPosition.CENTER)

    #dialog.set_size_request(800, 600)
    #dialog.set_default_size(800, 600)

    dialog.alt = 0
    dialog.ctrl = 0
    dialog.nofeed = False

    dialog.connect("key-press-event", area_key, dialog)
    dialog.connect("key-release-event", area_key, dialog)
    dialog.connect("button-press-event", area_butt, dialog)

    # Spacers
    dialog.pbox = dialog.get_content_area()
    dialog.cal = Gtk.Calendar()
    dialog.cal.connect("day-selected", day_changed, dialog)
    dialog.cal.connect("month-changed", day_changed, dialog)

    dialog.cal.connect("key-press-event", cal_key, dialog)
    dialog.cal.connect("key-release-event", cal_key, dialog)
    dialog.cal.connect("button-press-event", cal_butt, dialog)

    dialog.entry = Gtk.Entry()
    dialog.entry.connect("key-press-event", entry_key, dialog)
    dialog.entry.connect("key-release-event", entry_key, dialog)

    # Adjust for zero based
    try:
        dialog.cal.select_month(int(ddd[1])-1, int(ddd[0]))
        dialog.cal.select_day(int(ddd[2]))
    except:
        pass
    helpx = Gtk.Label(  \
        "Day --      \tLeft-Arrow            \tDay ++    \t     \tRight-Arrow\n"
        "Week --     \tUp-Arrow              \tWeek ++   \t     \tUp-Arrow\n"
        "Month --    \tCtrl-Left-Arrow       \tMonth ++  \t     \tCtrl-Right-Arrow\n"
        "Year --     \tAlt-Left-Arrow        \tYear ++   \t     \tAlt-Right-Arrow\n"
        "Decade --   \tAlt-S   \t  \t   \t   \tDecade ++ \t     \tAlt-A")

    hbox3 = Gtk.HBox()
    lab2 = Gtk.Label.new_with_mnemonic(" Dat_e: ")
    lab2.set_mnemonic_widget(dialog.entry)
    hbox3.pack_start(lab2, 0, 0, 2)
    hbox3.pack_start(dialog.entry, 1, 1, 2)
    hbox3.pack_start(Gtk.Label(" Entered text sets date as well. "), 0, 0, 2)

    dialog.pbox.pack_start(helpx, 1, 1, 0)

    dialog.pbox.pack_start(dialog.cal, 1, 1, 0)
    dialog.pbox.pack_start(pggui.xSpacer(8), 0, 0, 0)
    dialog.pbox.pack_start(hbox3, 0, 0, 0)
    dialog.pbox.pack_start(pggui.xSpacer(8), 0, 0, 0)

    dialog.abox = dialog.get_action_area()

    buttnow = Gtk.Button.new_with_mnemonic("Go to to_day")
    buttnow.connect("clicked", pynow, dialog.cal)
    dialog.abox.pack_start(buttnow, 0, 0, 0)

    buttpp = Gtk.Button.new_with_mnemonic("_Add 10 Years")
    buttpp.connect("clicked", decade_up, dialog.cal)
    dialog.abox.pack_start(buttpp, 0, 0, 0)

    buttmm = Gtk.Button.new_with_mnemonic("_Sub 10 Years")
    buttmm.connect("clicked", decade_down, dialog.cal)
    dialog.abox.pack_start(buttmm, 0, 0, 0)

    # Rearrange
    dialog.abox.reorder_child(buttnow, 0)
    dialog.abox.reorder_child(buttpp,  0)
    dialog.abox.reorder_child(buttmm,  0)

    dialog.entry.select_region(0, 0)
    dialog.show_all()
    #dialog.set_focus(dialog.entry)
    response = dialog.run()

    res = []
    if response == Gtk.ResponseType.ACCEPT:
        res = list(dialog.cal.get_date())
        # Adjust for zero based
        res[1] += 1

    #print ("date response", response, "result", res  )
    dialog.destroy()
    #del dialog
    return response, res

def entry_key(arg, event, self):
    if  event.type == Gdk.EventType.KEY_PRESS:
        #print("entry key:", arg, event,)
        pass
    elif  event.type == Gdk.EventType.KEY_RELEASE:
        #print("entry", self.entry.get_text())

        ppp = self.entry.get_text().split("/")
        if len(ppp) == 3:
            #print("ppp", ppp)
            self.nofeed = True
            self.cal.select_month(int(ppp[1])-1, int(ppp[0]))
            self.cal.select_day(int(ppp[2]))
            self.nofeed = False
    else:
        pass

def edit_changed(arg):
    print("edit changed:", arg)

def pynow(self, cal):
    dd = datetime.datetime.now()
    cal.select_month(int(dd.month)-1, dd.year)
    cal.select_day(dd.day)

def decade_up(self, cal):
    ddd = cal.get_date()
    cal.select_month(1, ddd[0] + 10)

def decade_down(self, cal):
    ddd = cal.get_date()
    cal.select_month(1, ddd[0] - 10)

def day_changed(arg1, self):

    if self.nofeed:
        return

    ddd = self.cal. get_date()
    #print("Day change", ddd)
    self.entry.set_text(str(ddd[0]) + "/" + str(ddd[1]+1) + \
                            "/" + str(ddd[2]))
    #sutil.usleep(10)
    #self.entry.select_region(0, 0)

# ------------------------------------------------------------------------

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
    ''' Compare for sort '''
    sort_column, _ = model.get_sort_column_id()
    value1 = model.get_value(row1, sort_column)
    value2 = model.get_value(row2, sort_column)
    #print("n", sort_column, value1, value2, type(value1))
    if int(value1) < int(value2):
        return -1
    elif int(value1) == int(value2):
        return 0
    else:
        return 1

def create_ftree(ts, text = None):
    ''' Create tree '''
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

# Butt handler
def area_butt(area, event, self):

    #print("area_butt", event.type)
    pass

# Cal butt handler
def cal_butt(area, event, self):

    #print("area_butt", event.type)
    if event.type == Gdk.EventType._2BUTTON_PRESS:
        #res = self.cal.get_date()
        #print("area_butt", "double_click", res)
        self.response(Gtk.ResponseType.ACCEPT)

def area_key(area, event, self):

    ''' Dialog key handler '''

    #print("area_key", event)

    # Do key down:
    if  event.type == Gdk.EventType.KEY_PRESS:

        if event.keyval == Gdk.KEY_Escape:
            return None

        if event.keyval == Gdk.KEY_Return:
            self.response(Gtk.ResponseType.ACCEPT)

        if event.keyval == Gdk.KEY_Alt_L or \
                event.keyval == Gdk.KEY_Alt_R:
            self.alt = True

        if event.keyval == Gdk.KEY_Control_L or \
                event.keyval == Gdk.KEY_Control_R:
            self.ctrl = True

        if event.keyval == Gdk.KEY_x or \
                event.keyval == Gdk.KEY_X:
            if self.alt:
                self.response(Gtk.ResponseType.CANCEL)

    elif  event.type == Gdk.EventType.KEY_RELEASE:
        if event.keyval == Gdk.KEY_Alt_L or \
              event.keyval == Gdk.KEY_Alt_R:
            self.alt = False

        if event.keyval == Gdk.KEY_Control_L or \
                event.keyval == Gdk.KEY_Control_R:
            self.ctrl = False
    else:
        pass
        #print("Invalid key state:", event.type)

    return None

def cal_set_date(tdiff, calx):

    ddd = calx.get_date()
    dd = datetime.datetime.now()
    dd = dd.replace(year=ddd[0], month=ddd[1]+1, day=ddd[2],
                                 hour=0, minute=0, second=0, microsecond=0)
    #print("prev", dd)
    dd += tdiff
    #print("after", dd)
    try:
        calx.select_month(dd.month-1, dd.year)
        calx.select_day(dd.day)
    except:
        #print("Cannot set date", dd)
        pass

# Call key handler
def cal_key(area, event, self):

    #print("cal_key", event)

    if  event.type == Gdk.EventType.KEY_PRESS:

        if self.alt:
            if event.keyval == Gdk.KEY_Left:
                #print("Alt left")
                ddd = self.cal.get_date()
                self.cal.select_month(ddd[1], ddd[0] - 1)
                return True

            if event.keyval == Gdk.KEY_Right:
                #print("Alt right")
                ddd = self.cal.get_date()
                self.cal.select_month(ddd[1], ddd[0] + 1)
                return True

        elif self.ctrl:
            if event.keyval == Gdk.KEY_Left:
                #print("Control left")
                delta = datetime.timedelta(-30.25)
                cal_set_date(delta, self.cal)
                return True

            if event.keyval == Gdk.KEY_Right:
                #print("Control right")
                delta = datetime.timedelta(+30.25)
                cal_set_date(delta, self.cal)
                return True
        else:
            if event.keyval == Gdk.KEY_Up:
                delta = datetime.timedelta(-7)
                cal_set_date(delta, self.cal)
                return True

            if event.keyval == Gdk.KEY_Down:
                delta = datetime.timedelta(7)
                cal_set_date(delta, self.cal)
                return True

            if event.keyval == Gdk.KEY_Left:
                delta = datetime.timedelta(-1)
                cal_set_date(delta, self.cal)
                return True

            if event.keyval == Gdk.KEY_Right:
                delta = datetime.timedelta(1)
                cal_set_date(delta, self.cal)
                return True

    return None

# eof
