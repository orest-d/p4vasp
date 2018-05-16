#!/usr/bin/python2

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



from string import *
import re
import traceback
from p4vasp.setutils import *
from p4vasp import *
from p4vasp.applet import *
from UserList import *

t_all           = re.compile("^\\s*all")
t_indices       = re.compile("^\\s*\\(\\s*([+-]?[0-9]+)\\s+([+-]?[0-9]+)\\s+([+-]?[0-9]+)\\s*\\)")
t_num           = re.compile("^\\s*([0-9]+)")
t_lrange        = re.compile("^\\s*-([0-9]+)")
t_rrange        = re.compile("^\\s*([0-9]+)-")
t_range         = re.compile("^\\s*([0-9]+)-([0-9]+)")
t_spec          = re.compile("^\\s*#([0-9]+)")
t_specnum       = re.compile("^\\s*#([0-9]+):([0-9]+)")
t_specrange     = re.compile("^\\s*#([0-9]+):([0-9]+)-([0-9]+)")
t_speclrange    = re.compile("^\\s*#([0-9]+):-([0-9]+)")
t_specrrange    = re.compile("^\\s*#([0-9]+):([0-9]+)-")
t_id            = re.compile("^\\s*([a-zA-Z_]+)")
t_idnum         = re.compile("^\\s*([a-zA-Z_]+):([0-9]+)")
t_idrange       = re.compile("^\\s*([a-zA-Z_]+):([0-9]+)-([0-9]+)")
t_idlrange      = re.compile("^\\s*([a-zA-Z_]+):-([0-9]+)")
t_idrrange      = re.compile("^\\s*([a-zA-Z_]+):([0-9]+)-")

def createRangeForSpec(n,struct):
    before=0
    info=struct.info
    if n>=len(info):
        return []
    for i in range(n):
        before+=info[i].atomspertype
    return range(before,before+info[n].atomspertype)

def createRangeForId(I,struct):
    info=struct.info
    l=[]
    before=0
    for i in range(len(info)):
        if strip(info[i].element)==I:
            l.extend(range(before,before+info[i].atomspertype))
        before+=info[i].atomspertype
    return l

class SelectionListener:
    def notifyAtomSelection(self, sel,origin):
        pass

