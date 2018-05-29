#!/usr/bin/python2
#
# HappyDoc:docStringFormat='ClassicStructuredText'
#
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



"""
This module encapsulates the access to informations in VASP calculations.
The property is read only when it is requested. If it is not available, *None* is returned.
For more details see the p4vasp.Property module.

Following calculation properties are available:

  || **property**           || **type**                                || **comment**                                      ||
  ||URL                     || string                                  || URL pointing to the system resources             ||
  ||PATH                    || string                                  || PATH pointing to the directory of system         ||
  ||DOM                     || DOM Document                            || vasprun dom document                             ||
  ||DATE                    || time.struct_time                        || date and time of creation (from generator or file modification time)||
  ||KEYWORDS                || string                                  || keywords (currently only supported in a database ||
  ||GENERATORINFO           || p4vasp.Dictionary.Incar                 || generator info (date, time, VASP version)        ||
  ||INCAR                   || p4vasp.Dictionary.Incar                 || INCAR dictionary                                 ||
  ||DYNA                    || p4vasp.Dyna.Dyna                        || DYNA structure with k-points segments            ||
  ||PARAMETERS              || p4vasp.Dictionary.Incar                 || all VASP parameters (INCAR+defaults)             ||
  ||NAME                    || string                                  || name, typically from INCAR SYSTEM tag            ||
  ||ATOMINFO                || p4vasp.Structure.AtomInfo               ||  AtomInfo structure                              ||
  ||TOTAL_DOS               || p4vasp.Array.Array                      || total density of states                          ||
  ||PARTIAL_DOS             || p4vasp.Array.Array                      || partial density of states                        ||
  ||PARTIAL_DOS_L           || p4vasp.Array.Array (with LateLists)     || partial density of states (LateList version)     ||
  ||INITIAL_STRUCTURE       || p4vasp.Structure.Structure              || initial structure                                ||
  ||FINAL_STRUCTURE         || p4vasp.Structure.Structure              || final structure                                  ||
  ||PRIMITIVE_STRUCTURE     || p4vasp.Structure.Structure              || primitive cell structure                         ||
  ||STRUCTURE_SEQUENCE      || list of p4vasp.Structure.Structure      || structures in relaxation run                     ||
  ||STRUCTURE_SEQUENCE_L    || LateList of p4vasp.Structure.Structure  || structures in relaxation run (LateList version)  ||
  ||CSTRUCTURE_SEQUENCE_L   || LateList of p4vasp.cStructure.Structure || c-structures in relaxation run (LateList version)||
  ||RELAXATION_SEQUENCE_L   || LateList of p4vasp.Structure.Structure  || structures in relaxation run (LateList version)  ||
  ||MD_SEQUENCE_L           || LateList of p4vasp.Structure.Structure  || structures in MD run (LateList version)          ||
  ||PRIMITIVE_INDEX         || list of int                             || List of indices of primitive cell atoms          ||
  ||E_FERMI                 || float                                   || Fermi energy                                     ||
  ||FREE_ENERGY_SEQUENCE    || list of float                           || sequence of free energies                        ||
  ||FREE_ENERGY             || float                                   || free energy (last of the FREE_ENERGY_SEQUENCE)   ||
  ||FORCES_SEQUENCE         || list of lists                           || sequence of forces                               ||
  ||FORCES_SEQUENCE_L       || LateList of lists                       || sequence of forces (LateList version)            ||
  ||FORCE_CONSTANTS         || p4vasp.Array.Array                      || force constants                                  ||
  ||VELOCITY_SEQUENCE       || list of lists                           || sequence of velocities                           ||
  ||VELOCITY_SEQUENCE_L     || LateList of lists                       || sequence of velocities (LateList version)        ||
  ||EIGENVALUES             || p4vasp.Array.Array                      || eigenvalues                                      ||
  ||EIGENVALUES_L           || p4vasp.Array.Array (with LateLists)     || eigenvalues (LateList version)                   ||
  ||PROJECTED_EIGENVALUES   || p4vasp.Array.Array                      || projected eigenvalues                            ||
  ||PROJECTED_EIGENVALUES_L || p4vasp.Array.Array (with LateLists)     || projected eigenvalues (LateList version)         ||
  ||PROJECTED_EIGENVALUES_ENERGIES   || p4vasp.Array.Array                       || projected eigenvalues                            ||
  ||PROJECTED_EIGENVALUES_ENERGIES_L || p4vasp.Array.Array (with LateLists)     || projected eigenvalues        (LateList version)         ||
  ||KPOINT_LIST             || KpointList(VArray)                      || list of kpoints                                  ||
  ||KPOINT_WEIGHTS          || p4vasp.Array.VArray                     || list of kpoint weights                           ||
  ||KPOINT_DIVISIONS        || int                                     || number of divisions for listgenerated kpoints    ||
  ||KPOINT_GENERATION       || KpointGeneration                        || Dictionary with k-point generation info          ||
  ||KPOINTS_TEXT            || string                                  || text of the KPOINTS file                         ||
  ||CHGCAR                  || cp4vasp.Chgcar                          || CHGCAR                                           ||
  ||ELFCAR                  || cp4vasp.Chgcar                          || ELFCAR                                           ||
  ||LOCPOT                  || cp4vasp.Chgcar                          || LOCPOT                                           ||
  ||PARCHG                  || cp4vasp.Chgcar                          || PARCHG                                           ||
  ||INCAR_FILE              || string                                  || INCAR content                                    ||
  ||KPOINTS_FILE            || string                                  || KPOINTS content                                  ||
  ||POTCAR_FILE             || string                                  || POTCAR content                                   ||
  ||POSCAR_FILE             || string                                  || POSCAR content                                   ||
  ||CONTCAR_FILE            || string                                  || CONTCAR content                                  ||
  ||DOSCAR_FILE             || string                                    || DOSCAR content                                   ||
  ||DIELECTRIC              || tuple of two p4vasp.p4vasp.Array          || real and imaginary part of the dielectric func.  ||
  ||DIELECTRIC_FUNCTIONS    || list of tuples of two p4vasp.p4vasp.Array || list of dielectric functions.  ||
  ||DIELECTRIC_FUNCTIONS_COMMENTS || list of tuples of two p4vasp.p4vasp.Array || real and imaginary part of the dielectric func.  ||
  ||PROGRAM                 || string                                    || vasp                                             ||
  ||VERSION                 || string                                    || vasp version                                     ||
  ||SUBVERSION              || string                                    || subversion                                       ||
  ||PLATFORM                || string                                    || platform                                         ||
  ||DESCRIPTION             || string                                    || description string                               ||

  Note: Elements of the LateList are parsed only when acesses, thus parsing of LateList
  properties is fast, but it takes time to process them.
  Use LateList version, if you do not need all the elements of the list.

  example:

    #!/usr/bin/python2
    from p4vasp.SystemPM import *
    s=XMLSystemPM('vasprun.xml')
    poscar=s.INITIAL_STRUCTURE
    print 'POSCAR:'
    print
    print poscar.toString()
    print
    contcar=s.FINAL_STRUCTURE
    contcar.setDirect()
    print 'CONTCAR:'
    print
    print contcar.toString()

"""

