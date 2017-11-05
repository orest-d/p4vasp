#!/usr/bin/python
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
SQLSystemPM - access to the data stored in a SQL database
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
from p4vasp.SystemPM import *


class SQLStructuresLL(LateList):
    def __init__(self,plist,dbi):
        LateList.__init__(self,plist)
        self.dbi=dbi
    def parse(self,x):
        return self.dbi.readStructure(x)

class SQLcStructuresLL(SQLStructuresLL):
    def parse(self,x):
        return self.dbi.readStructure(x,cstructure=True)

class SQLForcesSequenceLateList(LateList):
    def __init__(self,plist,dbi):
        LateList.__init__(self,plist)
        self.dbi=dbi
    def parse(self,x):
        return VArray(data=self.dbi.readForce(x),name="forces")

class SQLSystemPM(SystemPM):
    def __init__(self,dbi,Id):
        SystemPM.__init__(self)
        self.dbi=dbi
        self.Id=Id
        self.add("NAME",                read = self.getName)
        self.add("PATH",                read = self.getPath)
        self.add("KEYWORDS",            read = self.getKeywords)
        self.add("INITIAL_STRUCTURE",   read = self.getInitialStructure)
        self.add("FINAL_STRUCTURE",     read = self.getFinalStructure)
        self.add("STRUCTURE_SEQUENCE",  read = self.getStructureSequence)
        self.add("STRUCTURE_SEQUENCE_L",read = self.getStructureSequenceL)
        self.add("CSTRUCTURE_SEQUENCE_L",read =self.getCStructureSequenceL)
        self.add("FORCES_SEQUENCE",     read = self.getForcesSequence)
        self.add("FORCES_SEQUENCE_L",   read = self.getForcesSequenceL)
        self.add("FREE_ENERGY_SEQUENCE",read = self.getFreeEnergySequence)
        self.add("FREE_ENERGY",         read = lambda x,i=self.Id,d=self.dbi:d.fetchvalue(
                                               "SELECT free_energy FROM #CALC WHERE id=%d"%i))
        self.add("E_FERMI",             read = lambda x,i=self.Id,d=self.dbi:d.fetchvalue(
                                               "SELECT fermi_energy FROM #CALC WHERE id=%d"%i))
        self.add("PARTIAL_DOS",         read =self.getPartialDOS)
        self.add("PARTIAL_DOS_L",       read =self.getPartialDOS)
        self.add("KPOINTS_TEXT",        read =self.getKpointsText)
        self.add("INCAR",               read =self.getIncar)
        self.add("TOTAL_DOS",           read =self.getDOS)
        self.add("PARAMETERS",          read =lambda x,s=self:s.getIncar(x,False))
        self.add("DATE",                read =self.getDate)
        self.add("PROGRAM",             read=self.getProgram)
        self.add("VERSION",             read=self.getVersion)
        self.add("SUBVERSION",          read=self.getSubversion)
        self.add("PLATFORM",            read=self.getPlatform)
        self.add("DESCRIPTION",         read=self.getDescription)


    def getDate(self,x):
        import time
        s=self.dbi.fetchvalue("SELECT cdatetime FROM #CALC WHERE id=%d"%self.Id)
        return time.strptime(s,"%Y-%m-%d %H:%M:%S")

    def getProgram(self,x):
        return self.dbi.fetchvalue("SELECT program FROM #CALC WHERE id=%d"%self.Id)
    def getVersion(self,x):
        return self.dbi.fetchvalue("SELECT version FROM #CALC WHERE id=%d"%self.Id)
    def getSubversion(self,x):
        return self.dbi.fetchvalue("SELECT subversion FROM #CALC WHERE id=%d"%self.Id)
    def getPlatform(self,x):
        return self.dbi.fetchvalue("SELECT platform FROM #CALC WHERE id=%d"%self.Id)
    def getDescription(self,x):
        return self.dbi.fetchvalue("SELECT description FROM #CALC WHERE id=%d"%self.Id)

    def getDOS(self,x):
        tdos=Array()
        tdos.dimension=['gridpoints','spin']
        tdos.setupFields(['energy','total','integrated'],
                         [FLOAT_TYPE,FLOAT_TYPE,FLOAT_TYPE],
                         ['%+14.10f','%+14.10f','%+14.10f'])
        spins=self.dbi.fetchvalues("SELECT DISTINCT spin FROM #DOS WHERE calc_id=%d"%self.Id)
        if 1 in spins and 2 in spins:
            spins=[1,2]
        elif 0 in spins:
            spins=[0]
        else:
            spins=[-1,-2,-3,-4]

        for s in spins:
            tdos.append(self.dbi.fetchall("SELECT energy,density,integrated "
            "FROM #DOS WHERE calc_id=%d AND spin=%d ORDER BY energy"%(self.Id,s)))

        return tdos

    def getIncar(self,x,specified=True):
        d=p4vasp.Dictionary.Incar()
        if specified:
            cond=" AND isspecified<>0"
        else:
            cond=""
        for name, fieldtype, isarray, value, textvalue in self.dbi.fetchall(
          "SELECT name, fieldtype, isarray, value, textvalue FROM #PARAMETERS "
          "WHERE calc_id=%d%s"%(self.Id,cond)):
            if value is None:
                value=textvalue
            if type(value) not in (type(""),type(u"")):
                msg().error("Reading INCAR from a SQL database: unexpected type of %s"%name)
                continue
            try:
                if isarray:
                    try:
                        val = retypeVec(split(value),fieldtype)
                    except UnknownType:
                        val = split(value)
                else:
                    try:
                        val = retype(value,fieldtype)
                    except UnknownType:
                        val = value
                d[name]=val
            except:
                msg().exception()
        return d

    def getKpointsText(self,x):
        return self.dbi.fetchvalue("SELECT kpoints_text FROM #CALC WHERE id=%d"%self.Id)
    def getName(self,x):
        n=self.dbi.fetchvalue("SELECT name FROM #CALC WHERE id=%d"%self.Id)
        if n is None:
            n=""
        return n
    def getPath(self,x):
        return self.dbi.fetchvalue("SELECT path FROM #CALC WHERE id=%d"%self.Id)
    def getKeywords(self,x):
        v=self.dbi.fetchvalue("SELECT keywords FROM #CALC WHERE id=%d"%self.Id)
        if v is None:
            v=""
        return v
    def getInitialStructure(self,x):
        sid=self.dbi.fetchvalue("SELECT id FROM #STRUCT WHERE calc_id=%d AND step=-1"%self.Id)
        return self.dbi.readStructure(sid)
    def getFinalStructure(self,x):
        sid=self.dbi.fetchvalue("SELECT id FROM #STRUCT WHERE calc_id=%d AND step=-2"%self.Id)
        return self.dbi.readStructure(sid)
    def getStructureSequence(self,x):
        sids=self.dbi.fetchvalues("SELECT id FROM #STRUCT WHERE calc_id=%d AND step>=0 ORDER BY step"%self.Id)
        l=[]
        for i in sids:
            l.append(self.dbi.readStructure(i))
        return l

    def getFreeEnergySequence(self,x):
        return self.dbi.fetchvalues("SELECT energy FROM #ENERGY WHERE calc_id=%d AND step>=0 ORDER BY step"%self.Id)

    def getStructureSequenceL(self,x):
        sids=self.dbi.fetchvalues("SELECT id FROM #STRUCT WHERE calc_id=%d AND step>=0 ORDER BY step"%self.Id)
        return SQLStructuresLL(sids,self.dbi)
    def getCStructureSequenceL(self,x):
        sids=self.dbi.fetchvalues("SELECT id FROM #STRUCT WHERE calc_id=%d AND step>=0 ORDER BY step"%self.Id)
        return SQLcStructuresLL(sids,self.dbi)


    def getForcesSequenceL(self,x):
        sids=self.dbi.fetchvalues("SELECT id FROM #STRUCT WHERE calc_id=%d AND step>=0 ORDER BY step"%self.Id)
        return SQLForcesSequenceLateList(sids,self.dbi)


    def getForcesSequence(self,x):
        sids=self.dbi.fetchvalues("SELECT id FROM #STRUCT WHERE calc_id=%d AND step>=0 ORDER BY step"%self.Id)
        l=[]
        for i in sids:
            l.append(self.dbi.readForce(i))
        return l

    def getPartialDOS(self,x):
        a=Array()
        spins    = self.dbi.fetchvalues("SELECT DISTINCT spin    FROM #LDOS WHERE calc_id=%d"%self.Id)
        orbitals = self.dbi.fetchvalues("SELECT DISTINCT orbital FROM #LDOS WHERE calc_id=%d"%self.Id)
        ions     = self.dbi.fetchvalue("SELECT MAX(atomnumber)  FROM #LDOS WHERE calc_id=%d"%self.Id)
        energies = self.dbi.fetchvalues("SELECT DISTINCT energy FROM #LDOS WHERE calc_id=%d"%self.Id)
        energies.sort()
        spins.sort()
        if spins[0]<0:
            spins.reverse()
        sorbitals=map(intern,["s","p","px","py","pz","d","dxy","dyz","dxz","dz2","dx2","f",
                           "f1","f2","f3","f4","f5","f6","f7"])
        for x in orbitals[:]:
            if x not in sorbitals:
                orbitals.remove(x)
        orbitals=map(lambda x,so=sorbitals:(so.index(x),str(x)),orbitals)
        orbitals.sort()
        orbitals=map(lambda x:x[1],orbitals)
        a.field=["energy"]+orbitals
        a.type =len(a.field)*[FLOAT_TYPE]
        a.defaultFormat()
        a.dimension=["gridpoints","spin","ion"]
        a.data=[]
        for ion in xrange(ions+1):
            il=[]
            for spin in xrange(len(spins)):
                sl=[]
                for g in xrange(len(energies)):
                    sl.append([energies[g]]+[0.0]*len(orbitals))
                il.append(sl)
            a.data.append(il)

        for (ion,s,e,o,d) in self.dbi.fetchiter("SELECT atomnumber,spin,energy,orbital,density FROM #LDOS WHERE calc_id=%d"%self.Id):
            spin=spins.index(s)
            i=energies.index(e)
            j=orbitals.index(o)+1
            a.data[ion][spin][i][j]=d

        return a
