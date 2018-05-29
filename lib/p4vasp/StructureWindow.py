#!/usr/bin/python2
#
# HappyDoc:docStringFormat='ClassicStructuredText'
#
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



import _cp4vasp
import cp4vasp
import p4vasp.cStructure
from p4vasp import *
from p4vasp.matrix import *

#zombies=[]

class StructureWindow(cp4vasp.VisWindow):
    def __init__(self,x=0,y=0,w=400,h=400,title="",this=None,atomtypes=None):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.title=title
        self.atomtypes=atomtypes
        self.win=cp4vasp.VisWindow(x,y,w,h,title)
        self.navigator           = cp4vasp.VisNavDrawer()
        self.structure_drawer    = cp4vasp.VisStructureDrawer()
        self.arrows_drawer       = cp4vasp.VisStructureArrowsDrawer(self.structure_drawer)
        self.arrows_drawer.red   =0.5
        self.arrows_drawer.green =1.0
        self.arrows_drawer.blue  =0.5
        self.isosurface_drawer     = cp4vasp.VisIsosurfaceDrawer()
        self.neg_isosurface_drawer = cp4vasp.VisIsosurfaceDrawer()
        self.isosurface_drawer.red    = 99/255.0
        self.isosurface_drawer.green  = 195/255.0
        self.isosurface_drawer.blue   = 255/255.0
        self.neg_isosurface_drawer.red    = 198/255.0
        self.neg_isosurface_drawer.green  = 29/255.0
        self.neg_isosurface_drawer.blue   = 72/255.0
        self.setIsosurfaceLevel(0.0)
#    self.setChgcar("/home/orest/work/p4vasp-0.1.2/CHARGTEST")
#    self.setChgcar("/fs/home2/odubay/work/p4vasp/p4vasp/CHARGTEST")

        self.navigator.append(self.structure_drawer)
        self.navigator.append(self.arrows_drawer)
        self.navigator.append(self.isosurface_drawer)
        self.navigator.append(self.neg_isosurface_drawer)
        self.win.setDrawer(self.navigator)
        self.structure=None
        self.visible=1
        self.multiple=(1,1,1)
        self.dsx=2
        self.dsy=2
        self.dsz=2
        self.hide_atoms=[]
        self.chgcar=None
#    self.structure_drawer.setCellLineWidth(0)
    def getRotmat(self):
        m=[]
        for i in range(4):
            v=[]
            for j in range(4):
                v.append(self.navigator.getRotMatElement(i,j))
            m.append(v)
        return Matrix(m)

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

    def setCellColor(self,r,g,b):
        self.structure_drawer.setCellColor(r,g,b)
    def setBackground(self,r,g,b):
        self.navigator.setBackground(r,g,b)
    def getBackground(self):
        n=self.navigator
        return (n.bg_red,n.bg_green,n.bg_blue)

    def setChgcar(self,c,update_structure=0):
        if type(c)==type(""):
            self.chgcar=cp4vasp.Chgcar()
            self.chgcar.read(c)
        else:
            self.chgcar=c
        if self.chgcar is not None:
            self.chgcar.structure.correctScaling()
            nx=self.chgcar.nx
            ny=self.chgcar.ny
            nz=self.chgcar.nz
            for dsx in range(max(self.dsx,1),0,-1):
                if nx%dsx==0:
                    break
            for dsy in range(max(self.dsy,1),0,-1):
                if ny%dsy==0:
                    break
            for dsz in range(max(self.dsz,1),0,-1):
                if nz%dsz==0:
                    break
            if not(dsx==1 and dsy==1 and dsz==1):
                msg().status("Downsampling: %d %d %d"%(dsx,dsy,dsz))
                self.chgcar.downSampleByFactors(dsx,dsy,dsz)
        self.isosurface_drawer.setChgcar(self.chgcar)
        self.neg_isosurface_drawer.setChgcar(self.chgcar)
        if self.chgcar is not None:
            if update_structure:
                s=p4vasp.cStructure.Structure()
                s.setStructure(self.chgcar.structure)
                self.setStructure(s)

    def setIsosurfaceLevel(self,l):
        self.isosurface_drawer.setLevel(l)
        self.neg_isosurface_drawer.setLevel(-l)

    def getIsosurfaceLevel(self):
        return self.isosurface_drawer.getLevel()

    def setMultiple(self,a,b,c):
        self.multiple=(a,b,c)
        self.structure_drawer.setMultiple(int(a),int(b),int(c))
        self.isosurface_drawer.setMultiple(int(a),int(b),int(c))
        self.neg_isosurface_drawer.setMultiple(int(a),int(b),int(c))
    def getMultiple(self):
        return self.multiple
    def setStructure(self,structure):
        self.structure=structure
        if structure is None or not len(structure):
            self.structure_drawer.setStructure(None)
        else:
            structure=p4vasp.cStructure.Structure(structure)