from __future__ import generators

from p4vasp import *
from p4vasp.util import *
import p4vasp.Dictionary
from p4vasp.store import *
from p4vasp.Array import *
from p4vasp.Property import *
import os.path
from string import *
from p4vasp.util import *
import traceback
import os
import cp4vasp
from p4vasp.Structure import *
import p4vasp.cStructure
import p4vasp.repository as repository


#def systemlist():
#  return _systemlist

def getCurrentSystemPM():
    if len(systemlist()):
        return systemlist()[0]
    else:
        return None

#def readPhonons(f="OUTCAR",closeflag=0):
#  if type(f)==type(""):
#    f=open(f)
#    closeflag=1

def readDOSCAR(f="DOSCAR",closeflag=0):
    if type(f)==type(""):
        f=open(f)
        closeflag=1

    tdos=Array()
    tdos.dimension=['gridpoints','spin']
    tdos.setupFields(['energy','total','integrated'],
                     [FLOAT_TYPE,FLOAT_TYPE,FLOAT_TYPE],
                     ['%+14.10f','%+14.10f','%+14.10f'])
    d=[]
    tdos.append(d)

    s=f.readline()
    s=f.readline()
    s=f.readline()
    s=f.readline()
    s=f.readline()
    s=f.readline()
    v=split(s)
    Ef=float(v[3])
    s=f.readline()
    while s!="":
        v=split(s)
        if len(v)!=3:
            break
        d.append((float(v[0]),float(v[1]),float(v[2])))
        s=f.readline()

    if closeflag:
        f.close()

    return tdos

class Kpoints:
    def __init__(self,elem):
        self.generation=None
        self.kpointlist=None
        self.weights=None
        self.generation_type=None
        self.readFromNode(elem)

    def readFromNode(self,elem):
        for x in elem.childNodes:
            if x.nodeName=="generation":
                self.generation=p4vasp.Dictionary.Dictionary(x)
                self.generation_type=x.getAttribute("param")
            if x.nodeName=="varray":
                n=x.getAttribute("name")
                if n=="kpointlist":
                    self.kpointlist=VArray(x)
                elif n=="weights":
                    self.weights=VArray(x)

class KpointList(VArray):
    def __init__(self,data=[],t=FLOAT_TYPE,name=None):
        VArray.__init__(self,data,t=t,name=name)
    def getText(self,w=None):
        s="k-point mesh\n%d\nReciprocal lattice\n"%len(self)
        if w is None:
            w=[[1]]*len(self)
        for i in range(len(self)):
            v=map(float,self[i])
            s+="%+18.14f %+18.14f %+18.14f %f\n"%(v[0],v[1],v[2],float(w[i][0]))
        return s

class KpointGeneration(p4vasp.Dictionary.Dictionary):
    def __init__(self,elem=None):
        self.gtype=None
        p4vasp.Dictionary.Dictionary.__init__(self,elem)
        self.comment=""

    def readFromNode(self,elem):
        p4vasp.Dictionary.Dictionary.readFromNode(self,elem)
        self.gtype=elem.getAttribute("param")

    def getText(self):
        t=self.gtype.capitalize()
        if t[0]=="A":
            return "Automatic mesh\n0\n%s\n%s\n"%(t,str(self["subdivisionlength"]))
        elif  t[0] in ["G","M"]:
            try:
                d=map(int,self["divisions"])
            except:
                d=(1,1,1)
            try:
                s=map(float,self["usershift"])
            except:
                s=(0.0,0.0,0.0)
            return  "Automatic mesh\n0\n%s\n%d %d %d\n%f %f %f\n"%(
            t,d[0],d[1],d[2],s[0],s[1],s[2])
        elif  t[0]=="L":
            msg().error("KpointGeneration.getText() not supported for Line-mode KPOINTS")
            return None
        else:
            msg().error("KpointGeneration.getText() not supported for %s mode"%str(self.type))
            return None
class ChgcarStatisticsLateList(LateList):
    def __init__(self,chgcar,coord=0):
        if coord==0:
            plist=range(chgcar.nx)
        elif coord==1:
            plist=range(chgcar.ny)
        elif coord==2:
            plist=range(chgcar.nz)
        else:
            raise "Invalid coord in ChgcarStatisticsLateList"
        LateList.__init__(self,plist)
        self.chgcar=chgcar
        self.coord=coord

    def parse(self,x):
        c=self.chgcar
        if self.coord==0:
            c.calculatePlaneStatisticsX(x)
        elif self.coord==1:
            c.calculatePlaneStatisticsY(x)
        elif self.coord==2:
            c.calculatePlaneStatisticsZ(x)
        else:
            return None

        return (c.plane_minimum,c.plane_maximum,c.plane_average,c.plane_variance)

