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
from string import *
from p4vasp.SystemPM import *
s=XMLSystemPM('vasprun.xml')
p=s.FINAL_STRUCTURE
f=open("finaldist.csv","w")
f.write(",,"+join(map(str,range(1,len(p)+1)),",")+"\n,")
for i in range(len(p)):
    f.write(',"%s"'%strip(p.info[p.speciesIndex(i)].element))
f.write("\n")

for i in range(len(p)):
    f.write('%d,"%s"'%((i+1),strip(p.info[p.speciesIndex(i)].element)))
    for j in range(len(p)):
        f.write(",%f"%p.mindist(i,j))
    f.write("\n")
f.close()
