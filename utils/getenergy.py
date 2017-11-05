#!/usr/bin/python

from p4vasp.SystemPM import *
from glob import glob
import os.path
import traceback


def visit(arg,d,l):
    f1,f2=arg
    if "vasprun.xml" in l:
        s=XMLSystemPM("%s/vasprun.xml"%d)
        try:
            force =s.FORCES_SEQUENCE_L[-1]
            maxf= max(map(lambda x:x.length(),force))
            sforce="%10.6f"%maxf
        except:
            sforce="          "
            traceback.print_exc()

        try:
            energy="%+14.10f"%float(s.FREE_ENERGY)
        except:
            energy="               "
            traceback.print_exc()
        try:
            fermi="%+14.10f"%s.E_FERMI
        except:
            fermi="               "
            traceback.print_exc()

        try:
            name  ="%-20s"%s.NAME
        except:
            name  ="                    "
            traceback.print_exc()

        try:
            steps ="%3d"%len(s.STRUCTURE_SEQUENCE_L)
        except:
            steps="   "
            traceback.print_exc()
        print "%s %s %s %s %s %s"%(name,steps,energy,fermi,sforce,d)
        f1.write("%s %s %s %s %s %s\n"%(name,steps,energy,fermi,sforce,d))
        f2.write("%s,%s,%s,%s,%s,%s\n"%(name,steps,energy,fermi,sforce,d))


f1=open("energy.txt","w")
f2=open("energy.csv","w")
os.path.walk(".",visit,(f1,f2))
f1.close()
f2.close()