class Selection(UserList):
    def __init__(self, l=[],struct=None):
        UserList.__init__(self)
        if type(l)==type(""):
            self.decode(l,struct)
        elif isinstance(l,Selection):
            self.setSelection(l)
        else:
            ll=[]
            for x in l:
                if type(x)==type(1):
                    ll.append((x,0,0,0))
                else:
                    ll.append(x)

    def getInCellIndexes(self):
        f=filter(lambda x:(x[1]==0 and x[2]==0 and x[3]==0),self.data)
        return map(lambda x:x[0],f)
    def getAtoms(self):
        return map(lambda x:x[0],self.data)

    def notify(self,origin):
        global _selection
        if id(self)==id(_selection):
            for x in applets():
                if isinstance(x,SelectionListener):
                    if id(x)!=id(origin):
                        x.notifyAtomSelection(self,origin)

    def setSelection(self,sel):
        l=[]
        for x in sel:
            if type(x)==type(1):
                l.append((x,0,0,0,))
            else:
                l.append((x[0],x[1],x[2],x[3]))
        self.data=l

    def clone(self):
        l=[]
        for x in self.data:
            l.append(x[:])
        return Selection(l)

    def toSet(self):
        t=map(lambda x:(x[1],x[2],x[3],x[0]),to_set(self.data))
        t.sort()
        self.data=map(lambda x:(x[3],x[0],x[1],x[2]),t)
        return self
    def discardCellInfo(self):
        self.data=map(lambda x:(x[0],0,0,0),self.data)
    def discardOutOfCell(self):
        self.data=filter(lambda x:(x[1]==0 and x[2]==0 and x[3]==0),self.data)
    def decode(self,text,struct=None):
        self.data=[]
        self.appendSellang(text,struct)
        return self
    def appendSellang(self,text,struct=None):
        """Decode selection from text.
      If text contains a *selection* in the selection language, and (optionally)
      struct contains the structure, this function returns a list of indexes
      of the selected atoms.
      A valid Structure with AtomInfo is needed if the species indexes and/or elements
      are used in the selection string.
        """
        x=text
        nx,ny,nz=0,0,0
        msg().status("OK")
        while len(x):
            try:
                m=t_all.match(x)
                if m is not None:
                    self.data.extend(map(lambda x:(x,nx,ny,nz),range(len(struct))))
                    x=strip(x[m.end():])
                    continue

                m=t_indices.match(x)
                if m is not None:
                    nx,ny,nz=int(m.group(1)),int(m.group(2)),int(m.group(3))
                    x=strip(x[m.end():])
                    continue
                m=t_range.match(x)
                if m is not None:
                    self.data.extend(map(lambda x:(x,nx,ny,nz),range(int(m.group(1))-1, int(m.group(2)))))
                    x=strip(x[m.end():])
                    continue
                m=t_lrange.match(x)
                if m is not None:
                    self.data.extend(map(lambda x:(x,nx,ny,nz),range(0,int(m.group(1)))))
                    x=strip(x[m.end():])
                    continue
                m=t_rrange.match(x)
                if m is not None:
                    self.data.extend(map(lambda x:(x,nx,ny,nz),range(int(m.group(1))-1,len(struct))))
                    x=strip(x[m.end():])
                    continue
                m=t_num.match(x)
                if m is not None:
                    n=int(m.group(1))-1
                    self.data.append((n,nx,ny,nz))
                    x=strip(x[m.end():])
                    continue
                m=t_spec.match(x)
                if m is not None:
                    self.data.extend(map(lambda x:(x,nx,ny,nz),createRangeForSpec(int(m.group(1))-1,struct)))
                    x=strip(x[m.end():])
                    continue
                m=t_specnum.match(x)
                if m is not None:
                    n=createRangeForSpec(int(m.group(1))-1,struct)[int(m.group(2))-1]
                    self.data.append((n,nx,ny,nz))
                    x=strip(x[m.end():])
                    continue
                m=t_speclrange.match(x)
                if m is not None:
                    self.data.extend(map(lambda x:(x,nx,ny,nz),createRangeForSpec(int(m.group(1))-1,struct)[:int(m.group(2))]))
                    x=strip(x[m.end():])
                    continue
                m=t_specrrange.match(x)
                if m is not None:
                    self.data.extend(map(lambda x:(x,nx,ny,nz),createRangeForSpec(int(m.group(1))-1,struct)[int(m.group(2))-1:]))
                    x=strip(x[m.end():])
                    continue
                m=t_specrange.match(x)
                if m is not None:
                    self.data.extend(map(lambda x:(x,nx,ny,nz),createRangeForSpec(int(m.group(1))-1,struct)[int(m.group(2))-1:int(m.group(3))]))
                    x=strip(x[m.end():])
                    continue
                m=t_id.match(x)
                if m is not None:
                    self.data.extend(map(lambda x:(x,nx,ny,nz),createRangeForId(m.group(1),struct)))
                    x=strip(x[m.end():])
                    continue
                m=t_idnum.match(x)
                if m is not None:
                    n=createRangeForId(m.group(1),struct)[int(m.group(2))-1]
                    self.data.append((n,nx,ny,nz))
                    x=strip(x[m.end():])
                    continue
                m=t_idlrange.match(x)
                if m is not None:
                    self.data.extend(map(lambda x:(x,nx,ny,nz),createRangeForId(m.group(1),struct)[:int(m.group(2))]))
                    x=strip(x[m.end():])
                    continue
                m=t_idrrange.match(x)
                if m is not None:
                    self.data.extend(map(lambda x:(x,nx,ny,nz),createRangeForId(m.group(1),struct)[int(m.group(2))-1:]))
                    x=strip(x[m.end():])
                    continue
                m=t_idrange.match(x)
                if m is not None:
                    self.data.extend(map(lambda x:(x,nx,ny,nz),createRangeForId(m.group(1),struct)[int(m.group(2))-1:int(m.group(3))]))
                    x=strip(x[m.end():])
                    continue
