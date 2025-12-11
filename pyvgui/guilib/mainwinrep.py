#!/usr/bin/env python

import os, sys, getopt, signal, random, time, warnings, datetime, uuid

from pymenu import  *
from pgui import *

base = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(os.path.join(base, '../../'))

sys.path.append('../../')

from pyvguicom import pgutils # import  *
from pyvguicom import pggui   #import  *
from pyvguicom import pgsimp  #import  *

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

try:
    from pyvcommon import support

    # Get Parent of module root
    sf = os.path.dirname(support.__file__)
    sf = os.path.dirname(sf)
    #print("sf", sf)
    sys.path.append(os.path.join(sf, "pyvcommon"))
    sys.path.append(os.path.join(sf, "pyvserver"))
    sys.path.append(os.path.join(sf, "pyvgui"))
    sys.path.append(os.path.join(sf, "pyvgui", "guilib"))

except:
    #print("pip inc")
    base = os.path.dirname(__file__)
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    sys.path.append(os.path.join(base,  '..', "pyvserver"))
    sys.path.append(os.path.join(base, "..", "pyvgui"))
    sys.path.append(os.path.join(base, "..", "pyvgui", "guilib"))
    from pyvcommon import support

from pyvcommon import pyvhash, pyservsup

import pymisc

from pydbase import twincore

# ------------------------------------------------------------------------

STATE_FNAME   = "rstate.pydb"

def cutid(uuu):
    if len(uuu) < 32:
        return uuu
    return uuu[:12] + " .. " + uuu[-8:]

def print_handles(strx = ""):
    ''' Debug helper. Only on Linux. '''
    open_file_handles = os.listdir('/proc/self/fd')
    print(strx, 'open file handles: ' + ', '.join(map(str, open_file_handles)))

class   OneBox(Gtk.Frame):

    def __init__(self):

        super().__init__()

        vbox = Gtk.VBox()
        self.defarr = ("Org. Date", "Host", "Record", "Last Attempt",
                        "Try Count", "Message" )
        self.cnt = len(self.defarr)
        self.labarr = []

        for aa in range(self.cnt):
            self.labarr.append(Gtk.Label(label=self.defarr[aa]))

        for aa in range(self.cnt):
            vbox.pack_start(self.labarr[aa], 1, 1, 0)

        scroll = Gtk.ScrolledWindow() ; scroll.add(vbox)
        self.add(scroll)
        self.set_size_request(-1, 160)

    def filldef(self):
        for aa in range(self.cnt):
            self.labarr[aa].set_text(self.defarr[aa])

# ------------------------------------------------------------------------

