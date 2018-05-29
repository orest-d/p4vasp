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
from p4vasp.StructureWindow import *
from p4vasp.store import *
from p4vasp.applet.Applet import *
from p4vasp.applet.StructureWindowApplet import StructureWindowApplet
from p4vasp.util import getAtomtypes
import p4vasp.Structure
import p4vasp.cStructure
import p4vasp.cmatrix as cmatrix
import p4vasp.Selection

class STMWindowApplet(Applet,p4vasp.Selection.SelectionListener):
    menupath=["Electronic","STM Window"]
    showmode=Applet.EXTERNAL_ONLY_MODE
    CLAMP_OTHER=-1
    CLAMP_THRESHOLD=0
    CLAMP_COS=1
    CLAMP_ATAN=2
    CLAMP_FERMI=3

    NONE_SEQUENCE        = 0
    INITIAL_SEQUENCE     = 1
    FINAL_SEQUENCE       = 2
    UNDEFINED_SEQUENCE   = 3
    RELAXATION_SEQUENCE  = 4
    MD_SEQUENCE          = 5

    NONE_ARROWS          = 0
    FORCES_ARROWS        = 1
    DIFF_INITIAL_ARROWS  = 2
    DIFF_FINAL_ARROWS    = 3
    DIFF_PREVIOUS_ARROWS = 4
    DIFF_NEXT_ARROWS     = 5
    PHONON_ARROWS        = 6

    CELL_CENTERING_NONE   = 0
    CELL_CENTERING_INSIDE = 1
    CELL_CENTERING_ZERO   = 2

    def __init__(self):
        Applet.__init__(self)
        self.win=None
        self.a=None
        self.dir=2
        self.n=0
        self.value=0.0
#    self.sigmax=0
#    self.sigmay=0
#    self.sigmaz=0
        self.sh=0
        self.sv=0
        self.n1=0
        self.n2=0
        self.n3=0
        self.chgname="PARCHG"
        self.sd=None
        self.lo=0
        self.hi=1
        self.inv=0
        self.navigator=None
        self.clamp_type=0
        self.charge=None
        self.smooth_charge=None
        self.structure=None
        self.minimum=0
        self.maximum=0
        self.average=0
        self.sigma=0
        self.src=0
        self.mode=0
        self.interpolation=0
        self.postinterpolation=0
        self.postsigma=0
        self.postn=0
        self.atomtypes=getAtomtypes()
        self.structure_offset=0.0
        self.brightness=0.0
        self.contrast  =1.0
        self.multiple=(1,1,1)
        self.hide_atoms=[]
        self.b1=cmatrix.Vector(0,0,0)
        self.b2=cmatrix.Vector(0,0,0)
        self.bz=cmatrix.Vector(0,0,0)

        #DUMMY ATTRIBUTES -for compatibility with StructureWindowControlApplet
        self.chgcar=None
        self.index=0
        self.sequencetype=self.INITIAL_SEQUENCE
        self.arrowstype=0
        self.cell_centering=0


    def initUI(self):
        self.showStructureWindow()

    def setExternalMode(self):
        pass
    def setEmbeddedMode(self):
