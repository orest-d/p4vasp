#!/usr/bin/python2
#  p4vasp is a GUI-program and a library for processing outputs of the
#  Vienna Ab-inition Simulation Package (VASP)
#  (see http://cms.mpi.univie.ac.at/vasp/Welcome.html)
#
#  Copyright (C) 2003  Orest Dubay <dubay@danubiananotech.com>
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

import sys
from p4vasp.SystemPM import *

path="vasprun.xml"
out="ipr.dat"
if len(sys.argv)>1:
    path=sys.argv[1]
    if len(sys.argv)>2:
        out=sys.argv[2]

s=XMLSystemPM(path)
occ=s.PROJECTED_EIGENVALUES_L
energies=s.PROJECTED_EIGENVALUES_ENERGIES_L
fermi=s.E_FERMI

nions=len(occ[0][0][0])
f=open(out,"w")
for spin in range(len(occ)):
    for k in range(len(occ[spin])):
        for band in range(len(occ[spin][k])):
            sum1=0.0
            sum2=0.0
            for ion in range(len(occ[spin][k][band])):
                x=sum(occ[spin][k][band][ion])
                sum1+=x
                sum2+=x*x
            res=sum1*sum1/sum2/nions
            f.write("%f %f\n"%(energies[spin][k][band][0]-fermi,1/res))
f.close()