#       print "UTS",x
                msg().error("Unrecognized term in selection.")
                return self
            except:
                msg().exception()
        return self
    #  return map(int,split(text))

    def encodeSimple(self,sel=None):
        if sel is None:
            sel=self.data
        nx,ny,nz=0,0,0
        s=""
        last=None
        begin=None
        c=compile("""
if last==begin:
    s+=" %d"%(last+1)
elif (last-1)==begin:
    s+=" %d %d"%(begin+1,last+1)
else:
    s+=" %d-%d"%(begin+1,last+1)
last=None
begin=None
""","-","exec")
        for i,x,y,z in sel:
            if x!=nx or y!=ny or z!=nz:
                nx,ny,nz=x,y,z
                if begin is not None:
                    exec c
                s+=" (%d %d %d)"%(nx,ny,nz)
            if begin is None:
                last=i
                begin=i
            else:
                if i==last+1:
                    last=i
                else:
                    exec c
                    begin=i
                    last=i
        if begin is not None:
            exec c
        return strip(s)

    def splitParts(self,l=None):
        if l is None:
            l=self.data
        nx,ny,nz=0,0,0
        parts=[]
        ll=[]
        for i,x,y,z in l:
            if x!=nx or y!=ny or z!=nz:
                if len(ll):
                    parts.append(((nx,ny,nz),ll))
                nx,ny,nz=x,y,z
                ll=[i]
            else:
                ll.append(i)
        if len(ll):
            parts.append(((nx,ny,nz),ll))
            nx,ny,nz=x,y,z
        return parts

    def encode(self,struct=None,sel=None):
        if sel is None:
            sel=self.data
        if struct is None:
            return self.encodeSimple(sel)
        ll=self.splitParts(sel)
#    print ll
        s=""
        if len(ll):
            n,l =ll[0]
            if n==(0,0,0):
                s+=self.encodePart(l,struct)
                ll=ll[1:]
            for n,l in ll:
#        print "Encode part",n,l
                s+=" (%d %d %d) %s"%(n[0],n[1],n[2],self.encodePart(l,struct))
        return s

    def __str__(self):
        return self.encode()
    def encodePart(self,sel,struct=None):
        if sel==range(len(struct)):
            return "all"
        info=struct.info

        l=sel[:]
        s=""


        types=[]
        duplitypes=[]
        for x in info:
            e=strip(x.element)
            if e in types:
                if e not in duplitypes:
                    duplitypes.append(e)
                break
            else:
                types.append(e)
        while len(l):
            before=0
            flag=0
            for i in range(len(info)):
                r=range(before,before+info[i].atomspertype)
#       print "elem %02d %02s"%(i,info[i].element),r,l
                if l[:min(len(l),len(r))]==r:
                    if len(s):
                        s+=" "
                    ec=strip(info[i].element)
                    if (not len(ec)) or (ec in duplitypes):
                        ec="#%d"%(i+1)
                    s+=ec
                    l=l[len(r):]
                    flag=1
                    break
                before+=info[i].atomspertype
            if not len(l):
                break
            if flag:
                continue
            r=[l[0]]
#      print "before",l,r
            for i in range(1,len(l)):
#        print i,l[i],l[i-1],l[i]-l[i-1]
                if (l[i]-l[i-1])!=1:
#         print "break"
                    break
#       print "append",l[i]
                r.append(l[i])