#    msg().error("StructureWindowApplet.setEmbeddedMode() not supported.")
        raise "STMWindowApplet.setEmbeddedMode() not supported."

    def createPanel(self):
        return None
    def setSystem(self,x=None):
        if not self.pin_status:
            self.system=x
            self.updateSystem()

    def updateSystem(self,x=None):
        schedule(self.updateSystemGen())

    def updateSystemGen(self,x=None):
        self.showStructureWindow()
        self.system.scheduleFirst(self.chgname)
        yield 1
        c=self.system[self.chgname].get()
        if c is not None:
            c=c.clone()
        yield 1
        self.charge=c
        self.smooth_charge=None

        if c is not None:
            s=p4vasp.cStructure.Structure(pointer=c.structure)
            self.structure=s
        else:
            self.structure=None
            self.setStructure(None)

        self.updatePlane()
        ctl=applets().getActive(p4vasp.applet.STMWindowControlApplet.STMWindowControlApplet)
        ctl.applet_activated(None,self)

    def initDir(self,s=None):
        if s is None:
            c=self.getCharge()
            if c is None:
                return None
            s=p4vasp.cStructure.Structure(pointer=c.structure)

        if self.dir==0:
            self.b1=cmatrix.Vector(s.basis[1])
            self.b2=cmatrix.Vector(s.basis[2])
            self.bz=cmatrix.Vector(s.basis[0])
        elif self.dir==1:
            self.b1=cmatrix.Vector(s.basis[0])
            self.b2=cmatrix.Vector(s.basis[2])
            self.bz=cmatrix.Vector(s.basis[1])
        else:
            self.b1=cmatrix.Vector(s.basis[0])
            self.b2=cmatrix.Vector(s.basis[1])
            self.bz=cmatrix.Vector(s.basis[2])
#    print "initDir b1",b1
#    print "initDir b2",b2
        self.sd.setB1(self.b1.pointer)
        self.sd.setB2(self.b2.pointer)

    def setN(self,n):
        nn=self.getMaxN()
        if type(n)==type(""):
            if self.charge is None:
                msg().error("Charge not available in STM applet.")
                return None
            if self.structure is None:
                msg().error("Structure not available in STM applet.")
                return None
            try:
                txt=strip(n)
                if txt[0]=="#":
                    n=int(eval(txt[1:]))
                elif txt[-1]=="%":
                    f=float(eval(txt[:-1]))*0.01
                    n=int(100*nn+f*nn)%nn
                else:
                    zz=self.getMaxPos()
                    f=float(eval(txt))/zz
                    n=int(100*nn+f*nn)%nn
            except:
                msg().error("Format error for STM tip position.")
        self.n=min(max(n,0),nn-1)

    def getMaxN(self):
        if self.charge is None:
            return 0
        if self.dir==0:
            return self.charge.nx
        elif self.dir==1:
            return self.charge.ny
        else:
            return self.charge.nz

    def getMaxPos(self):
        if self.structure is None:
            return 0
        if self.dir==0:
            return self.structure.basis[0].length()
        elif self.dir==1:
            return self.structure.basis[1].length()
        else:
            return self.structure.basis[2].length()


#  def setPlaneN(self,n=None):
#    if self.charge is None:
#      msg().error("Charge not available in STM applet.")
#      return None
#    self.initDir()
#    if n is not None:
#      self.setN(n)
#    if self.dir==0:
#      a=self.charge.getPlaneX(self.n)
#    elif self.dir==1:
#      a=self.charge.getPlaneY(self.n)
#    else:
#      a=self.charge.getPlaneZ(self.n)
#    self.lo=a.getMinimum()
#    self.hi=a.getMaximum()
#    self.setFArray(a)

    def getCharge(self):
        import os.path
        if self.src:
            if self.smooth_charge is None:
                if os.path.exists(self.system.PATH+"PARCHG_SMOOTH"):
                    msg().status("Loading PARCHG_SMOOTH")
                    self.smooth_charge=cp4vasp.Chgcar()
                    self.smooth_charge.read(self.system.PATH+"PARCHG_SMOOTH")
                    msg().status("OK")
                    return self.smooth_charge
                msg().error("Smoothed PARCHG not available - press 'Smooth' to create.")
                return self.charge
            return self.smooth_charge
        else:
            if self.charge is None:
                msg().error("PARCHG not available in STM applet.")
            return self.charge


    def updateOrigin(self):
        orig=(-int(self.sd.n1/2))*self.b1+(-int(self.sd.n2/2))*self.b2
        if self.mode==0:
            if self.getMaxN():
                if self.dir==0:
                    orig[0]+=self.bz.length()*self.n/self.getMaxN()+self.structure_offset
                elif self.dir==1:
                    orig[1]+=self.bz.length()*self.n/self.getMaxN()+self.structure_offset
                else:
                    orig[2]+=self.bz.length()*self.n/self.getMaxN()+self.structure_offset
        else:
            if self.dir==0:
                orig[0]+=self.structure_offset
            elif self.dir==1:
                orig[1]+=self.structure_offset
            else:
                orig[2]+=self.structure_offset
        self.sd.setOrigin(orig.pointer)

    def updatePlane(self):
        c=self.getCharge()
        if c is None:
            return None
        s=p4vasp.cStructure.Structure(pointer=c.structure)
        self.initDir(s)

        self.updateOrigin()
        if self.mode==0:
            if self.dir==0:
                a=c.getPlaneX(self.n)
            elif self.dir==1:
                a=c.getPlaneY(self.n)
            else:
                a=c.getPlaneZ(self.n)
        else:
            if self.interpolation==0:
                if self.dir==0:
                    a=c.createCCPlaneX(self.value)
                elif self.dir==1:
                    a=c.createCCPlaneY(self.value)
                else:
                    a=c.createCCPlaneZ(self.value)
            else:
                if self.dir==0:
                    a=c.createCCPlaneCubicX(self.value)
                elif self.dir==1:
                    a=c.createCCPlaneCubicY(self.value)
                else:
                    a=c.createCCPlaneCubicZ(self.value)
        if self.postinterpolation>0:
            a=a.cubicInterpolation(self.postinterpolation,self.postinterpolation)
        if (self.postsigma>0) and (self.postn>0):
            a=a.smear(self.postsigma,self.postn,self.postn,self.b1.pointer,self.b2.pointer)
        self.lo=a.getMinimum()
        self.hi=a.getMaximum()
        self.setFArray(a)

