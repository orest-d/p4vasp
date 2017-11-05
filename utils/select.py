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

######################################################################
# DESCRIPTION:                                                       #
######################################################################
# This is a selection script example.                                #
# The purpose of this script is to select (in the sense of the       #
# "Selective dynamics") certain atom group.                          #
#                                                                    #
# It is very simple and it is easier to modify this source           #
# to do what you want, than to write a sophisticated user interface. #
# (see the comments)                                                 #
######################################################################

from p4vasp.Structure import *
from p4vasp.sellang import *
from p4vasp.SystemPM import *

# Read the structure.

p=Structure("POSCAR")

# Alternative:
#p=XMLSystemPM("vasprun.xml").FINAL_STRUCTURE

l=decode("#4",p)                # Select the 4th specie
p.setSelective()                # Selective mode.
for i in range(len(p)):
    if i in l:
        p.selective[i]=(1,1,1)
    else:
        p.selective[i]=(0,0,0)

p.write("POSCAR.selected")      # Write the output.
