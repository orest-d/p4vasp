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


"""
Isosurface tools.
"""
from p4vasp.cmatrix import *
from p4vasp.cStructure import Structure as CStructure

def handle_type1(va, vb, vc, vd,
                 nA, nB, nC, nD,
                  A,  B,  C,  D, level):
    if ((A == B) or (A == C) or (A == D)):
        return []
    f = B / (B - A)
    pos1=f*va+(1-f)*vb
    n1=f*nA+(1-f)*nB

    f = C / (C - A)
    pos2=f*va+(1-f)*vc
    n2=f*nA+(1-f)*nC

    f = D / (D - A)
    pos3=f*va+(1-f)*vd
    n3=f*nA+(1-f)*nD

    if (level>=0):
        return [(n1,n2,n3,pos1,pos2,pos3)]
    else:
        return [(-n1,-n2,-n3,pos1,pos2,pos3)]

def handle_type2(va, vb, vc, vd,
                 nA, nB, nC, nD,
                  A,  B,  C,  D, level):
    if ((A == C) or (A == D) or (B == C) or (B == D)):
        return []

    f = C / (C - A)
    posAC=f*va+(1-f)*vc
    nAC=f*nA+(1-f)*nC

    f = D / (D - A)
    posAD=f*va+(1-f)*vd
    nAD=f*nA+(1-f)*nD

    f = C / (C - B)
    posBC=f*vb+(1-f)*vc
    nBC=f*nB+(1-f)*nC

    f = D / (D - B)
    posBD=f*vb+(1-f)*vd
    nBD=f*nB+(1-f)*nD

    if (level>=0):
        sign=1
    else:
        sign=-1
    
    return [(sign*nAC,sign*nAD,sign*nBC,posAC,posAD,posBC),(sign*nAD,sign*nBD,sign*nBC,posAD,posBD,posBC)]

def handle_tetrahedron (chgcar, a1, a2, a3,
                                b1, b2, b3,
                                c1, c2, c3,
                                d1, d2, d3, level,basis):
    A = chgcar.get(a1, a2, a3) - level
    B = chgcar.get(b1, b2, b3) - level
    C = chgcar.get(c1, c2, c3) - level
    D = chgcar.get(d1, d2, d3) - level
    type = 0
    if (A > 0):
        type+=1
    if (B > 0):
        type+=1
    if (C > 0):
        type+=1
    if (D > 0):
        type+=1
    if (type == 0) or (type == 4):
        return []

    posA=(float(a1)/chgcar.nx)*basis[0]+(float(a2)/chgcar.ny)*basis[1]+(float(a3)/chgcar.nz)*basis[2]
    posB=(float(b1)/chgcar.nx)*basis[0]+(float(b2)/chgcar.ny)*basis[1]+(float(b3)/chgcar.nz)*basis[2]
    posC=(float(c1)/chgcar.nx)*basis[0]+(float(c2)/chgcar.ny)*basis[1]+(float(c3)/chgcar.nz)*basis[2]
    posD=(float(d1)/chgcar.nx)*basis[0]+(float(d2)/chgcar.ny)*basis[1]+(float(d3)/chgcar.nz)*basis[2]

    nA=Vector()
    chgcar.getGrad(nA.pointer,a1,a2,a3)
    nB=Vector()
    chgcar.getGrad(nB.pointer,b1,b2,b3)
    nC=Vector()
    chgcar.getGrad(nC.pointer,c1,c2,c3)
    nD=Vector()
    chgcar.getGrad(nD.pointer,d1,d2,d3)
    if (type == 3):
        A *= -1
        B *= -1
        C *= -1
        D *= -1
        type = 1

    if (type == 1):
        if (A > 0):
            return handle_type1 (posA, posB, posC, posD, nA, nB, nC, nD, A, B, C, D, level)
        elif (B > 0):
            return handle_type1 (posB, posC, posD, posA, nB, nC, nD, nA, B, C, D, A, level)
        elif (C > 0):
            return handle_type1 (posC, posD, posA, posB, nC, nD, nA, nB, C, D, A, B, level)
        elif (D > 0):
            return handle_type1 (posD, posA, posB, posC, nD, nA, nB, nC, D, A, B, C, level)
    else:
        if ((A > 0) and (B > 0)):
            return handle_type2 (posA, posB, posC, posD, nA, nB, nC, nD, A, B, C, D, level)
        elif ((B > 0) and (C > 0)):
            return handle_type2 (posB, posC, posD, posA, nB, nC, nD, nA, B, C, D, A, level)
        elif ((C > 0) and (D > 0)):
            return handle_type2 (posC, posD, posA, posB, nC, nD, nA, nB, C, D, A, B, level)
        elif ((D > 0) and (A > 0)):
            return handle_type2 (posD, posA, posB, posC, nD, nA, nB, nC, D, A, B, C, level)
        elif ((A > 0) and (C > 0)):
            return handle_type2 (posA, posC, posB, posD, nA, nC, nB, nD, A, C, B, D, level)
        elif ((B > 0) and (D > 0)):
            return handle_type2 (posB, posD, posA, posC, nB, nD, nA, nC, B, D, A, C, level)

