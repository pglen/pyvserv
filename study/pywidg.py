#!/usr/bin/env python
# vim: ts=4 sts=4 sw=4 ai et
# Copyright (C) 2006 Wander Boessenkool
#
#    sphinX is a graphical system-monitor using pycairo
#
#`   Author: Wander Boessenkool <wboessen@redhat.com>
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License as
#    published by the Free Software Foundation; either version 2 of
#    the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
#                                        02111-1307  USA
#

NAME = 'sphinX'
VERSION = '0.2'
AUTHORS = ['Wander Boessenkool <wboessen@redhat.com>']


import os
import sys

import gi
from gi.repository import GObject
import math
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
#import Gtk.gdk
import cairo
from datetime import datetime
from gi.repository import GConf

class cpustat(object):
    def __init__(self, u=0.0, n=0.0, s=0.0, id=0.0, io=0.0, ir=0.0, si=0.0):
        self.user = u
        self.nice = n
        self.system = s
        self.idle = id
        self.iowait = io
        self.irq = ir
        self.softirq = si
        self.cur_freq = 0.0
        self.max_freq = 1.0
        self.scale = self.cur_freq / self.max_freq

class memstat(object):
    def __init__(self, total=0 , free=0 , buffers=0, cached=0):
        self.total = total
        self.free = free
        self.buffers = buffers
        self.cached = cached
        self.used = total - free - buffers - cached

class wifistat(object):
    def __init__(self):
        self.quality = 0.0

def hr(i):
    sizes = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    i = float(i)
    index = 0
    while (i > 1024 and index < len(sizes) - 1):
        i = i / 1024.0
        index += 1
    return '%.2f %s' % (i, sizes[index])


class stats(object):
    def __init__(self):
        self.rawcpustats = [0 for i in range(8)]
        self.cpu = cpustat()
        self.mem = memstat()
        self.swap = memstat()
        self.wifi = wifistat()
        self.update_all()

    def update_mem(self):
        statlines = open('/proc/meminfo', 'r').readlines()
        meminfo = {}
        for line in statlines:
            splitline = line.split()
            meminfo[splitline[0]] = float(splitline[1])
        self.mem.total = meminfo['MemTotal:']
        self.mem.free = meminfo['MemFree:'] / self.mem.total
        self.mem.buffers = meminfo['Buffers:'] / self.mem.total
        self.mem.cached = meminfo['Cached:'] / self.mem.total
        self.mem.used = 1.0 \
                      - self.mem.free \
                      - self.mem.buffers \
                      - self.mem.cached
        self.swap.total = meminfo['SwapTotal:']
        if self.swap.total > 0:
            self.swap.free = meminfo['SwapFree:'] / self.swap.total
        else:
            self.swap.free = -1.0
        self.swap.used = 1.0 - self.swap.free

    def update_cpu(self):
        statlines = open('/proc/stat', 'r').readlines()
        for line in statlines:
            splitline = line.split()
            if splitline[0] == 'cpu':
                rawcpu = [int(i) for i in splitline[1:]]
        diff = [rawcpu[i] - self.rawcpustats[i] for i in range(8)]
        totaldiff = float(sum(diff))
        if totaldiff != 0:
            self.cpu.user = diff[0] / totaldiff
            self.cpu.nice = diff[1] / totaldiff
            self.cpu.system = diff[2] / totaldiff
            self.cpu.idle = diff[3] / totaldiff
            self.cpu.iowait = diff[4] / totaldiff
            self.cpu.irq = diff[5] / totaldiff
            self.cpu.softirq = diff[6] / totaldiff
        self.rawcpustats = rawcpu
        try:
            self.cpu.max_freq = float(file(
               '/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq', 'r').read())
            self.cpu.cur_freq = float(file(
               '/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq', 'r').read())
            self.cpu.scale = self.cpu.cur_freq / self.cpu.max_freq
        except:
            self.cpu.max_freq = 1.0
            self.cpu.cur_freq = 1.0
            self.cpu.scale = 0.0

    def update_wifi(self):
        try:
            statlines = file('/proc/net/wireless', 'r').readlines()
        except:
            statlines = ["", "", "0 0 0"]
        while len(statlines) < 3:
            statlines.append("0 0 0")
        self.wifi.quality = float(statlines[2].split()[2]) / 100.0

    def update_all(self):
        self.update_cpu()
        self.update_mem()
        self.update_wifi()

