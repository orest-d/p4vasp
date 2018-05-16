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

from __future__ import generators
from p4vasp.graph import *
#from p4vasp.GraphCanvas import *
#from p4vasp.store import *
from p4vasp.applet.Applet import *
from p4vasp.applet.GraphWindowApplet import *
from p4vasp.cStructure import *

class LocalPotentialApplet(GraphWindowApplet):
    menupath=["Electronic","Local potential"]
    def __init__(self):
        GraphWindowApplet.__init__(self)
#    self.gladefile="graphapplet.glade"
#    self.gladename="applet_frame"
        self.world_name="locpot"
        self.file="LOCPOT"
        self.coord=0
        self.graphdata=None

    def initUI(self):
        GraphWindowApplet.initUI(self)
        mitem=gtk.MenuItem("Show")
        menu=gtk.Menu()
        mitem.set_submenu(menu)

        item=gtk.MenuItem("X - direction")
        menu.append(item)
        item.show()
        item.connect("activate",self.dir_handler_,0)

        item=gtk.MenuItem("Y - direction")
        menu.append(item)
        item.show()
        item.connect("activate",self.dir_handler_,1)

        item=gtk.MenuItem("Z - direction")
        menu.append(item)
        item.show()
        item.connect("activate",self.dir_handler_,2)

        self.menubar.append(mitem)
        mitem.show()

    def dir_handler_(self,w,i):
        self.coord=i
        self.updateSystem()

    def updateSystemGen(self):
        msg().status("update local potentail data")
        system=self.system
        t=["X","Y","Z"]
        self.world[0].title="Local potential (%s dir.)"%t[self.coord]
        self.world[0].subtitle=""
        self.world[0].data=[]

        if system is not None:
            name=system.current("NAME")
            if name is not None:
                self.world[0].subtitle="%s"%name
#       self.window_world[0].subtitle="(%s)"%name
        self.system.scheduleFirst(self.file)
        yield 1
        c=self.system[self.file].get()
        if c is None:
            msg().error("%s not available"%self.file)
            self.update()
            return

        s=Structure(pointer=c.structure.this)
        s.correctScaling()
        vl=s.basis[self.coord].length()
        l=self.system[self.file+"_"+t[self.coord]].get()
        msg().status("Getting plane statistics")
        yield 1
        Avg=[]
        Min=[]
        Max=[]
        for i in range(len(l)):
            x=i*vl/len(l)
            msg().step(i,len(l))
            yield 1
            v=l[i]
            Min.append((x,v[0]))
            Max.append((x,v[1]))
            Avg.append((x,v[2]))
        smin=Set()
        smin.data=Min
        smin.line_color=3
        smin.legend="minimum"
        smax=Set()
        smax.data=Max
        smax.line_color=4
        smax.legend="maximum"
        savg=Set()
        savg.data=Avg
        savg.line_color=2
        savg.legend="average"

        self.world[0].append(smin)
        self.world[0].append(savg)
        self.world[0].append(smax)
        self.world[0].viewAll()
        msg().step(0,1)
        msg().status("OK")
        self.viewAll()
        self.update()

    def updateSystem(self,x=None):
        schedule(self.updateSystemGen())

LocalPotentialApplet.store_profile=AppletProfile(LocalPotentialApplet,tagname="LocalPotential")
#DOSApplet.config_profile=AppletProfile(TDOSApplet,tagname="TDOS")
