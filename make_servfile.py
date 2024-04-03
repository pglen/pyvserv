#!/usr/bin/env python3

import sys, os, site

os.system("which pyvserv > tmpfile")
fp = open("tmpfile") ;
execname  = fp.read().strip()
fp.close()
os.remove("tmpfile")

if not execname:
    print("pyvserv executable not found")
    sys.exit(1)

base = '''\
[Unit]
Description=pyvserv
After=multi-user.target

[Service]
Type=simple
# Run as installed user
Environment="PYTHONPATH=%s"
Environment="USER=%s"
Environment="HOME=%s"
ExecStart=%s

[Install]
WantedBy=multi-user.target
''' \
% (site.USER_SITE, os.getenv('USER'), os.getenv('HOME'), execname)

print(base)

