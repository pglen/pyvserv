#!/usr/bin/env python3

import os, sys, getopt, signal, select, string, time, stat
import platform
import logging

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

#print(dir(logging))

# Use these levels for logging
DEBUG = 10
INFO = 20
WARN = 30
ERROR = 40
FATAL = 50

loggers = {}

def init_loggers(*name_arr):

    global logger_arr

    #print(dir(logging))
    #print("levels", logging.LOG_NOTICE, LOG_NOTICE)

    for aa, bb in name_arr:
        #print("logfile:", bb)
        loggerx  = _setup_logger(aa, bb)
        loggers[aa] = loggerx

    # TEST
    #for aa in loggers:
    #    print(aa.name)
    #    loggers[aa].info("")

def syslog(*message, **options):

    ''' Log to syslog '''

    #print("system:", message)

    mmm = ""
    for aa in message:
        mmm += str(aa) + " "

    #print(options)

    # DEBUG = 10  INFO = 20  WARN = 30  ERROR = 40  FATAL = 50
    lev = options.get("level", 20)
    if   lev == 10 :
        loggers['system'].debug(mmm)
    elif lev == 20 :
        loggers['system'].info(mmm)
    elif lev == 30 :
        loggers['system'].warn(mmm)
    elif lev == 40 :
        loggers['system'].error(mmm)
    elif lev == 50 :
        loggers['system'].fatal(mmm)
    else:
        # Assume info
        loggers['system'].info(mmm)

def    repliclog (*message, **options):

    ''' Log to replicator '''

    #print("replicate log:", message)
    mmm = ""
    for aa in message:
        mmm += str(aa) + " "

    lev = options.get("level", 20)
    if   lev == 10 :
        loggers['replic'].debug(mmm)
    elif lev == 20 :
        loggers['replic'].info(mmm)
    elif lev == 30 :
        loggers['replic'].warn(mmm)
    elif lev == 40 :
        loggers['replic'].error(mmm)
    elif lev == 50 :
        loggers['replic'].fatal(mmm)
    else:
        # Assume info
        loggers['replic'].info(mmm)

def _setup_logger(logger_name, log_file, level=LOG_NOTICE):

    logx = logging.getLogger(logger_name)
    format='%(asctime)s %(levelname)s %(message)s'
    datefmt='%Y/%m/%d %H:%M:%S'
    formatter = logging.Formatter(format, datefmt)
    fileHandler = logging.FileHandler(log_file)
    fileHandler.setFormatter(formatter)
    fileHandler.setLevel(level)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    streamHandler.setLevel(level)

    logx.setLevel(level)
    logx.addHandler(fileHandler)
    #logx.addHandler(streamHandler)
    return logx


#def openlog(ident=sys.argv[0], logoptions=0, facility=LOG_NOTICE):
#
#    logname = os.path.expanduser("~/pyvserver/log")
#    #print("openlog", logname)
#    if not os.path.isdir(logname):
#        os.mkdir(logname)
#
#    logging.basicConfig(filename=os.path.join(logname, "pyvserv.log"),
#                    filemode='a',
#                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
#                    datefmt='%Y/%m/%d %H:%M:%S',
#                    level=logging.DEBUG)
#
#    #if "Linux" in platform.system():
#    #    print("openlog:", ident)
#    #    syslog.openlog(ident) #, logoptions, facility)
#    #else:
#    #    pass
#

# EOF