class SystemPM(PropertyManager):
    def __init__(self,url=None):
        PropertyManager.__init__(self)
        self.add("URL",url)
        for name in ["CHG","CHGCAR","LOCPOT","ELFCAR","PARCHG"]:
            self.add(name,read      = lambda x,s=self,f=name:s.getChargeFile(x,f),
                          generator = lambda x,s=self,f=name:s.getChargeFileGenerator(x,f))
        for name in ["POSCAR","POTCAR","INCAR","KPOINTS","CONTCAR","DESCRIPTION"]:
            self.add(name+"_FILE",read      = lambda x,s=self,f=name:s.getSetupFile(x,f))
        for name in ["DESCRIPTION"]:
            self.add(name,read      = lambda x,s=self,f=name:s.getSetupFile(x,f))

        self.add("CHG_X",   read=lambda x:ChgcarStatisticsLateList(x.manager["CHG"].get(),0))
        self.add("CHG_Y",   read=lambda x:ChgcarStatisticsLateList(x.manager["CHG"].get(),1))
        self.add("CHG_Z",   read=lambda x:ChgcarStatisticsLateList(x.manager["CHG"].get(),2))
        self.add("CHGCAR_X",read=lambda x:ChgcarStatisticsLateList(x.manager["CHGCAR"].get(),0))
        self.add("CHGCAR_Y",read=lambda x:ChgcarStatisticsLateList(x.manager["CHGCAR"].get(),1))
        self.add("CHGCAR_Z",read=lambda x:ChgcarStatisticsLateList(x.manager["CHGCAR"].get(),2))
        self.add("LOCPOT_X",read=lambda x:ChgcarStatisticsLateList(x.manager["LOCPOT"].get(),0))
        self.add("LOCPOT_Y",read=lambda x:ChgcarStatisticsLateList(x.manager["LOCPOT"].get(),1))
        self.add("LOCPOT_Z",read=lambda x:ChgcarStatisticsLateList(x.manager["LOCPOT"].get(),2))
        self.add("ELFCAR_X",read=lambda x:ChgcarStatisticsLateList(x.manager["ELFCAR"].get(),0))
        self.add("ELFCAR_Y",read=lambda x:ChgcarStatisticsLateList(x.manager["ELFCAR"].get(),1))
        self.add("ELFCAR_Z",read=lambda x:ChgcarStatisticsLateList(x.manager["ELFCAR"].get(),2))
        self.add("PARCHG_X",read=lambda x:ChgcarStatisticsLateList(x.manager["PARCHG"].get(),0))
        self.add("PARCHG_Y",read=lambda x:ChgcarStatisticsLateList(x.manager["PARCHG"].get(),1))
        self.add("PARCHG_Z",read=lambda x:ChgcarStatisticsLateList(x.manager["PARCHG"].get(),2))
        self.add("KEYWORDS",read=lambda x:"")
        self.add("DYNA",          read=self.getDyna)
        self.add("DATE",          read=self.getDate)
        self.add("PROGRAM",       read=self.getProgram)
        self.add("VERSION",       read=self.getVersion)
        self.add("SUBVERSION",    read=self.getSubversion)
        self.add("PLATFORM",      read=self.getPlatform)


    def getDate(self,x):
        return None
    def getProgram(self,x):
        return "VASP"
    def getVersion(self,x):
        return None
    def getSubversion(self,x):
        return None
    def getPlatform(self,x):
        return None

    def getDyna(self,x):
        import p4vasp.Dyna
        p=os.path.join(x.manager.PATH,"DYNA")
        msg().message("get DYNA file %s"%p)
        if os.path.isfile(p):
            return p4vasp.Dyna.Dyna(p)
        else:
            return None
    def getChargeFile(self,x,f):
        p=os.path.join(x.manager.PATH,f)
        msg().message("get Charge file %s"%p)
        if os.path.isfile(p):
            c=cp4vasp.Chgcar()
            c.read(str(p))
            return c
        return None

    def getSetupFile(self,x,f):
        p=os.path.join(x.manager.PATH,f)
        if os.path.isfile(p):
            f=open(p,"r")
            s=f.read()
            f.close()
            return s
        return None

    def getChargeFileGenerator(self,x,f):
        yield 1
        p=os.path.join(x.manager.PATH,f)
        msg().message("read %s from %s"%(f,p))
        if os.path.isfile(p):
            c=cp4vasp.Chgcar()
            g=c.createReadProcess(str(p))
            yield 1
            while g.next():
                s=g.error()
                if s is not None:
                    msg().error(s)
                    x.value=None
                    #x.status=x.ERROR
                    #return
                s=g.status()
                if s is not None:
                    msg().status(s)
                msg().step(g.step(),g.total())
                yield 1
            s=g.error()
            if s is not None:
                msg().error(s)
            s=g.status()
            if s is not None:
                msg().status(s)
            msg().step(g.step(),g.total())
            x.value=c
            x.status=x.READY
            msg().step(0,1)
            return
        msg().error("Can not read %s"%p)
        msg().step(0,1)
        x.value=None
        x.status=x.ERROR

    def getForces(self,i):
        return None


class StructureSequenceLateList(LateList):
    def __init__(self,plist,atominfo):
        LateList.__init__(self,plist)
        self.atominfo=atominfo

    def parse(self,x):
        f=x.getElementsByTagName("structure")
        a=Structure()
        a.readFromNode(f[0],self.atominfo)
        return a

class cStructureSequenceLateList(LateList):
    def __init__(self,plist,atominfo):
        LateList.__init__(self,plist)
        self.atominfo=p4vasp.cStructure.AtomInfo(atominfo)

    def parse(self,x):
        f=x.getElementsByTagName("structure")
        a=p4vasp.cStructure.Structure(pointer=cp4vasp.createStructure(f[0].this).this)
        a.info.setAtomInfo(self.atominfo)
        return a

class ForcesSequenceLateList(LateList):
    def parse(self,x):
        f=getChildrenByTagName(x,"varray","forces")
        if len(f)==0:
            return None
        a=VArray()
        try:
            a.readFromNodeFast(f[0])
        except:
            a.readFromNode(f[0])
        return a.data

class VelocitiesSequenceLateList(LateList):
    def parse(self,x):
        f=getChildrenByTagName(x,"varray","velocities")
        if len(f)==0:
            return None
        a=VArray()
        try:
            a.readFromNodeFast(f[0])
        except:
            a.readFromNode(f[0])
        return a.data