def partialIsosurface(chgcar,level):
    """Returns parts of the isosurface as a lists of tuples in form (n1,n2,n3,p1,p2,p3),
where each tuple represents a triangle on on the isosurface with vertices p1,p2,p3 and normals n1,n2,n3.
Since this may be time consuming, parts of the list are yielded at a time in form of a tuple (step,total,mesh),
where step is an integer number of a current step, total is an integer total number of steps and mesh is a part of the
mesh in the above mentioned format. Complete isosurface can be obtained by concatenating all parts.
"""
    structure=CStructure(pointer=chgcar.structure)
    basis=structure.basis
    for i in range(chgcar.nx):
        mesh=[]
        for j in range(chgcar.ny):
            for k in range(chgcar.nz):
                mesh.extend(handle_tetrahedron (chgcar, i + 0, j + 0, k + 0,
                                                        i + 1, j + 0, k + 0,
                                                        i + 0, j + 1, k + 0,
                                                        i + 1, j + 0, k + 1, level,basis))
                mesh.extend(handle_tetrahedron (chgcar, i + 0, j + 0, k + 0,
                                                        i + 0, j + 0, k + 1,
                                                        i + 0, j + 1, k + 0,
                                                        i + 1, j + 0, k + 1, level,basis))
                mesh.extend(handle_tetrahedron (chgcar, i + 0, j + 0, k + 1,
                                                        i + 0, j + 1, k + 1,
                                                        i + 0, j + 1, k + 0,
                                                        i + 1, j + 0, k + 1, level,basis))
                mesh.extend(handle_tetrahedron (chgcar, i + 1, j + 0, k + 0,
                                                        i + 1, j + 1, k + 0,
                                                        i + 0, j + 1, k + 0,
                                                        i + 1, j + 0, k + 1, level,basis))
                mesh.extend(handle_tetrahedron (chgcar, i + 1, j + 1, k + 0,
                                                        i + 1, j + 1, k + 1,
                                                        i + 0, j + 1, k + 0,
                                                        i + 1, j + 0, k + 1, level,basis))
                mesh.extend(handle_tetrahedron (chgcar, i + 0, j + 1, k + 1,
                                                        i + 1, j + 1, k + 1,
                                                        i + 0, j + 1, k + 0,
                                                        i + 1, j + 0, k + 1, level,basis))
        yield i,chgcar.nx,mesh

def completeIsosurface(chgcar,level):
    """Returns the complete isosurface as a list of tuples in form (n1,n2,n3,p1,p2,p3),
where each tuple represents a triangle on on the isosurface with vertices p1,p2,p3 and normals n1,n2,n3.
"""
    mesh=[]
    for step,total,meshpart in partialIsosurface(chgcar,level):
        mesh.extend(meshpart)
    return mesh

def convertMeshFormat(mesh,offset=Vector(0,0,0)):
    """Convert the mesh format delivered by completeIsosurface into a format accepted by paint3d (coordinates, normals, triangles)."""
    coordinates=[]
    normals=[]
    triangles=[]
    for n1,n2,n3,p1,p2,p3 in mesh:
        t=len(coordinates)
        coordinates.append(Vector(p1[0]+offset[0],p1[1]+offset[1],p1[2]+offset[2]))
        coordinates.append(Vector(p2[0]+offset[0],p2[1]+offset[1],p2[2]+offset[2]))
        coordinates.append(Vector(p3[0]+offset[0],p3[1]+offset[1],p3[2]+offset[2]))
        normals.append(n1)
        normals.append(n2)
        normals.append(n3)
        triangles.append((t,t+1,t+2))
    return coordinates,normals,triangles

