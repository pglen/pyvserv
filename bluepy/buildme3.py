#!/usr/bin/env python3

import os, sys

from distutils.core import Extension, setup

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.argv = [sys.argv[0], 'build_ext', '-i']
setup(ext_modules = [Extension('bluepy3', ["bluepy_c.c", "bluepoint2.c"])])








