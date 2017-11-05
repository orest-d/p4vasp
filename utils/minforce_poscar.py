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
s=XMLSystemPM('vasprun.xml')
forces=s.FORCES_SEQUENCE
avgf=[]
maxf=[]
if forces is not None:
    for i in range(len(forces)):
        f=filter(lambda x:len(x)==3,forces[i])
        f=map(lambda x:sqrt(x[0]*x[0]+x[1]*x[1]+x[2]*x[2]),f)
        maxf.append((max(f),i))
        avgf.append((float(reduce(lambda x,y:x+y,f))/len(f),i))

minavgforce, minavgindex= min(avgf)
minmaxforce, minmaxindex= min(maxf)
print "Minimal average: step %3d average force %+14.10f, maximal force %+14.10f"%(minavgindex,minavgforce,maxf[minavgindex][0])
print "Minimal maximum: step %3d average force %+14.10f, maximal force %+14.10f"%(minmaxindex,avgf[minmaxindex][0],minmaxforce)

pseq=s.STRUCTURE_SEQUENCE_L
pa=pseq[minavgindex]
pa.comment="%s (avg. f. %f, max. f. %f, step %d)"%(s.NAME,minavgforce,maxf[minavgindex][0],minavgindex)
pa.setCarthesian()
pa.write("POSCAR.minavg")
pm=pseq[minmaxindex]
pm.comment="%s (avg. f. %f, max. f. %f, step %d)"%(s.NAME,avgf[minmaxindex][0],minmaxforce,minmaxindex)
pm.setCarthesian()
pm.write("POSCAR.minmax")