class XMLSystemPM(SystemPM):
    def __init__(self,url="vasprun.xml"):
        SystemPM.__init__(self,url)
        self.add("PATH",                    read=    self.getPath)
        self.add("DOM",
          read=lambda x:parseXMLfromURL(x.manager.URL))
        self.add("INCAR",
          read=lambda x:Incar(x.manager.DOM.getElementsByTagName("incar")[0]))
        self.add("GENERATORINFO",
          read=lambda x:Incar(x.manager.DOM.getElementsByTagName("generator")[0]))
        self.add("PARAMETERS",
          read=lambda x:Incar(x.manager.DOM.getElementsByTagName("parameters")[0]))
        self.add("NAME",
          read=lambda x:x.manager.INCAR["SYSTEM"])
        self.add("ATOMINFO",                read     =self.getAtomInfo)
        self.add("TOTAL_DOS",               read     =self.getTotalDOS)
        self.add("PARTIAL_DOS",             read     =self.getPartialDOS)
        self.add("PARTIAL_DOS_L",           read     =self.getPartialDOS_L)
        self.add("INITIAL_STRUCTURE",       read     =self.getInitialStructure)
        self.add("FINAL_STRUCTURE",         read     =self.getFinalStructure)
        self.add("PRIMITIVE_STRUCTURE",     read     =self.getPrimitiveStructure)
        self.add("PRIMITIVE_INDEX",         read     =self.getPrimitiveIndex)
        self.add("E_FERMI",                 read     =self.getEFermi)
        self.add("EIGENVALUES",             read     =self.getEigenvalues)
        self.add("EIGENVALUES_L",           read     =self.getEigenvalues_L)
        self.add("PROJECTED_EIGENVALUES",   read     =self.getProjectedEigenvalues)
        self.add("PROJECTED_EIGENVALUES_L", read     =self.getProjectedEigenvalues_L)
        self.add("PROJECTED_EIGENVALUES_ENERGIES",   read =self.getProjectedEigenvaluesEnergies)
        self.add("PROJECTED_EIGENVALUES_ENERGIES_L", read =self.getProjectedEigenvaluesEnergies_L)
        self.add("KPOINT_LIST",             read     =self.getKpointList)
        self.add("KPOINT_WEIGHTS",          read     =self.getKpointWeights)
        self.add("KPOINT_DIVISIONS",        read     =self.getKpointDivisions)
        self.add("KPOINT_GENERATION",       read     =self.getKpointGeneration)
        self.add("KPOINTS_TEXT",            read     =self.getKpointsText)
        self.add("KPOINTS",
          read=lambda x:Kpoints(x.manager.DOM.getElementsByTagName("kpoints")[0]))
        self.add("FREE_ENERGY_SEQUENCE",          read     =self.getFreeEnergySequence,
                                                  generator=self.getFreeEnergySequenceGen)
        self.add("FREE_ENERGY",                   read     =lambda x,s=self:s.getFreeEnergySequence(x)[-1])
        self.add("FORCES_SEQUENCE",               read     =self.getForcesSequence,
                                                  generator=self.getForcesSequenceGen)
        self.add("FORCES_SEQUENCE_L",             read     =self.getForcesSequence_L)
        self.add("FORCE_CONSTANTS",               read     =self.getForceConstants)
        self.add("VELOCITIES_SEQUENCE",           read     =self.getVelocitiesSequence,
                                                  generator=self.getVelocitiesSequenceGen)
        self.add("VELOCITIES_SEQUENCE_L",         read     =self.getVelocitiesSequence_L)
        self.add("STRUCTURE_SEQUENCE",            read     =self.getStructureSequence,
                                                  generator=self.getStructureSequenceGen)
        self.add("STRUCTURE_SEQUENCE_L",          read     =self.getStructureSequence_L)
        self.add("CSTRUCTURE_SEQUENCE_L",         read     =self.getCStructureSequence_L)
        self.add("RELAXATION_SEQUENCE_L",         read     =self.getRelaxationSequence_L)
        self.add("MD_SEQUENCE_L",                 read     =self.getMDSequence_L)
        self.add("DIELECTRIC",                    read     =self.getDielectric)
        self.add("DIELECTRIC_FUNCTIONS",          read     =self.getDielectricFunctions)
        self.add("DIELECTRIC_FUNCTIONS_COMMENTS", read     =self.getDielectricFunctionsComments)
        self.add("DATE",                          read     =self.getDate)
        self.add("PROGRAM",                       read     =self.getProgram)
        self.add("VERSION",                       read     =self.getVersion)
        self.add("SUBVERSION",                    read     =self.getSubversion)
        self.add("PLATFORM",                      read     =self.getPlatform)


    def getPath(self,x):
        p=getDirFromURL(x.manager.URL)
        if not len(p):
            p="."
        return os.path.abspath(p)
    def getDate(self,x):
        import time
        g=x.manager.GENERATORINFO
        s=strip(g["date"])+" "+strip(g["time"])
        return time.strptime(s,"%Y %m %d %H:%M:%S")

    def getProgram(self,x):
        return x.manager.GENERATORINFO["program"]

    def getVersion(self,x):
        return x.manager.GENERATORINFO["version"]

    def getSubversion(self,x):
        return x.manager.GENERATORINFO["subversion"]

    def getPlatform(self,x):
        return x.manager.GENERATORINFO["platform"]

    def getAtomInfo(self,x):
        dom=x.manager.DOM
        return AtomInfo(dom.getElementsByTagName("atominfo")[0])

    def getDielectric(self,x):
        dom=x.manager.DOM
        d=dom.getElementsByTagName("dielectricfunction")[0]
        imag=d.getElementsByTagName("imag")[0].getElementsByTagName("array")[0]
        real=d.getElementsByTagName("real")[0].getElementsByTagName("array")[0]
        ai=Array(imag,fastflag=1)
        ar=Array(real,fastflag=1)
        return (ai,ar)

    def getDielectricFunctions(self,x):
        dom=x.manager.DOM
        dielectric_functions=[]
        for d in dom.getElementsByTagName("dielectricfunction"):
            imag=d.getElementsByTagName("imag")[0].getElementsByTagName("array")[0]
            real=d.getElementsByTagName("real")[0].getElementsByTagName("array")[0]
            ai=Array(imag,fastflag=1)
            ar=Array(real,fastflag=1)
            dielectric_functions.append((ai,ar))
        return dielectric_functions

    def getDielectricFunctionsComments(self,x):
        dom=x.manager.DOM
        dielectric_functions_comments=[]
        for d in dom.getElementsByTagName("dielectricfunction"):
            if d.hasAttribute("comment"):
                dielectric_functions_comments.append(d.getAttribute("comment"))
            else:
                dielectric_functions_comments.append(d.getAttribute(""))
        return dielectric_functions_comments

    def getFreeEnergySequence(self,x):
        msg().status("Parsing free energy sequence")
        dom=x.manager.DOM
        energy=[]
        i=1
        for calc in dom.getElementsByTagName("calculation"):
            try:
                eg =getChildrenByTagName(calc,"energy")
                fre=getChildrenByTagName(eg[-1],"i","e_fr_energy")
                energy.append(float(getTextFromElement(fre[-1])))
            except:
                msg().exception()
            i=i+1
        msg().status("OK")
        return energy

    def getFreeEnergySequenceGen(self,x):
        msg().status("Parsing free energy sequence")
        yield 1
        dom=x.manager.DOM
        energy=[]
        i=1
        yield 1
        calcs=dom.getElementsByTagName("calculation")
        for calc in calcs:
            try:
                eg =getChildrenByTagName(calc,"energy")
                fre=getChildrenByTagName(eg[-1],"i","e_fr_energy")
                energy.append(float(getTextFromElement(fre[-1])))
            except:
                msg().exception()

            i=i+1
            msg().step(i,len(calcs))
            yield 1
        msg().step(0,1)
        msg().status("OK")
        x.value=energy
        x.status=x.READY

    def getForces(self,i):
        dom=self.DOM
        calc=dom.getElementsByTagName("calculation")
        if len(calc)<i:
            return None
        try:
            f=getChildrenByTagName(calc[i],"varray","forces")
            a=VArray()
            a.readFromNode(f[0])
            return a
        except:
            return None

    def getForcesSequence(self,x):
        msg().status("Parsing forces sequence")
        dom=x.manager.DOM
        seq=[]
        i=0;
        calcs=dom.getElementsByTagName("calculation")
        for calc in calcs:
            msg().step(i,len(calcs))
            i+=1
            try:
                f=getChildrenByTagName(calc,"varray","forces")
                a=VArray()
                a.readFromNode(f[0])
                seq.append(a.data)
            except:
                msg().exception()

        msg().step(0,1)
        msg().status("OK")
        return seq

    def getForcesSequenceGen(self,x):
        msg().status("Parsing forces sequence")
        yield 1
        dom=x.manager.DOM
        seq=[]
        i=0;
        calcs=dom.getElementsByTagName("calculation")
        yield 1
        for calc in calcs:
            msg().step(i,len(calcs))
            i+=1
            try:
                f=getChildrenByTagName(calc,"varray","forces")
                a=VArray()
                a.readFromNode(f[0])
                seq.append(a.data)
            except:
                msg().exception()
            yield 1
        msg().step(0,1)
        msg().status("OK")

    def getForcesSequence_L(self,x):
        dom=x.manager.DOM
        return ForcesSequenceLateList(dom.getElementsByTagName("calculation"))

    def getVelocitiesSequence(self,x):
        msg().status("Parsing velocities sequence")
        dom=x.manager.DOM
        seq=[]
        i=0;
        calcs=dom.getElementsByTagName("calculation")
        for calc in calcs:
            msg().step(i,len(calcs))
            i+=1
            try:
                f=getChildrenByTagName(calc,"varray","velocities")
                a=VArray()
                a.readFromNode(f[0])
                seq.append(a.data)
            except:
                msg().exception()

        msg().step(0,1)
        msg().status("OK")
        return seq

    def getVelocitiesSequenceGen(self,x):
        msg().status("Parsing velocities sequence")
        yield 1
        dom=x.manager.DOM
        seq=[]
        i=0;
        calcs=dom.getElementsByTagName("calculation")
        yield 1
        for calc in calcs:
            msg().step(i,len(calcs))
            i+=1
            try:
                f=getChildrenByTagName(calc,"varray","velocities")
                a=VArray()
                a.readFromNode(f[0])
                seq.append(a.data)
            except:
                msg().exception()
            yield 1
        msg().step(0,1)
        msg().status("OK")

    def getVelocitiesSequence_L(self,x):
        dom=x.manager.DOM
        return VelocitiesSequenceLateList(dom.getElementsByTagName("calculation"))

    def getStructureSequence(self,x):
        msg().status("Parsing structure sequence")
        dom=x.manager.DOM
        atominfo=x.manager.ATOMINFO
        seq=[]
        i=1
        calcs=dom.getElementsByTagName("calculation")
        for calc in calcs:
            msg().step(i,len(calcs))
            i+=1
            try:
                f=calc.getElementsByTagName("structure")
                a=Structure()
                a.readFromNode(f[0],atominfo)
                seq.append(a)
            except:
                msg().exception()
        msg().step(0,1)
        msg().status("OK")
        return seq

    def getStructureSequenceGen(self,x):
        msg().status("Parsing structure sequence")
        yield 1
        dom=x.manager.DOM
        atominfo=x.manager.ATOMINFO
        seq=[]
        i=1
        calcs=dom.getElementsByTagName("calculation")
        yield 1
        for calc in calcs:
            msg().step(i,len(calcs))
            i+=1
            try:
                f=calc.getElementsByTagName("structure")
                a=Structure()
                a.readFromNode(f[0],atominfo)
                seq.append(a)
            except:
                msg().exception()
            yield 1
        msg().step(0,1)
        msg().status("OK")

    def getStructureSequence_L(self,x):
        dom=x.manager.DOM
        atominfo=x.manager.ATOMINFO
        d=dom.getElementsByTagName("calculation")
        if d is None:
            return None
        if len(d)==0:
            return None
        return StructureSequenceLateList(d,atominfo)

    def getCStructureSequence_L(self,x):
        dom=x.manager.DOM
        atominfo=x.manager.ATOMINFO
        d=dom.getElementsByTagName("calculation")
        if d is None:
            return None
        if len(d)==0:
            return None
        return cStructureSequenceLateList(d,atominfo)

    def getRelaxationSequence_L(self,x):
        try:
            p=x.manager.PARAMETERS["IBRION"]
        except:
            try:
                p=x.manager.INCAR["IBRION"]
            except:
                return None
        if strip(str(p)) in ["1","2","3"]:
            return x.manager.STRUCTURE_SEQUENCE_L
        return None
    def getMDSequence_L(self,x):
        try:
            p=x.manager.PARAMETERS["IBRION"]
        except:
            try:
                p=x.manager.INCAR["IBRION"]
            except:
                return None
        if strip(str(p)) == "0":
            return x.manager.STRUCTURE_SEQUENCE_L
        return None

    def getStructure(self,i):
        dom=self.DOM
        atominfo=self.ATOMINFO
        calc=dom.getElementsByTagName("calculation")[i]
        f=calc.getElementsByTagName("structure")
        a=Structure()
        a.readFromNode(f[0],atominfo)
        return a

    def getKpointList(self,x):
        dom=x.manager.DOM
        kpoints =  dom.getElementsByTagName("kpoints")[0]
        varrays =  kpoints.getElementsByTagName("varray")
        for va in varrays:
            if va.getAttribute("name")=="kpointlist":
                return KpointList(va,name="kpointlist")

    def getKpointWeights(self,x):
        dom=x.manager.DOM
        kpoints =  dom.getElementsByTagName("kpoints")[0]
        varrays =  kpoints.getElementsByTagName("varray")
        for va in varrays:
            if va.getAttribute("name")=="weights":
                return VArray(va)

    def getPrimitiveIndex(self,x):
        dom=x.manager.DOM
        dynmat =  dom.getElementsByTagName("dynmat")[0]
        varrays =  dynmat.getElementsByTagName("varray")
        for va in varrays:
            if va.getAttribute("name")=="primitive_index":
                return [int(row[0]) for row in VArray(va)]

    def getKpointDivisions(self,x):
        dom=x.manager.DOM
        kpoints =  dom.getElementsByTagName("kpoints")[0]
        g       =  kpoints.getElementsByTagName("generation")[0]
        return resolveItemElement(getChildrenByTagName(g,"i","divisions")[0])[1]

    def getKpointGeneration(self,x):
        dom=x.manager.DOM
        kpoints =  dom.getElementsByTagName("kpoints")[0]
        return KpointGeneration(kpoints.getElementsByTagName("generation")[0])

    def getKpointsText(self,x):
        g=x.manager.KPOINT_GENERATION
        if g is not None:
            s=g.getText()
            if s is not None:
                return s
        l=x.manager.KPOINT_LIST
        if l is not None:
            return l.getText(x.manager.KPOINT_WEIGHTS)
        return x.manager.KPOINTS_FILE

    def getEFermi(self,x):
        try:
            dom=x.manager.DOM
            dos    =  dom.getElementsByTagName("dos")[0]
            for x in dos.getElementsByTagName("i"):
                if x.getAttribute("name")=="efermi":
                    return float(strip(getTextFromElement(x)))
        except:
            try:
                msg().message("EFermi hack: reading EFermi from DOSCAR")
                d=open(os.path.join(x.manager.PATH,"DOSCAR"),"r")
                d.readline()
                d.readline()
                d.readline()
                d.readline()
                d.readline()
                e= float(split(d.readline())[3])
                d.close()
                msg().message("EFermi hack: EFermi=%f"%e)
                return e
            except:
                msg().error("EFermi hack failed")
                msg().exception()
                raise
        return None

    def getTotalDOS(self,x):
        msg().status("Parsing DOS, please wait")
        try:
            dom=x.manager.DOM
            dos    =  dom.getElementsByTagName("dos")[0]
            total  =  dos.getElementsByTagName("total")[0]
            array  =total.getElementsByTagName("array")[0]
            a=Array(array,fastflag=1)
            msg().status("OK")
            return a
        except:
            try:
                msg().error("Reading DOS from DOSCAR")
                return readDOSCAR(os.path.join(x.manager.PATH,"DOSCAR"))
            except:
                msg().exception()
                raise

    def getPartialDOS(self,x):
        msg().status("Parsing partial DOS")
        try:
            dom=x.manager.DOM
            dos    =     dom.getElementsByTagName("dos")[0]
            partial=     dos.getElementsByTagName("partial")[0]
            array  = partial.getElementsByTagName("array")[0]
            a=Array(array,fastflag=1)
            msg().status("OK")
            return a
        except:
            msg().error("Error - no partial DOS available")
            msg().exception()
            raise

    def getPartialDOS_L(self,x):
        msg().status("Parsing partial DOS")
        try:
            dom=x.manager.DOM
            dos    =     dom.getElementsByTagName("dos")[0]
            partial=     dos.getElementsByTagName("partial")[0]
            array  = partial.getElementsByTagName("array")[0]
            a=Array()
            a.readFromNode(array,late=1,fastflag=1)
            msg().status("OK")
            return a
        except:
            msg().error("Error - no partial DOS available")
            msg().exception()
            raise

    def getEigenvalues(self,x):
        msg().status("Parsing eigenvalues")
        try:
            dom=x.manager.DOM
