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


from p4vasp.StructureWindow import *
from p4vasp.store import *
from p4vasp.applet.Applet import *
from p4vasp.util import getAtomtypes
import p4vasp.Selection
import p4vasp.Structure
import p4vasp.cStructure

class StructureWindowApplet(Applet,p4vasp.Selection.SelectionListener):
    menupath=["Structure","Window"]
    showmode=Applet.EXTERNAL_ONLY_MODE
    NONE_SEQUENCE        = 0
    INITIAL_SEQUENCE     = 1
    FINAL_SEQUENCE       = 2
    PRIMITIVE_SEQUENCE   = 3
    UNDEFINED_SEQUENCE   = 4
    RELAXATION_SEQUENCE  = 5
    MD_SEQUENCE          = 6

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

    def notifyAtomSelection(self, sel,origin):
#    self.atom_selection.set_text(sel.encode(self.structure))
        sel=p4vasp.Selection.selection()
        self.swin.removeSelectedAll()
        for i,nx,ny,nz in sel:
            self.swin.selectAtom(i,nx,ny,nz)

    def __init__(self):
        Applet.__init__(self)
        self.swin=None
        self.radius_factor=1.0
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
        raise "StructureWindowApplet.setEmbeddedMode() not supported."

    def createPanel(self):
        return None
    def setSystem(self,x=None):
        if not self.pin_status:
            self.system=x
            self.updateSystem()

    def updateSystem(self,x=None):
#    self.swin.setStructure(self.system.INITIAL_STRUCTURE)
        self.updateSeq()

    def showStructureWindow(self):
        if self.swin is None:
            l=[(0,0,0,0)]
            for a in applets():
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
            self.swin=StructureWindow(x=xx,y=yy,w=500,h=400,title="p4vasp Structure",atomtypes=getAtomtypes())
            self.swin.setRadiusFactor(0.5*self.radius_factor)
#      self.swin.setBackground(1,1,1)
        self.swin.show()

    def getSequence(self):
        if self.sequencetype==self.NONE_SEQUENCE:
            return None
        if self.sequencetype==self.INITIAL_SEQUENCE:
            s=self.system.INITIAL_STRUCTURE
            if s is not None:
                return [s]
            else:
                return None
        if self.sequencetype==self.FINAL_SEQUENCE:
            s=self.system.FINAL_STRUCTURE
            if s is not None:
                return [s]
            else:
                return None
        if self.sequencetype==self.PRIMITIVE_SEQUENCE:
            s=self.system.PRIMITIVE_STRUCTURE
            if s is not None:
                return [s]
            else:
                return None
        if self.sequencetype==self.UNDEFINED_SEQUENCE:
            return self.system.STRUCTURE_SEQUENCE_L
        if self.sequencetype==self.RELAXATION_SEQUENCE:
            return self.system.RELAXATION_SEQUENCE_L
        if self.sequencetype==self.MD_SEQUENCE:
            return self.system.MD_SEQUENCE_L
        return None

    def getArrows(self,index=None):
        if index is None:
            index=self.index
        if self.system is None:
            return None
        if self.arrowstype==self.FORCES_ARROWS:
            f=self.system.FORCES_SEQUENCE_L
            if f is not None:
                if index < len(f):
                    return f[index]
        seq=self.getSequence()
        if seq is not None:
            if index<len(seq):
                if len(seq[index])==0:
                    return None
                si=p4vasp.cStructure.Structure(seq[index])
                si.setCarthesian()
                if self.arrowstype==self.DIFF_INITIAL_ARROWS:
                    rel=self.system.INITIAL_STRUCTURE
                    if rel is not None:
                        rel=p4vasp.cStructure.Structure(rel)
                        rel.setCarthesian()
                        l=[]
                        for i in range(min(len(si),len(rel))):
                            l.append(si[i]-rel[i])
                        return l
                if self.arrowstype==self.DIFF_FINAL_ARROWS:
                    rel=self.system.FINAL_STRUCTURE
                    if rel is not None:
                        rel=p4vasp.cStructure.Structure(rel)
                        rel.setCarthesian()
                        l=[]
                        for i in range(min(len(si),len(rel))):
                            l.append(rel[i]-si[i])
                        return l
        return None

    def getArrowsSequence(self):
        if self.arrowstype == self.NONE_ARROWS:
            return None
        sequence=self.getSequence()
        if sequence is None:
            return None
        arrows_sequence=[]
        for i in range(len(sequence)):
            arrows_sequence.append(self.getArrows(i))
        return arrows_sequence

    def setStructure(self,s):
        if s is not None:
            s=p4vasp.Structure.Structure(s)
            if self.cell_centering==self.CELL_CENTERING_INSIDE:
                s.toUnitCell()
            elif self.cell_centering==self.CELL_CENTERING_ZERO:
                s.toCenteredUnitCell()
            self.swin.setStructure(s)
        else:
            self.swin.setStructure(None)

    def updateSeq(self):
        index=self.index
        seq=self.getSequence()
#    print "updateSeq",index,len(seq)
        if seq is not None:
            if index=="last":
                index=len(seq)-1
#      print "  a",index,len(seq)
            if index<0:
                index=len(seq)+index
            elif index>=len(seq):
                index=len(seq)-1
#      print "  b",index,len(seq)
            if index<0:
                index=0
#      print "  c",index,len(seq)

            self.index=index
            self.setStructure(seq[index])
        else:
            index=0
            self.index=0
            self.setStructure(None)
        self.swin.setArrows(self.getArrows())

    def setIndex(self,index):
        self.index=index
        self.updateSeq()
    def setSequenceType(self,seqtype):
        self.sequencetype=seqtype
        self.updateSeq()
    def setArrowsType(self,atype):
        self.arrowstype=atype
        self.updateSeq()

    def getWindowPtr(self):
        if self.swin is not None:
            if self.swin.win is not None:
                return self.swin.win.this
        return None


StructureWindowApplet.store_profile=AppletProfile(StructureWindowApplet,tagname="StructureWindow",
attr_setup="""
float radius_factor
int   index
int   sequencetype
int   arrowstype
int   cell_centering
""")
#DOSApplet.config_profile=AppletProfile(TDOSApplet,tagname="TDOS")
