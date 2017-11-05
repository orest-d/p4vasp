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


import p4vasp.repository as repository
from string import *
import os
import os.path
from glob import glob
import sys
import p4vasp.SystemPM
from p4vasp import *
from types import *
from p4vasp.applet.appletlist import appletlist

class AppletTag:
    pass

class AppletRepository(repository.Repository,p4vasp.SystemPM.SystemListListener):
    def getStoreProfile(self):
        return AppletRepositoryProfile()
#  def getStoreProfile(self):
#    return RepositoryProfile(factoryprofile=self.factory.getStoreProfile())

    def notifySystemListUpdated(self,l):
        for x in self.data:
            if isinstance(x,p4vasp.SystemPM.SystemListListener):
                x.notifySystemListUpdated(l)
    def notifySystemActivated(self,l,s):
        for x in self.data:
            if isinstance(x,p4vasp.SystemPM.SystemListListener):
                x.notifySystemActivated(l,s)

    def getActive(self,x,showmode=None):
#    print "getActive",x
        r=self.findActive(x)
        if r is None:
#      print "  new"
            if self.factory is None:
                return None
            if type(x) in [ListType,TupleType]:
                x=x[0]
            if showmode is None:
                return self.activate(self.factory.create(x))
            else:
                x=self.factory.create(x)
                x.showmode=showmode
                self.activate(x)
                return x
        return r


def getClass(c):
    v=map(strip,split(c,"."))
    if len(v) and len(c):
        if len(v)==1:
            c=eval(c)
        else:
#            print "import %s\no=%s\n"%(join(v[:-1],"."),c)
            exec "import %s\nc=%s\n"%(join(v[:-1],"."),c)
    return c

def findApplets(include=[],exclude=["p4vasp.applet.Applet.Applet"],
modules=["p4vasp.applet","applets",""]):
    l=include
    for p in sys.path:
        if len(p) and p[-1]!=os.sep:
            p+=os.sep
        for pe in modules:
            if pe=="":
                pp=""
            else:
                pp=p+join(split(pe,"."),os.sep)+os.sep
            for ext in ["*.py","*.pyc","*.pyo","*.pyw"]:
                pl=map(lambda x:os.path.splitext(os.path.basename(x))[0],glob(pp+ext))
                for x in pl:
                    if find(x,"Applet")==(len(x)-len("Applet")):
                        if len(pe):
                            c=pe+"."+x+"."+x
                        else:
                            c=x+"."+x
                        if c not in l and c not in exclude:
                            l.append(c)

    ll=[]
    for c in l:
#    print "test",c
        try:
            o=getClass(c)
            if issubclass(o,AppletTag):
                ll.append(c)
        except:
            msg().exception()

    return ll

class AppletFactory(repository.Factory):
    def add(self,x):
        if type(x)==type(""):
            c=getClass(x)
            x=repository.Descriptor(Class=c,prototype=c.prototype)
        repository.Factory.add(self,x)

    def registerApplets(self,
      include=[
        "p4vasp.applet.NewApplet.NewApplet",
        "p4vasp.applet.StructureWindowApplet.StructureWindowApplet",
        "p4vasp.applet.StructureWindowControlApplet.StructureWindowControlApplet",
        "p4vasp.applet.ElectronicApplet.ElectronicApplet",
        "p4vasp.applet.ElectronicControlApplet.ElectronicControlApplet"
      ],
      exclude=[
        "p4vasp.applet.Applet.Applet"
      ],
      modules=[
        "p4vasp.applet",
        "applets",
        ""
      ]):
        for a in appletlist():
            if a not in include:
                include.append(a)
        for x in findApplets(include,exclude,modules):
            self.add(x)

    def showApplet(self,a,*arg):
        return self.getActive(a)

_appletfactory=AppletFactory()

AppletRepository.store_profile=repository.RepositoryProfile(AppletRepository,"applets")
AppletFactory.store_profile=repository.FactoryProfile(AppletFactory,"appletconfig")

_applets=None
_frame=None

def applets():
    return _applets
def appletfactory():
    return _appletfactory


def getAppletFrame():
    global _frame
    return _frame

def setAppletFrame(f):
    global _frame
    _frame=f

def setAppletRepository(a):
    global _applets
    if _applets is not None:
        p4vasp.SystemPM.systemlist().removeSystemListListener(_applets)
    _applets = a
    p4vasp.SystemPM.systemlist().addSystemListListener(_applets)

setAppletRepository(AppletRepository(factory=_appletfactory))

def setAppletFactory(a):
    global _appletfactory
    _appletfactory = a

class AppletRepositoryProfile(repository.RepositoryProfile):
    def __init__(self,name=AppletRepository,tagname="applets"):
        repository.RepositoryProfile.__init__(self,name,tagname=tagname)
        for f in appletfactory().values():
            if f.Class.store_profile is not None:
                self.addClass(f.Class.store_profile)
