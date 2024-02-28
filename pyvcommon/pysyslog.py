#!/usr/bin/env python3

import os, sys, getopt, signal, select, string, time, stat
import platform
try:
    import logging
except:
    print("using fake syslog")

LOG_EMERG, LOG_ALERT, LOG_CRIT, LOG_ERR, LOG_WARNING, \
LOG_NOTICE, LOG_INFO, LOG_DEBUG = range(8)

LOG_KERN, LOG_USER, LOG_MAIL, LOG_DAEMON, LOG_AUTH, \
LOG_SYSLOG, LOG_LPR, LOG_NEWS, LOG_UUCP = range(0,65,8)

LOG_CRON   = 120
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

def syslog(*message, **options):

    #print("syslog:", message)
    mmm = ""
    for aa in message:
        mmm += str(aa)
    logging.info(mmm)

    #if "Linux" in platform.system():
    #    #print("syslog linux", message)
    #    #syslog.syslog(message)
    #    logging.info(message)
    #else:
    #    print (message)
    #pass

def openlog(ident=sys.argv[0], logoptions=0, facility=LOG_NOTICE):

    logname = os.path.expanduser("~/pyvserver/log")
    print("openlog", logname)
    if not os.path.isdir(logname):
        os.mkdir(logname)

    logging.basicConfig(filename=os.path.join(logname, "pyvserv.log"),
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S',
                    level=logging.DEBUG)

    #if "Linux" in platform.system():
    #    print("openlog:", ident)
    #    syslog.openlog(ident) #, logoptions, facility)
    #else:
    #    pass

def closelog():
    pass

def setlogmask(maskpri):
    pass

#EOF
