#!/usr/bin/env python3

import sys, os, site

progname = "pyvserv"
dirname  = "./pip_pyvserv/"
execname = os.path.realpath(dirname + "bin/" + progname)

if not os.path.isfile(dirname + "bin/" + progname):
    print("pip_pyvserver virtual env is not installed. Use: ./pyvserv_env_insall.sh")
    sys.exit(1)

def find(what):
    aa = os.listdir(dirname + "lib" + os.sep)
    for bb in aa:
        if "python" in bb:
            #print("found", bb)
            return dirname + "lib" + os.sep + bb + os.sep + what

ppath = os.path.realpath(find("site-packages"))
#print("ppath:", ppath)

base = '''\
[Unit]
Description=pyvserv
After=multi-user.target

[Service]
Type=simple
ProtectHome=false

# Run as installed user
Environment="PYTHONPATH=%s"
Environment="USER=%s"
Environment="HOME=%s"
ExecStart=%s

[Install]
WantedBy=multi-user.target
''' \
% (ppath, os.getenv('USER'), os.getenv('HOME'), execname)

print(base)

# EOF
