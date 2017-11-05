from p4vasp.matrix import *
from math import *

def cylinderMesh(n):
    coordinates=[]
    normals=[]
    triangles=[]
    for i in range(n):
        alpha=i*2*pi/n
        coordinates.append(Vector(sin(alpha),cos(alpha),0))
        coordinates.append(Vector(sin(alpha),cos(alpha),1))
        normals.append(Vector(sin(alpha),cos(alpha),0))
        normals.append(Vector(sin(alpha),cos(alpha),0))
        j=(i+1)%n
        triangles.append((2*i,2*i+1,2*j))
        triangles.append((2*i+1,2*j+1,2*j))
    return coordinates,normals,triangles

def sphereMesh(n):
    coordinates=[]
    normals=[]
    triangles=[]

    for i in range(n):
        alpha=i*pi/n
        ii=(i+1)%n
        for j in range(n):
            jj=(j+1)%n
            beta=j*2*pi/n
            v=Vector(sin(alpha)*sin(beta),sin(alpha)*cos(beta),cos(alpha))
            coordinates.append(v)
            normals.append(v)
            i1=i*n+j
            i2=i*n+jj
            i3=ii*n+jj
            i4=ii*n+j
            triangles.append((i1,i2,i3))
            triangles.append((i1,i3,i4))
    return coordinates,normals,triangles

def coneMesh(n):
    coordinates=[]
    normals=[]
    triangles=[]

    for i in range(n):
        alpha=i*2*pi/n
        coordinates.append(Vector(sin(alpha),cos(alpha),0))
        coordinates.append(Vector(0,0,1))
        normal=Vector(sin(alpha),cos(alpha),1).normal()
        normals.append(normal)
        normals.append(normal)
        j=(i+1)%n
        triangles.append((2*i,2*i+1,2*j))
    return coordinates,normals,triangles