#  def setSmoothPlaneNGen(self,n=None):
#    msg().status("STM Smoothing")
#    yield 1
#    if self.charge is None:
#      msg().error("Charge not available in STM applet.")
#    elif self.structure is None:
#      msg().error("Structure not available in STM applet.")
#    else:
#      self.initDir()
#      if n is not None:
#       self.setN(n)
#      else:
#       self.setN(self.n)
#      msg().status("STM Smoothing.")
#      yield 1
#      if self.dir==0:
#       ap=self.charge.createSmoothPlaneProcessX(self.n,self.sigmax,self.sigmay,self.sigmaz,self.limit)
#      elif self.dir==1:
#       ap=self.charge.createSmoothPlaneProcessY(self.n,self.sigmax,self.sigmay,self.sigmaz,self.limit)
#      else:
#       ap=self.charge.createSmoothPlaneProcessZ(self.n,self.sigmax,self.sigmay,self.sigmaz,self.limit)
#      msg().status("STM Smoothing..")
#      yield 1
#      while ap.next():
#       msg().status(ap.status())
#       msg().step(ap.step(),ap.total())
#       yield 1
#      msg().status("STM OK")
#      yield 1
#      self.setFArray(ap.getPlane())
#      msg().status("OK")
#      msg().step(0,1)

    def updateSmoothGen(self):
        if (self.charge is not None):
            msg().status("Start smearing")
            yield 1
            chsmear=cp4vasp.GaussianChgcarSmear()
            chsmear.lx=self.n1
            chsmear.ly=self.n2
            chsmear.lz=self.n3
            chsmear.dir=self.dir
            chsmear.horizontal_sigma=self.sh
            chsmear.vertical_sigma=self.sv
