#
# HappyDoc:docStringFormat='ClassicStructuredText'
#
#  p4vasp is a GUI-program and a library for processing outputs of the
#  Vienna Ab-inition Simulation Package (VASP)
#  (see http://cms.mpi.univie.ac.at/vasp/Welcome.html)
#
#  Copyright (C) 2003  Orest Dubay <odubay@users.sourceforge.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA



"""
P4VASP is a library for processing outputs from a VASP program
(http://cms.mpi.univie.ac.at/vasp/Welcome.html)
It is focussed mainly on the new xml output format,
but it offers also limited support for some older formats
(POSCAR, INCAR).

P4Vasp contains also an extensible GUI for visualisation and
an api for (reasonably) easy creation of extension applets.

For people, who want to write just a simple script rather than
an real applet, the easiest way
to get informations from the *vasprun.xml* file is to use
the XMLSystemPM class defined in p4vasp.SystemPM.

Here in the module root, the following things are defined:

Basic types:

  || **type**          || **string representation of type**  || **python type** ||
  || INTEGER_TYPE      || "int"                              || int             ||
  || STRING_TYPE       || "string"                           || str             ||
  || LOGICAL_TYPE      || "logical"                          || int             ||
  || FLOAT_TYPE        || "float"                            || float           ||

"""

import os
import os.path
import p4vasp.message
import p4vasp.schedule
import sys

try:
    from p4vasp.config import *
except:
    p4vasp_home = "/usr/lib/p4vasp"

#Indentaion string - two whitespaces by default.
INDENT        = "  "
INT_TYPE      = intern("int")
STRING_TYPE   = intern("string")
LOGICAL_TYPE  = intern("logical")
FLOAT_TYPE    = intern("float")

try:
    p4vasp_home = os.environ["P4VASP_HOME"]
except:
    pass

if getattr(sys,"frozen",None): # For PyInstaller standalone executables
    p4vasp_home = sys._MEIPASS

msg_=p4vasp.message.MessageDriver()
scheduler_=p4vasp.schedule.Scheduler()

def msg():
    return msg_

def scheduler():
    return scheduler_
def schedule(x):
    return scheduler_.schedule(x)
def scheduleFirst(x):
    return scheduler_.scheduleFirst(x)

def setMessageDriver(msgd):
    global msg_
    msg_=msgd


def getUserConfigurationDirectory():
    home=os.path.expanduser("~")
    p4vasp_dir=os.path.join(home,".p4vasp")
    if not os.path.isdir(p4vasp_dir):
        os.mkdir(p4vasp_dir)
    return p4vasp_dir

#def createGeneratorFromProcess(p):
#  while 1:
#    e=p.error()
#    if e:
#      msg().error(e)
#    else:
#      s=p.status()
#      if s:
#        msg().status(s)
#    msg().step(p.step(),p.total())
#    r = p.next()
#    if r:
#      yield r
#    else:
#      return
#
#def reportGenerator(g):
#  while 1:
#    msg().step()
#    yield g.next()
