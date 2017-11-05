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
# paints a sphere mesh in povray -                                   #
# This is not realy useful - it is an example                        #
######################################################################

from p4vasp.paint3d.MeshTools import *
from p4vasp.paint3d.PovrayPaint3D import *
from p4vasp.matrix import Vector

paint = ExtendedPovrayPaint3D()
material=paint.colorMaterial(Vector(1,0,0),"MeshMaterial")
paint.background(Vector(0,0,0))
paint.pointLight(position=Vector(10,10,10),color=Vector(1,1,1))
paint.orthographicCamera(look_at=Vector(0,0,0),position=(10,0,-10),right=Vector(0,8,0),up=Vector(0,0,6))
#paint.sphere(position=Vector(0,0,0),radius=1.0,material="MeshMaterial")
coordinates,normals,triangles=sphereMesh(6)
paint.mesh(coordinates,normals,triangles,material="MeshMaterial")
paint.width=800
paint.height=600
paint.exportTo("povraysphere.pov")

