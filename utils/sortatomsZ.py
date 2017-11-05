#!/usr/bin/python

from p4vasp.Structure import *
from sys import argv

p=Structure(argv[1])
#p.setSelective(0)

for i in range(p.types):
    f=p.info.firstAtomIndexForSpecie(i)
    l=[]
    if p.isSelective():
        for j in range(p.atomspertype[i]):
            l.append((p[j][2],p[j],p.selective[j]))
        l.sort()
        for j in range(p.atomspertype[i]):
            p[j]=l[j][1]
            p.selective[j]=l[j][2]
    else:
        for j in range(p.atomspertype[i]):
            l.append((p[j][2],p[j]))
        l.sort()
        for j in range(p.atomspertype[i]):
            p[j]=l[j][1]
p.write(argv[1]+".sorted")
