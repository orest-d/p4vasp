#!/usr/bin/env python2

import os
import os.path
import sys
from string import *

def run(cmd):
    os.system("%s >fltk-config.tmp"%cmd)
    return open("fltk-config.tmp").read()

# https://stackoverflow.com/questions/9877462/is-there-a-python-equivalent-to-the-which-command
def which(pgm):
    path=os.getenv('PATH')
    for p in path.split(os.path.pathsep):
        p=os.path.join(p,pgm)
        if os.path.exists(p) and os.access(p,os.X_OK):
            return p

if which('fltk-config')!=None and strip(run("fltk-config --version")) in ["1.3.4","1.3.5"]:
    print run("fltk-config "+" ".join(sys.argv[1:]))
else:
    if not os.path.exists("../ext/bin/fltk-config"):
        os.system("cd ../ext; bash build-fltk.sh >build-fltk.log 2>build-fltk.err")
    print run("../ext/bin/fltk-config "+" ".join(sys.argv[1:]))
    
