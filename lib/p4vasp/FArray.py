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




"""
Wrapper for two array objects written in c++:
FArray1D and FArray2D.
These are the one and two dimensional arrays of real numbers (double).
"""

from UserList import *
from string import *
from p4vasp.cmatrix import *
import cp4vasp
import _cp4vasp
from types import *

class FArray1D(cp4vasp.FArray1D):
    def __init__(self,l=[],pointer=None):
        if pointer is not None:
            self.this=pointer
        else:
            if type(l) == type(1):
                cp4vasp.FArray1D.__init__(self,l)
            if (type(l) in (ListType,TupleType)) or isinstance(l,UserList):
                cp4vasp.FArray1D.__init__(self,len(l))
                for i in range(len(l)):
                    self.set(i,l[i])
    __len__=cp4vasp.FArray1D.size
    __getitem__=cp4vasp.FArray1D.get
    __setitem__=cp4vasp.FArray1D.set
    def getVector(self):
        return Vector(pointer=self.cloneBuff())
    def __str__(self):
        return "["+join(map(lambda x:"%+14.10f"%x,self),",")+"]"
    def __repr__(self):
        return "FArray1D(["+join(map(lambda x:"%+14.10f"%x,self),",")+"])"


class FArray2D(cp4vasp.FArray2D):
    def __init__(self,n=0,m=0,pointer=None,elem=None,tag="v"):
        if elem is not None:
            a=cp4vasp.createFArray2Dsimple(elem,tag)
            a.thisown=0
            self.this=a.this
            self.thisown=1
        else:
            if pointer is not None:
                self.this=pointer
                self.thisown=1
            else:
                cp4vasp.FArray2D.__init__(self,n,m)

    __len__=cp4vasp.FArray2D.sizeX


    def __getitem__(self,i):
        return FArray1D(pointer=self.getArray(i))
    def __setitem__(self,i,l):
        for j in range(min(self.sizeY(),len(l))):
            self.set(i,j,float(l[j]))
    def getVector(self,i):
        return Vector(pointer=self.cloneVector(i))
    def __str__(self):
        return "[\n"+join(map(lambda x:"  "+str(x),self),",\n")+"]"
    def __repr__(self):
        return "FArray2D(%d,%d,%s)"%(self.sizeX(),self.sizeY(),str(self))
