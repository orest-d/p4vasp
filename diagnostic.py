#!/usr/bin/python2


print "p4vasp Diagnostics"
try:
  import os
except:
  print """Can not import the os module.
This indicates a serious problem with your python instalation.
"""
  raise SystemExit
try:
  import os.path
except:
  print """Can not import the os.path module.
This indicates a serious problem with your python instalation.
"""
  raise SystemExit
try:
  import sys
except:
  print """Can not import the sys module.
This indicates a serious problem with your python instalation.
"""
  raise SystemExit
try:
  import traceback
except:
  print """Can not import the traceback module.
This indicates a serious problem with your python instalation.
"""
  raise SystemExit
try:
  from string import *
except:
  print """Can not import the string module.
This indicates a serious problem with your python instalation.
"""
  raise SystemExit

def strfile(path):
  try:
    f=open(path,"r")
    s=f.read()
    f.close()
    return s
  except:
    return "???"

def sfile(path):
  return join(split(strip(strfile(path)),"\n"),"\n                ")

def strcmd(cmd):
  try:
    f=os.popen(cmd,"r")
    s=f.read()
    f.close()
    return s
  except:
    return "???"
def scmd(cmd):
  return join(split(strip(strcmd(cmd)),"\n"),"\n                ")
  
  
print
print "Python version:",join(split(sys.version,"\n"),"\n                ")
print "Platform:      ",sys.platform
print "Issue:         ",sfile("/etc/issue")
print "Hostname:      ",sfile("/proc/sys/kernel/hostname")
print "LINUX:         ",sfile("/proc/sys/kernel/ostype"),sfile("/proc/sys/kernel/osrelease")

print  
print "Executable:    ",sys.executable
print
print "Module paths:  ",join(sys.path,      "\n                ")
print 
print "Enviromental variables:"
for x in ["P4VASP_HOME","PYTHONPATH","PYTHONHOME"]:
  if x in os.environ:
    print "%-14s= %s"%(x,os.environ[x])
  else:
    print "%-14s  not set"%(x)



def get_pygtk():
  print """You need to get version 2.x of PyGTK for this to work.
Usually it is located in a python-gtk or python-pygtk package.
You can get source code from http://www.pygtk.org """
  raise SystemExit



try:
  import pygtk
  pygtk.require("2.0")
except ImportError:
  try:
    import gtk
  except ImportError:
    get_pygtk()
  if not hasattr(gtk, "Window"): # renamed in version 2.0
    get_pygtk()
  try:
    import gtk.gdk
  except ImportError:
    print """Your python-gtk instalation is not complete.
Though the gtk seems to be working, the gtk.gdk is missing.
You can get complete source code from http://www.pygtk.org
"""
  try:
    import gtk.glade
  except ImportError:
    print """Your python-gtk instalation is not complete.
Though the gtk seems to be working, the gtk.glade is missing.
Try to find the corresponding package.
You can get complete source code from http://www.pygtk.org
"""
  try:
    import pango
  except ImportError:
    print """Your python-gtk instalation is not complete.
Though the gtk seems to be working, the pango is missing.
Try to find the corresponding package.
You can get complete source code from http://www.pygtk.org
"""
    
except AssertionError:
  get_pygtk()

print
s="/usr/include/python/Python.h"
if not os.path.exists(s):
  print "Python.h was not found in",s
else:
  print "Python.h:      ",s

if "usage" not in lower(strcmd("fltk-config")):
  print """
The fltk-config does not seem to work.
Please, try it manually. (Type fltk-config in your console.)
"""
print "FLTK:"
print "  fltk-config: ",scmd("which fltk-config")
print "  version:     ",scmd("fltk-config --version")
print "  api-version: ",scmd("fltk-config --api-version")
print "  libs:        ",join(split(strip(strcmd("fltk-config --use-gl --libs"))),"\n                ")
print "  c++ flags:   ",join(split(strip(strcmd("fltk-config --use-gl --cxxflags"))),"\n                ")

try:
  from p4vasp import *
  print  
  print "p4vasp configuration info:"
  for x in ["p4vasp_home","name","version","release","build_date"]:
    try:
      val=eval(x)
      print "%-14s= %s"%(x,str(val))
    except NameError:
      print "%-14s  not defined"%(x)
except:
  print
  print
  print """Can not import the p4vasp module.
The p4vasp seems not to be installed.
"""

try:
  import _cp4vasp
except:
  print """Can not import _cp4vasp. Have you compiled and installed it ?
(make; make install)
"""
  s="/usr/include/python/Python.h"
  if not os.path.exists(s):
    print """
You probably will not be able to compile, since Python.h is missing.
It is expected to be in %s.
Most likely you do not have the python development headders installed.
They are usually located in a package called python-devel (or something like that).
If you have the headders at a non-standart path, you will need to modify
your Makefiles (mainly thesrc/Makefile).
"""
  if "usage" not in lower(strcmd("fltk-config")):
    print """
Since the fltk-config does not seem to work (please, try it manually),
you probably will not be able to compile.
Check your fltk instalation. Maybe you are missing the whole installation,
or just the development headders (usually in a package called fltk-devel).
You can download fltk from www.fltk.org.
"""
  
try:
  import cp4vasp
except:
  print """
Can not import cp4vasp, however the _cp4vasp can be imported.
I have no clue what is the problem...
Maybe the stack trace will help:
"""
  traceback.print_exc()
