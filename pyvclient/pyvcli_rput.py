#!/usr/bin/env python3

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, uuid, atexit, datetime

from Crypto import Random

# This repairs the path from local run to pip run.
# Remove pip version for local tests

try:
    from pyvcommon import support
    #print("sf", sf)
    # Get Parent of module root
    sf = os.path.dirname(support.__file__)
    sf = os.path.dirname(sf)
    sys.path.append(os.path.join(sf, "pyvcommon"))
    sys.path.append(os.path.join(sf, "pyvserver"))
except:
    #print("pathching")
    base = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    sys.path.append(os.path.join(base,  '..', "pyvserver"))
    from pyvcommon import support

from pyvcommon import support, pycrypt, pyservsup, pyclisup, pyvhash
from pyvcommon import pysyslog, comline

from pyvguicom import pgutils, pgtests

# ------------------------------------------------------------------------
# Functions from command line

#print( "            -n        - Number of records to put")

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p port   - Port to use (default: 6666)")
    print( "            -k keyval - Put this key")
    print( "            -n numrec - Put this many records")
    print( "            -t        - Test. Weak hash for testing")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    print()
    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", support.version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,      None],      \
    ["p:",  "port",     6666,   None],      \
    ["c:",  "comm",     "",     None],      \
    ["v",   "verbose",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["k:",  "putkey",   "",     None],      \
    ["n:",  "numrec",   1,     None],      \
    ["t",   "test",     0,    None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

conf = comline.Config(optarr)


# Vote structure: Sun 12.May.2024

#Save_data 730f3e8a-10c2-11ef-8e2a-d970e1627f70
#{'nuuid': 'c83c6562-0867-11ef-871c-6d4329725b1a',
#'name': 'Peter Glen', 'ndob': '1959/11/20', 'nnow': '2024-05-02T05:38:53',
#'noper': 'admin', 'uuid': '730f3e8a-10c2-11ef-8e2a-d970e1627f70',
#'vguid': '57d626a8-719c-4fc0-8bfa-62c214da695c',
#'vouid': '24573422-079a-11ef-8787-539d6f89ec87',
#'now': '2024-05-12T20:48:01', 'voper': 'admin',
#'buuid': '09269680-079e-11ef-8787-539d6f89ec87',
#'bname': 'New Test Ballot', 'dob': '2024/1/2',
#'vprim': 'John Doe', 'vsec': 'test',
#'vnotes': '', 'can1': 'John Doe', 'can2': 'Jane Dow',
#'can3': 'Johan Citizen', 'can4': 'Jorge Naturez',
#'can5': 'Jill Carpenter', 'can6': 'Jack Savage',
#'can7': 'James Folie', 'can8': 'Joe Cry'}

