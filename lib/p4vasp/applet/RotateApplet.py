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

from p4vasp.store import *
from p4vasp.applet.Applet import *
from p4vasp.Selection import Selection,selection
from p4vasp.Structure import Structure
from p4vasp.matrix import *
from p4vasp.util import getAtomtypes
from p4vasp.SystemPM import systemlist
from math import *

def first(s,sel):
    if s is None:
        return None
    s=Structure(s)
    s.setCarthesian()
    if len(sel):
        i,nx,ny,nz=sel[0]
        if len(s)>i:
            return s[i]+nx*s.basis[0]+ny*s.basis[1]+nz*s.basis[2]
    return None

def last(s,sel):
    if s is None:
        return None
    s=Structure(s)
    s.setCarthesian()
    if len(sel):
        i,nx,ny,nz=sel[-1]
        if len(s)>i:
            return s[i]+nx*s.basis[0]+ny*s.basis[1]+nz*s.basis[2]
    return None

def average(s,sel):
    if s is None:
        return None
    s=Structure(s)
    s.setCarthesian()
    w=Vector(0.0,0.0,0.0)
    n=0
    for i,nx,ny,nz in sel:
        if i<len(s) and i>=0:
            w=w+s[i]+nx*s.basis[0]+ny*s.basis[1]+nz*s.basis[2]
            n=n+1
    w=(1.0/float(n))*w
    return w

def cms(s,sel):
    at=getAtomtypes()
    if at is None:
        msg().error("Atom-types information not available, calculating average.")
    if s is None:
        return None
    s=Structure(s)
    s.setCarthesian()
    w=Vector(0.0,0.0,0.0)
    M=0.0
    try:
        for i,nx,ny,nz in sel:
            if i<len(s) and i>=0:
                try:
                    m=float(s.info.getRecordForAtom(i).mass)
                except:
                    m=float(at.getRecordForElement(s.info.getRecordForAtom(i).element).mass)
                w=w+m*(s[i]+nx*s.basis[0]+ny*s.basis[1]+nz*s.basis[2])
                M=M+m
        w=(1.0/M)*w
        return w
    except:
        msg().exception()
        msg().error("CMS not aplicable, calculating an average.")
        return average(s,sel)

#def covalent(s,sel,r):
#  at=getAtomtypes()
#  if at is None:
#    msg().error("Atom-types information not available, calculating average.")
#  s=Structure(s)
#  s.setCarthesian()
#  if len(sel)==1:
#    if len(s)>0:
#      i,nx,ny,nz=sel[0]
#      return s[i]+nx*s.basis[0]+ny*s.basis[1]+nz*s.basis[2]+Vector(0.0,0.0,r)
#  elif len(sel)==2:
#    i,nx,ny,nz=sel[0]
#    v1=s[i]+nx*s.basis[0]+ny*s.basis[1]+nz*s.basis[2]
#    r1=float(at.getRecordForElement(s.info.getRecordForAtom(i).element).covalent)+r
#    i,nx,ny,nz=sel[1]
#    v2=s[i]+nx*s.basis[0]+ny*s.basis[1]+nz*s.basis[2]
#    r2=float(at.getRecordForElement(s.info.getRecordForAtom(i).element).covalent)+r



