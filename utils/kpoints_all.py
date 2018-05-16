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


from p4vasp.SystemPM import *

s=XMLSystemPM("vasprun.xml")

l=s.KPOINT_LIST
w=s.KPOINT_WEIGHTS

f=open("KPOINTS_ALL","w")
f.write("%s\n%d\nreciprocal\n"%(s.NAME,len(l)))
for i in range(len(l)):
    v=l[i]
#  print i,l[i],w[i]
    f.write("%+14.10f %+14.10f %+14.10f  %+14.10f\n"%(v[0],v[1],v[2],w[i][0]))

f.close()
