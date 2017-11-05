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
Basic support for the DYNA file describing a k-point path
"""

from p4vasp.matrix import *
from p4vasp import *
from p4vasp.util import *

class Dyna(Parseable,ToString):
    """
    DYNA structure contains a sequence of k-point segments.
    """
    def __init__(self,d=None):
        self.comment=""
        self.head=""
        self.coordinates = "recip"
        self.size=51
        self.segments=[]
        self.labels=[]
        self.basis=None
        self.rbasis=None
        if isinstance(d,Dyna):
            self.comment==d.comment
            self.head=d.head
            self.coordinates = d.coordinates
            self.size=d.size
            self.segments=d.segments[:]
            self.labels=d.labels[:]
            self.basis=d.basis
            self.rbasis=d.rbasis
        elif d is not None:
            self.read(d)
    def clone(self):
        return Dyna(self)

    def updateRecipBasis(self,l=None):
        """Calculate reciprocal basis from the direct basis.
    Returns and sets the new reciprocal basis.
    The parameter *l* specifies the direct basis for conversion. If *None* , the *self.basis* is used.
        """
        if l is None:
            l=self.basis

        Omega=l[0]*(l[1].cross(l[2]))
        b0=1.0/Omega*(l[1].cross(l[2]))
        b1=1.0/Omega*(l[2].cross(l[0]))
        b2=1.0/Omega*(l[0].cross(l[1]))

        self.rbasis=[b0,b1,b2]
        return self.rbasis

    def withBasis(self,basis):
        "Returns a copy of Dyna structure with a specified direct basis. Reciprocal basis is calculated from the direct basis."
        d=self.clone()
        d.basis=basis
        d.updateRecipBasis()
        return d

    def cartesian(self):
        """Return a copy of Dyna structure in Cartesian coordinates.
        If Dyna is already in Cartesian coordinates, it returns itself.
        """
        if self.isCartesian():
            return self
        else:
            return self.clone().forceConvertToCartesian()
    def reciprocal(self):
        """Return a copy of Dyna structure in reciprocal coordinates.
        If Dyna is already in reciprocal coordinates, it returns itself.
        """
        if self.isReciprocal():
            return self
        else:
            return self.clone().forceConvertToReciprocal()
    def convertToCartesian(self,v):
        return v[0]*self.rbasis[0]+v[1]*self.rbasis[1]+v[2]*self.rbasis[2]
    def convertToReciprocal(self,v):
        return v[0]*self.basis[0]+v[1]*self.basis[1]+v[2]*self.basis[2]
    def forceConvertToCartesian(self):
        """Perform the conversion from direct to cartesian coordinates,
        (even if the Dyna is in cartesian coordinates).
        For internal use, don't use directly, use cartesian() method instead.
        """
        self.segments = [(self.convertToCartesian(p1),self.convertToCartesian(p2)) for (p1,p2) in self.segments]
        self.coordinates = "Cartesian"
        return self
    def forceConvertToReciprocal(self):
        """Perform the conversion from cartesian to reciprocal coordinates,
        even if the Dyna is in reciprocal coordinates.
        For internal use, don't use directly, use direct() method instead.
        """
        self.segments = [(self.convertToReciprocal(p1),self.convertToReciprocal(p2)) for (p1,p2) in self.segments]
        self.coordinates = "Reciprocal"
        return self
    def isCartesian(self):
        "Returns true if the Dyna is in cartesian coordinates."
        if self.coordinates:
            if len(self.coordinates):
                return lower(self.coordinates[0]) in ("c","k")
        return 0
    def isReciprocal(self):
        "Returns true if the Dyna is in reciprocal coordinates."
        return not self.isCartesian()

    def read(self,f="DYNA",closeflag=0):
        """Read DYNA from file *f* (file object or path).
        """
        if (type(f) == type("")):
            f = open(f,"r")
            closeflag = 1

        lines=f.readlines()
        if (closeflag):
            f.close()
        self.comment = lines[0].strip()
        self.head=lines[1].strip()
        self.coordinates=lines[2].strip()
        self.size = int(lines[3].split()[0])

        self.segments=[]
        self.labels=[]
        parts=[lines[i:i+3] for i in range(4,len(lines),3)]
        for p in parts:
            if len(p)==3:
                p1=Vector(map(float,p[1].split()[:3]))
                p2=Vector(map(float,p[2].split()[:3]))
                self.segments.append((p1,p2))
                self.labels.append([p[0].split()[0][1:-1],""])
            else:
                self.labels[-1][1]=p[0].split()[0][1:-1]
        return self

    def write(self,f="DYNA",newformat=1,closeflag=0):
        "Write DYNA to file *f* (file object or path)."
        if (type(f) == type("")):
            f = open(f,"w+")
            closeflag = 1
        f.write(self.comment)
        f.write("\n")
        f.write(self.head)
        f.write("\n")
        f.write(self.coordinates)
        f.write("\n")
        f.write(str(self.size))
        f.write("\n")
        for label,segment in zip(self.labels,self.segments):
            f.write("'%s'  0.0\n"%label[0])
            f.write("%10.8f %10.8f %10.8f\n"%(segment[0][0],segment[0][1],segment[0][2]))
            f.write("%10.8f %10.8f %10.8f\n"%(segment[1][0],segment[1][1],segment[1][2]))
            f.write("'%s'  0.0\n"%self.labels[-1][1])
        if (closeflag):
            f.close()
        return self
    def pointsAlongPath(self,pointsPerSegment=None):
        """Generate points along the path defined by Dyna. Each segment will generate pointsPerSegment equidistant points.
        If not specified, size is used as points-per-segment.
        """
        n=pointsPerSegment
        if n is None:
            n=self.size
        for p1,p2 in self.segments:
            for i in range(n):
                a=float(i)/(n-1)
                yield (1.0-a)*p1 + a*p2

    def pointsAlongPathWithDistanceAndLabel(self,pointsPerSegment=None):
        """Generate points along the path defined by Dyna. Each segment will generate pointsPerSegment equidistant points.
        Generates a sequence of tuples with 3 elements: point, cumulative distance and label.
        Labels are present only ot the segment edges, they are None elsewhere.
        If not specified, size is used as points-per-segment.
        """
        n=pointsPerSegment
        if n is None:
            n=self.size
        points=list(self.pointsAlongPath(n))
        path=0.0
        i=0
        for p1,p2 in zip(points,[points[0]]+points):
            path+=(p2-p1).length()
            label=None
            if i%n==0:
                label=self.labels[i/n][0]
            if i==len(points)-1:
                label=self.labels[-1][1]
            yield (p1,path,label)
            i+=1

    def deleteSegment(self,i):
        del self.segments[i]
        del self.labels[i]

    def addSegment(self,pos1=Vector(0,0,0),label1="",pos2=Vector(0,0,0),label2=""):
        self.segments.append((pos1,pos2))
        self.labels.append((label1,label2))

    def insertSegment(self,index,pos1=Vector(0,0,0),label1="",pos2=Vector(0,0,0),label2=""):
        self.segments.insert(index,(pos1,pos2))
        self.labels.insert(index,(label1,label2))

class DynaListener:
    def dynaUpdated(self,dyna):
        pass

class DynaPublisher:
    def __init__(self):
        self.dyna=Dyna()
        self.listeners=[]
    def addListener(self,listener):
        self.listeners.append(listener)
    def removeListener(self,listener):
        self.listeners.remove(listener)
    def updateDyna(self,dyna):
        self.dyna = dyna
        self.notifyUpdate()
    def notifyUpdate(self):
        for x in self.listeners:
            x.dynaUpdated(self.dyna)

_dynaPublisher = None

def dynaPublisher():
    global _dynaPublisher

    if _dynaPublisher is None:
        _dynaPublisher = DynaPublisher()
    return _dynaPublisher
