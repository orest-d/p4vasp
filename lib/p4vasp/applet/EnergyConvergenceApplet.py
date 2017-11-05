#!/usr/bin/python

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

from __future__ import generators

#from p4vasp.graph import *
#from p4vasp.GraphCanvas import *
#from p4vasp.store import *
from p4vasp.applet.Applet import *
from p4vasp.applet.GraphWindowApplet import *

class EnergyConvergenceApplet(GraphWindowApplet):
    menupath=["Convergence","Energy"]
    def __init__(self):
        GraphWindowApplet.__init__(self)
#    self.gladefile="graphapplet.glade"
#    self.gladename="applet_frame"
        self.world_name="econvergence"
        self.required=["NAME"]

    def updateSystem(self,x=None):
        schedule(self.updateSystemGen(x))

    def updateSystemGen(self,x=None):
        msg().status("Update System in Energy Convergence applet")
        system=self.system
        self.world[0].subtitle=""
#    self.window_world[0].subtitle=""
        yield 1

        if system is not None:
            name=system.current("NAME")
            if name is not None:
                self.world[0].subtitle="(%s)"%name
#       self.window_world[0].subtitle="(%s)"%name

            system.scheduleFirst("FREE_ENERGY_SEQUENCE")
            yield 1
            energy=system.FREE_ENERGY_SEQUENCE
            gd=[]
            msg().status("Filling in graph")
            if energy is not None:
                for i in range(len(energy)):
                    gd.append((i+1,energy[i]))
                    if (i%10)==0:
                        msg().step(i+1,len(energy))
                        yield 1
                self.setGraphData([[gd]])
            else:
                self.setGraphData([[]])
        self.update()
        self.viewAll()
        msg().step(0,1)
        msg().status("OK")



EnergyConvergenceApplet.store_profile=AppletProfile(EnergyConvergenceApplet,tagname="EnergyConvergence")