def genrec():

    pvh = pyvhash.BcData()
    # We mark this as 'test' so it can stay in the chain, if desired
    pvh.addpayload({"Test": "test" ,})
    dd = datetime.datetime.now()
    dd = dd.replace(microsecond=0)

    pvh.addpayload({'nuuid': str(uuid.uuid1()) })
    pvh.addpayload({'name': pgtests.simname(12) })
    pvh.addpayload({'ndob': pgtests.randate() })
    pvh.addpayload({'nnow': pgtests.randisodate() })
    pvh.addpayload({'noper': pgtests.randstr(random.randint(6, 22)) })
    pvh.addpayload({'uuid':  str(uuid.uuid1()) })
    pvh.addpayload({'vguid': str(uuid.uuid1()) })
    pvh.addpayload({'vouid': str(uuid.uuid1()) })

    pvh.addpayload({'now': dd.isoformat()} )

    pvh.addpayload({'buuid': str(uuid.uuid1()) })
    pvh.addpayload({'voper': pgtests.randstr(random.randint(6, 22)) })
    pvh.addpayload({'bname': pgtests.randstr(random.randint(6, 22)) })
    pvh.addpayload({'dob':   pgtests.randate()})

    lenx = 8
    randx =  random.randint(0, lenx-1)
    randy =  random.randint(0, lenx-1)
    for aa in range(lenx):
        rrr = pgtests.randstrrand(6, 22)
        pvh.addpayload({"can%d" % (aa+1)  : rrr,})

        if aa == randx:
            pvh.addpayload({'vprim': rrr, })
        if aa == randy:
            pvh.addpayload({'vsec': rrr, })

    rrr = pgtests.randstrrand(12, 32)
    pvh.addpayload({'vnotes': rrr})

    if conf.putkey:
        pvh.datax['header'] = conf.putkey

    #"test=%d" % pvh.num_zeros,

    #if not conf.quiet:
    #    print("Calculating hash ....",    end = " " );
    #    sys.stdout.flush()

    pvh.hasharr();
    if not pvh.checkhash():
        print("Error on check hash .. ")
        sys.exit(1)

    #if not conf.quiet:
    #    print("OK")

    if conf.test:
        pvh.num_zeros = 1

    if not conf.quiet:
        print("Calc PROW payload ...", end = " ")

    ttt = time.time()
    for aa in range(10):
        if pvh.powarr():
            break
        print("Calc PROW retrying ... %d" % aa)

    if not conf.quiet:
        print("OK, calc time %.3fms"% ((time.time() - ttt) * 1000) )

    if not pvh.checkpow():
        print("Giving up ... Error on PROW payload .. ")
        sys.exit(1)

    # Falsify test (passed)
    #pvh.datax["PayLoad"] |= {"Hello": 0}

    if conf.verbose:
        print(pvh.datax)

    #print("Chain cnt", pvh.cnt)
    #print("chain %.3fms" % ((time.time() - ttt) * 1000) )

    return pvh

# ------------------------------------------------------------------------

def mainfunct():

    args = conf.comline(sys.argv[1:])
    #print(vars(conf))

    pyclisup.verbose = conf.verbose
    pyclisup.pgdebug = conf.pgdebug

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    hand = pyclisup.CliSup()
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug
    hand.comm  = conf.comm

    pvh = genrec()
    try:
        respc = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    atexit.register(pyclisup.atexit_func, hand, conf)

    #resp3 = hand.client(["hello", "world"] , "", False)
    #print("Hello Resp:", resp3)

    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        sys.exit(0)

    #ttt = time.time()
    # Session estabilished, try a simple command
    #resp4 = hand.client(["hello",], conf.sess_key)
    #print("hello %.3fms" % ((time.time() - ttt) * 1000) )
    #if resp4[0] != "OK":
    #    print("Server hello resp:", resp4[1])
    #    sys.exit()

    #ttt = time.time()
    cresp = hand.client(["user", "admin"], conf.sess_key)
    #print("user %.3fms" % ((time.time() - ttt) * 1000) )
    #print ("Server user respo:", cresp)
    #ttt = time.time()
    cresp = hand.client(["pass", "1234"], conf.sess_key)
    #print("pass %.3fms" % ((time.time() - ttt) * 1000) )
    if cresp[0] != "OK":
        print("Cannot log on")
        sys.exit(1)
    if not conf.quiet:
        print ("Server pass resp:", cresp)

    cresp = hand.client(["dmode",], conf.sess_key)
    #print("dmode", cresp)
    if cresp[1] == '0':
        print("Enter twofa code: (ret to skip)", end = "")
        sesscode = input()
        if sesscode:
            cresp = hand.client(["twofa", sesscode], conf.sess_key)
            print ("Server twofa resp:", cresp)
            if cresp[0] != OK:
                print ("Server twofa failed")
                sys.exit(0)

    if conf.pgdebug > 2:
        print(pvh.datax)

    if hand.verbose:
        print("Sending Data:", pvh.datax)

    if conf.numrec == 1:
        cresp = hand.client(["rput", "vote", pvh.datax], conf.sess_key)
        if not conf.quiet:
            print ("resp:", cresp)
    else:
        for aa in range(conf.numrec):
            pvh = genrec()
            ttt = time.time()
            cresp = hand.client(["rput", "vote", pvh.datax], conf.sess_key)
            if not conf.quiet:
                print("putrec: %s  %.3fms" % (cresp[0], (time.time() - ttt) * 1000) )
            #print ("rput resp:", cresp)

    sys.exit(0)

if __name__ == '__main__':
    mainfunct()

# EOF

