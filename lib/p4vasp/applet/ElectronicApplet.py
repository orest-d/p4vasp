#!/usr/bin/python2

#  p4vasp is a GUI-program and a library for processing outputs of the
#  Vienna Ab-inition Simulation Package (VASP)
#  (see http://cms.mpi.univie.ac.at/vasp/Welcome.html)
#
#  Copyright (C) 2003-2012  Orest Dubay <dubay@danubiananotech.com>
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

from __future__ import generators
from p4vasp import *
from p4vasp.applet.Applet import *
from p4vasp.applet.GraphWindowApplet import *
from p4vasp.Selection import Selection
from p4vasp.setutils import *
from p4vasp.graph import *
import time

import gtk


orbitals  =map(intern,["s","px","py","pz","dxy","dyz","dxz","dz2","dx2",
                       "f1","f2","f3","f4","f5","f6","f7"])
orbitals_p=map(intern,["px","py","pz"])
orbitals_d=map(intern,["dxy","dyz","dxz","dz2","dx2"])
orbitals_f=map(intern,["f1","f2","f3","f4","f5","f6","f7"])

class Line:
    SHOW_NONE=0
    SHOW_DOS=1
    SHOW_BANDS=2
    SHOW_DOS_BANDS=3
    def __init__(self,name=None,selection="",orbital=[],spin=3,symbol=0,scale=1,symbol_size=1.0,color=1,first_band=0,last_band=-1,showmode=3):
        self.name=name
        self.selection=selection
        self.orbital=orbital
        self.spin=spin
        self.item=None
        self.scale=scale
        self.symbol=symbol
        self.symbol_size=symbol_size
        self.color=color
        self.first_band=first_band
        self.last_band=last_band
        self.showmode=showmode
        self.eigenval=None
        self.dos=None

    def clone(self):
        return Line(name=self.name,
                    selection=self.selection,
                    orbital=self.orbital[:],
                    spin=self.spin,
                    symbol=self.symbol,
                    scale=self.scale,
                    symbol_size=self.symbol_size,
                    color=self.color,
                    first_band=self.first_band,
                    last_band=self.last_band,
                    showmode=self.showmode
                    )

    def setLine(self,l):
        self.name        = l.name
        self.selection   = l.selection
        self.orbital     = l.orbital
        self.spin        = l.spin
        self.symbol      = l.symbol
        self.scale       = l.scale
        self.symbol_size = l.symbol_size
        self.color       = l.color
        self.first_band  = l.first_band
        self.last_band   = l.last_band
        self.showmode    = l.showmode

    def getName(self,system=None):
        if self.name is not None:
            if len(self.name)==0:
                return self.getAutoName(system)
            return self.name
        return self.getAutoName(system)

    def getAutoName(self,system=None):
        s=""
        if len(s):
            s+=" "
        s+=self.selection
        if self.spin==1:
            s+=" spin up"
        elif self.spin==2:
            s+=" spin down"

        if not contains_set(self.orbital,orbitals):

            o=[]
            if "s" in self.orbital:
                o.append("s")

            if contains_set(self.orbital,orbitals_p):
                o.append("p")
            else:
                for x in orbitals_p:
                    if x in self.orbital:
                        o.append(x)

            if contains_set(self.orbital,orbitals_d):
                o.append("d")
            else:
                for x in orbitals_d:
                    if x in self.orbital:
                        o.append(x)

            if contains_set(self.orbital,orbitals_f):
                o.append("f")
            else:
                for x in orbitals_f:
                    if x in self.orbital:
                        o.append(x)

            s+=" (%s)"%join(o)
        return s


    def getSelection(self,struct=None):
