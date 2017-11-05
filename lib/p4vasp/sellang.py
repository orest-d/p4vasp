#!/usr/bin/python

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

t_all           = re.compile("^all$")
t_num           = re.compile("^([0-9]+)$")
t_lrange        = re.compile("^-([0-9]+)$")
t_rrange        = re.compile("^([0-9]+)-$")
t_range         = re.compile("^([0-9]+)-([0-9]+)$")
t_spec          = re.compile("^#([0-9]+)$")
t_specnum       = re.compile("^#([0-9]+):([0-9]+)$")
t_specrange     = re.compile("^#([0-9]+):([0-9]+)-([0-9]+)$")
t_speclrange    = re.compile("^#([0-9]+):-([0-9]+)$")
t_specrrange    = re.compile("^#([0-9]+):([0-9]+)-$")
t_id            = re.compile("^([a-zA-Z_]+)$")
t_idnum         = re.compile("^([a-zA-Z_]+):([0-9]+)$")
t_idrange       = re.compile("^([a-zA-Z_]+):([0-9]+)-([0-9]+)$")
t_idlrange      = re.compile("^([a-zA-Z_]+):-([0-9]+)$")
t_idrrange      = re.compile("^([a-zA-Z_]+):([0-9]+)-$")


def getRangeForSpec(n,struct):
    before=0
    info=struct.info
    if n>=len(info):
        return []
    for i in range(n):
        before+=info[i].atomspertype
    return range(before,before+info[n].atomspertype)

def getRangeForId(I,struct):
    info=struct.info
    l=[]
    before=0
    for i in range(len(info)):
        if strip(info[i].element)==I:
            l.extend(range(before,before+info[i].atomspertype))
        before+=info[i].atomspertype
    return l

def decode(text,struct=None):
    """Decode selection from text.
  If text contains a *selection* in the selection language, and (optionally)
  struct contains the structure, this function returns a list of indexes
  of the selected atoms.
  A valid Structure with AtomInfo is needed if the species indexes and/or elements
  are used in the selection string.
    """
    l=[]
    v=split(text)
    for x in v:
        try:
            m=t_all.match(x)
            if m is not None:
                return range(len(struct))
            m=t_num.match(x)
            if m is not None:
                n=int(m.group(1))-1
                if n not in l:
                    l.append(n)
                continue
            m=t_lrange.match(x)
            if m is not None:
                append_set(l,range(0,int(m.group(1))))
                continue
            m=t_rrange.match(x)
            if m is not None:
                append_set(l,range(int(m.group(1))-1,len(struct)))
                continue
            m=t_range.match(x)
            if m is not None:
                append_set(l,range(int(m.group(1))-1, int(m.group(2))))
                continue
            m=t_spec.match(x)
            if m is not None:
                append_set(l,getRangeForSpec(int(m.group(1))-1,struct))
                continue
            m=t_specnum.match(x)
            if m is not None:
                n=getRangeForSpec(int(m.group(1))-1,struct)[int(m.group(2))-1]
                if n not in l:
                    l.append(n)
                continue
            m=t_speclrange.match(x)
            if m is not None:
                append_set(l,getRangeForSpec(int(m.group(1))-1,struct)[:int(m.group(2))])
                continue
            m=t_specrrange.match(x)
            if m is not None:
                append_set(l,getRangeForSpec(int(m.group(1))-1,struct)[int(m.group(2))-1:])
                continue
            m=t_specrange.match(x)
            if m is not None:
                append_set(l,getRangeForSpec(int(m.group(1))-1,struct)[int(m.group(2))-1:int(m.group(3))])
                continue
            m=t_id.match(x)
            if m is not None:
                append_set(l,getRangeForId(m.group(1),struct))
                continue
            m=t_idnum.match(x)
            if m is not None:
                n=getRangeForId(m.group(1),struct)[int(m.group(2))-1]
                if n not in l:
                    l.append(n)
                continue
            m=t_idlrange.match(x)
            if m is not None:
                append_set(l,getRangeForId(m.group(1),struct)[:int(m.group(2))])
                continue
            m=t_idrrange.match(x)
            if m is not None:
                append_set(l,getRangeForId(m.group(1),struct)[int(m.group(2))-1:])
                continue
            m=t_idrange.match(x)
            if m is not None:
                append_set(l,getRangeForId(m.group(1),struct)[int(m.group(2))-1:int(m.group(3))])
                continue
        except:
            traceback.print_exc()