#      projected   =         dom.getElementsByTagName("projected")[0]
#      eigenvalues =   projected.getElementsByTagName("eigenvalues")[0]
            eigenvalues =   dom.getElementsByTagName("eigenvalues")[0]
            array       = eigenvalues.getElementsByTagName("array")[0]
            a=Array(array,fastflag=1)
            msg().status("OK")
            return a
        except:
            msg().error("Error - no eigenvalues available")
            msg().exception()
            raise

    def getEigenvalues_L(self,x):
        msg().status("Parsing eigenvalues (L)")
        try:
            dom=x.manager.DOM
#      projected   =         dom.getElementsByTagName("projected")[0]
#      eigenvalues =   projected.getElementsByTagName("eigenvalues")[0]
            eigenvalues =   dom.getElementsByTagName("eigenvalues")[0]
            array       = eigenvalues.getElementsByTagName("array")[0]
            a=Array()
            a.readFromNode(array,late=1,fastflag=1)
            msg().status("OK")
            return a
        except:
            msg().error("Error - no eigenvalues available")
            msg().exception()
            raise

    def getProjectedEigenvaluesEnergies(self,x):
        msg().status("Parsing projected eigenvalues - energies")
        try:
            dom=x.manager.DOM
            projected   =         dom.getElementsByTagName("projected")[0]
            eigenvalues =   projected.getElementsByTagName("eigenvalues")[0]
            for x in eigenvalues.childNodes:
                if x.nodeType==x.ELEMENT_NODE:
                    if x.nodeName=="array":
                        a=Array(x,fastflag=1)
                        msg().status("OK")
                        return a
        except:
            msg().error("Error - no projected eigenvalues - energies available")
            msg().exception()
            raise
        msg().error("Error - no projected eigenvalues - energies available")
        msg().exception()

    def getProjectedEigenvaluesEnergies_L(self,x):
        msg().status("Parsing projected eigenvalues - energies")
        try:
            dom=x.manager.DOM
            projected   =         dom.getElementsByTagName("projected")[0]
            eigenvalues =   projected.getElementsByTagName("eigenvalues")[0]
            for x in eigenvalues.childNodes:
                if x.nodeType==x.ELEMENT_NODE:
                    if x.nodeName=="array":
                        a=Array()
                        a.readFromNode(x,late=1,fastflag=1)
                        msg().status("OK")
                        return a
        except:
            msg().error("Error - no projected eigenvalues - energies available")
            msg().exception()
            raise
        msg().error("Error - no projected eigenvalues - energies available")
        msg().exception()

    def getProjectedEigenvalues(self,x):
        msg().status("Parsing projected eigenvalues")
        try:
            dom=x.manager.DOM
            projected   =         dom.getElementsByTagName("projected")[0]
            for x in projected.childNodes:
                if x.nodeType==x.ELEMENT_NODE:
                    if x.nodeName=="array":
                        a=Array(x,fastflag=1)
                        msg().status("OK")
                        return a
        except:
            msg().error("Error - no projected eigenvalues available")
            msg().exception()
            raise
        msg().error("Error - no projected eigenvalues available")
        msg().exception()

    def getProjectedEigenvalues_L(self,x):
        msg().status("Parsing projected eigenvalues (L)")
        try:
            dom=x.manager.DOM
            projected   =         dom.getElementsByTagName("projected")[0]
            for x in projected.childNodes:
                if x.nodeType==x.ELEMENT_NODE:
                    if x.nodeName=="array":
                        a=Array()
                        a.readFromNode(x,late=1,fastflag=1)
                        msg().status("OK")
                        return a
        except:
            msg().error("Error - no projected eigenvalues available")
            msg().exception()
            raise
        msg().error("Error - no projected eigenvalues available")


    def fetchStructure(self,x,token,name):
        msg().status("Parsing %s"%name)
        try:
            dom=x.manager.DOM
            atominfo=x.manager.ATOMINFO
            for e in dom.getElementsByTagName("structure"):
                if e.getAttribute("name")==token:
                    s=Structure()
                    s.readFromNode(e,atominfo)
                    msg().status("OK")
                    return s
        except:
            msg().error("Error - no %s available"%name)
            msg().exception()
        msg().error("Error - no %s available, empty structure created."%name)
        return Structure() # Empty structure if no structure is found.

    def getInitialStructure(self,x):
        return self.fetchStructure(x,"initialpos","initial structure")

    def getFinalStructure(self,x):
        return self.fetchStructure(x,"finalpos","final structure")

    def getPrimitiveStructure(self,x):
        s=self.fetchStructure(x,"primitive_cell","primitive cell")
        # Temporary hack which allows to display structure even without correct atominfo
        s.info = AtomInfo(s.info)
        s.info.downscale(len(self.INITIAL_STRUCTURE)/len(s))
        return s

    def getForceConstants(self,x):
        msg().status("Parsing force constants")
        try:
            dom=x.manager.DOM
            for e in dom.getElementsByTagName("array"):
                if e.getAttribute("name") == "force_constants":
                    a=Array(e,fastflag=1)
                    msg().status("OK")
                    return a
        except:
            msg().error("Force constants not available")
            msg().exception()
        msg().error("Force constants not available")
        msg().exception()
        return None