#      chsmear.setChgcar(self.charge)

            cap=cp4vasp.ChgcarSmearProcess(self.charge,chsmear)
            msg().status("Start smearing.")
            yield 1
            while cap.next():
                msg().status(cap.status())
                msg().step(cap.step(),cap.total())
                yield 1
            self.smooth_charge=cap.get().clone()
            self.smooth_charge.write(self.system.PATH+"PARCHG_SMOOTH")
            msg().status("OK")
            msg().step(0,1)
            self.updatePlane()

    def setFArray(self,a=0):
        if a is None:
            self.a=None
            self.minimum=0
            self.maximum=0
            self.sigma=0
            self.average=0
            self.sd.setFArray(None)
            self.sd.scale=0
        else:
            if a is not 0:
                self.a=a
            self.minimum=a.getMinimum()
            self.maximum=a.getMaximum()
            self.sigma=a.getSigma()
            self.average=a.getAverage()
            self.sd.setFArray(self.a)
            sc=abs(self.maximum-self.minimum)
            if sc:
                self.sd.scale=1.0/sc
            else:
                self.sd.scale=0
        self.redraw()

    def redraw(self):
        if self.inv:
            self.sd.lo=self.hi
            self.sd.hi=self.lo
        else:
            self.sd.lo=self.lo
            self.sd.hi=self.hi
        self.win.redraw()
        cp4vasp.VisSync()

    def setClamp(self,c):
        if c==self.CLAMP_THRESHOLD:
            self.clamp=cp4vasp.ThresholdClamp()
            self.clamp.thisown=0
            self.clamp_type=c
        elif c==self.CLAMP_COS:
            self.clamp=cp4vasp.CosClamp()
            self.clamp.thisown=0
            self.clamp_type=c
        elif c==self.CLAMP_ATAN:
            self.clamp=cp4vasp.AtanClamp()
            self.clamp.thisown=0
            self.clamp_type=c
        elif c==self.CLAMP_FERMI:
            self.clamp=cp4vasp.FermiClamp()
            self.clamp.thisown=0
            self.clamp_type=c
        else:
            self.clamp=c
            self.clamp.thisown=0
            self.clamp_type=self.CLAMP_OTHER
        self.sd.setClamp(self.clamp)
        self.redraw()


    def showStructureWindow(self):
        if self.win is None:
            l=[(0,0,0,0)]
            for a in applets():
                if isinstance(a,STMWindowApplet):
                    if a.win is not None:
                        w=a.win
                        if w is not None:
                            l.append((w.x,w.y,w.w,w.h))
                if isinstance(a,StructureWindowApplet):
                    if a.swin is not None:
                        w=a.swin.win
                        if w is not None:
                            l.append((w.x,w.y,w.w,w.h))
            xx=max(map(lambda x:x[0]+x[2],l))
            yy=max(map(lambda x:x[1]+x[3],l))
            if yy<=600:
                xx=0
            else:
                yy=0
            self.win                 = cp4vasp.VisWindow(xx,yy,500,400,"p4vasp STM")
            self.navigator           = cp4vasp.VisNavDrawer()
            self.structure_drawer    = cp4vasp.VisStructureDrawer()
            self.sd                  = cp4vasp.VisSlideDrawer()
            self.setClamp(0)
            self.grad=cp4vasp.GrayColorGradient()
            self.grad.thisown=0
            self.sd.setGradient(self.grad)
            b1=cmatrix.Vector(1,0,0)
            b2=cmatrix.Vector(0,1,0)
            orig=cmatrix.Vector(0,0,0)
            self.sd.setB1(b1.pointer)
            self.sd.setB2(b2.pointer)
            self.sd.setOrigin(orig.pointer)
            self.sd.scale=10
            self.sd.n1=1
            self.sd.n2=1
            self.navigator.append(self.sd)
            self.navigator.append(self.structure_drawer)
            self.win.setDrawer(self.navigator)
            self.setRadiusFactor(0.5)

#    self.win.show()

    def setCellColor(self,r,g,b):
        self.structure_drawer.setCellColor(r,g,b)
    def setBackground(self,r,g,b):
        self.navigator.setBackground(r,g,b)
    def getBackground(self):
        n=self.navigator
        return (n.bg_red,n.bg_green,n.bg_blue)
    def setIsosurfaceLevel(self,l):
        msg().status("Function 'setIsosurfaceLevel' not implemented in the STM window.")
    def getIsosurfaceLevel(self):
        msg().status("Function 'getIsosurfaceLevel' not implemented in the STM window.")
    def setChgcar(self,c,update_structure=0):
        msg().status("Function 'setChgcar' not implemented in the STM window.")
    def getArrowsScale(self):
        msg().status("Function 'getArrowsScale' not implemented in the STM window.")
    def setArrowsScale(self,s):
        msg().status("Function 'setArrowsScale' not implemented in the STM window.")
    def getRadiusFactor(self):
        return self.structure_drawer.getRadiusFactor()
    def setRadiusFactor(self,s):
        return self.structure_drawer.setRadiusFactor(s)
    def showCell(self,s):
        return self.structure_drawer.showCell(s)
    def setIndex(self,index):
        msg().status("Function 'setIndex' not implemented in the STM window.")
        self.index=index
