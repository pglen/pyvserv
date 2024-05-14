#!/usr/bin/env python3

import os, string, random, sys, subprocess, time, signal, base64
sys.path.append("..")

# Set parent as module include path
base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..', '..' ))

from pyvecc.Key import Key
from Crypto.Hash import SHA256
from Crypto import Random


# This repairs the path from local run to pip run.
# Remove pip version for local tests
try:
    from pyvcommon import support

    # Get Parent of module root
    sf = os.path.dirname(support.__file__)
    sf = os.path.dirname(sf)
    #print("sf", sf)
    sys.path.append(os.path.join(sf, "pyvcommon"))
    sys.path.append(os.path.join(sf, "pyvserver"))
    #sys.path.append(os.path.join(sf, "pyvgui"))
    #sys.path.append(os.path.join(sf, "pyvgui", "guilib"))

except:
    base = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    sys.path.append(os.path.join(base,  '..', "pyvserver"))
    #sys.path.append(os.path.join(base, "..", "pyvgui"))
    #sys.path.append(os.path.join(base, "..", "pyvgui", "guilib"))
    from pyvcommon import support


from pyvcommon import support, pycrypt, pyservsup, pyclisup
from pyvcommon import pysyslog

fdirx = os.path.expanduser("~/pyvserver/")
lockname = "tmp/lockfile"
exename = "../../pyvserver/pyvserv.py"

def start_server():

    return

    ''' Start server if needed. We start the server on the first test
      (they are executed aplhabettically), and end the server on
      the last test; '''

    if not os.path.isfile(fdirx + lockname):
        print("lockfile", os.path.isfile(fdirx + lockname))
        print("servfile", os.path.isfile(exename))
        print("servfile", exename)
        subprocess.Popen([exename, "-D"])

        #time.sleep(1)
        # wait until it starts .... with a fake connection
        ip = '127.0.0.1'
        hand = pyclisup.CliSup()
        try:
            resp2 = hand.connect(ip, 6666)
        except:
            pass
        hand.client(["quit"], "")

def stop_server():

    return

    # Stop server if needed
    if os.path.isfile(fdirx + lockname):
        print("lockfile", os.path.isfile(fdirx + lockname))
        fp = open(fdirx + lockname)
        buff = fp.read()
        print("buff:", buff)
        fp.close()
        os.kill(int(buff), signal.SIGTERM)
        time.sleep(1)

# Return a random string based upon length
allstr =  string.ascii_lowercase +  string.ascii_uppercase

def randstr(lenx):

    strx = ""
    for aa in range(lenx):
        ridx = random.randint(0, len(allstr)-1)
        rr = allstr[ridx]
        strx += str(rr)
    return strx

# ------------------------------------------------------------------------

test_dir = "test_data"
#if not os.path.isdir(test_dir):
#    os.mkdir(test_dir)

tmpfile = ""

#tmpfile = os.path.splitext(os.path.basename(__file__))[0]
#tmpfile = randstr(8)

# This one will get the last one
for mm in sys.modules:
    if "test_" in mm:
        #print("mod", mm)
        tmpfile = mm

#print("tmpfile", tmpfile)


baseall = os.path.join(test_dir, tmpfile)
print("baseall", baseall)
#assert 0

def createname(file):
    datafile = os.path.splitext(os.path.basename(file))[0]
    return test_dir + os.sep + datafile + ".pydb"

def createidxname(file):
    datafile = os.path.splitext(os.path.basename(file))[0]
    return test_dir + os.sep + datafile + ".pidx"

def create_db(fname = ""):

    core = None

    if fname == "":
       fname = baseall + ".pydb"

    try:
        # Fresh start
        os.remove(fname)
        pass
    except:
        pass

    try:
        core = twincore.TwinCore(fname)
        #print(core)
        #assert 0
    except:
        print(sys.exc_info())

    return core

def uncreate_db(fname = ""):

    if fname == "":
       fname = baseall + ".pydb"
       iname = baseall + ".pidx"
    try:
        # Fresh start for next run
        os.remove(fname)
        os.remove(iname)
        pass
    except:
        pass

# ------------------------------------------------------------------------
# Support utilities

# Return a random string based upon length

def randbin(lenx):

    strx = ""
    for aa in range(lenx):
        ridx = random.randint(0, 255)
        strx += chr(ridx)
    return strx.encode("cp437", errors="ignore")

# Re implemented just to show a different codebase. use: hand.session()

def session(hand, org_sess_key):

    resp = hand.client(["akey"], org_sess_key)
    assert resp[0] == 'OK'

    hhh = SHA256.new(); hhh.update(resp[2].encode())

    # Remember key
    if hhh.hexdigest() != resp[1]:
        print("Tainted key, aborting.")
        hand.client(["quit"])
        hand.close();
        assert 0

    hhh = SHA256.new(); hhh.update(resp[2].encode())
    ddd = hhh.hexdigest()
    assert ddd  == resp[1]

    try:
        #hand.pubkey = RSA.importKey(resp[2])
        hand.pubkey = Key.import_pub(resp[2])
    except:
        print("Cannot import public key.")
        support.put_exception("import key")
        #print ("cipher", cipher.can_encrypt())
        hand.client(["quit"])
        assert 0

    global cipher
    cipher = hand.pubkey

    # Generate communication key
    sess_key = base64.b64encode(Random.new().read(128))
    sss = SHA256.new(); sss.update(sess_key)

    sess_keyx = cipher.encrypt(sess_key)
    ttt = SHA256.new(); ttt.update(sess_keyx.encode())

    resp3 = hand.client(["sess", sss.hexdigest(), ttt.hexdigest(), sess_keyx],
                                 org_sess_key, False)
    #print(resp3)
    assert resp3[0] ==  "OK"

    return sess_key

def login(hand, sess_key, userx = "admin", passx = "1234"):

    resp = hand.client(["user", userx, ], sess_key)
    #print ("Server user response:", resp)
    #assert resp[0] == 'OK'
    resp = hand.client(["pass", passx, ], sess_key)
    #print ("Server pass response:", resp)
    #assert resp[0] == 'OK'
    return resp

# EOF

