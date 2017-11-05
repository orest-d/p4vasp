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

from UserDict import *
from types import *
from string import *
from p4vasp import *
from p4vasp.store import *

class Factory(UserDict):
    def __init__(self,d={}):
        UserDict.__init__(self,d)
        self.sortedvalues=d.values()[:]

    def add(self,x):
        self[x.Class]=x
        self[x.getFullName()]=x
        self.sortedvalues.append(x)

    def findDescriptor(self,c):
        if self.has_key(c):
            return self[c]
        else:
            for x in self.values():
                if isinstance(x,c):
                    return x
            return None

    def getClass(self,c):
        if self.has_key(c):
            return self[c].Class
        v=map(strip,split(c,"."))
        if len(v) and len(c):
            if len(v)==1:
                c=eval(c)
            else:
                exec "import %s\nc=%s\n"%(join(v[:-1],"."),c)
        return c

    def create(self,c,*arg):
        if self.has_key(c):
            return apply(self[c].create,arg)
        if type(c) is StringType:
            return apply(self.getClass(c),arg)

    def getStoreProfile(self):
        return FactoryProfile(factory=self)



class Repository:
    def __init__(self,l=[],factory=None):
        self.data=l[:]
        self.factory=factory
        self.notify_on_append=[]
        self.notify_on_remove=[]
        self.notify_on_activate=[]
        self.temporary_active=None

    def getClass(self,c):
        v=map(strip,split(c,"."))
        if len(v) and len(c):
            if len(v)==1:
                c=eval(c)
            else:
                exec "import %s\nc=%s\n"%(join(v[:-1],"."),c)
        return c
    def __len__(self):
        if self.temporary_active is None:
            return len(self.data)
        else:
            return len(self.data)+1

    def __getitem__(self, i):
        if self.temporary_active is None:
            return self.data[i]
        else:
            d=[self.temporary_active]+self.data
            return d[i]

    def append(self,x):
        self.data.append(x)
        for f in self.notify_on_append:
            f(self,x)

    def insert(self, i, item):
        if self.temporary_active is None:
            self.data.insert(i, item)
        else:
            self.data.insert(i-1, item)
        for f in self.notify_on_append:
            f(self,item)

    def remove(self,x):
        try:
            self.data.remove(x)
            if id(x) == id(self.temporary_active):
                self.temporary_active=None
            for f in self.notify_on_remove:
                f(self,x)
        except:
            msg().exception()

    def findActive(self,c):
        if type(c) == type(""):
            c=self.getClass(c)
        if self.temporary_active is not None:
            d=[self.temporary_active]+self.data
        else:
            d=self.data
        if type(c) in [ListType,TupleType]:
            l=[]
            for x in c:
                if type(x) == type(""):
                    x=self.getClass(x)
                l.append(x)
            for x in d:
                for c in l:
                    if isinstance(x,c):
                        return x
        else:
            for x in d:
                if isinstance(x,c):
                    return x
        return None

    def activate(self,x):
#    print "acrivate",x
        self.temporary_active=None
        if x is not None:
            m=map(id,self.data)
            if id(x) in m:
                del self.data[m.index(id(x))]
                self.insert(0,x)
            else:
                self.insert(0,x)
                for f in self.notify_on_append:
                    f(self,x)

            for f in self.notify_on_activate:
                f(self,x)
            return x

    def getActive(self,x):
#    print "getActive",x
        r=self.findActive(x)
        if r is None:
#      print "  new"
            if self.factory is None:
                return None
            if type(x) in [ListType,TupleType]:
                x=x[0]
            return self.activate(self.factory.create(x))
        return r

    def setTemporaryActive(self,x):
        if self.temporary_active is not None:
            for f in self.notify_on_remove:
                f(self,x)
        self.temporary_active=x
        if x is not None:
            for f in self.notify_on_append:
                f(self,x)
            for f in self.notify_on_activate:
                f(self,x)

    def getStoreProfile(self):
        return RepositoryProfile(factoryprofile=self.factory.getStoreProfile())

class Descriptor:
    def __init__(self,Class=None,keywords=[],prototype=None):
        self.Class=Class
        if type(keywords)==StringType:
            keywords=split(keywords)
        self.keywords=map(intern,keywords)
        self.prototype=prototype

    def getFullName(self):
        if self.Class.__module__=="__main__":
            return self.Class.__name__
        else:
            return self.Class.__module__+"."+self.Class.__name__

    def getName(self):
        return self.Class.__name__

    def create(self,*arg):
        if self.prototype is not None:
            return apply(self.prototype.create,arg)
        else:
            return apply(self.Class,arg)



class DescriptorProfile(Profile):
    def __init__(self,name=Descriptor,tagname="d"):
        Profile.__init__(self,name,tagname=tagname,
        attr_setup="stringlist keywords")
        self.addAttr(ClassAttribute("class","Class",tag=1,tagattr=1))

class FactoryProfile(Profile):
    def __init__(self,name=Factory,tagname="descriptors",factory=None):
        Profile.__init__(self,name,tagname=tagname,disable_attr=1)
        dp=DescriptorProfile()
        self.addClass(dp)
        if factory is not None:
            for f in factory.values():
                if f.prototype is not None:
                    if f.prototype.setup_profile is not None:
                        dp.addClass(f.prototype.setup_profile)

    def retrieveObj(self,elem,c=None):
        if elem.nodeType == elem.ELEMENT_NODE:
            label=elem.getAttribute("label")
            if c is None:
                c=Factory()
            if label:
                self.getRoot().retrieve_reftable[label]=c
            for x in elem.childNodes:
                if x.nodeType==x.ELEMENT_NODE:
                    c.add(self.retrieve(x))
            return c

    def writeObj(self,f,obj,indent=0,label=None):
        in0=indent*INDENT
        in1=in0+INDENT

        f.write('%s<%s'%(in0,self.tagname))
        if label:
            f.write(' label="%s"'%label)
        f.write(">\n")

        for x in obj.values():
            self.write(f,x,indent+1)

        f.write("%s</%s>\n"%(in0,self.tagname))

class RepositoryProfile(Profile):
    def __init__(self,name=Repository,tagname="active",factoryprofile=None):
        Profile.__init__(self,name,tagname=tagname,disable_attr=1)
        self.factoryprofile=factoryprofile
        if factoryprofile is not None:
            self.addClass(factoryprofile)

    def retrieveObj(self,elem,c=None):
        if elem.nodeType == elem.ELEMENT_NODE:
            label=elem.getAttribute("label")
            if c is None:
                c=Repository()
            if label:
                self.getRoot().retrieve_reftable[label]=c
            fp=self.factoryprofile
            if fp is None:
                fp=self
            for x in elem.childNodes:
                if x.nodeType==x.ELEMENT_NODE:
                    c.append(fp.retrieve(x))
            return c

    def writeObj(self,f,obj,indent=0,label=None):
        in0=indent*INDENT
        in1=in0+INDENT

        f.write('%s<%s'%(in0,self.tagname))
        if label:
            f.write(' label="%s"'%label)
        f.write(">\n")
#    print obj
        fp=self.factoryprofile
        if fp is None:
            fp=self
        for x in obj:
            fp.write(f,x,indent+1)

        f.write("%s</%s>\n"%(in0,self.tagname))
