#!/usr/bin/python2
from math import *
from p4vasp.paint3d.OpenGLPaint3D import *
from p4vasp.paint3d.PovrayPaint3D import *
from p4vasp.matrix import *
from p4vasp.SystemPM import *
from sys import *
import os

def Acos(x):
    if x>=1.0:
        return 0.0
    if x<=-1.0:
        return -pi
    return acos(x)

class ConvexShape:
    def __init__(self):
        self.vertices=[]
        self.planes=[]

    def cleanup(self):
        l=[]
        for a in self.planes:
            for b in a:
                if b not in l:
                    l.append(b)
        l.sort()
        v=[]
        for i in l:
            v.append(self.vertices[i])
        self.vertices=v
        for i in range(len(self.planes)):
            self.planes[i]=map(lambda x,l=l:l.index(x),self.planes[i])
    def removeEmptyPlanes(self):
        self.planes=filter(len,self.planes)

    def removeVertices(self,l):
        for i in range(len(self.planes)):
            self.planes[i]=filter(lambda x,l=l:x not in l,self.planes[i])
        self.cleanup()
    def findDuplicateVertices(self):
        merge=[]
        processed=set()
        for i in range(len(self.vertices)):            
            if i in processed:
                continue
            m=[i]
            processed.add(i)     
            for j in range(i+1,len(self.vertices)):
                if j in processed:
                    continue            
                if (self.vertices[i]-self.vertices[j]).length()<1e-5:
                    m.append(j)
                    processed.add(j)
            merge.append(m)            
        return merge
    def removeDuplicateVertices(self):
        merge=self.findDuplicateVertices()
        p=self.planes
        self.planes=[]
        for plane in p:
            fixedplane=[]
            for i in plane:
                for m in merge:
                    if i in m:
                        fixedplane.append(m[0])
                        break
            self.planes.append(fixedplane)                            
        self.cleanup()
    def removeDegenerateSegments(self):
        self.removeDuplicateVertices()
        p=self.planes
        self.planes=[]
        for plane in p:
            fixedplane=[]
            last=None
            for i in plane:
                if last==i:
                    continue
                else:
                    fixedplane.append(i)
                    last=i
            self.planes.append(fixedplane)                            
        self.cleanup()
        
    def move(self,v,r=None):
        if r is None:
            r=range(len(self.vertices))
        for i in r:
            w=self.vertices[i]
            self.vertices[i]=Vector(w[0]+v[0],w[1]+v[1],w[2]+v[2])

    def findclip(self,n,r):
        d=n*r
        l=[]
        for i in range(len(self.vertices)):
            if n*self.vertices[i]>d:
                l.append(i)
        return l

    def planeArea(self,l):
        if type(l)==type(0):
            l=self.planes[l]
        if len(l)<3:
            return 0
        A=0.0
        v=self.vertices
        o=v[l[0]]
        flag=1
        for i in l:
            a=v[i]-o
            for j in l:
                b=v[j]-o
                n=a.cross(b)
                if n.length()>0.0:
                    flag=0
                    break
            if not flag:
                break
        if flag:
            return 0.0
        n=(1.0/n.length())*n
        for i in range(len(l)):
            j=(i+1)%len(l)
            A=A+(v[l[i]]-o).cross(v[l[j]]-o)*n
        A=0.5*A
        return abs(A)

    def area(self):
        A=0.0
        for p in self.planes:
            A=A+self.planeArea(p)
        return A

    def volume(self):
        R=Vector(0.0,0.0,0.0)
        for v in self.vertices:
            R=R+v
        R=(1.0/len(self.vertices))*R
        V=0.0
        v=self.vertices
        for p in self.planes:
            if len(p)>2:
                A=self.planeArea(p)
                o=v[p[0]]
                flag=1
                for i in p:
                    a=v[i]-o
                    for j in p:
                        b=v[j]-o
                        n=a.cross(b)
                        if n.length()>0.0:
                            flag=0
                            break
                    if not flag:
                        break
                if flag:
                    continue
                if n.length()==0.0:
                    continue
                n=(1.0/n.length())*n
                h=abs(n*(R-o))
                V=V+A*h
        return V/3


    def planeBasis(self,l):
        m=self.meanPoint(l)
        for i in l:
            e1=self.vertices[i]-m
            if e1.length()>1e-6:
                break
        e1=e1.normal()
        for i in l:
            e2=self.vertices[i]-m
            e2=e2-(e1*e2)*e1
            if e2.length()>1e-6:
                break
        e2=e2.normal()
        n=e1.cross(e2)
        return e1,e2,n
    def convexSort(self,l):
        if len(l)<2:
            return l
        m=self.meanPoint(l)
        e1,e2,normal=self.planeBasis(l)
        ll=map(lambda i,m=m,e1=e1,e2=e2,v=self.vertices:(atan2(e1*(v[i]-m),e2*(v[i]-m)),i),l)
        ll.sort()
        return map(lambda x:x[1],ll)

    def meanPoint(self,l):
        v=Vector(0.0,0.0,0.0)
        for i in l:
            v=v+self.vertices[i]
        v=v*(1.0/len(l))
        return v

    def clip(self,n,r):
        n=(1.0/n.length())*n
        l=self.findclip(n,r)
        if len(l)==0:
            return
        p=self.planes
        vdic={}
        self.planes=[]
        newplane=[]
        for i in range(len(p)):
            plane=p[i]
            cutplane=[]
            for j in range(-1,len(plane)-1):
                if plane[j] not in l:
                    cutplane.append(plane[j])
                    if plane[j+1] not in l:
                        continue
                if plane[j] in l and plane[j+1] in l:
                    continue
                key=min(plane[j],plane[j+1]),max(plane[j],plane[j+1])
                if vdic.has_key(key):
                    cutplane.append(vdic[key])
                else:
                    a=self.vertices[plane[j]]
                    b=self.vertices[plane[j+1]]
                    v=b-a
                    if abs(n*v)<1e-5:
                        if plane[j] not in l:
                            cutplane.append(plane[j])
                        else:
                            cutplane.append(plane[j+1])
                    else:
                        x=a+(n*(r-a)/(n*v))*v
                        I=len(self.vertices)
                        vdic[key]=I
                        self.vertices.append(x)
                        cutplane.append(I)
                        newplane.append(I)
            if len(cutplane)>2:
                self.planes.append(cutplane)
        if len(newplane)>2:
            newplane=self.convexSort(newplane)
            self.planes.append(newplane)

        self.removeVertices(l)
        self.removeDegenerateSegments()
        
    def cube(self,a=1.0):
        d=len(self.vertices)
        self.vertices.append(Vector(-a,-a,-a))
        self.vertices.append(Vector(+a,-a,-a))
        self.vertices.append(Vector(+a,+a,-a))
        self.vertices.append(Vector(-a,+a,-a))
        self.vertices.append(Vector(-a,+a,+a))
        self.vertices.append(Vector(+a,+a,+a))
        self.vertices.append(Vector(+a,-a,+a))
        self.vertices.append(Vector(-a,-a,+a))
        self.planes.append([d+0,d+1,d+2,d+3])
        self.planes.append([d+2,d+3,d+4,d+5])
        self.planes.append([d+4,d+5,d+6,d+7])
        self.planes.append([d+0,d+1,d+6,d+7])
        self.planes.append([d+1,d+2,d+5,d+6])
        self.planes.append([d+0,d+3,d+4,d+7])

    def cell(self,cell):
        f=1.0
        d=len(self.vertices)
        self.vertices.append(cell[0]*(-f)+cell[1]*(-f)+cell[2]*(-f))
        self.vertices.append(cell[0]*(+f)+cell[1]*(-f)+cell[2]*(-f))
        self.vertices.append(cell[0]*(+f)+cell[1]*(+f)+cell[2]*(-f))
        self.vertices.append(cell[0]*(-f)+cell[1]*(+f)+cell[2]*(-f))
        self.vertices.append(cell[0]*(-f)+cell[1]*(+f)+cell[2]*(+f))
        self.vertices.append(cell[0]*(+f)+cell[1]*(+f)+cell[2]*(+f))
        self.vertices.append(cell[0]*(+f)+cell[1]*(-f)+cell[2]*(+f))
        self.vertices.append(cell[0]*(-f)+cell[1]*(-f)+cell[2]*(+f))
        self.planes.append([d+0,d+1,d+2,d+3])
        self.planes.append([d+2,d+3,d+4,d+5])
        self.planes.append([d+4,d+5,d+6,d+7])
        self.planes.append([d+0,d+1,d+6,d+7])
        self.planes.append([d+1,d+2,d+5,d+6])
        self.planes.append([d+0,d+3,d+4,d+7])

    def samePlane(self,p1,p2):
        if len(p1)<3:
            return False
        if len(p2)<3:
            return False
        e1,e2,normal1=self.planeBasis(p1)
        e1,e2,normal2=self.planeBasis(p2)
        if normal1.length()!=1:
            return False
        if normal2.length()!=1:
            return False
        if normal1.cross(normal2).length()<1e-5:
            if abs(normal1*self.vertices[p1[0]]-normal1*self.vertices[p2[0]])<1e-8:
                return True
        return False

    def identifyPlanesToMerge(self):
        p=self.planes
        merge=[]
        processed=set()
        for i in range(len(p)):            
            if i in processed:
                continue
            m=[i]
            processed.add(i)     
            for j in range(i+1,len(p)):
                if j in processed:
                    continue            
                if self.samePlane(self.planes[i],self.planes[j]):
                    m.append(j)
                    processed.add(j)
            merge.append(m)
        return merge

    def writeVRML(self,f,closeflag=0):
        if type(f)==type(""):
            f=open(f,"w")
            closeflag=1
        f.write("""#VRML V1.0 ascii

    Separator {
      Coordinate3 {
        point [
    """)
        for v in self.vertices:
            f.write("      %10.6f %10.6f %10.6f,\n"%(v[0],v[1],v[2]))
        f.write("""    ]
      }
      IndexedFaceSet {
        coordIndex [
    """)
        for l in self.planes:
            f.write("      %s,%d,-1,\n"%(join(map(str,l),","),l[0]))
        f.write("""
        ]
      }
    }
    """)
        if closeflag:
            f.close()

    def paint(self,p,radius,material):
        for v in self.vertices:
            p.sphere(v,radius,material)
        for l in self.planes:
            for i in range(-1,len(l)-1):
                a=l[i]
                b=l[i+1]
                p.cylinder(self.vertices[a],self.vertices[b],radius,material)


def createBrillouinZone(basis,scale=1.0):
    shape=ConvexShape()
    b=basis
    b[0]=scale*b[0]
    b[1]=scale*b[1]
    b[2]=scale*b[2]
    for i in (-1,0,1):
        for j in (-1,0,1):
            for k in (-1,0,1):
                if i==0 and j==0 and k==0:
                    continue
                v=(b[0]*float(i)+b[1]*float(j)+b[2]*float(k))*0.5
                shape.clip(v,v)
    return shape
