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

from p4vasp.Structure import *
from p4vasp.sellang import *
#from p4vasp.SystemPM import *
#s=XMLSystemPM('vasprun.xml')
#p=s.INITIAL_STRUCTURE

p=Structure("CONTCAR")
p.setCarthesian()
l1=decode("-160",p)
l2=decode("161-",p)
print "Group 1 has %3d elements."%len(l1)
print "Group 2 has %3d elements."%len(l2)

d=[]
for i in l1:
    for j in l2:
        if i==j:
            print "Substructures have a common atom %d."%(i+1)
        else:
            d.append((p.mindistCartVectors(p[i],p[j]),i,j))

m,i,j=min(d)
print "Minimal distance:",m
print "for atoms %3d    "%i,p[i]
print "          %3d    "%j,p[j]
