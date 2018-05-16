#!/usr/bin/python2

import sys
from math import *
from p4vasp.matrix import *
from p4vasp.Structure import *


def makeZigzag(nn,aCC=1.419398,r=None,x_shift=0.0,y_shift=0.0,z_shift=0.0):
    s=Structure()
    s.setCartesian()
    s.comment="zigzag (%d,0), aCC=%f"%(nn,aCC)

    shift = 0.0
    fi   = 2*pi/nn
    if r is None:
        r = aCC*sqrt(3.0)/4/sin(fi/4)

    for i in range(0,nn):
        ffi=fi*i
        s.appendAtom(0,Vector(x_shift+r*cos(ffi),y_shift+r*sin(ffi),z_shift+shift))

    shift = shift + aCC/2
    for i in range(0,nn):
        ffi=fi*(i+0.5)
        s.appendAtom(0,Vector(x_shift+r*cos(ffi),y_shift+r*sin(ffi),z_shift+shift))

    shift = shift + aCC
    for i in range(0,nn):
        ffi=fi*(i+0.5)
        s.appendAtom(0,Vector(x_shift+r*cos(ffi),y_shift+r*sin(ffi),z_shift+shift))

    shift = shift + aCC/2
    for i in range(0,nn):
        ffi=fi*(i)
        s.appendAtom(0,Vector(x_shift+r*cos(ffi),y_shift+r*sin(ffi),z_shift+shift))

    s.basis[0][0] = 2*r+7
    s.basis[1][1] = 2*r+7
    s.basis[2][2] = shift
    s.R           = r
    return s

def makeArmchair(nn,aCC=1.419398,r=None,x_shift=0.0,y_shift=0.0,z_shift=0.0):
    s=Structure()
    s.setCartesian()

    s.comment="armchair (%d,%d), aCC=%f"%(nn,nn,aCC)

    shift = 0.0

    fi   = 2*pi/nn
    al   = 2*atan(2*sin(fi/4)/(1+2*cos(fi/4)))
    be   = fi/2-al

    if r is None:
        r    = aCC/2/sin(al/2)

    for i in range(0,nn):
        ffi=fi*i
        s.appendAtom(0,Vector(x_shift+r*cos(ffi),y_shift+r*sin(ffi),z_shift+shift))

    for i in range(0,nn):
        ffi=al+fi*i
        s.appendAtom(0,Vector(x_shift+r*cos(ffi),y_shift+r*sin(ffi),z_shift+shift))

    shift = shift + aCC*sqrt(3.0)/2

    for i in range(0,nn):
        ffi=al+be+fi*(i)
        s.appendAtom(0,Vector(x_shift+r*cos(ffi),y_shift+r*sin(ffi),z_shift+shift))

    for i in range(0,nn):
        ffi=2*al+be+fi*(i)
        s.appendAtom(0,Vector(x_shift+r*cos(ffi),y_shift+r*sin(ffi),z_shift+shift))

    shift = shift + aCC*sqrt(3.0)/2

    s.basis[0][0] = 2*r+7
    s.basis[1][1] = 2*r+7
    s.basis[2][2] = shift
    s.R           = r
    return s

if __name__=="__main__":
    if len(argv)<3:
        print "%s n m"
        print "Creates an (n,m) nanotube - only zigzag and armchair tubes are supported."
    else:
        n,m=int(argv[1]),int(argv[2])
        if m:
            makeArmchair(n).write("POSCAR.%d-%d"%(n,n))
        else:
            makeZigzag(n).write("POSCAR.%d-%d"%(n,0))
