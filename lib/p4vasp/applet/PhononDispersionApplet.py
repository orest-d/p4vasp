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

#from p4vasp.graph import *
#from p4vasp.GraphCanvas import *
#from p4vasp.store import *
from p4vasp.applet.Applet import *
from p4vasp.applet.GraphWindowApplet import *

import p4vasp.matrix as p4m
import numpy as np
import math
from p4vasp.PhononsCalculation import  PhononsCalculation
from p4vasp.Dyna import DynaListener,dynaPublisher

def make_k_path(v_from, v_to, points):
    v_diff = v_to - v_from
    return [v_from + v_diff * n for n in np.linspace(0, 1, points).tolist()]

class PhononDispersionApplet(GraphWindowApplet,DynaListener):
    menupath=["Mechanics","Phonon dispersion"]
    def __init__(self):
        GraphWindowApplet.__init__(self)
#    self.gladefile="graphapplet.glade"
#    self.gladename="applet_frame"
        self.world_name="phonondispersion"
        self.required=["NAME"]
        dynaPublisher().addListener(self)
    def destroy(self):
        GraphWindowApplet.destroy(self)
        dynaPublisher().removeListener(self)

    def updateSystem(self,x=None):
        schedule(self.updateSystemGen(x))

    def dynaUpdated(self,dyna):
        self.updateSystem()
    def updateSystemGen(self,x=None):
        msg().status("Update System in Energy Convergence applet")
        system=self.system
        self.world[0].subtitle=""
#    self.window_world[0].subtitle=""
        self.setGraphData([[]])
        self.update()
        yield 1

        if system is not None:
            name=system.current("NAME")
            if name is not None:
                self.world[0].subtitle="(%s)"%name

            super_cell = system.INITIAL_STRUCTURE
            system.scheduleFirst("FORCE_CONSTANTS")
            force_const_mat = system.FORCE_CONSTANTS
            primitive_cell = system.PRIMITIVE_STRUCTURE
            if primitive_cell is None:
                return
            basis_masses = [primitive_cell.getRecordForAtom(x)["mass"]
                    for x in range(len(primitive_cell))]
            yield 1

            msg().status("Reading DYNA")
            dyna=dynaPublisher().dyna
            if dyna is None:
                dyna=system.DYNA
            if dyna is None:
                msg().error("DYNA file not found, k-point path not specified.")
                self.setGraphData([[]])
                yield 1
            else:
                print "Dyna in dispersion:"
                print dyna.toString()
                dyna=dyna.withBasis(primitive_cell.basis).reciprocal()
                steps=dyna.size
                if len(dyna.segments)<1:
                    msg().error("At least one segment is necessary for a k-point path")
                    return
                msg().status("Generating k-point path")
                yield 1
                k_path = list(dyna.pointsAlongPath(steps))
                k_path_ext = list(dyna.pointsAlongPathWithDistanceAndLabel(steps))
                msg().status("Start phonon calculation")
                yield 1

                p_calc = PhononsCalculation(primitive_cell, super_cell, force_const_mat, basis_masses)
                omega=[]
                for i,x in enumerate(p_calc.calcPhononFrequencies(k_path)):
                    msg().step(i,len(k_path_ext))
                    msg().status("Calculation k-point %s"%str(k_path[i]))
                    omega.append(x)
                    if (i%5==0):
                        yield 1
                msg().step(0,1)
                msg().status("OK")
                yield 1

                msg().status("Filling in graph")
                yield 1

                if omega is not None:
                    assert(len(omega)==len(k_path_ext))

                    g=[]

                    for i in range(len(omega[0])):
                        gd=[]
                        for j in range(len(omega)):
                            point,distance,label=k_path_ext[j]
                            gd.append((distance,omega[j][i]))

                        g.append(gd)
                    self.setGraphData([g])

# Create lines
                    self.viewAll()
                    self.update()
                    w=self.canvas.world
                    wg=w[0]
                    x1=wg.world_xmin
                    x2=wg.world_xmax
                    y1=wg.world_ymin
                    y2=wg.world_ymax
                    wg.graph_lines=[
                        GraphLine(distance,y1,distance,y2,7)
                        for point,distance,label in k_path_ext if label is not None and distance>x1 and distance < x2
                    ]
                    self.viewAll()
                    self.update()
                else:
                    self.setGraphData([[]])
                    wg.graph_lines=[]
        self.update()
        self.viewAll()
        msg().step(0,1)
        msg().status("OK")

PhononDispersionApplet.store_profile=AppletProfile(PhononDispersionApplet,tagname="PhononDispersion")
