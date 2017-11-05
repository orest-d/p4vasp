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

from math import *
#from p4vasp.graph import *
#from p4vasp.GraphCanvas import *
#from p4vasp.store import *
from p4vasp.applet.Applet import *
from p4vasp.applet.GraphWindowApplet import *

class SelForcesConvergenceApplet(GraphWindowApplet):
    menupath=["Convergence","Selected forces"]
    def __init__(self):
        GraphWindowApplet.__init__(self)
#    self.gladefile="graphapplet.glade"
#    self.gladename="applet_frame"
        self.world_name="sfconvergence"
        self.required=["NAME","INITIAL_STRUCTURE"]

    def updateSystem(self,x=None):
        schedule(self.updateSystemGen(x))

    def updateSystemGen(self,x=None):
        msg().status("Update System in Selected Forces Convergence applet")
        yield 1
        system=self.system
        self.world[0].subtitle=""
#    self.window_world[0].subtitle=""
        yield 1

        if system is not None:
            name=system.current("NAME")
            if name is not None:
                self.world[0].subtitle="(%s)"%name
#       self.window_world[0].subtitle="(%s)"%name
#      print system.INITIAL_STRUCTURE.toxml()


            avgf=[]
            maxf=[]


            forces=system.FORCES_SEQUENCE_L

            if forces is not None:
                struct=system.current("INITIAL_STRUCTURE")
                if struct is None:
                    dof=range(3*len(forces[0]))
                else:
                    if struct.isSelective():
                        dof=[]
                        sel=struct.selective
                        for i in range(3*len(sel)):
                            if sel[i/3][i%3]:
                                dof.append(i)
                    else:
                        dof=range(3*len(forces[0]))
                yield 1
                for i in range(len(forces)):
                    msg().step(i+1,len(forces))
                    if forces[i] is not None:
                        ff=filter(lambda x:len(x)==3,forces[i])
                        f=[]
                        for j in dof:
                            try:
                                f.append(abs(ff[j/3][j%3]))
                            except:
                                pass
                        maxf.append((i+1,max(f)))
                        avgf.append((i+1,float(reduce(lambda x,y:x+y,f))/len(f)))
                    yield 1

            self.world[0].data=[]
            avgset=Set()
            avgset.data=avgf
            avgset.color=1
            avgset.line_color=1
            avgset.legend="average"
            maxset=Set()
            maxset.data=maxf
            maxset.color=2
            maxset.line_color=2
            maxset.legend="maximal"
            self.world[0].append(avgset)
            self.world[0].append(maxset)
            self.graphdata=[[maxf,avgf]]
#      self.setGraphData([[maxf,avgf]])
            self.update()
        else:
            self.setGraphData([[]])
            self.update()
        self.viewAll()
        msg().status("OK")
        msg().step(0,1)


SelForcesConvergenceApplet.store_profile=AppletProfile(SelForcesConvergenceApplet,tagname="SelForcesConvergence")
#SelForcesConvergenceApplet.config_profile=AppletProfile(SelForcesConvergenceApplet,tagname="SelForcesConvergence")