#    print "selection:",self.selection
        s=Selection(self.selection,struct)
        return s.getAtoms()


    def updateEigenvaluesGen(self,ea):
        msg().status("Update eigenvalues:%s"%self.getName())
        yield 1
        first_band=self.first_band
        last_band =self.last_band
        system=ea.system
        eigenval=ea.eigenval
        if eigenval is None:
            self.eigenval=[]
            return
        kpoints=ea.kpoints
        if kpoints is None:
            self.eigenval=[]
            return
        struct=ea.struct
        e=ea.e_fermi
        evspins=ea.evspins
        evbands=ea.evbands
        has_phases=0#(system.PARAMETERS["LORBIT"]==12)


        msg().status("Read projected eigenvalues")
        yield 1
        data=ea.system.PROJECTED_EIGENVALUES_L
        if data is None:
            self.eigenval=[]
            return

        msg().status("Setup projected eigenvalues")
        yield 1

        sel = self.getSelection(struct)
        orb=self.orbital[:]
        if contains_some_elements_from_set(orb,orbitals_p):
            orb.append("p")
        if contains_some_elements_from_set(orb,orbitals_d):
            orb.append("d")
        if contains_some_elements_from_set(orb,orbitals_f):
            orb.append("f")
        yield 1

        indexes=filter(lambda x:x is not None,map(data.fieldIndex,orb))

        spinrange=range(len(data))
        if len(data)>1:
            if self.spin==1:
                spinrange=[0]
            elif self.spin==2:
                spinrange=[1]
            else:
                spinrange=[0,1]

        kdiv=system.KPOINT_DIVISIONS
        msg().status("Process projected eigenvalues")
        yield 1

        kpoints_len=len(data[0])
        if first_band<0:
            first_band=0
        if first_band>=len(data[0][0]):
            first_band=len(data[0][0])-1
        if last_band<0:
            last_band=len(data[0][0])-1
        if last_band>=len(data[0][0]):
            last_band=len(data[0][0])-1

        d=[]
        yield 1
        begin_time=time.time()
        pstep=1
        ptotal=len(spinrange)*(last_band-first_band+1)
        for spin in spinrange:
            evspin=min(spin,evspins-1)
            for band in range(first_band,last_band+1):
                db=[]
                if has_phases:
                    for k in range(kpoints_len):
                        w=0.0
                        sdata=data[spin][k][band]
                        for ion in sel:
                            for o in indexes:
                                w+=(sdata[ion][o]**2)
                        db.append((kpoints[k],eigenval[band+spin*evbands][k][1],w))
                else:
                    for k in range(kpoints_len):
                        w=0.0
                        sdata=data[spin][k][band]
                        for ion in sel:
                            for o in indexes:
                                w+=abs(sdata[ion][o])
                        db.append((kpoints[k],eigenval[band+spin*evbands][k][1],w))

                d.append(db)
                deltatime=int(time.time()-begin_time)
                totaltime=int(deltatime*ptotal/float(pstep))
                msg().status("Processing spin %d/%d, band %d/%d, step %d/%d, time %d/%d s"%
                (spin+1,len(spinrange),band-first_band+1,last_band-first_band+1,pstep,ptotal,
                deltatime,totaltime))
                msg().step(pstep,ptotal)
                pstep+=1
                yield 1
        msg().step(0,1)
        msg().status("OK")
        self.eigenval=d

    def updateDosGen(self,ea):
        msg().status("Reading partial DOS")
        yield 1
        system=ea.system
        data=system.PARTIAL_DOS_L
        struct=ea.struct
        e=ea.e_fermi

        if data is None:
            self.dos=[]
            return
        msg().status("Prepare.")
        yield 1
        sel = self.getSelection(struct)
        d=[]
        l=len(data[0][0])
        orb=self.orbital[:]
        if contains_some_elements_from_set(orb,orbitals_p):
            orb.append("p")
        if contains_some_elements_from_set(orb,orbitals_d):
            orb.append("d")
        if contains_some_elements_from_set(orb,orbitals_f):
            orb.append("f")

        indexes=filter(lambda x:x is not None,map(data.fieldIndex,orb))

        msg().status("Prepare..")
        yield 1
        spinrange=range(len(data[0]))
        if len(data[0])>1:
            if self.spin==1:
                spinrange=[0]
            elif self.spin==2:
                if len(data[0])==4:
                    spinrange=[3]
                else:
                    spinrange=[1]
            else:
                if len(data[0])==4:
                    spinrange=[0,3]
                else:
                    spinrange=[0,1]

        msg().status("Prepare...")
        yield 1

        ptotal=len(sel)*len(spinrange)*len(indexes)*l
        pstep=0
        for i in range(l):
            val=0.0
            for ion in sel:
                for spin in spinrange:
                    for j in indexes:
                        val+=abs(data[ion][spin][i][j])
                        pstep+=1
                        if (pstep%100)==0:
                            msg().status("Processing DOS step %d/%d"%(pstep,ptotal))
                            msg().step(pstep,ptotal)
                            yield 1
            d.append((data[0][0][i][0]-e,self.scale*val))
        self.dos=d
        msg().step(0,1)
        msg().status("OK")

