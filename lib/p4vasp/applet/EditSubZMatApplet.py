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
from p4vasp.store import *
from p4vasp.applet.Applet import *
from p4vasp.Selection import Selection,selection,SelectionListener
from p4vasp.Structure import Structure
from p4vasp.matrix import *
from p4vasp.util import getAtomtypes
from p4vasp.SystemPM import systemlist



def rot(O,n,R,a):
    n=n.normal()
    r=R-O
    A=(n*r)*n
    B=r.cross(n)
    return O+A+cos(a)*(r-A)+sin(a)*B

class EditSubZMatApplet(Applet,SelectionListener):
    menupath=["Edit","Edit sub-Z-matrix"]
    showmode=Applet.EXTERNAL_MODE
    def __init__(self):
        Applet.__init__(self)
        self.gladefile="eszmapplet.glade"
        self.gladename="applet_frame"

    def notifyAtomSelection(self, sel,origin):
        self.sel=sel
        self.updateSystem()

    def initUI(self):
        self.l1_entry    =self.xml.get_widget("l1_entry")
        self.l2_entry    =self.xml.get_widget("l2_entry")
        self.l3_entry    =self.xml.get_widget("l3_entry")
        self.a2_entry    =self.xml.get_widget("a2_entry")
        self.a3_entry    =self.xml.get_widget("a3_entry")
        self.d3_entry    =self.xml.get_widget("d3_entry")
        self.first_label =self.xml.get_widget("first_label")
        self.second_label=self.xml.get_widget("second_label")
        self.third_label =self.xml.get_widget("third_label")
        self.fourth_label=self.xml.get_widget("fourth_label")
        self.first_label.set_use_markup(True)
        self.second_label.set_use_markup(True)
        self.third_label.set_use_markup(True)
        self.fourth_label.set_use_markup(True)


    def updateLabels(self):
        if len(self.sel)>0:
            sel=self.sel[0]
            try:
                elem=self.system.INITIAL_STRUCTURE.getRecordForAtom(sel[0]).element
                m="%s <b>%d</b> (%d %d %d)"%(elem,sel[0],sel[1],sel[2],sel[3])
            except:
                m="<b>%d</b> (%d %d %d)"%(sel[0],sel[1],sel[2],sel[3])
                msg().exception()
            self.first_label.set_label(m)
        else:
            self.first_label.set_label("")
        if len(self.sel)>1:
            sel=self.sel[1]
            try:
                elem=self.system.INITIAL_STRUCTURE.getRecordForAtom(sel[0]).element
                m="%s <b>%d</b> (%d %d %d)"%(elem,sel[0],sel[1],sel[2],sel[3])
            except:
                m="<b>%d</b> (%d %d %d)"%(sel[0],sel[1],sel[2],sel[3])
            self.second_label.set_label(m)
        else:
            self.second_label.set_label("")
        if len(self.sel)>2:
            sel=self.sel[2]
            try:
                elem=self.system.INITIAL_STRUCTURE.getRecordForAtom(sel[0]).element
                m="%s <b>%d</b> (%d %d %d)"%(elem,sel[0],sel[1],sel[2],sel[3])
            except:
                m="<b>%d</b> (%d %d %d)"%(sel[0],sel[1],sel[2],sel[3])
            self.third_label.set_label(m)
        else:
            self.third_label.set_label("")
        if len(self.sel)>3:
            sel=self.sel[3]
            try:
                elem=self.system.INITIAL_STRUCTURE.getRecordForAtom(sel[0]).element
                m="%s <b>%d</b> (%d %d %d)"%(elem,sel[0],sel[1],sel[2],sel[3])
            except:
                m="<b>%d</b> (%d %d %d)"%(sel[0],sel[1],sel[2],sel[3])
            self.fourth_label.set_label(m)
        else:
            self.fourth_label.set_label("")

    def updateCoord(self):
        s=self.getStructure()
        if s is not None:
            s=Structure(s)
            s.setCarthesian()
        sel=self.sel
        if len(sel)>1:
            try:
                i,nx,ny,nz=sel[0]
                v1=s[i]+s.basis[0]*nx+s.basis[1]*ny+s.basis[2]*nz
                i,nx,ny,nz=sel[1]
                v2=s[i]+s.basis[0]*nx+s.basis[1]*ny+s.basis[2]*nz
                l=(v1-v2).length()
                self.l1_entry.set_text("%14.8f"%l)
            except:
                self.l1_entry.set_text("")
        else:
            self.l1_entry.set_text("")
        if len(sel)>2:
            try:
                i,nx,ny,nz=sel[0]
                a=s[i]+s.basis[0]*nx+s.basis[1]*ny+s.basis[2]*nz
                i,nx,ny,nz=sel[1]
                b=s[i]+s.basis[0]*nx+s.basis[1]*ny+s.basis[2]*nz
                i,nx,ny,nz=sel[2]
                c=s[i]+s.basis[0]*nx+s.basis[1]*ny+s.basis[2]*nz
                l=(b-c).length()
                self.l2_entry.set_text("%14.8f"%l)
                angle=(a-b).angle(c-b)*180.0/pi
                self.a2_entry.set_text("%+7.4f"%angle)
            except:
                msg().exception()
                self.l2_entry.set_text("")
                self.a2_entry.set_text("")
        else:
            self.l2_entry.set_text("")
            self.a2_entry.set_text("")

        if len(sel)>3:
            try:
                i,nx,ny,nz=sel[0]
                a=s[i]+s.basis[0]*nx+s.basis[1]*ny+s.basis[2]*nz
                i,nx,ny,nz=sel[1]
                b=s[i]+s.basis[0]*nx+s.basis[1]*ny+s.basis[2]*nz
                i,nx,ny,nz=sel[2]
                c=s[i]+s.basis[0]*nx+s.basis[1]*ny+s.basis[2]*nz
                i,nx,ny,nz=sel[3]
                d=s[i]+s.basis[0]*nx+s.basis[1]*ny+s.basis[2]*nz
                l=(d-c).length()
                self.l3_entry.set_text("%14.8f"%l)
                angle=(b-c).angle(d-c)*180.0/pi
                self.a3_entry.set_text("%+7.4f"%angle)
                try:
                    dihedral=(c-b).cross(a-b).angle((b-c).cross(d-c))*180.0/pi
                    self.d3_entry.set_text("%+7.4f"%dihedral)
                except:
                    self.d3_entry.set_text("")
            except:
                msg().exception()
                self.l3_entry.set_text("")
                self.a3_entry.set_text("")
                self.d3_entry.set_text("")
        else:
            self.l3_entry.set_text("")
            self.a3_entry.set_text("")
            self.d3_entry.set_text("")

    def updateSystem(self,x=None):
        self.sel=selection()
        self.updateCoord()
        self.updateLabels()


    def getStructure(self):
        if self.system is not None:
            return self.system.INITIAL_STRUCTURE
        return None

    def on_l1_entry_activate_handler(self,*arg):
        self.changePositions()
    def on_l2_entry_activate_handler(self,*arg):
        self.changePositions()
    def on_l3_entry_activate_handler(self,*arg):
        self.changePositions()
    def on_a2_entry_activate_handler(self,*arg):
        self.changePositions()
    def on_a3_entry_activate_handler(self,*arg):
        self.changePositions()
    def on_d3_entry_activate_handler(self,*arg):
        self.changePositions()

    def changePositions(self):
        sel=self.sel
        if len(sel)==0:
            msg().status("No atoms selected.")
            return
        if len(sel)>1:
            try:
                l1=float(eval(self.l1_entry.get_text()))
                print "l1",l1
            except:
                msg().error("Error parsing length 1 in sub-Z-matrix")
                return

        if len(sel)>2:
            try:
                l2=float(eval(self.l2_entry.get_text()))
                print "l2",l2
            except:
                msg().error("Error parsing length 2 in sub-Z-matrix")
                return
            try:
                a2=float(eval(self.a2_entry.get_text()))
                print "a2",a2
            except:
                msg().error("Error parsing angle 1 in sub-Z-matrix")
                return

        if len(sel)>3:
            try:
                l3=float(eval(self.l3_entry.get_text()))
                print "l3",l3
            except:
                msg().error("Error parsing length 3 in sub-Z-matrix")
                return
            try:
                a3=float(eval(self.a3_entry.get_text()))
                print "a3",a3
            except:
                msg().error("Error parsing angle 2 in sub-Z-matrix")
                return
            try:
                d3=float(eval(self.d3_entry.get_text()))
                print "d3",d3
            except:
                msg().error("Error parsing dihedral angle in sub-Z-matrix")
                return

        s=self.system.INITIAL_STRUCTURE
        if s is not None:
            s.setCarthesian()
        else:
            msg().error("No initial structure available.")

        if len(sel)>=2:
            i,nx,ny,nz=sel[0]
            v1=s[i]+s.basis[0]*nx+s.basis[1]*ny+s.basis[2]*nz
            i,nx,ny,nz=sel[1]
            v2=s[i]+s.basis[0]*nx+s.basis[1]*ny+s.basis[2]*nz
            dv=v2-v1
            l=(v1-v2).length()
            if l!=0.0:
                s[i]=v1+(l1/l)*dv-s.basis[0]*nx-s.basis[1]*ny-s.basis[2]*nz
            else:
                msg().status("Atoms have the same position, moving in X-direction")
                s[i]=v1+Vector(l1,0.0,0.0)-s.basis[0]*nx-s.basis[1]*ny-s.basis[2]*nz

        if len(sel)>=3:
            i0,nx0,ny0,nz0=sel[0]
            a=s[i0]+s.basis[0]*nx0+s.basis[1]*ny0+s.basis[2]*nz0
            i1,nx1,ny1,nz1=sel[1]
            b=s[i1]+s.basis[0]*nx1+s.basis[1]*ny1+s.basis[2]*nz1
            i2,nx2,ny2,nz2=sel[2]
            c=s[i2]+s.basis[0]*nx2+s.basis[1]*ny2+s.basis[2]*nz2

            l=(a-b).length()
            dv=(b-a)
            angle=(a-b).angle(c-b)*180.0/pi
            if l==0.0:
                msg().status("First two atoms have the same position, moving in X-direction")
                dv=Vector(1.0,0.0,0.0)
                l=1.0

            try:
                n1=(c-b).cross(a-b).normal()
            except:
                msg().status("First three atoms do not define a plane, using Z-axis for rotation.")
                try:
                    n1=Vector(0.0,-dv[2],dv[1]).normal()
                except:
                    n1=Vector(0.0,0.0,1.0)

            s[i2]=rot(b,n1,b-(l2/l)*dv,a2*pi/180.0)-s.basis[0]*nx2-s.basis[1]*ny2-s.basis[2]*nz2

        if len(sel)>=4:
            i0,nx0,ny0,nz0=sel[0]
            a=s[i0]+s.basis[0]*nx0+s.basis[1]*ny0+s.basis[2]*nz0
            i1,nx1,ny1,nz1=sel[1]
            b=s[i1]+s.basis[0]*nx1+s.basis[1]*ny1+s.basis[2]*nz1
            i2,nx2,ny2,nz2=sel[2]
            c=s[i2]+s.basis[0]*nx2+s.basis[1]*ny2+s.basis[2]*nz2
            i3,nx3,ny3,nz3=sel[3]
            d=s[i3]+s.basis[0]*nx3+s.basis[1]*ny3+s.basis[2]*nz3


            try:
                n1=(c-b).cross(a-b).normal()
            except:
                msg().status("First three atoms do not define a plane, using Z-axis.")
                try:
                    n1=Vector(0.0,-dv[2],dv[1]).normal()
                except:
                    n1=Vector(0.0,0.0,1.0)

            l=(b-c).length()
            dv=(c-b)
            angle=(b-c).angle(d-c)*180.0/pi
            if l==0.0:
                msg().status("Second and third have the same position, using X-direction")
                dv=Vector(1.0,0.0,0.0)
                l=1.0


            newd=rot(c,n1,c-(l3/l)*dv,a3*pi/180.0)
            s[i3]=rot(c,c-b,newd,(180+d3)*pi/180.0)-s.basis[0]*nx3-s.basis[1]*ny3-s.basis[2]*nz3


        systemlist().notifySystemChanged()




EditSubZMatApplet.store_profile=AppletProfile(EditSubZMatApplet,tagname="ESZM")