#    self.updateSeq()
    def setSequenceType(self,seqtype):
        msg().status("Function 'setSequenceType' not implemented in the STM window.")
        self.sequencetype=seqtype
#    self.updateSeq()
    def setArrowsType(self,atype):
        msg().status("Function 'setArrowsType' not implemented in the STM window.")
        self.arrowstype=atype
#    self.updateSeq()
    def updateSeq(self):
        msg().status("Function 'updateSeq' not implemented in the STM window.")
    def setMultiple(self,a,b,c):
        self.multiple=(a,b,c)
        self.structure_drawer.setMultiple(int(a),int(b),int(c))
    def getMultiple(self):
        return self.multiple


    def setStructure(self,structure):
        self.vstructure=structure
        if structure is None or not len(structure):
            self.structure_drawer.setStructure(None)
        else:
            structure=p4vasp.cStructure.Structure(structure)
            structure.correctScaling()
            if self.atomtypes is not None:
                structure.info.fillAttributesWithTable(p4vasp.cStructure.AtomInfo(self.atomtypes))
            self.structure_drawer.setStructure(structure.this)
            info=self.structure_drawer.info
            for i in range(info.len()):
                info.getRecord(i).hidden=0
            for i in self.hide_atoms:
                if i>=0 and i<len(structure):
                    info.getRecord(i).hidden=1
            self.vstructure=structure

    def updateStructure(self):
        if self.visible:
            self.structure_drawer.updateStructure()
    def getHiddenAtoms(self):
        return self.hide_atoms
    def setHiddenAtoms(self,l):
        self.hide_atoms=l
        if self.structure is not None:
            info=self.structure_drawer.info
            for i in range(info.len()):
                info.getRecord(i).hidden=0
            for i in self.hide_atoms:
                if i>=0 and i<len(self.structure):
                    info.getRecord(i).hidden=1
        self.structure_drawer.updateStructure()
    def removeSelectedAll(self):
        return self.structure_drawer.removeSelectedAll()
    def selectAtom(self,atom,nx=0,ny=0,nz=0):
        return self.structure_drawer.selectAtom(atom,nx,ny,nz)
    def deselectAtom(self,atom,nx=0,ny=0,nz=0):
        return self.structure_drawer.deselectAtom(atom,nx,ny,nz)
    def getSelectedCount(self):
        return self.structure_drawer.getSelectedCount()
    def getSelected(self,i):
        return self.structure_drawer.getSelected(i)


    def notifyAtomSelection(self, sel,origin):
#    self.atom_selection.set_text(sel.encode(self.structure))
        sel=p4vasp.Selection.selection()
        self.removeSelectedAll()
        for i,nx,ny,nz in sel:
            self.selectAtom(i,nx,ny,nz)

    def getWindowPtr(self):
        if self.win is not None:
            return self.win.this
        return None

STMWindowApplet.store_profile=AppletProfile(STMWindowApplet,tagname="STMWindow",
attr_setup="""
int    dir
int    n
float  value
float  sh
float  sv
int    n1
int    n2
int    n3
string chgname
float  lo
float  hi
int    inv
int    clamp_type
int    src
int    mode
int    interpolation
int    postinterpolation
float  postsigma
int    postn
float  brightness
float  contrast
""")

#DOSApplet.config_profile=AppletProfile(TDOSApplet,tagname="TDOS")
