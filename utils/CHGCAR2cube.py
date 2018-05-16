#!/usr/bin/python2
#  This utility is a part of p4vasp package.
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

from cp4vasp import *
from p4vasp.cStructure import *
from sys import *

if len(argv)<3:
    print "%s inputfile outputfile"%argv[0]
    exit(-1)

c=Chgcar()
print "Reading"
c.read(argv[1])
print "OK"
struct=Structure(pointer=c.structure)
#struct.setDirect()
#struct.translate(Vector(-0.5,-0.5,-0.5))
struct.setCarthesian()
comment=struct.comment
print comment
print "Dimensions:",c.nx,c.ny,c.nz
f=open(argv[2],"w")

volume=abs(struct.basis[0].cross(struct.basis[1])*struct.basis[2])
f.write("%s\nconverted with p4vasp; src:%s\n"%(comment, argv[1]))
f.write("%5d %12.6f %12.6f %12.6f\n"%(struct.len(),0.0,0.0,0.0))
v=(1.0/c.nx)*struct.basis[0]
f.write("%5d %12.6f %12.6f %12.6f\n"%(c.nx,v[0],v[1],v[2]))
v=(1.0/c.ny)*struct.basis[1]
f.write("%5d %12.6f %12.6f %12.6f\n"%(c.ny,v[0],v[1],v[2]))
v=(1.0/c.nz)*struct.basis[2]
f.write("%5d %12.6f %12.6f %12.6f\n"%(c.nz,v[0],v[1],v[2]))
for i in range(len(struct)):
    v=struct[i]
    f.write("%5d %12.6f %12.6f %12.6f %12.6f\n"%(struct.speciesIndex(i)+1,0.0,v[0],v[1],v[2]))


for x in range(c.nx):
    print x,"/",c.nx
    for y in range(c.ny):
        for z in range(c.nz):
            f.write("%g "%(c.get(x,y,z)/volume))
            if z%6 == 5:
                f.write("\n")
        f.write("\n")

f.close()
