#!/usr/bin/env python2

import os
import os.path
import sys
from string import *

def run(cmd):
    os.system("%s >fltk-config.tmp"%cmd)
    return open("fltk-config.tmp").read()

if 0 and strip(run("fltk-config --version")) in ["1.1.5","1.1.6","1.1.7","1.1.8"]:
    print run("fltk-config "+" ".join(sys.argv[1:]))
else:
    if not os.path.exists("../ext/bin/fltk-config"):
        os.system("cd ../ext; bash build-fltk.sh >build-fltk.log 2>build-fltk.err")
    print run("../ext/bin/fltk-config "+" ".join(sys.argv[1:]))
    