class OldSystemPM(SystemPM):
    def __init__(self,url=None):
        if url is not None:
            if url[-1]!=os.sep:
                url=url+os.sep
        SystemPM.__init__(self,url)
        self.add("URL",url)
        self.add("PATH",read=self.getPath)
        self.add("INCAR",
          read=lambda x:Incar(os.path.join(x.manager.PATH,"INCAR")))
        self.add("NAME",
          read=self.getName)
        self.add("INITIAL_STRUCTURE",
          read=lambda x:Structure(os.path.join(x.manager.PATH,"POSCAR")))
        self.add("FINAL_STRUCTURE",
          read=lambda x:Structure(os.path.join(x.manager.PATH,"CONTCAR")))
        self.add("FINAL_STRUCTURE",
          read=lambda x:Structure(os.path.join(x.manager.PATH,"CONTCAR")))
        self.add("TOTAL_DOS", read=self.getTotalDOS)
        self.add("KPOINTS_TEXT",             read     =self.getKpointsText)
    def getKpointsText(self,x):
        return open(os.path.join(x.manager.PATH,"KPOINTS")).read()
    def getPath(self,x):
        p=getDirFromURL(x.manager.URL)
        if not len(p):
            p="."
        return os.path.abspath(p)
    def getName(self,x):
        incar=x.manager.INCAR
        if incar is not None:
            try:
                return incar["SYSTEM"]
            except:
                pass
        struct=x.manager.INITIAL_STRUCTURE
        return struct.comment

    def getTotalDOS(self,x):
        return readDOSCAR(os.path.join(x.manager.PATH,"DOSCAR"))


