#!/usr/bin/python2
from string import *
from glob import glob
import os.path
from UserList import *
import re

class PotcarRecord:
    fpp=re.compile("(?P<key>[A-Z]+)\\s*=\\s*(?P<value>[+-]?\\d*\\.\\d+)")
    spp=re.compile("(?P<key>[A-Z]+)\\s*=\\s*(?P<value>.*)")
    def __init__(self,path=None):
        self.path=None
        self.params={}
        self.title=None
        self.pp_type="?"
        self.pp_specie="?"
        self.pp_version="?"
        self.element="?"
        if path is not None:
            self.path=path
            try:
                f=open(self.path)
                self.title=strip(f.readline())
                f.close()
                self.parseTitle()
            except:
                pass

    def parseLine(self,x):
        v=split(x)
        self.element=v[0]
        self.pp_type=v[1]
        self.pp_specie=v[2]
        self.pp_version=v[3]
        self.path=v[4]
        self.title=self.pp_type+" "+self.pp_specie

        if self.pp_version!="?":
            self.title=self.title+" "+self.pp_version

    def parseTitle(self):
        v=split(self.title)
        self.pp_type=strip(v[0])
        self.pp_specie=strip(v[1])
        if len(v)>2:
            self.pp_version=strip(v[2])
        self.element=self.pp_specie[:2]
        if len(self.element)==2:
            if self.element[1] not in letters:
                self.element=self.element[0]

    def parse(self,p=None):
        if p is None:
            p=self.path
        else:
            self.path=p
        h=self.getHead(p)
        for x in h:
            for y in split(x,";"):
                self.parseStringParam(y)
                self.parseFloatParam(y)
        self.title=strip(h[0])
        self.table=self.parseDescriptionTable(h)

        print p
        print self.params
        print

    def parseFloatParam(self,s):
        m=self.fpp.search(s)
        if m is not None:
#      setattr(self,m.group("key"),float(m.group("value"))
            self.params[m.group("key")]=float(m.group("value"))

    def parseStringParam(self,s):
        m=self.spp.search(s)
        if m is not None:
#      setattr(self,m.group("key"),float(m.group("value"))
            self.params[m.group("key")]=m.group("value")

    def parseDescriptionTable(self,l):
        t=None
        for i in range(len(l)):
            x=strip(l[i])
            if x=="Description":
                ll=[]
                for xx in l[i+1:]:
                    v=split(x)
                    try:
                        if len(v)==4:
                            ll.append((int(v[0]),float(v[1]),int(v[2]),float(v[3])))
                        else:
                            ll.append((int(v[0]),float(v[1]),int(v[2]),float(v[3]),int(v[4]),float(v[5])))
                    except:
                        break
                return ll
        return None
    def getHead(self,p=None):
        if p is None:
            p=self.path
        f=open(p)
        s=f.readline()
        l=[]
        while s!="":
            l.append(s)
            if s[:3]=="END":
                break
            s=f.readline()
        f.close()
        return l

    def __str__(self):
        return self.title

class PotcarDatabase(UserList):
    def __init__(self,path=None,
    collections=[
    "potpaw","potpaw_GGA","potpaw_PBE","potpaw_RPBE","potpaw_rc",
    "refpot","refpot_GGA","refpot_nc"]
    ):
        UserList.__init__(self)
        if path is not None:
            self.data.extend(self.scanRepository(path, collections))
    def scanDir(self,p):
        l=[]
        pp=os.path.join(p,"POTCAR")
        if os.path.isfile(pp):
            try:
                l.append(PotcarRecord(pp))
            except IOError:
                pass
        return l

    def scanCollection(self,p):
        l=[]
        for x in glob(os.path.join(p,"*")):
            if os.path.isdir(x):
                l.extend(self.scanDir(x))
        return l

    def scanRepository(self,p,collections=[
    "potpaw","potpaw_GGA","potpaw_PBE","potpaw_RPBE","potpaw_rc",
    "refpot","refpot_GGA","refpot_nc"]):
        l=[]
        for x in collections:
            l.extend(self.scanCollection(os.path.join(p,x)))
        return l

    def write(self,f,closeflag=0):
        if type(f)==type(""):
            f=open(f,"w")
            closeflag=1
        f.write("# Pseudopotential database\n")
        for x in self:
            f.write("%2s %-9s %-10s %10s %s\n"%(x.element,x.pp_type,x.pp_specie,x.pp_version,x.path))
        if closeflag:
            f.close()
    def clean(self):
        self.data=[]
    def read(self,f,closeflag=0):
        if type(f)==type(""):
            f=open(f)
            closeflag=1
        v=filter(lambda x:len(x) and x[0]!="#",split(f.read(),"\n"))
        for x in v:
            r=PotcarRecord()
            r.parseLine(x)
            self.append(r)
        if closeflag:
            f.close()


d=PotcarDatabase("/fs/home1/kresse")
#print join(map(lambda x:x.path,d),"\n")
d.write("ppdb.txt")
d1=PotcarDatabase()
d1.read("ppdb.txt")
d1.write("ppdb1.txt")