#      print "get",l,r

            if len(s):
                s+=" "
            if len(r)==1:
                s+=str(r[0]+1)
            else:
                if r[0]==0:
                    s+="-%d"%(r[-1]+1)
                elif r[-1]>=(len(struct)-1):
                    s+="%d-"%(r[0]+1)
                else:
                    s+="%d-%d"%(r[0]+1,r[-1]+1)
            l=l[len(r):]
        if len(s):
            s+=" "
        s+=join(map(str,l))
        return s

_selection=Selection()

def selection():
    global _selection
    return _selection

def encodeRange(sel):
    l=sel[:]
    before=0
    s=""

    l.sort()
    while len(l):
        r=[l[0]]
        for i in range(1,len(l)):
            if (l[i]-l[i-1])>1:
                break
            r.append(l[i])
        if len(s):
            s+=" "
        if len(r)==1:
            s+=str(r[0]+1)
        else:
            if r[0]==0:
                s+="1-%d"%(r[-1]+1)
            else:
                s+="%d-%d"%(r[0]+1,r[-1]+1)
        remove_set(l,r)
    if len(s):
        s+=" "
    s+=join(map(str,l))
    return s

if __name__=="__main__":
    from SystemPM import *

    system=XMLSystemPM("../../vasprun.xml")
    print system.INITIAL_STRUCTURE.info.toxml()
    sel=Selection()
    s="#1"
    print s,sel.appendSellang(s,system.INITIAL_STRUCTURE)
    s="#2"
    print s,sel.appendSellang(s,system.INITIAL_STRUCTURE)
    s="#1 #2"
    print s,sel.appendSellang(s,system.INITIAL_STRUCTURE)
    s="-2"
    print s,sel.appendSellang(s,system.INITIAL_STRUCTURE)
    s="N Ni"
    print s,sel.appendSellang(s,system.INITIAL_STRUCTURE)
    sel.toSet()
    print "set",sel
    print "atoms",sel.getAtoms()
    print "encode simple",sel.encodeSimple()
    sel.append((2,0,0,0))
    sel.append((6,0,0,0))
    sel.append((7,0,0,0))
    sel.append((9,0,1,0))
    sel.append((10,0,1,0))
    sel.append((11,0,1,0))
    sel.append((12,1,1,0))
    sel.append((13,1,1,0))
    sel.append((14,1,1,0))
    sel.append((2,1,1,0))
    sel.append((3,1,1,0))
    sel.append((4,1,1,0))
    sel.toSet()
    print "encode simple",sel.encodeSimple()
    s="N Ni (1 0 0) H C O"
    print s,sel.decode(s,system.INITIAL_STRUCTURE)
    print s,sel.encodeSimple()
    print sel.splitParts()
    print s,sel.encode(system.INITIAL_STRUCTURE)

    print
    print
    try:
        s=Structure("../../POSCAR")
    except:
        print "POSCAR not found."
        raise "stop"
    sel=Selection()
    sel.append((7,1,0,0))
    sel.append((5,0,0,0))
    sel.append((1,0,0,0))
    print sel.encodeSimple()
    print sel.encode(s)
    sel=Selection()
    sel.append((5,1,0,0))
    sel.append((6,0,0,0))
    sel.append((7,0,0,0))
    print sel.encodeSimple()
    print sel.encode(s)

#  s="#2"
#  s="#1 #2"
#  s="#2:1"
#  s="#2:2-"
#  s="#2:-3"
#  s="#2:2-3"
#  s="2-4"
#  s="-4"
#  s="2-"
#  s="Ti"
#  s="O"
#  s="O:2"
#  s="O:2-"
#  s="O:-3"
#  s="O:2-3"
#
#  print
#
#  r=[0,1,2,3,4,5]
#  s=encode(r,system.FINAL_STRUCTURE)
#  c=decode(s,system.FINAL_STRUCTURE)
#  print r
#  print s
#  print c
#  print