#  l.sort()
    return l
#  return map(int,split(text))

def encode(sel,struct=None):
    if contains_set(sel,range(len(struct))):
        return "all"
    info=struct.info
    l=sel[:]
    before=0
    s=""
    for i in range(len(info)):
        r=range(before,before+info[i].atomspertype)
        if contains_set(l,r):
            if len(s):
                s+=" "
            s+=strip(info[i].element)
            remove_set(l,r)
        before+=info[i].atomspertype

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
                s+="-%d"%(r[-1]+1)
            elif r[-1]>=(len(struct)-1):
                s+="%d-"%(r[0]+1)
            else:
                s+="%d-%d"%(r[0]+1,r[-1]+1)
        remove_set(l,r)
    if len(s):
        s+=" "
    s+=join(map(str,l))
    return s


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

    system=XMLSystemPM("../vasprun2.xml")
    print system.FINAL_STRUCTURE.info.toxml()
    s="#1"
    print s,decode(s,system.FINAL_STRUCTURE)
    s="#2"
    print s,decode(s,system.FINAL_STRUCTURE)
    s="#1 #2"
    print s,decode(s,system.FINAL_STRUCTURE)
    s="#2:1"
    print s,decode(s,system.FINAL_STRUCTURE)
    s="#2:2-"
    print s,decode(s,system.FINAL_STRUCTURE)
    s="#2:-3"
    print s,decode(s,system.FINAL_STRUCTURE)
    s="#2:2-3"
    print s,decode(s,system.FINAL_STRUCTURE)
    s="2-4"
    print s,decode(s,system.FINAL_STRUCTURE)
    s="-4"
    print s,decode(s,system.FINAL_STRUCTURE)
    s="2-"
    print s,decode(s,system.FINAL_STRUCTURE)
    s="Ti"
    print s,decode(s,system.FINAL_STRUCTURE)
    s="O"
    print s,decode(s,system.FINAL_STRUCTURE)
    s="O:2"
    print s,decode(s,system.FINAL_STRUCTURE)
    s="O:2-"
    print s,decode(s,system.FINAL_STRUCTURE)
    s="O:-3"
    print s,decode(s,system.FINAL_STRUCTURE)
    s="O:2-3"
    print s,decode(s,system.FINAL_STRUCTURE)

    print

    r=[0,1,2,3,4,5]
    s=encode(r,system.FINAL_STRUCTURE)
    c=decode(s,system.FINAL_STRUCTURE)
    print r
    print s
    print c
    print
    r=[1,2,3,4,5]
    s=encode(r,system.FINAL_STRUCTURE)
    c=decode(s,system.FINAL_STRUCTURE)
    print r
    print s
    print c
    print
    r=[0,1,2,3,4]
    s=encode(r,system.FINAL_STRUCTURE)
    c=decode(s,system.FINAL_STRUCTURE)
    print r
    print s
    print c
    print
    r=[3,4,5]
    s=encode(r,system.FINAL_STRUCTURE)
    c=decode(s,system.FINAL_STRUCTURE)
    print r
    print s
    print c
    print
    r=[0,1]
    s=encode(r,system.FINAL_STRUCTURE)
    c=decode(s,system.FINAL_STRUCTURE)
    print r
    print s
    print c
    print
    #decode("1 2- -3 4-5 Au #6 #7:8 #9:10- #11:-12 #13:14-15 B:16 C:17- Cd:-18 Eu:19-20")