class ElectronicApplet(GraphWindowApplet):
    menupath=["Electronic","DOS + bands"]
    SHOW_DOS_X     =0
    SHOW_DOS_Y     =1
    SHOW_BANDS     =2
    SHOW_DOS_BANDS =3
    SHOW_IPR       =4
    SHOW_DOS_IPR   =5
    DOSGIL         =[   0,   0,None,   1,None,0]
    BANDSGIL       =[None,None,   0,   0,None,None]
    IPRGIL         =[None,None,None,None,   0,1]

    def __init__(self):
        GraphWindowApplet.__init__(self)
#    self.gladefile="graphapplet.glade"
#    self.gladename="applet_frame"
        self.world_name="dos"
        self.world_names=["dos_x","dos_y","bands","dosbands","inverse_participation_ratio","dos_ipr"]
        self.worlds=None
        self.required=["NAME"]
        self.showtype=self.SHOW_DOS_Y
        self.total_dos=None
        self.eigenval=None
        self.struct=None
        self.ipr=None
#    self.lines=[Line(orbital=orbitals,selection="C",first_band=300,last_band=310,showmode=Line.SHOW_DOS)]
#    self.lines=[Line(orbital=orbitals,selection="1",showmode=Line.SHOW_DOS_BANDS)]
        self.lines=[]
        self.klines=[]
        self.show_DOS=True
        self.view_all=True

    def initUI(self):
        GraphWindowApplet.initUI(self)
        mitem=gtk.MenuItem("Show")
        menu=gtk.Menu()
        mitem.set_submenu(menu)

        item=gtk.CheckMenuItem("show DOS")
        menu.append(item)
        item.show()
        item.set_active(self.show_DOS)
        item.connect("toggled",self.show_DOS_handler_)


        item=gtk.MenuItem("DOS")
        menu.append(item)
        item.show()
        item.connect("activate",self.setshowtype_handler_,self.SHOW_DOS_Y)

        item=gtk.MenuItem("DOS (X-axis)")
        menu.append(item)
        item.show()
        item.connect("activate",self.setshowtype_handler_,self.SHOW_DOS_X)

        item=gtk.MenuItem("Bands")
        menu.append(item)
        item.show()
        item.connect("activate",self.setshowtype_handler_,self.SHOW_BANDS)

        item=gtk.MenuItem("DOS and Bands")
        menu.append(item)
        item.show()
        item.connect("activate",self.setshowtype_handler_,self.SHOW_DOS_BANDS)

        item=gtk.MenuItem("Inverse Participation Ratio")
        menu.append(item)
        item.show()
        item.connect("activate",self.setshowtype_handler_,self.SHOW_IPR)

        item=gtk.MenuItem("DOS + Inverse PR")
        menu.append(item)
        item.show()
        item.connect("activate",self.setshowtype_handler_,self.SHOW_DOS_IPR)

        self.menubar.append(mitem)
        mitem.show()
        if self.worlds is None:
            self.worlds=[]
            for x in self.world_names:
                if x is None:
                    w=World()
                else:
                    w=createGraph(x)
                self.worlds.append(w)

    def setshowtype_handler_(self,w,t):
        self.setShowType(t)

    def setShowType(self,t):
        self.view_all=True
        self.showtype=t
        self.updateShow()

    def updateKpointsGen(self):
        msg().status("Update k-points")
        yield 1
        system=self.system
        kpoints=system.KPOINT_LIST
        kdiv=system.KPOINT_DIVISIONS
        struct=system.INITIAL_STRUCTURE
        struct.updateRecipBasis()
        b1=struct.rbasis[0]
        b2=struct.rbasis[1]
        b3=struct.rbasis[2]

        self.klines=[]
        if kpoints is None:
            msg().status("No k-points available")
            yield 1
            self.kpoints=None
        else:
            msg().status("Scanning k-points")
            yield 1
            kp=[0.0]
            kpoints_track=0.0
            for k in range(1,len(kpoints)):
                if k%10==0:
                    msg().step(k,len(kpoints))
                    yield 1
                if (kdiv is None ) or (k%kdiv):
                    kk=kpoints[k-1]
                    k0=kk[0]*b1+kk[1]*b2+kk[2]*b3
                    kk=kpoints[k]
                    k1=kk[0]*b1+kk[1]*b2+kk[2]*b3

                    dx=k0[0]-k1[0]
                    dy=k0[1]-k1[1]
                    dz=k0[2]-k1[2]
                    kpoints_track+=sqrt(dx*dx+dy*dy+dz*dz)
                if kdiv is not None:
                    if k%kdiv ==0:
                        self.klines.append(kpoints_track)

                kp.append(kpoints_track)
            self.kpoints=kp
            msg().status("OK")
            msg().step(0,1)

    def updateEigenvaluesGen(self):
        msg().status("Update eigenvalues")
        yield 1


        ev=self.system.EIGENVALUES_L
        e=self.e_fermi

        if ev is not None:
            msg().status("Scanning eigenvalues.")
            yield 1
            ly=len(ev[0][0])
            lx=len(ev[0])
            self.evkpoints =lx
            self.evbands   =ly
            self.evspins   =len(ev)
            data=[]
            for i in range(len(ev)):
                for j in range(ly):
                    msg().step(i*ly+j,len(ev)*ly)
                    yield 1
                    data.append([(self.kpoints[0],ev[i][0][j][0]-e)])
            msg().status("Scanning eigenvalues..")
            yield 1
            for i in range(len(ev)):
                for j in range(ly):
                    msg().step(i*ly+j,len(ev)*ly)
                    yield 1
                    for k in range(1,lx):
                        data[j+i*ly].append((self.kpoints[k],ev[i][k][j][0]-e))
            msg().step(len(ev),len(ev))
            yield 1
            self.eigenval=data

            yield 1
            msg().step(0,1)
            msg().status("Eigenvalues updated")

    def updateDataGen(self):
        msg().status("Update data")
        system=self.system
        yield 1
        if system is not None:
            self.e_fermi=system.E_FERMI
            if self.e_fermi is None:
                self.e_fermi=0.0
                msg().status("Fermi energy not available, using 0.0")
                yield 1
            if system is not None:
                t=self.showtype
                if self.struct is None:
                    msg().status("Read structure")
                    yield 1
                    self.struct=system.INITIAL_STRUCTURE
                    msg().status("OK")
                    yield 1
                if t in [self.SHOW_DOS_X,self.SHOW_DOS_Y,self.SHOW_DOS_BANDS]:
                    if self.total_dos is None:
                        self.view_all=True
                        msg().status("Update DOS data")
                        yield 1
                        tdos=system.TOTAL_DOS
                        e=self.e_fermi
                        if tdos is not None:
                            if len(tdos)==2:
                                self.total_dos=[map(lambda x,e=e:(x[0]-e,x[1]),tdos[0]),
                                map(lambda x,e=e:(x[0]-e,-x[1]),tdos[1])]
                            else:
                                self.total_dos=[map(lambda x,e=e:(x[0]-e,x[1]),tdos[0])]

                        msg().status("OK")
                        yield 1
                    for l in self.lines:
                        if l.dos is None:
                            if l.showmode in [Line.SHOW_DOS,Line.SHOW_DOS_BANDS]:
                                scheduleFirst(l.updateDosGen(self))
                                yield 1
                if t in [self.SHOW_IPR,self.SHOW_DOS_IPR]:
                    if self.ipr is None:
                        self.ipr=[]
                        self.view_all=True
                        msg().status("Update IPR data")
                        yield 1
                        occ=system.PROJECTED_EIGENVALUES_L
                        energies=system.PROJECTED_EIGENVALUES_ENERGIES_L
                        if energies==None:
                            msg().error("Energies for projected eigenvalues are missing.")
                            return
                        e=self.e_fermi
                        nions=len(occ[0][0][0])
                        for spin in range(len(occ)):
                            for k in range(len(occ[spin])):
                                for band in range(len(occ[spin][k])):
                                    if 0==band%20:
                                        msg().status("Update IPR data (k-point %d/%d, band %d/%d)"%(k+1,len(occ[spin]),band,len(occ[spin][k])))
                                        msg().step(k*len(occ[spin][k])+band,len(occ[spin])*len(occ[spin][k]))
                                        yield 1
                                    sum1=0.0
                                    sum2=0.0
                                    for ion in range(len(occ[spin][k][band])):
                                        x=sum(occ[spin][k][band][ion])
                                        sum1+=x
                                        sum2+=x*x
                                    if sum1>0 and sum2>0:
                                        res=sum1*sum1/sum2/nions
                                        self.ipr.append((energies[spin][k][band][0]-e,1/res))

                        msg().status("OK")
                        yield 1
                if t in [self.SHOW_BANDS,self.SHOW_DOS_BANDS]:
                    if self.kpoints is None:
                        self.view_all=True
                        scheduleFirst(self.updateKpointsGen())
                        yield 1
                    if self.eigenval is None:
                        self.view_all=True
                        scheduleFirst(self.updateEigenvaluesGen())
                        yield 1
                    for l in self.lines:
                        if l.eigenval is None:
                            if l.showmode in [Line.SHOW_BANDS,Line.SHOW_DOS_BANDS]:
                                scheduleFirst(l.updateEigenvaluesGen(self))
                                yield 1
        msg().status("OK")



    def updateSystem(self,x=None):
        system=self.system
        self.total_dos=None
        self.eigenval=None
        self.kpoints=None
        self.struct=None
        self.ipr=None
        self.view_all=True
        for l in self.lines:
            l.eigenval = None
            l.dos=None
        self.updateShow()
        schedule(self.viewAllGen())

    def viewAllGen(self):
        yield 1
        self.viewAll()

    def updateKlines(self,g):
        l=[]
        x1=g.world_xmin
        x2=g.world_xmax
        y1=g.world_ymin
        y2=g.world_ymax
        for x in self.klines:
            if x>x1 and x<x2:
                l.append(GraphLine(x,y1,x,y2,7))
        g.graph_lines=l

    def updateShowGen(self):
        msg().status("Update")
        yield 1
        t=self.showtype
        w=self.worlds[t]
        w[0].subtitle=""
        if self.system is not None:
            name=self.system.NAME
            if name is not None:
                w[0].subtitle=str(name)
        for i in range(len(w)):
            w[i].data=[]
        scheduleFirst(self.updateDataGen())
        yield 1
        self.setWorld(w)
        dos=[]
        bands=[]
        dosgi  =self.DOSGIL[t]
        bandsgi=self.BANDSGIL[t]
        iprgi  =self.IPRGIL[t]

        if self.show_DOS:
            if self.total_dos is not None:
                if len(self.total_dos)==2:
                    dos.append(self.total_dos[0])
                    dos.append(self.total_dos[1])
                    if dosgi is not None:
                        s=Set()
                        s.data=self.total_dos[0]
                        w[dosgi].append(s)
                        s=Set()
                        s.data=self.total_dos[1]
                        w[dosgi].append(s)
                else:
                    dos.append(self.total_dos[0])
                    if dosgi is not None:
                        s=Set()
                        s.data=self.total_dos[0]
                        w[dosgi].append(s)


        if self.eigenval is not None:
            bands.extend(self.eigenval)
            if bandsgi is not None:
                for i in range(len(self.eigenval)):
                    s=Set()
                    s.data=self.eigenval[i]
                    w[bandsgi].append(s)

        for i in range(len(self.lines)):
            l=self.lines[i]
            if l.dos is not None:
                dos.append(l.dos)
                if dosgi is not None:
                    s=Set()
                    s.data=l.dos
                    if l.color==-1:
                        s.line_color=2+i%13
                    else:
                        s.line_color=l.color
                    if l.getName()=="-":
                        s.legend=""
                    else:
                        s.legend=l.getName()
                    w[dosgi].append(s)
            if l.eigenval is not None:
                bands.extend(l.eigenval)
                if bandsgi is not None:
                    for j in range(len(l.eigenval)):
                        s=Set()
                        s.type="xysize"
                        s.data=map(lambda x,s=l.symbol_size:(x[0],x[1],s*x[2]),l.eigenval[j])
                        s.line=0
                        s.symbol=l.symbol
                        if l.symbol==-1:
                            s.symbol=1+i%10
                        else:
                            s.symbol=l.symbol
                        if l.color==-1:
                            s.symbol_fill_color=2+i%13
                        else:
                            s.symbol_fill_color=l.color
                        w[bandsgi].append(s)
        if bandsgi is not None:
            self.updateKlines(w[bandsgi])

        if t in [self.SHOW_DOS_X,self.SHOW_DOS_BANDS]:
            g=w[dosgi]
            for i in range(len(g)):
                g[i].data = map(lambda x:(x[1],x[0]),g[i].data)
        if t in [self.SHOW_IPR,self.SHOW_DOS_IPR]:
            if self.ipr is not None:
                s=Set()
                s.symbol=1
                s.symbol_size=0.5
                s.symbol_color=1
                s.symbol_fill_color=0
                s.symbol_linewidth=1.0
                s.line=0
                s.line_width=1.0
                s.line_color=1

                s.data=self.ipr
                w[iprgi].append(s)

        self.setWorldAndData(w,None)

        if self.view_all:
            self.viewAll()
            self.view_all=False
        if self.canvas is not None:
            if self.canvas.area_drawable() is not None:
                self.canvas.updateSize()
                self.canvas.updateGraph()

        msg().step(0,1)
        msg().status("OK")

    def updateShow(self):
        schedule(self.updateShowGen())

    def update(self):
        if self.canvas is not None:
            self.canvas.updateGraph()

    def zoomAtPoint(self,x,y,factor):
        gi=self.canvas.world.identifyGraphIndex(x,y)
