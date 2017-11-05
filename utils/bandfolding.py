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


from p4vasp.SystemPM import *
from string import split


s=XMLSystemPM("vasprun.xml")

#kpoints=s.KPOINT_LIST
kpoints=None
ev=s.EIGENVALUES
e=s.E_FERMI
divisions=s.KPOINT_DIVISIONS
print "Divisions:",divisions


if (e is None):
    print "Reading E_FERMI from DOSCAR"
    d=open("DOSCAR","r")
    d.readline()
    d.readline()
    d.readline()
    d.readline()
    d.readline()
    e=float(split(d.readline())[3])
    print "E_FERMI=",e
    d.close()

ly=len(ev[0][0])
lx=len(ev[0])
data=[]
for i in range(len(ev)):
    for j in range(ly):
        data.append([(0,ev[i][0][j][0])])
for i in range(len(ev)):
    for j in range(ly):
        kpoints_track=0.0
        for k in range(1,lx):
            if kpoints is not None:
                k0=kpoints[k-1]
                k1=kpoints[k]

                dx=k0[0]-k1[0]
                dy=k0[1]-k1[1]
                dz=k0[2]-k1[2]
                kpoints_track+=sqrt(dx*dx+dy*dy+dz*dz)
            else:
                kpoints_track+=1
            data[j+i*ly].append((kpoints_track,ev[i][k][j][0]-e))

f=open("bands.dat","w")
for set in data:
    for x,y in set:
        if x%divisions==0:
            f.write("\n")
        f.write("%d %f\n"%(x%divisions,y))
    f.write("\n")
f.close()