class PoscarSystemPM(SystemPM):
    def __init__(self,path=None):
        self.poscarpath=path
        url=self._geturl()
        SystemPM.__init__(self,url)
        self.add("URL", read=lambda x:x.manager._geturl())
        self.add("PATH",read=self.getPath)
        self.add("INCAR",
          read=lambda x:Incar(os.path.join(x.manager.PATH,"INCAR")))
        self.add("NAME",
          read=self.getName)
        self.add("INITIAL_STRUCTURE",
          read=lambda x:Structure(x.manager.poscarpath))
        self.add("FINAL_STRUCTURE",
          read=lambda x:Structure(os.path.join(x.manager.PATH,"CONTCAR")))
        self.add("TOTAL_DOS", read=self.getTotalDOS)
        self.add("KPOINTS_TEXT", read=self.getKpointsText)
    def getKpointsText(self,x):
        return open(os.path.join(x.manager.PATH,"KPOINTS")).read()
    def getPath(self,x):
        p=getDirFromURL(x.manager.URL)
        if not len(p):
            p="."
        return os.path.abspath(p)
    def _geturl(self):
        url=os.path.split(self.poscarpath)[0]
        if url is not None:
            if len(url):
                if url[-1]!=os.sep:
                    url=url+os.sep
        return url
    def getName(self,x):
        struct=x.manager.INITIAL_STRUCTURE
        return struct.comment
    def getTotalDOS(self,x):
        return readDOSCAR(os.path.join(x.manager.PATH,"DOSCAR"))



