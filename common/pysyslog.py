#!/usr/bin/env python3

import os, sys, getopt, signal, select, string, time, stat
import platform
import syslog as sl

LOG_EMERG, LOG_ALERT, LOG_CRIT, LOG_ERR, LOG_WARNING, \
LOG_NOTICE, LOG_INFO, LOG_DEBUG = range(8)

LOG_KERN, LOG_USER, LOG_MAIL, LOG_DAEMON, LOG_AUTH, \
LOG_SYSLOG, LOG_LPR, LOG_NEWS, LOG_UUCP = range(0,65,8)

LOG_CRON = 120
LOG_LOCAL0 = 128
LOG_LOCAL1 = 136
LOG_LOCAL2 = 144
LOG_LOCAL3 = 152
LOG_LOCAL4 = 160
LOG_LOCAL5 = 168
LOG_LOCAL6 = 176
LOG_LOCAL7 = 184

LOG_PID = 1
LOG_CONS = 2
LOG_NDELAY = 8
LOG_NOWAIT = 16

def syslog(message):

    print("loging:", message)

    if "Linux" in platform.system():
        #print("syslog linux")
        sl.syslog(message)
    else:
        print (message)

    pass

def openlog(ident=sys.argv[0], logoptions=0, facility=LOG_NOTICE):

    if "Linux" in platform.system():
        print("openlog:", ident)
        sl.openlog(ident) #, logoptions, facility)
    else:
        pass

def closelog():
    pass

def setlogmask(maskpri):
    pass

#EOF






