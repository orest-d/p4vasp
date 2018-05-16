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


from p4vasp.util import ParseException
from p4vasp import *
from p4vasp.store import *
from p4vasp.applet.Applet import *

from p4vasp.StructureWindow import *

from p4vasp.util import getAtomtypes
import p4vasp.applet.StructureWindowApplet

import gtk
import gobject
import pango

from p4vasp.paint3d.PovrayPaint3D import *

from p4vasp.export.Exporter import Exporter, Attributes, Data
from p4vasp.export.PoscarExporter import PoscarExporter
from p4vasp.export.PaintExporter import PaintExporter

import os.path

class ExportApplet(Applet):
    menupath=["Structure","Export"]
    showmode=Applet.EXTERNAL_MODE

    def __init__(self):
        Applet.__init__(self)
        self.gladefile="export.glade"
        self.gladename="applet_frame"
        self.exporters=[
          PaintExporter("Povray",".pov",ExtendedPovrayPaint3D),
          PoscarExporter(),
        ]
        self.active=0
        self.init_done=False

    def getSWinApplet(self):
        return applets().getActive([p4vasp.applet.StructureWindowApplet.StructureWindowApplet,
                                    p4vasp.applet.STMWindowApplet.STMWindowApplet])
    def getSWinControlApplet(self):
        return applets().getActive([p4vasp.applet.StructureWindowControlApplet.StructureWindowControlApplet])

    def swin(self):
        w=self.getSWinApplet()
        if isinstance(w,p4vasp.applet.StructureWindowApplet.StructureWindowApplet):
            return w.swin
        else:
            return w

    def updateSystem(self,x=None):
        pass

    def initUI(self):
        if self.init_done:
            return
        self.fileentry = self.xml.get_widget("fileentry") #needs to be initialised before fixOutputPath is called
        self.init_done=True

        self.model=gtk.ListStore(str)
        self.exporterchoice = self.xml.get_widget("exporterchoice")
        self.exporterchoice.set_model(self.model)
        self.cell = gtk.CellRendererText()
        self.exporterchoice.pack_start(self.cell, True)
        self.exporterchoice.add_attribute(self.cell, 'text', 0)
        self.exporterchoice.connect('changed', self.exporterchoice_cb)

        self.model.clear()
        for x in self.exporters:
            self.model.append([x.name()])
        self.exporterchoice.set_active(0)

        self.selectbutton = self.xml.get_widget("selectbutton")
        self.selectbutton.connect('clicked', self.select_cb)
        self.exportbutton = self.xml.get_widget("exportbutton")
        self.exportbutton.connect('clicked', self.export_cb)

        self.fixOutputPath()

    def exporterchoice_cb(self, combobox):
        if not self.init_done:
            self.initUI()
        model = combobox.get_model()
        index = combobox.get_active()
        if index > -1:
            self.active=index
        self.fixOutputPath()

    def select_cb(self, *arg):
        d=gtk.FileChooserDialog(title="File to export to", parent=None,
            action=gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK), backend=None)
        response=d.run()
        if response == gtk.RESPONSE_OK:
            self.fileentry.set_text(d.get_filename())
        d.destroy()

    def attributes(self):
        swin=self.swin()
        a=Attributes()
        a.background=Vector(swin.getBackground())
        a.cell_color=Vector(
          swin.structure_drawer.cell_red,
          swin.structure_drawer.cell_green,
          swin.structure_drawer.cell_blue)
        a.perspective=swin.navigator.getPerspective()
        a.zoom=swin.navigator.getZoom()
        a.rotmat=swin.getRotmat()
        a.width=swin.structure_drawer.getWidth()
        a.height=swin.structure_drawer.getHeight()
        a.showcell=swin.structure_drawer.showcellflag
        a.cell_line_width=swin.structure_drawer.cell_line_width
        a.multiple=swin.getMultiple()
        a.radius_factor=swin.getRadiusFactor()
        a.speed=self.getSWinControlApplet().mdstep()
        a.arrow_scale=swin.getArrowsScale()
        a.arrow_color=Vector(swin.arrows_drawer.red,swin.arrows_drawer.green,swin.arrows_drawer.blue)
        a.arrow_radius=swin.arrows_drawer.arrow_radius
        a.arrowhead_radius=swin.arrows_drawer.arrowhead_radius
        a.arrowhead_length=swin.arrows_drawer.arrowhead_length
        a.cell_centering=self.getSWinApplet().cell_centering
        return a

    def export_cb(self, *arg):
        sequence=self.getSWinApplet().getSequence()
        if sequence is None:
            msg().status("Please specify a structure or sequence type in the Structure Control")
            return
        single=self.xml.get_widget("single").get_active()
        try:
            index=self.getSWinApplet().index
        except:
            index=0        
        if single:
            sequence=[sequence[max(min(len(sequence)-1,index),0)]]
       
        data=Data(
          structures=sequence,
          vectors=self.getSWinApplet().getArrowsSequence(),
          index=index,
          process_sequence=not single
        )
        data.isosurfaces=[]
        if self.swin().chgcar is not None:
            d=self.swin().isosurface_drawer
            data.isosurfaces.append((self.swin().chgcar,d.getLevel(),Vector(d.red,d.green,d.blue)))
            d=self.swin().neg_isosurface_drawer
            data.isosurfaces.append((self.swin().chgcar,d.getLevel(),Vector(d.red,d.green,d.blue)))
 
        path=self.fileentry.get_text()
        if len(path)==0:
            path=self.fixOutputPath()
        self.exporters[self.active].export(
            data,
            self.attributes(),
            path
        )
    def fixOutputPath(self):
        text=self.fileentry.get_text()
        if len(text)==0:
            text="output"
        path,filename=os.path.split(text)
        v=filename.split(".")
        if len(v)>1:
           filename=".".join(v[:-1])
        text=os.path.join(path,filename+self.exporters[self.active].fileExtension())
        self.fileentry.set_text(text)
        return text
ExportApplet.store_profile=AppletProfile(ExportApplet,tagname="Exporter")