#    print "zoomAtPoint",x,y,f,gi
        w=self.canvas.world
        if gi is not None:
            g=w[gi]
            x=g.screen2worldX(x)
            y=g.screen2worldY(y)
#      x=(g.world_xmin+g.world_xmax)/2
#      y=(g.world_ymin+g.world_ymax)/2
            xmin=x+(g.world_xmin-x)*factor
            xmax=x+(g.world_xmax-x)*factor
            ymin=y+(g.world_ymin-y)*factor
            ymax=y+(g.world_ymax-y)*factor
            self.adjustGraphs(g,xmin,xmax,ymin,ymax)
        if len(w):
            self.updateKlines(w[0])
            self.canvas.updateGraph()
    def adjustGraphs(self,g,xmin,xmax,ymin,ymax):
        if self.showtype in [self.SHOW_DOS_IPR]:
            g.world_ymin=ymin
            g.world_ymax=ymax
            for g in self.canvas.world:
                g.world_xmin=xmin
                g.world_xmax=xmax
        else:
            g.world_xmin=xmin
            g.world_xmax=xmax
            for g in self.canvas.world:
                g.world_ymin=ymin
                g.world_ymax=ymax

#    self.canvas.zoomAtPoint(x,y,factor)
    def zoomTo(self,x1,y1,x2,y2):
        w=self.canvas.world
        gi=w.identifyGraphIndex(x1,y1)
