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


from p4vasp.util import ParseException
from p4vasp import *
from p4vasp.matrix import *
from p4vasp.store import *
from p4vasp.applet.Applet import *
from p4vasp.SystemPM import *
import gtk
import gobject
import pango
from math import *

class LatticeApplet(Applet):
    menupath=["Structure","Lattice"]
    showmode=Applet.EXTERNAL_MODE

    def __init__(self):
        Applet.__init__(self)
        self.gladefile="lattice.glade"
        self.gladename="applet_frame"
        self.allow_parameters_update=True
        self.allow_cell_update=True
        self.in_apply=False

    def updateSystem(self,x=None):
        pass

    def on_triclinic_radiobutton_toggled_handler(self,w,*arg):
        if w.get_active():
            self.widgets.a_entry.set_sensitive(True)
            self.widgets.b_entry.set_sensitive(True)
            self.widgets.c_entry.set_sensitive(True)
            self.widgets.alpha_entry.set_sensitive(True)
            self.widgets.beta_entry.set_sensitive(True)
            self.widgets.gamma_entry.set_sensitive(True)           
    def on_monoclinic_radiobutton_toggled_handler(self,w,*arg):
        if w.get_active():
            self.toMonoclinic()
    def on_orthorhombic_radiobutton_toggled_handler(self,w,*arg):
        if w.get_active():
            self.toOrthorhombic()
    def on_tetragonal_radiobutton_toggled_handler(self,w,*arg):
        if w.get_active():
            self.toTetragonal()
    def on_rhombohedral_radiobutton_toggled_handler(self,w,*arg):
        if w.get_active():
            self.toRhombohedral()
    def on_hexagonal_radiobutton_toggled_handler(self,w,*arg):
        if w.get_active():
            self.toHexagonal()
    def on_cubic_radiobutton_toggled_handler(self,w,*arg):
        if w.get_active():
            self.toCubic()

    def on_parameter_updated_handler(self,*arg):
        print "on_parameter_updated",self.allow_parameters_update,self.allow_cell_update
        if self.allow_parameters_update:
            self.allow_parameters_update=False
            print "self.allow_parameters_update=False [[["
            self.fixParameters()
            self.updateCell()
            self.allow_parameters_update=True
            print "self.allow_parameters_update=True  ]]]"

    def on_cell_updated_handler(self,*arg):
        if self.allow_cell_update:
            print "on_cell_updated_handler",self.allow_cell_update,self.allow_parameters_update
            self.allow_cell_update=False
            print "self.allow_cell_update=False       [[["
            self.updateParameters()
            self.allow_cell_update=True
            print "self.allow_cell_update=True        ]]]"

    def on_apply_button_clicked_handler(self,*arg):
        b1,b2,b3 = self.getCell()
        s=self.getCurrentStructure()
        s.basis[0]=b1
        s.basis[1]=b2
        s.basis[2]=b3
        self.in_apply=True
        systemlist().notifySystemChanged()
        self.in_apply=False

    def fixParameters(self):
        if self.widgets.monoclinic_radiobutton.get_active():
            self.toMonoclinic()
        if self.widgets.orthorhombic_radiobutton.get_active():
            self.toOrthorhombic()
        if self.widgets.tetragonal_radiobutton.get_active():
            self.toTetragonal()
        if self.widgets.rhombohedral_radiobutton.get_active():
            self.toRhombohedral()
        if self.widgets.hexagonal_radiobutton.get_active():
            self.toHexagonal()
        if self.widgets.cubic_radiobutton.get_active():
            self.toCubic()
    def toMonoclinic(self):
        self.widgets.a_entry.set_sensitive(True)
        self.widgets.b_entry.set_sensitive(True)
        self.widgets.c_entry.set_sensitive(True)
        self.widgets.alpha_entry.set_sensitive(False)
        self.widgets.beta_entry.set_sensitive(True)
        self.widgets.gamma_entry.set_sensitive(False)
        a=self.widgets.a_entry.get_text()
        self.widgets.b_entry.set_text(a)
        self.widgets.c_entry.set_text(a)
        self.widgets.alpha_entry.set_text("90")
        self.widgets.gamma_entry.set_text("90")
        self.updateCell()
    def toOrthorhombic(self):
        self.widgets.a_entry.set_sensitive(True)
        self.widgets.b_entry.set_sensitive(True)
        self.widgets.c_entry.set_sensitive(True)
        self.widgets.alpha_entry.set_sensitive(False)
        self.widgets.beta_entry.set_sensitive(False)
        self.widgets.gamma_entry.set_sensitive(False)
        self.widgets.alpha_entry.set_text("90")
        self.widgets.beta_entry.set_text("90")
        self.widgets.gamma_entry.set_text("90")
        self.updateCell()
    def toTetragonal(self):
        self.widgets.a_entry.set_sensitive(True)
        self.widgets.b_entry.set_sensitive(False)
        self.widgets.c_entry.set_sensitive(True)
        self.widgets.alpha_entry.set_sensitive(False)
        self.widgets.beta_entry.set_sensitive(False)
        self.widgets.gamma_entry.set_sensitive(False)
        a=self.widgets.a_entry.get_text()
        self.widgets.b_entry.set_text(a)
        self.widgets.alpha_entry.set_text("90")
        self.widgets.beta_entry.set_text("90")
        self.widgets.gamma_entry.set_text("90")
        self.updateCell()
    def toRhombohedral(self):
        self.widgets.a_entry.set_sensitive(True)
        self.widgets.b_entry.set_sensitive(False)
        self.widgets.c_entry.set_sensitive(False)
        self.widgets.alpha_entry.set_sensitive(True)
        self.widgets.beta_entry.set_sensitive(True)
        self.widgets.gamma_entry.set_sensitive(True)
        a=self.widgets.a_entry.get_text()
        self.widgets.b_entry.set_text(a)
        self.widgets.c_entry.set_text(a)
        self.updateCell()
    def toHexagonal(self):
        self.widgets.a_entry.set_sensitive(True)
        self.widgets.b_entry.set_sensitive(False)
        self.widgets.c_entry.set_sensitive(True)
        self.widgets.alpha_entry.set_sensitive(False)
        self.widgets.beta_entry.set_sensitive(False)
        self.widgets.gamma_entry.set_sensitive(False)
        a=self.widgets.a_entry.get_text()
        self.widgets.b_entry.set_text(a)
        self.widgets.alpha_entry.set_text("90")
        self.widgets.beta_entry.set_text("90")
        self.widgets.gamma_entry.set_text("120")
        self.updateCell()
    def toCubic(self):
        self.widgets.a_entry.set_sensitive(True)
        self.widgets.b_entry.set_sensitive(False)
        self.widgets.c_entry.set_sensitive(False)
        self.widgets.alpha_entry.set_sensitive(False)
        self.widgets.beta_entry.set_sensitive(False)
        self.widgets.gamma_entry.set_sensitive(False)
        a=self.widgets.a_entry.get_text()
        self.widgets.b_entry.set_text(a)
        self.widgets.c_entry.set_text(a)
        self.widgets.alpha_entry.set_text("90")
        self.widgets.beta_entry.set_text("90")
        self.widgets.gamma_entry.set_text("90")
        self.updateCell()

    def getParameter(self,name):
        return self.getValue(name+"_entry")
    def getValue(self,name):
        txt=self.xml.get_widget(name).get_text()
        try:
            return float(eval(txt))
        except:
            return 0.0
    def updateCell(self):
        a=self.getParameter("a")
        b=self.getParameter("b")
        c=self.getParameter("c")
        alpha=self.getParameter("alpha")*pi/180
        beta=self.getParameter("beta")*pi/180
        gamma=self.getParameter("gamma")*pi/180
        
        cosA=cos(alpha)
        cosB=cos(beta)
        cosC=cos(gamma)
        sinC=sin(gamma)

        b1=Vector(a,0.0,0.0)        
        b2=Vector(cosC,sinC,0.0)*b
        try:
            x=cosB
            y=(cosA-cosB*cosC)/sinC
            z=sqrt(1.0-x*x-y*y)
            b3=Vector(x,y,z)*c
        except:
            b3=Vector(0.0,0.0,0.0)
        self.setBasis((b1,b2,b3))
        
    def updateSystem(self,x=None):
        if not self.in_apply:
            s=self.getCurrentStructure()
            self.setBasis(s.basis)
            self.updateParameters()

    def setBasis(self,basis):
        print "setBasis"
        s=self.getCurrentStructure()
        self.widgets.a11.set_text("%17.15f"%(basis[0][0]))
        self.widgets.a12.set_text("%17.15f"%(basis[0][1]))
        self.widgets.a13.set_text("%17.15f"%(basis[0][2]))
        self.widgets.a21.set_text("%17.15f"%(basis[1][0]))
        self.widgets.a22.set_text("%17.15f"%(basis[1][1]))
        self.widgets.a23.set_text("%17.15f"%(basis[1][2]))
        self.widgets.a31.set_text("%17.15f"%(basis[2][0]))
        self.widgets.a32.set_text("%17.15f"%(basis[2][1]))
        self.widgets.a33.set_text("%17.15f"%(basis[2][2]))
    def getCurrentStructure(self):
        s=getCurrentSystemPM()
        if s is not None:
            return s.INITIAL_STRUCTURE
    def getCell(self):
        b1=Vector(self.getValue("a11"),self.getValue("a12"),self.getValue("a13"))
        b2=Vector(self.getValue("a21"),self.getValue("a22"),self.getValue("a23"))
        b3=Vector(self.getValue("a31"),self.getValue("a32"),self.getValue("a33"))
        return (b1,b2,b3)
    def updateParameters(self):
        self.widgets.triclinic_radiobutton.set_active(True)
        b1,b2,b3 = self.getCell()
        a=b1.length()
        b=b2.length()
        c=b3.length()
        alpha=b2.angle(b3)*180/pi
        beta=b3.angle(b1)*180/pi
        gamma=b1.angle(b2)*180/pi
        self.widgets.a_entry.set_text(str(a))
        self.widgets.b_entry.set_text(str(b))
        self.widgets.c_entry.set_text(str(c))
        self.widgets.alpha_entry.set_text(str(alpha))
        self.widgets.beta_entry.set_text(str(beta))
        self.widgets.gamma_entry.set_text(str(gamma))
    def initUI(self):
        pass
        
#BuilderApplet.store_profile=AppletProfile(BuilderApplet,tagname="Builder")