class Witsjet(Gdk.Window):
    '''
    __gsignals__ = {
    'draw':   'override',
    'screen-changed': 'override',
    }
    '''
    #window = Gdk.Window
    def __init__(self, stats):
        GObject.GObject.__init__(self)
        #Gtk.Window.__init__(self, title="clock")
        #super().__init__(title="Hello World")
        self.gconfclient = GConf.Client.get_default()
        sw = self.gconfclient.get_int('/apps/sphinX/width')
        if sw is 0:
            sw = 200
        sh = self.gconfclient.get_int('/apps/sphinX/height')
        if sh is 0:
            sh = 200
        sx = self.gconfclient.get_int('/apps/sphinX/xpos')
        sy = self.gconfclient.get_int('/apps/sphinX/ypos')
        self.set_size_request(32, 32)
        self.set_default_size(sw, sh)
        self.move(sx, sy)
        self.stats = stats
        self.stick()
        self.set_keep_below(True)
        self.set_property('accept-focus', False)
        self.set_property('skip-pager-hint', True)
        self.set_property('skip-taskbar-hint', True)
        self.set_property('resizable', True)
        self.drawing_stack = []
        self.set_app_paintable(True)
        self.set_decorated(False)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect('button-press-event', self.buttonpress)
        self.connect('configure-event', self.configure_handler)
        self.do_screen_changed()
        self.swapgradient = cairo.LinearGradient(0.2, 0.8, 1.0, 0.5)
        self.swapgradient.add_color_stop_rgba(0.0, 1.0, 0.0, 0.0, 0.6)
        self.swapgradient.add_color_stop_rgba(1.0, 1.0, 0.0, 0.0, 1.0)
        self.memgradient = cairo.LinearGradient(0.8, 0.2, 0.0, 0.5)
        self.memgradient.add_color_stop_rgba(0.0, 0.0, 1.0, 0.0, 0.6)
        self.memgradient.add_color_stop_rgba(1.0, 0.0, 1.0, 0.0, 1.0)
        self.scalegradient = cairo.LinearGradient(0.2, 0.8, 1.0, 0.5)
        self.scalegradient.add_color_stop_rgba(0.0, 0.0, 0.0, 1.0, 0.3)
        self.scalegradient.add_color_stop_rgba(1.0, 0.0, 0.0, 1.0, 1.0)
        self.menu = Gtk.Menu()
        '''
        about = Gtk.Action('About', None, None, Gtk.STOCK_ABOUT)
        about.connect('activate', self.about)
        aboutmenu = Gtk.ImageMenuItem()
        about.connect_proxy(aboutmenu)
        self.menu.add(aboutmenu)
        quit = Gtk.Action('Quit', None, None, Gtk.STOCK_QUIT)
        quit.connect('activate', Gtk.main_quit)
        quitmenu = Gtk.ImageMenuItem()
        quit.connect_proxy(quitmenu)
        self.menu.add(quitmenu)
        '''

    def about(self, *args):
        dialog = Gtk.AboutDialog()
        dialog.set_name('sphinX')
        dialog.set_logo_icon_name('system')
        dialog.set_copyright('(C) 2006 Red Hat, Inc.')
        dialog.set_authors(AUTHORS)
        dialog.set_version(VERSION)
        dialog.connect('response', lambda d, r: d.destroy())
        dialog.show()


    def configure_handler(self, window, event):
        w,h = self.get_size()
        x, y = self.get_position()
        self.gconfclient.set_int('/apps/sphinX/width', w)
        self.gconfclient.set_int('/apps/sphinX/height', h)
        self.gconfclient.set_int('/apps/sphinX/xpos', x)
        self.gconfclient.set_int('/apps/sphinX/ypos', y)
        return False

    def buttonpress(self, window, event):
        if event.button == 1:
            self.begin_move_drag(event.button,
                                 int(event.x_root),
                                 int(event.y_root),
                                 event.time)
            return True
        if event.button == 2:
            self.begin_resize_drag(Gdk.WINDOW_EDGE_SOUTH_EAST,
                                   event.button,
                                   int(event.x_root),
                                   int(event.y_root),
                                   event.time)
            return True
        if event.button == 3:
            self.menu.popup(None, None, None, event.button, event.time)
            return True

    def do_expose_event(self, event):
        window = self.get_window()
        (width, height) = self.get_size()
        self.Gtk.Window.begin_paint_rect(width, height)
        bmp = Gdk.Pixmap(None, width, height, 1)
        cm = bmp.cairo_create()
        cm.translate(5, 5)
        cm.scale(width - 10, height -10)
        cm.set_source_rgb(0, 0, 0)
        cm.set_operator(cairo.OPERATOR_DEST_OUT)
        cm.paint()
        cm.set_operator(cairo.OPERATOR_OVER)
        cm.arc(0.5, 0.5, 0.51, 0, 2 * math.pi)
        cm.fill()
        if not self.supports_alpha:
            self.window.shape_combine_mask(bmp, 0, 0)
        else:
            self.window.input_shape_combine_mask(bmp, 0, 0)
        cr = self.window.cairo_create()
        self.draw(cr, width, height)
        self.window.end_paint()

    def draw(self, cr, width, height):
        if self.supports_alpha:
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.0)
        else:
            cr.set_source_rgb(0.5, 0.5, 0.5)
        # Draw the background
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        cr.translate(5, 5)
        cr.scale(width - 10 , height -10)
        #Inner circle - wifi
        cr.move_to(0.8, 0.5)
        cr.arc(0.5, 0.5, 0.3, 0, 2 * math.pi)
        wifigrad = cairo.RadialGradient(0.5, 0.5, 0.0, 0.5, 0.5, 0.3)
        wifigrad.add_color_stop_rgba(0.0, 0.0, 0.0, 1.0, 1.0)
        interval = 0.02
        while interval < self.stats.wifi.quality:
            wifigrad.add_color_stop_rgba(interval, 0.0, 0.0, 1.0, 0.8)
            interval += 0.04
            wifigrad.add_color_stop_rgba(interval, 0.0, 0.0, 1.0, 0.4)
            interval += 0.04
        wifigrad.add_color_stop_rgba(1.0, 0.0, 0.0, 1.0, 0.0)
        cr.set_source(wifigrad)
        cr.fill()
        if self.stats.swap.free >= 0:
            #Lower small bar - swap
            cr.move_to(0.2, 0.5)
            cr.arc_negative(0.6, 0.5, 0.4, math.pi, self.stats.swap.free * math.pi)
            cr.arc(0.5, 0.5, 0.3, self.stats.swap.free * math.pi, math.pi)
            cr.close_path()
            cr.set_source(self.swapgradient)
            cr.fill()
            #Lower small outline
            cr.move_to(0.2, 0.5)
            cr.arc_negative(0.6, 0.5, 0.4, math.pi, 0)
            cr.arc(0.5, 0.5, 0.3, 0, math.pi)
            cr.close_path()
            cr.set_source_rgba(1.0, 1.0, 1.0, 1.0)
            cr.set_line_width(0.01)
            cr.stroke()
        #Lower large bar - cpu
        cr.move_to(1.0, 0.5)
        cr.arc(0.5, 0.5, 0.5, 0, (1.0 - self.stats.cpu.idle) * math.pi)
        cr.arc_negative(0.6, 0.5, 0.4, (1.0 - self.stats.cpu.idle) * math.pi, 0)
        cr.close_path()
        gradient = cairo.LinearGradient(1.0, 1.0, 0.0, 0.5)
        gradient.add_color_stop_rgba(0.0, 0.0, 1.0, 0.0, 0.6)
        u = self.stats.cpu.user + self.stats.cpu.nice
        s = self.stats.cpu.system + u
        i = self.stats.cpu.irq + self.stats.cpu.softirq + \
            self.stats.cpu.iowait + s
        gradient.add_color_stop_rgba(u, 0.0, 1.0, 0.0, 0.8)
        gradient.add_color_stop_rgba(s, 1.0, 1.0, 0.0, 0.8)
        gradient.add_color_stop_rgba(i, 1.0, 0.0, 0.0, 1.0)
        gradient.add_color_stop_rgba(1.0, 1.0, 0.0, 0.0, 1.0)
        cr.set_source(gradient)
        cr.fill()
        #Lower large outline
        cr.move_to(1.0, 0.5)
        cr.arc(0.5, 0.5, 0.5, 0, math.pi)
        cr.arc_negative(0.6, 0.5, 0.4, math.pi, 0)
        cr.close_path()
        cr.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        cr.set_line_width(0.01)
        cr.stroke()
        #Upper small bar - mem
        cr.move_to(0.8, 0.5)
        cr.arc_negative(0.4, 0.5, 0.4, 0, -self.stats.mem.used * math.pi)
        cr.arc(0.5, 0.5, 0.3, -self.stats.mem.used * math.pi, 0)
        cr.close_path()
        cr.set_source(self.memgradient)
        cr.fill()
        #Upper small outline
        cr.move_to(0.8, 0.5)
        cr.arc_negative(0.4, 0.5, 0.4, 0, math.pi)
        cr.arc(0.5, 0.5, 0.3, math.pi, 0)
        cr.close_path()
        cr.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        cr.set_line_width(0.01)
        cr.stroke()
        if self.stats.cpu.scale > 0.0:
            #Upper large bar - cpu-scale
            cr.move_to(0.0, 0.5)
            cr.arc(0.4, 0.5, 0.4, math.pi, math.pi * -(1 - self.stats.cpu.scale))
            cr.arc_negative(0.5, 0.5, 0.5, math.pi * -(1 - self.stats.cpu.scale),
                            math.pi)
            cr.close_path()
            cr.set_source(self.scalegradient)
            cr.fill()
            #Upper large outline
            cr.move_to(0.0, 0.5)
            cr.arc(0.4, 0.5, 0.4, math.pi, 0)
            cr.arc_negative(0.5, 0.5, 0.5, 0, math.pi)
            cr.close_path()
            cr.set_source_rgba(1.0, 1.0, 1.0, 1.0)
            cr.set_line_width(0.01)
            cr.stroke()
        #Clock
        curtime = datetime.now()
        h = float(curtime.hour)
        m = float(curtime.minute)
        s = float(curtime.second)
        m += s / 60
        h += m / 60
        h = (h % 12) / 6 * math.pi
        m = m / 30 * math.pi
        s = s / 30 * math.pi
        try:
            cr.push_group()
        except:
            pass
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.move_to(0.5, 0.5)
        cr.line_to(0.5 + 0.3 * math.sin(h), 0.5 - 0.3 * math.cos(h))
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.8)
        cr.set_line_width(0.075)
        cr.stroke_preserve()
        cr.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        cr.set_line_width(0.05)
        cr.stroke()
        cr.move_to(0.5, 0.5)
        cr.line_to(0.5 + 0.35 * math.sin(m), 0.5 - 0.35 * math.cos(m))
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.8)
        cr.set_line_width(0.065)
        cr.stroke_preserve()
        cr.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        cr.set_line_width(0.04)
        cr.stroke()
        cr.move_to(0.5, 0.5)
        cr.line_to(0.5 + 0.4 * math.sin(s), 0.5 - 0.4 * math.cos(s))
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.8)
        cr.set_line_width(0.055)
        cr.stroke_preserve()
        cr.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        cr.set_line_width(0.03)
        cr.stroke()
        cr.move_to(0.55, 0.5)
        cr.arc(0.5, 0.5, 0.05, 0, 2 * math.pi)
        cr.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        cr.fill_preserve()
        cr.set_line_width(0.015)
        cr.set_source_rgba(0.0, 0.0, 0.0, 1.0)
        cr.stroke()
        try:
            cr.pop_group_to_source()
            cr.paint_with_alpha(0.5)
        except:
            pass

    def do_screen_changed(self, old_screen=None):
        screen = self.get_screen()
        try:
            colormap = screen.get_rgba_visual()
            if colormap:
                self.supports_alpha = True
            else:
                self.supports_alpha = False
        except:
            colormap = screen.get_rgb_visual()
            self.supports_alpha = False
        if colormap:
            self.set_visual(colormap)

    def update(self):
        self.stats.update_all()
        self.do_expose_event('update')
        return True

if __name__ == '__main__':
    mystat = stats()
    mystat.update_all()
    window = Witsjet(mystat)
    window.set_title('Witsjet Demo')
    window.connect('delete-event', Gtk.main_quit)
    window.show()
    GObject.timeout_add(1000, window.update)
    try:
        Gtk.main()
    except KeyboardInterrupt:
        pass



































































































































































































































































































































































































































