class MainWin(Gtk.Window):

    def __init__(self, globals):

        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)

        self.globals = globals
        self.in_timer = False
        self.old_curr = 0
        self.old_size = 0
        self.globals.conf.iconf  = os.path.dirname(globals.conf.me) + \
                                     os.sep + "images/pyvvotemon.png"
        try:
            #print("iconf", self.conf.iconf)
            ic = Gtk.Image(); ic.set_from_file(self.globals.conf.iconf)
            self.set_icon(ic.get_pixbuf())
        except:
            pass

        self.set_title("PyVServer Replication Monitor GUI")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

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

        if www / hhh > 2:
            self.set_default_size(6*www/8, 6*hhh/8)
        else:
            self.set_default_size(6*www/8, 6*hhh/8)

        '''self.set_flags(Gtk.CAN_FOCUS | Gtk.SENSITIVE)
        self.set_events(  Gdk.POINTER_MOTION_MASK |
                            Gdk.POINTER_MOTION_HINT_MASK |
                            Gdk.BUTTON_PRESS_MASK |
                            Gdk.BUTTON_RELEASE_MASK |
                            Gdk.KEY_PRESS_MASK |
                            Gdk.KEY_RELEASE_MASK |
                            Gdk.FOCUS_CHANGE_MASK )
        '''
        self.connect("destroy", self.OnExit)
        self.connect("key-press-event", self.key_press_event)
        self.connect("button-press-event", self.button_press_event)

        try:
            self.set_icon_from_file("icon.png")
        except:
            pass

        vbox = Gtk.VBox(); hbox4 = Gtk.HBox()
        self.allbox = []

        #merge = Gtk.UIManager()
        #self.mywin.set_data("ui-manager", merge)
        #aa = create_action_group(self)
        #merge.insert_action_group(aa, 0)
        #self.add_accel_group(merge.get_accel_group())
        #merge_id = merge.new_merge_id()
        #try:
        #    mergeid = merge.add_ui_from_string(ui_info)
        #except GLib.GError as msg:
        #    print("Building menus failed: %s" % msg)
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
        self.status = pymisc.Status()
        self.status.maxlen = 128
        self.status.idlestr = "Waiting ..."

        hbox4.pack_start(self.status.scroll, 1, 1, 0)
        lab1a = Gtk.Label("   ");
        hbox4.pack_start(lab1a, 0, 0, 0)

        self.dblab = Gtk.Label("  ");

        hbox4.pack_start(self.dblab, 0, 0, 4)

        #butt1 = Gtk.Button.new_with_mnemonic(" _New ")
        ##butt1.connect("clicked", self.show_new, window)
        #hbox4.pack_start(butt1, False, 0, 2)

        butt2 = Gtk.Button.new_with_mnemonic(" E_xit ")
        butt2.connect("clicked", self.OnExit, self)
        hbox4.pack_start(butt2, False, 0, 0)

        lab2 = Gtk.Label("  ");  hbox4.pack_start(lab2, 0, 0, 0)

        #hbox2 = Gtk.HBox()
        #lab3 = Gtk.Label("q");  hbox2.pack_start(lab3, 0, 0, 0)
        #lab4 = Gtk.Label("r");  hbox2.pack_start(lab4, 0, 0, 0)
        #vbox.pack_start(hbox2, False, 0, 0)

        self.numofcols = 4 ;  self.numofrows = 8
        vbox3 = Gtk.VBox()
        for bb in range(self.numofrows):
            hbox5 = Gtk.HBox()
            for aa in range(self.numofcols):
                vbox_1 = Gtk.VBox()
                pos = bb * self.numofcols + aa
                onebox = OneBox()
                self.allbox.append(onebox)
                hbox5.pack_start(onebox, 1, 1, 2)
            vbox3.pack_start(hbox5, 1, 1, 2)

        scroll = Gtk.ScrolledWindow()
        scroll.add(vbox3)
        vbox.pack_start(scroll, 1, 1, 4)
        vbox.pack_start(hbox4, False, 0, 2)

        self.add(vbox)
        self.show_all()

        self.timer()    # Respond before timer
        GLib.timeout_add(2000, self.timer)

    def main(self):
        Gtk.main()

    def  OnExit(self, arg, srg2 = None):
        self.exit_all()

    def exit_all(self):
        Gtk.main_quit()

    def key_press_event(self, win, event):
        #print( "key_press_event", win, event)
        pass

    def button_press_event(self, win, event):
        #print( "button_press_event", win, event)
        pass

    def activate_action(self, action):

        #dialog = Gtk.MessageDialog(None, Gtk.DIALOG_DESTROY_WITH_PARENT,
        #    Gtk.MESSAGE_INFO, Gtk.BUTTONS_CLOSE,
        #    'Action: "%s" of type "%s"' % (action.get_name(), type(action)))
        # Close dialog on user response
        #dialog.connect ("response", lambda d, r: d.destroy())
        #dialog.show()

        warnings.simplefilter("ignore")
        strx = action.get_name()
        warnings.simplefilter("default")

        #print ("activate_action", strx)

    def activate_quit(self, action):
        #print( "activate_quit called")
        self.OnExit(False)

    def activate_exit(self, action):
        #print( "activate_exit called" )
        self.OnExit(False)

    def activate_about(self, action):
        #print( "activate_about called")
        pass

    def timer(self):

        #print("Called timer")

        if self.in_timer:
            return True
        in_timer = True

        conf = self.globals.conf

        # Read status
        stname = os.path.join(pyservsup.globals.chaindir, conf.kind, STATE_FNAME)

        statecore  = twincore.TwinCore(stname)
        statebdsize = statecore.getdbsize()

        curr = 0
        for cc in range(statebdsize -1, -1, -1):
            try:
                srec = statecore.get_rec(cc)
            except:
                pass
            if not srec:
                continue        # Deleted record

            if srec[0] == b"del":
                sarr = conf.packer.decode_data(srec[2])[0]
                if conf.verbose:
                    print("del sarr:", sarr)
                else:
                    dd = datetime.datetime.strptime(sarr['orgnow'], pyvhash.datefmt)
                    #print(pyvrepsup.cutid(sarr['header']), dd, sarr['host'], sarr['count'])
                    print("del:", sarr['header'], sarr['host'], sarr['count'])
            else:
                sarr = conf.packer.decode_data(srec[1])[0]
                #print("sarr:", sarr)
                #dd = datetime.datetime.strptime(sarr['orgnow'], pyvhash.datefmt)
                #print(pyvrepsup.cutid(sarr['header']), dd, sarr['host'], sarr['count'])
                #print(sarr['header'], sarr['host'], sarr['count'])

                self.allbox[curr].labarr[0].set_text(cutid(sarr['orgnow']))

                self.allbox[curr].labarr[1].set_text(cutid(sarr['host']))
                self.allbox[curr].labarr[1].set_tooltip_text(sarr['host'])

                self.allbox[curr].labarr[2].set_text(cutid(sarr['header']))
                self.allbox[curr].labarr[2].set_tooltip_text(sarr['header'])

                self.allbox[curr].labarr[3].set_text(cutid(sarr['LastAttempt']))
                self.allbox[curr].labarr[4].set_text(cutid(sarr['count']))
                self.allbox[curr].labarr[5].set_text(sarr['message'].strip())
                curr += 1

            if curr >= self.numofrows * self.numofcols:
                break

        #print("curr", curr)
        if self.old_curr != curr or self.old_size != statebdsize:
            self.status.set_status_text("%d entries shown, total of %d records." % (curr, statebdsize))
            self.old_curr = curr
            self.old_size = statebdsize

        self.dblab.set_text("Replicator data size: %-12d" % statebdsize)

        while True:
            if curr >= self.numofrows * self.numofcols:
                break
            self.allbox[curr].filldef()
            curr += 1

        del statecore

        #print_handles()

        in_timer = False
        return True

# Start of program:

if __name__ == '__main__':

    pass

# EOF