#      print "set structure - scaling",structure.scaling
            structure.correctScaling()
#      print "set structure - scaling",structure.scaling
            if self.atomtypes is not None:
                structure.info.fillAttributesWithTable(p4vasp.cStructure.AtomInfo(self.atomtypes))
            self.structure_drawer.setStructure(structure.this)
            info=self.structure_drawer.info
            for i in range(info.len()):
                info.getRecord(i).hidden=0
            for i in self.hide_atoms:
                if i>=0 and i<len(structure):
                    info.getRecord(i).hidden=1
            self.structure=structure
        self.arrows_drawer.updateStructure()

    def show(self):
        if not self.visible:
            self.navigator           = cp4vasp.VisNavDrawer()
            self.structure_drawer    = cp4vasp.VisStructureDrawer()
            self.arrows_drawer       = cp4vasp.VisStructureArrowsDrawer(self.structure_drawer)
            self.arrows_drawer.red   =0.5
            self.arrows_drawer.green =1.0
            self.arrows_drawer.blue  =0.5
            self.isosurface_drawer     = cp4vasp.VisIsosurfaceDrawer()
            self.neg_isosurface_drawer = cp4vasp.VisIsosurfaceDrawer()
            self.isosurface_drawer.red    = 99/255.0
            self.isosurface_drawer.green  = 195/255.0
            self.isosurface_drawer.blue   = 255/255.0
            self.neg_isosurface_drawer.red    = 198/255.0
            self.neg_isosurface_drawer.green  = 29/255.0
            self.neg_isosurface_drawer.blue   = 72/255.0
            self.setIsosurfaceLevel(0.0)
    #    self.setChgcar("/home/orest/work/p4vasp-0.1.2/CHARGTEST")
    #    self.setChgcar("/fs/home2/odubay/work/p4vasp/p4vasp/CHARGTEST")

            self.navigator.append(self.structure_drawer)
            self.navigator.append(self.arrows_drawer)
            self.navigator.append(self.isosurface_drawer)
            self.navigator.append(self.neg_isosurface_drawer)
            self.win.setDrawer(self.navigator)
            self.setStructure(self.structure)
            self.win.show()
            self.visible=1

    def setDrawIsosurfaceAsPoints(self,flag):
        self.isosurface_drawer.setDrawAsPoints(flag)
        self.neg_isosurface_drawer.setDrawAsPoints(flag)
    def getDrawIsosurfaceAsPoints(self):
        return self.isosurface_drawer.getDrawAsPoints()

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

    def setArrows(self,l=None):
        a=self.arrows_drawer
        for i in range(a.len()):
            a.setArrow(i,0,0,0)
        if l is not None:
            for i in range(min(len(l),a.len())):
                v=l[i]
                a.setArrow(i,v[0],v[1],v[2])
        self.redraw()

    def getArrowsScale(self):
        return self.arrows_drawer.getScale()

    def setArrowsScale(self,s):
        return self.arrows_drawer.setScale(s)

    def getRadiusFactor(self):
        return self.structure_drawer.getRadiusFactor()

    def setRadiusFactor(self,s):
        return self.structure_drawer.setRadiusFactor(s)

    def showCell(self,s):
        return self.structure_drawer.showCell(s)

    def hide(self):
        print "StructureWindow.hide"
        if self.visible:

            ###############################################################
            # THE FOLLOWING LINE IS A QUICK BUGFIX                        #
            # I do not fully understand the bug, but when it is not there,#
            # it could end with segmentation fault when using in threads  #
            # see test_StructureWindow_th.py                          oD  #
            self.win.setDrawer(None)
            ###############################################################

            self.neg_isosurface_drawer=None
            self.isosurface_drawer=None
            self.arrows_drawer=None
            self.structure_drawer=None
            self.navigator=None
            print "StructureWindow.hide a"
            self.win.hide()
            print "StructureWindow.hide b"
            self.visible=0
        print "StructureWindow.hide -"

    def redraw(self):
        if self.visible:
            self.win.redraw()
    def updateStructure(self):
        if self.visible:
            self.structure_drawer.updateStructure()
        self.arrows_drawer.updateStructure()

    def __del__(self):
#    print "del StructureWindow"
#    zombies.append(self.win)
        self.win=None
        cp4vasp.VisSync()