class RotateApplet(Applet):
    menupath=["Edit","Rotate atoms"]
    showmode=Applet.EXTERNAL_MODE
    def __init__(self):
        Applet.__init__(self)
        self.gladefile="rotateapplet.glade"
        self.gladename="applet_frame"

    def initUI(self):
        self.group_entry=self.xml.get_widget("group_entry")
        self.fromx_entry=self.xml.get_widget("fromx_entry")
        self.fromy_entry=self.xml.get_widget("fromy_entry")
        self.fromz_entry=self.xml.get_widget("fromz_entry")
        self.tox_entry  =self.xml.get_widget("tox_entry")
        self.toy_entry  =self.xml.get_widget("toy_entry")
        self.toz_entry  =self.xml.get_widget("toz_entry")
        self.vx_entry   =self.xml.get_widget("vx_entry")
        self.vy_entry   =self.xml.get_widget("vy_entry")
        self.vz_entry   =self.xml.get_widget("vz_entry")
        self.angle_entry=self.xml.get_widget("angle_entry")
        self.angle_scale=self.xml.get_widget("angle_scale")

    def updateSystem(self,x=None):
        pass

    def getStructure(self):
        if self.system is not None:
            return self.system.INITIAL_STRUCTURE
        return None

    def setFrom(self,v):
        if v is not None:
            self.fromx_entry.set_text(str(v[0]))
            self.fromy_entry.set_text(str(v[1]))
            self.fromz_entry.set_text(str(v[2]))
        else:
            self.fromx_entry.set_text("")
            self.fromy_entry.set_text("")
            self.fromz_entry.set_text("")
    def setTo(self,v):
        if v is not None:
            self.tox_entry.set_text(str(v[0]))
            self.toy_entry.set_text(str(v[1]))
            self.toz_entry.set_text(str(v[2]))
        else:
            self.tox_entry.set_text("")
            self.toy_entry.set_text("")
            self.toz_entry.set_text("")
    def setV(self,v):
        if v is not None:
            self.vx_entry.set_text(str(v[0]))
            self.vy_entry.set_text(str(v[1]))
            self.vz_entry.set_text(str(v[2]))
        else:
            self.vx_entry.set_text("")
            self.vy_entry.set_text("")
            self.vz_entry.set_text("")
    def updateV(self):
        try:
            f=Vector(float(eval(self.fromx_entry.get_text())),
                     float(eval(self.fromy_entry.get_text())),
                     float(eval(self.fromz_entry.get_text())))
            t=Vector(float(eval(self.tox_entry.get_text())),
                     float(eval(self.toy_entry.get_text())),
                     float(eval(self.toz_entry.get_text())))
            v=t-f
        except:
            v=None
        self.setV(v)

    def on_fromfirst_button_clicked_handler(self,*arg):
        s=self.getStructure()
        sel=Selection(self.group_entry.get_text(),s)
        self.setFrom(first(s,sel))
        self.updateV()
    def on_fromlast_button_clicked_handler(self,*arg):
        s=self.getStructure()
        sel=Selection(self.group_entry.get_text(),s)
        self.setFrom(last(s,sel))
        self.updateV()
    def on_fromavg_button_clicked_handler(self,*arg):
        s=self.getStructure()
        sel=Selection(self.group_entry.get_text(),s)
        self.setFrom(average(s,sel))
        self.updateV()
    def on_fromcms_button_clicked_handler(self,*arg):
        s=self.getStructure()
        sel=Selection(self.group_entry.get_text(),s)
        self.setFrom(cms(s,sel))
        self.updateV()
    def on_tofirst_button_clicked_handler(self,*arg):
        self.setTo(first(self.getStructure(),selection()))
        self.updateV()
    def on_tolast_button_clicked_handler(self,*arg):
        self.setTo(last(self.getStructure(),selection()))
        self.updateV()
    def on_toavg_button_clicked_handler(self,*arg):
        self.setTo(average(self.getStructure(),selection()))
        self.updateV()
    def on_tocms_button_clicked_handler(self,*arg):
        self.setTo(cms(self.getStructure(),selection()))
        self.updateV()
    def on_from_entry_activate_handler(self,*arg):
        self.updateV()
    def on_to_entry_activate_handler(self,*arg):
        self.updateV()
    def on_rotate_button_clicked_handler(self,*arg):
        self.rotate()
    def rotate(self):
        try:
            v1=float(eval(self.vx_entry.get_text()))
        except:
            msg().error("Invalid x-field in axis.")
        try:
            v2=float(eval(self.vy_entry.get_text()))
        except:
            msg().error("Invalid y-field in axis.")
        try:
            v3=float(eval(self.vz_entry.get_text()))
        except:
            msg().error("Invalid z-field in axis.")
        v=Vector(v1,v2,v3)

        try:
            o1=float(eval(self.fromx_entry.get_text()))
        except:
            msg().error("Invalid x-field in center.")
        try:
            o2=float(eval(self.fromy_entry.get_text()))
        except:
            msg().error("Invalid y-field in center.")
        try:
            o3=float(eval(self.fromz_entry.get_text()))
        except:
            msg().error("Invalid z-field in center.")
        o=Vector(o1,o2,o3)

        try:
            a=float(eval(self.angle_entry.get_text()))
        except:
            msg().error("Invalid angle.")
        a*=pi/180.0

        n=v.normal()
        if self.system is not None:
            if self.system.INITIAL_STRUCTURE is not None:
                s=self.system.INITIAL_STRUCTURE
                s.setCarthesian()
                sel=Selection(self.group_entry.get_text(),s)
                for i,nx,ny,nz in sel:
                    d=nx*s.basis[0]+ny*s.basis[1]+nz*s.basis[2]
                    if i>=0 and i<len(s):
                        r=s[i]+d-o
                        s[i]=cos(a)*r+((n*r)*(1-cos(a)))*n+sin(a)*r.cross(n)+o-d

                msg().status("OK")
                systemlist().notifySystemChanged()
            else:
                msg().error("No initial structure in the current system.")
        else:
            msg().error("No system selected.")
#    print "move",v

    def on_getgroup_button_clicked_handler(self,*arg):
#    print "sel",selection().encodeSimple()
        s=self.getStructure()
        sel=selection()
        if s is None:
            self.group_entry.set_text(sel.encodeSimple())
            self.setFrom(None)
        else:
            self.group_entry.set_text(sel.encode(s))
            self.setFrom(first(s,sel))
    def on_x_button_clicked_handler(self,*arg):
        self.setV([1,0,0])
    def on_y_button_clicked_handler(self,*arg):
        self.setV([0,1,0])
    def on_z_button_clicked_handler(self,*arg):
        self.setV([0,0,1])
    def on_a1_button_clicked_handler(self,*arg):
        if self.system.INITIAL_STRUCTURE is not None:
            self.setV(self.system.INITIAL_STRUCTURE.basis[0])
        else:
            msg().error("Basis unknown - no initial structure in the current system.")
    def on_a2_button_clicked_handler(self,*arg):
        if self.system.INITIAL_STRUCTURE is not None:
            self.setV(self.system.INITIAL_STRUCTURE.basis[1])
        else:
            msg().error("Basis unknown - no initial structure in the current system.")
    def on_a3_button_clicked_handler(self,*arg):
        if self.system.INITIAL_STRUCTURE is not None:
            self.setV(self.system.INITIAL_STRUCTURE.basis[2])
        else:
            msg().error("Basis unknown - no initial structure in the current system.")
    def on_angle_entry_activate_handler(self,*arg):
        self.rotate()

#  def on_angle_scale_value_changed_handler(self,*arg):
#    self.angle_entry.set_text(str(self.angle_scale.get_value()))
#    self.rotate()

RotateApplet.store_profile=AppletProfile(RotateApplet,tagname="RotateAtoms")
