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
import gtk

class DielectricApplet(GraphWindowApplet):
    menupath=["Electronic","Dielectric function"]
    def __init__(self):
        GraphWindowApplet.__init__(self)
        self.gladefile="dielectric.glade"
        self.gladename="applet_frame"
        self.world_name="dielectric"
        self.required=["NAME"]
        self.isini=0
        self.active=0

    def initUI(self):
        GraphWindowApplet.initUI(self)
        self.xml.get_widget("rxx").set_active(1)
        self.xml.get_widget("ryy").set_active(1)
        self.xml.get_widget("rzz").set_active(1)
        self.xml.get_widget("ixx").set_active(1)
        self.xml.get_widget("iyy").set_active(1)
        self.xml.get_widget("izz").set_active(1)
        self.model=gtk.ListStore(str)
        self.combobox=self.xml.get_widget("dielectriccombobox")
        self.combobox.set_model(self.model)
        self.isini=1
        self.cell = gtk.CellRendererText()
        self.combobox.pack_start(self.cell, True)
        self.combobox.add_attribute(self.cell, 'text', 0)
        self.combobox.connect('changed', self.changed_cb)

    def changed_cb(self, combobox):
        model = combobox.get_model()
        index = combobox.get_active()
        if index > -1:
            self.active=index
            schedule(self.updateDF())

    def updateSystem(self,x=None):
        schedule(self.updateSystemGen(x))

    def on_toggled_handler(self,*argv):
        if self.isini:
            self.updateSystem()

    def updateSystemGen(self,x=None):
        msg().status("Updating the dielectric function")
        system=self.system

#    active=self.combobox.get_active()
        self.model.clear()

        comments=system.DIELECTRIC_FUNCTIONS_COMMENTS
        if comments is not None:
            for c in comments:
                self.model.append([c])
#      active=min(active,len(comments)-1)
#    active=max(0,active)
#    self.combobox.set_active(active)
#    self.active=active
        self.world[0].subtitle=""
#    self.window_world[0].subtitle=""
        yield 1
        schedule(self.updateDF())


    def updateDF(self):
        self.world[0].data=[]
        yield 1
        system=self.system
        active=self.active
        if system is not None:
            name=system.current("NAME")
            if name is not None:
                self.world[0].subtitle="(%s)"%name
#       self.window_world[0].subtitle="(%s)"%name

            yield 1
            dielectric=system.DIELECTRIC_FUNCTIONS

            color=1
            if dielectric is not None:
                active=min(active,len(dielectric)-1)
                if active<0:
                    msg().error("Dielectric functions not available.")
                    return
                comments=system.DIELECTRIC_FUNCTIONS_COMMENTS
                try:
                    c=comments[active].strip()
                    if len(c):
                        self.world[0].title="%s"%(c)
                    else:
                        self.world[0].title="Dielectric Function"
                except:
                    self.world[0].title="Dielectric Function"

                dielectric=dielectric[active]
                dr,di=dielectric
                msg().status("Filling in graph")
                try:
                    energy_index=dr.field.index("energy")
                except:
                    msg().error("Energy field not available for real dielectric function.")
                    return
                l=["xx","yy","zz","xy","yz","zx"]
                for j in range(len(l)):
                    gd=[]
                    try:
                        projection_index=dr.field.index(l[j])
                    except:
                        msg().error("Data for real dielectric function %s not available."%l[j])
                        continue
                    if self.xml.get_widget("r"+l[j]).get_active():
                        for i in range(len(dr)):
                            gd.append((dr[i][energy_index],dr[i][projection_index]))
                            if (i%50)==0:
                                msg().step(i+1,len(dr))
                                yield 1
                        set=Set()
                        set.data=gd
                        set.line_color=color
                        color+=1
                        set.legend="Re "+l[j]

                        self.world[0].append(set)
                try:
                    energy_index=di.field.index("energy")
                except:
                    msg().error("Energy field not available for imaginary dielectric function.")
                    return
                for j in range(len(l)):
                    gd=[]
                    try:
                        projection_index=di.field.index(l[j])
                    except:
                        msg().error("Data for imaginary dielectric function %s not available."%l[j])
                        continue
                    if self.xml.get_widget("i"+l[j]).get_active():
                        for i in range(len(di)):
                            gd.append((di[i][energy_index],di[i][projection_index]))
                            if (i%50)==0:
                                msg().step(i+1,len(di))
                                yield 1
                        set=Set()
                        set.data=gd
                        set.line_color=color
                        color+=1
                        set.legend="Im "+l[j]

                        self.world[0].append(set)
        self.viewAll()
        self.update()
        msg().step(0,1)
        msg().status("OK")



DielectricApplet.store_profile=AppletProfile(DielectricApplet,tagname="Dielectric")