#    print "zoomTo",x1,y1,x2,y2,gi
        if gi is not None:
            g=self.canvas.world[gi]
            x1=g.screen2worldX(x1)
            y1=g.screen2worldY(y1)
            x2=g.screen2worldX(x2)
            y2=g.screen2worldY(y2)
            xmin=min(x1,x2)
            xmax=max(x1,x2)
            ymin=min(y1,y2)
            ymax=max(y1,y2)
            self.adjustGraphs(g,xmin,xmax,ymin,ymax)
        if len(w):
            self.updateKlines(w[0])
            self.canvas.updateGraph()

    def move(self,x1,y1,x2,y2):
        w=self.canvas.world
        gi=w.identifyGraphIndex(x1,y1)
        if gi is not None:
            g=self.canvas.world[gi]
            x1=g.screen2worldX(x1)
            y1=g.screen2worldY(y1)
            x2=g.screen2worldX(x2)
            y2=g.screen2worldY(y2)
            dx=x2-x1
            dy=y2-y1
            xmin=g.world_xmin-dx
            xmax=g.world_xmax-dx
            ymin=g.world_ymin-dy
            ymax=g.world_ymax-dy
            self.adjustGraphs(g,xmin,xmax,ymin,ymax)
        if len(w):
            self.updateKlines(w[0])
            self.canvas.updateGraph()

    def viewAll(self):
        if self.canvas is not None:
            self.canvas.viewAll()
            w=self.canvas.world
            if len(w)>1:
                if self.showtype in [self.SHOW_DOS_IPR]:
                    xmin=min(w[0].world_xmin,w[1].world_xmin)
                    xmax=max(w[0].world_xmax,w[1].world_xmax)
                    for g in self.canvas.world:
                        g.world_xmin=xmin
                        g.world_xmax=xmax
                else:
                    ymin=min(w[0].world_ymin,w[1].world_ymin)
                    ymax=max(w[0].world_ymax,w[1].world_ymax)
                    for g in self.canvas.world:
                        g.world_ymin=ymin
                        g.world_ymax=ymax
            if len(w):
                self.updateKlines(w[0])
                self.canvas.updateGraph()

    def viewAllX(self):
        if self.canvas is not None:
            self.canvas.viewAllX()
            w=self.canvas.world
            if len(w):
                self.updateKlines(w[0])
                self.canvas.updateGraph()

    def viewAllY(self):
        if self.canvas is not None:
            self.canvas.viewAllY()
            w=self.canvas.world
            if len(w)>1:
                ymin=min(w[0].world_ymin,w[1].world_ymin)
                ymax=max(w[0].world_ymax,w[1].world_ymax)
                g=self.canvas.world[0]
                g.world_ymin=ymin
                g.world_ymax=ymax
                self.updateKlines(g)
                g=self.canvas.world[1]
                g.world_ymin=ymin
                g.world_ymax=ymax
            if len(w):
                self.updateKlines(w[0])
                self.canvas.updateGraph()

    def show_DOS_handler_(self,w):
        self.show_DOS=w.active
        self.updateShow()

ElectronicApplet.store_profile=AppletProfile(ElectronicApplet,tagname="Electronic",
attr_setup="""int type showtype
int dos show_DOS
lines
"""
)

lineprofile=Profile(Line,tagname="line",disable_attr=1,attr_setup='''
   string     name
   string     selection
   stringlist orbital
   int        spin
   float      scale
   int        symbol
   float      symbolsize symbol_size
   int        firstband first_band
   int        lastband  last_band
   int        showmode
   item
  ''')
ElectronicApplet.store_profile.addClass(lineprofile)

#DOSApplet.config_profile=AppletProfile(TDOSApplet,tagname="TDOS")
