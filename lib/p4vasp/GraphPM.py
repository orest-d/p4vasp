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


from p4vasp import *
import p4vasp.Property
from p4vasp.graph import *
from os import sep


class GraphProperty(p4vasp.Property.Property):
    def __init__(self,name=None,path=None,manager=None):
        p4vasp.Property.Property.__init__(self,name,manager=manager)
        self.path=path

    def read(self):
        msg().status("reading graph %s from %s"%(self.name,self.path))
        w=World()
        r=w.parseGrace(self.path)
        return w

class GraphPM(p4vasp.Property.PropertyManager):
    def __init__(self):
        p4vasp.Property.PropertyManager.__init__(self)

    def addGraph(self,name,path):
        self.add(GraphProperty(name,path))

    def getGraphProperty(self,name):
        if name in self.keys():
            return self[name]
        else:
            self.addGraph(name,"%s%sdata%sgraphs%s%s.agr"%(p4vasp_home,sep,sep,sep,name))
            return self[name]

graph_pm=GraphPM()

def createGraph(name):
    global graph_pm
    gp=graph_pm.getGraphProperty(name)
    status=gp.status
    w = gp.get()
#  if self.dummy_canvas is not None:
#    if (status != gp.READY) and (w is not None):
#      w.setupFonts(self.dummy_canvas)
    if status==gp.ERROR:
        msg().error("Can't load graph %s, using default graph."%name)
        gp=graph_pm.getGraphProperty("default")
        w = gp.get()
#    if self.dummy_canvas is not None:
#      if (status != Property.READY) and (w is not None):
#        w.setupFonts(self.dummy_canvas)
    if w is None:
        msg().error("Can't load default graph, using - well, another default graph...")
        return p4vasp.graph.World()
    return w.clone()
