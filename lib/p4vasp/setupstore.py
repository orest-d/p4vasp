#!/usr/bin/python2

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
 setupstore serves for creation of setup StoreProfile
"""


from p4vasp.store import *
from string import *
from types import *

import p4vasp.applet.Applet
import p4vasp.applet.EnergyConvergenceApplet
import p4vasp.applet.ForcesConvergenceApplet
import p4vasp.applet.SelForcesConvergenceApplet
import p4vasp.applet.StructureApplet

import p4vasp.applet
import p4vasp.Property
import p4vasp.SystemPM



class SetupProfile(Profile):
#  frame=None
    def __init__(self):
        Profile.__init__(self)
        self.addClass(p4vasp.applet.applets().getStoreProfile())
        self.addClass(p4vasp.SystemPM.systemlist().store_profile)

class SetupProfile_old(Profile):
#  frame=None
    def __init__(self):
        Profile.__init__(self)

        sp=p4vasp.applet.applets().store_profile

        for x in [
                  p4vasp.applet.Applet.Applet,
                  p4vasp.applet.EnergyConvergenceApplet.EnergyConvergenceApplet,
                  p4vasp.applet.ForcesConvergenceApplet.ForcesConvergenceApplet,
                  p4vasp.applet.SelForcesConvergenceApplet.SelForcesConvergenceApplet,
                  p4vasp.applet.StructureApplet.StructureApplet,
                 ]:
            #print "subprofile:",x
            sp.addClass(x.store_profile)


#if __name__=="__main__":
#  import LDOSApplet
#  from sys import *
#  f=stdout
#  sp=SetupProfile()
#  obj=LDOSApplet.LDOSApplet()
#  obj.lines.append(LDOSApplet.Line())
#  sp.dump(obj,f)