def getSystem(path):
    if os.path.isdir(path):
        return OldSystemPM(path)
    elif lower(path[-4:])==".xml":
        return XMLSystemPM(path)
    else:
        return PoscarSystemPM(path)

if __name__=="__main__":
    system=getSystem("../vasprun_bands.xml")
#  ev=system.PARTIAL_DOS
#  ev=system.PROJECTED_EIGENVALUES
    print system.KPOINTS.generation.toxml()

    ev=system.EIGENVALUES

    print
    print ev.toxml()
    print "fields:"
    for f in ev.field:
        print "  ",f
    print

    print "dimensions:"
    x=ev
    for i in range(len(ev.dimension)):
        print "  %2d %10s %3d"%(i,ev.dimension[-(i+1)],len(x))
        try:
            x=x[0]
        except:
            print "END"


class SystemPM_URL_Attribute(AttributeProfile):
    def __init__(self,name="url",attribute="URL",encode=1,tag=1,tagattr=1):
        AttributeProfile.__init__(self,name,attribute=attribute,encode=encode,tag=tag,tagattr=tagattr)
    def setEncodedValue(self,obj,val):
        self.setValue(obj,str(val))
    def setValue(self,obj,val):
        prop=obj["URL"]
        prop.value=val
        prop.status=p4vasp.Property.Property.READY

class SetupPM(SystemPM):
    def __init__(self,s=None):
        SystemPM.__init__(self)
        self.add("NAME",
          read=lambda x:x.manager.INCAR["SYSTEM"])
        self.add("INCAR",Incar())
        self.add("INITIAL_STRUCTURE",Structure())
        self.add("KPOINTS_TEXT","Dummy k-points file\nGamma\n1 1 1\n0 0 0\n")
        self.inherit(s)
    def inherit(self,s=None):
        if s is not None:
            if s.INCAR is not None:
                self.INCAR=p4vasp.Dictionary.Incar(s.INCAR)
            else:
                self.INCAR=p4vasp.Dictionary.Incar()
            self.INITIAL_STRUCTURE=p4vasp.Structure.Structure()
            if s.FINAL_STRUCTURE is not None:
                self.INITIAL_STRUCTURE.setStructure(s.FINAL_STRUCTURE)
            elif s.INITIAL_STRUCTURE is not None:
                self.INITIAL_STRUCTURE.setStructure(s.INITIAL_STRUCTURE)
            if s.KPOINTS_TEXT is not None:
                self.KPOINTS_TEXT=s.KPOINTS_TEXT
            else:
                self.KPOINTS_TEXT="Dummy k-points file\nGamma\n1 1 1\n0 0 0\n"
        else:
            self.INCAR=p4vasp.Dictionary.Incar()
            self.INITIAL_STRUCTURE=p4vasp.Structure.Structure()
            self.KPOINTS_TEXT="Dummy k-points file\nGamma\n1 1 1\n0 0 0\n"
    def write(self,path="./"):
        self.INITIAL_STRUCTURE.write(path+"POSCAR")
        self.INCAR.write(path+"INCAR")
        f=open(path+"KPOINTS","w")
        f.write(self.KPOINTS_TEXT)
        f.close()



class SystemListListener:
    def notifySystemListUpdated(self,l):
        pass
    def notifySystemActivated(self,l,s):
        pass
    def SystemListListener_callback(self,l,s):
        self.notifySystemListUpdated(l)

#class TestSystemListListener(SystemListListener):
#  def notifySystemListUpdated(self,l):
#    print "list updated",len(l)
#  def notifySystemActivated(self,l,s):
#    print "system activated",s.URL

class SystemRepository(repository.Repository):
    def __init__(self,l=[],factory=None):
        repository.Repository.__init__(self,l,factory)
        self.notify_systemlist=[]
#    self.addSystemListListener(TestSystemListListener())
    def addSystemListListener(self,x):
        self.notify_systemlist.append(x)
        self.notify_on_append.append(x.SystemListListener_callback)
        self.notify_on_remove.append(x.SystemListListener_callback)
        self.notify_on_activate.append(x.notifySystemActivated)
    def removeSystemListListener(self,x):
        for i in range(len(self.notify_systemlist)):
            if id(self.notify_systemlist[i])==id(x):
                del self.notify_on_append[i]
                del self.notify_on_remove[i]
                del self.notify_on_activate[i]
    def notifySystemChanged(self):
        if len(self):
            x=self[0]
            for f in self.notify_on_activate:
                f(self,x)

SystemRepository.store_profile=repository.RepositoryProfile(name=SystemRepository,
tagname="systemlist")
c=Profile(XMLSystemPM,tagname="vasprun",disable_attr=1)
c.addAttr(SystemPM_URL_Attribute())
SystemRepository.store_profile.addClass(c)
c=Profile(PoscarSystemPM,tagname="poscar",disable_attr=1)
c.addAttr(StringAttribute("poscarpath"))
SystemRepository.store_profile.addClass(c)
c=Profile(SetupPM,tagname="calcsetup",disable_attr=1)
c.addAttr(StringAttribute("poscarpath"))
SystemRepository.store_profile.addClass(c)

c=Profile(OldSystemPM,tagname="OldSystem",disable_attr=1)
c.addAttr(SystemPM_URL_Attribute())
SystemRepository.store_profile.addClass(c)
systemlist_=SystemRepository()

def systemlist():
    return systemlist_
