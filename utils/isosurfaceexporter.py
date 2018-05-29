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

######################################################################
# DESCRIPTION:                                                       #
######################################################################
# export chgcar isosurface to povray                                 #
######################################################################
from p4vasp.paint3d.PovrayPaint3D import *
from p4vasp.matrix import Vector
from p4vasp.isosurface import *
from cp4vasp import *

paint = ExtendedPovrayPaint3D()
material=paint.colorMaterial(Vector(0.5,0.5,1.0),"MeshMaterial")

paint.background(Vector(0,0,0))
paint.pointLight(position=Vector(10,10,10),color=Vector(1,1,1))
paint.orthographicCamera(look_at=Vector(0,0,0),position=(100,0,0),right=Vector(0,80,0),up=Vector(0,0,60))

chgcar=Chgcar()
chgcar.read("CHGCAR")
mesh=completeIsosurface(chgcar,chgcar.getAverage())
coordinates,normals,triangles=convertMeshFormat(mesh)
paint.mesh(coordinates,normals,triangles,material="MeshMaterial")

paint.width=800
paint.height=600
paint.exportTo("CHGCAR.pov")


