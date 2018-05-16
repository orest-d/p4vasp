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

import sys
from p4vasp.SystemPM import *

if len(sys.argv)>1:
    path=sys.argv[1]
else:
    path="vasprun.xml"

s=XMLSystemPM(path)
poscar=s.INITIAL_STRUCTURE
poscar.comment=s.NAME
poscar.write("POSCAR")

f=open("KPOINTS","w+")
f.write(s.KPOINTS_TEXT)
f.close()

s.INCAR.write()
