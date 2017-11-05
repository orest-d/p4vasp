#!/usr/bin/python

#  p4vasp is a GUI-program and a library for processing outputs of the
#  Vienna Ab-inition Simulation Package (VASP)
#  (see http://cms.mpi.univie.ac.at/vasp/Welcome.html)
#
#  Copyright (C) 2005  Tomas Bucko, Orest Dubay <odubay@users.sourceforge.net>
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
#from p4vasp.graph import *
#from p4vasp.GraphCanvas import *
#from p4vasp.store import *
from p4vasp.applet.Applet import *
from p4vasp.applet.GraphWindowApplet import *
from numpy import transpose,zeros,ones,dot,array
from numpy.fft import fft
from numpy.linalg import inv
from math import *
from p4vasp.SystemPM import systemlist
import time,string
import p4vasp.Selection

inverse = inv
matrixmultiply=dot
Float=float

def give_vac(velocities):
    """calculates the velocity autocorrelation
    function
    """
    numofatoms=len((velocities[0]))
    vac=zeros(len(velocities),Float)
    for i in range(len(velocities)):
        vac_i=0
        for j in range(len(velocities[0])):
            norm1=(sum(velocities[0][j]**2))**0.5
            norm2=(sum(velocities[i][j]**2))**0.5
            if norm1>0 and norm2>0:
                vac_i+=sum(velocities[0][j]*velocities[i][j])/norm1/norm2
        vac[i]=(vac_i/numofatoms)
    vac/=vac[0]
    return vac


def savitzky_reg(data,position,dimension):
    """regresion for savitzky filter.
    """
    A=zeros((len(data),dimension),Float)
    for i in range(len(data)):
        for j in range(dimension):
            A[i][j]=i**j
    G=matrixmultiply(transpose(A),A)
    G=matrixmultiply(inverse(G),transpose(A))
    coefs=matrixmultiply(G,data)
    newdat=sum(coefs*A[position])
    return newdat

def savitzky_golay_filter(freq,nleft,nright,dimension):
    """digital filter in the time domain. window
    of dimension nleft+nright is moving along data.
    data in the window are fitted by polynom of
    dimension order.
    """
    freq_=[]
    for i in range(len(freq)):
        if i>=nleft and i<=(len(freq)-nright):
            data=freq[i-nleft:i+nright+1]
            position=nleft
        elif i<nleft and i<=(len(freq)-nright):
            data=freq[:i+nright+1]
            position=len(data)-nright
        elif i>=nleft and i>(len(freq)-nright):
            data=freq[i-nleft:]
            position=nleft
        dimension_=dimension
        if len(data)<dimension:dimension_=len(data)
        regdat=savitzky_reg(data,position,dimension_)
        freq_.append(regdat)
    return freq_

def window_function(vac,param):
    """window function for filtering
    in the frequency domain
    """
    N=len(vac)
    wf=zeros(N,Float)
    for j in range(N):
        if param==1:
            #! Barlett window
            wf[j]=(1-abs((j-0.5*N)/(0.5*N)))
        elif param==2:
            #! Hann window
            wf[j]=0.5*(1-cos(2*pi*j/N))
        elif param==3:
            #! Welchwindow
            wf[j]=(1-((j-0.5*N)/(0.5*N))**2)
    return wf


class VACApplet(GraphWindowApplet,p4vasp.Selection.SelectionListener):
    menupath=["Mechanics","VAC"]
    def __init__(self):
        self.windowfunction=0
        self.freq=[]
        self.vac=[]
        self.multi=1
        GraphWindowApplet.__init__(self)
        self.gladefile="vac.glade"
#    self.gladename="applet_frame"
        self.world_name="vac"
        self.world_names=["vac","fft","vacfft"]
        self.worlds=None
        self.showtype=0
#    self.required=["NAME"]

    def notifyAtomSelection(self, sel,origin):
        sel=p4vasp.Selection.Selection(sel).toSet()
        self.sel=sel
        l=self.xml.get_widget("selectionlabel")
#    l.set_use_markup(True)
        if l is not None:
            if len(sel):
                s=self.system
                if s is not None:
                    s=s.INITIAL_STRUCTURE
                s=sel.encode(s)
                l.set_markup("Selected:<i>%s</i>"%s)
            else:
                l.set_markup("Selected all atoms.\n<span foreground=\"blue\">"
                +"<i>Tip:</i>Use <b>Selection</b> for local VAC.</span>")

    def initUI(self):
        GraphWindowApplet.initUI(self)
        if self.worlds is None:
            self.worlds=[]
            for x in self.world_names:
                if x is None:
                    w=World()
                else:
                    w=createGraph(x)
                self.worlds.append(w)
        self.notifyAtomSelection(p4vasp.Selection.selection(),None)
    def giveVacGen(self,velocities):
        """calculates the velocity autocorrelation
        function
        """
        msg().status("Calculating VAC")
        numofatoms=len((velocities[0]))
        vac=zeros(len(velocities),Float)
        yield 1
        for i in range(len(velocities)):
            vac_i=0
            if i%10==0:
                msg().step(i,len(velocities))
                yield 1
            for j in range(len(velocities[0])):
                norm1=(sum(velocities[0][j]**2))**0.5
                norm2=(sum(velocities[i][j]**2))**0.5
                if norm1>0 and norm2>0:
                    vac_i+=sum(velocities[0][j]*velocities[i][j])/norm1/norm2
            vac[i]=(vac_i/numofatoms)
        vac/=vac[0]
        self.vac=vac
        msg().status("OK")
        msg().step(1,0)

    def updateSystem(self,x=None):
        msg().status("OK")
        pass
#    schedule(self.updateSystemGen())

    def readVacGen(self):
        self.select_atoms=self.sel.getAtoms()


#    print self.select_atoms
#    selectedatoms=string.split(self.xml.get_widget("sel_entry").get_text())
#    self.select_status=0
#    self.select_atoms=[]
#    try:
#      for i in range(len(selectedatoms)):
#        self.select_atoms.append(int(selectedatoms[i]))
#        self.select_status=1
#    except ValueError:
#      self.select_status=0
#      self.select_atoms=[]
#    #else:
#    print 'selected are:',selectedatoms


        system=self.system
        self.world[0].subtitle=""
        if len(self.sel):
            if system is not None:
                s=system.INITIAL_STRUCTURE
            st=self.sel.encode(s)
            self.world[0].subtitle="Selected atoms:%s"%st

        msg().status("VAC")
        yield 1
        if system is not None:
            name=system.current("NAME")
            if name is not None:
                self.world[0].subtitle="(%s)"%name
            t0=time.clock()
            natoms=None
            if self.multi:
                totalnumconfigs=0
                systems=systemlist()
                for s in systems:
                    cs=s.CSTRUCTURE_SEQUENCE_L
                    if cs is not None:
                        totalnumconfigs+=len(cs)
                        natoms=len(cs[0])        # number of atoms in single config

                try:
                    initconfigs=int(self.xml.get_widget("init_entry").get_text()) # configs to be skipped
                except:
                    initconfigs=0
                allcarts=zeros((totalnumconfigs-initconfigs,natoms,3),Float)

                t1=time.clock()
                indx=0
                for si in range(len(systems)):
                    ss=systems[si].CSTRUCTURE_SEQUENCE_L
                    if ss is not None:
                        msg().message('t(parsing): %f'%(t1-t0))
                        if initconfigs>(len(ss)):
                            initconfigs-=(len(ss))
                            continue

                        #if si!=0:initconfigs+=1
                        numconfigs=len(ss)  # total number of configs
                        for i in range(initconfigs,numconfigs):
                            if indx%50==0:
                                msg().status("Reading %s positions (%f s)"%(systems[si].NAME,time.clock()-t1))
                                msg().step(indx,len(allcarts))
                                yield 1
                            ss[i].setCarthesian()
                            ssi=map(array,ss[i])
                            allcarts[indx]=ssi#ss[i] #.positions
                            indx+=1
                        msg().step(0,1)
                        initconfigs=0
            else:
                s=system
                ss=s.CSTRUCTURE_SEQUENCE_L
                t1=time.clock()
                msg().message('t(parsing): %f'%(t1-t0))

                numconfigs=len(ss)  # total number of configs
                natoms=len(ss[0])        # number of atoms in single config
                try:
                    initconfigs=int(self.xml.get_widget("init_entry").get_text()) # configs to be skipped
                except:
                    initconfigs=0
                allcarts=zeros((numconfigs-initconfigs,natoms,3),Float)
                for i in range(initconfigs,numconfigs):
                    indx=i-initconfigs
                    if indx%50==0:
                        msg().status("Reading positions (%f s)"%(time.clock()-t1))
                        msg().step(indx,numconfigs-initconfigs)
                        yield 1
                    ss[i].setCarthesian()
                    allcarts[indx]=ss[i] #.positions
                msg().step(0,1)
            velocities=zeros((len(allcarts)-2,len(allcarts[0]),3),Float)
            msg().status("Calculating velocities")
            yield 1
            if len(self.select_atoms)>0:
                pattern=zeros((len(allcarts[0]),3))
                for i in self.select_atoms:
                    pattern[i]=1
            else:
                pattern=ones((len(allcarts[0]),3))
            allcarts=allcarts*pattern
            for i in range(1,len(allcarts)-1):
                velocities[i-1]=(allcarts[i+1]-allcarts[i-1]) #*pattern
                if i%100==0:
                    msg().step(i,len(allcarts)-1)
                    yield 1

            msg().step(0,1)
            t2=time.clock()
            msg().message('t(velocities): %f'%(t2-t1))
            msg().status('Calculating VAC')
            yield 1
            scheduleFirst(self.giveVacGen(velocities))  ###???????
            yield 1
            t3=time.clock()
            msg().message('t(vac):%f'%(t3-t2))
        else:
            self.vac=[]
        msg().step(0,1)
        msg().status("OK")
        self.xml.get_widget("win_lab").set_sensitive(True)
        self.xml.get_widget("winopt").set_sensitive(True)
        self.xml.get_widget("filter_button").set_sensitive(True)
        self.xml.get_widget("fft_button").set_sensitive(True)
        self.freq=[]
        self.updateGraph()

    def updateGraph(self):
        outvac=zeros((len(self.vac),2),Float)
        for i in range(len(self.vac)):
            outvac[i]=[i,self.vac[i]]

        freq=self.freq
        if len(freq):
            outf=zeros((len(freq)/2,2),Float)
            try:
                timestep=self.system.PARAMETERS["POTIM"]*1e-15
            except:
                msg().error("POTIM not known, using 1")
                l=self.xml.get_widget("selectionlabel")
                l.set_markup("<span foreground=\"red\">POTIM not known, using 1.\nResult is not correctly scaled.</span>")
                timestep=1e-15
            for i in range(len(freq)/2):
                point=i/float(len(freq))/2.997925e10/timestep
                outf[i]=[point,2/self.Wss*freq[i]*0.7]
            self.setGraphData([[outf]])
        else:
            outf=[]
        if self.showtype==0:
            self.setWorldAndData(self.worlds[0],[[outvac]])
        elif self.showtype==1:
            self.setWorldAndData(self.worlds[1],[[outf]])
        else:
            self.setWorldAndData(self.worlds[2],[[outvac],[outf]])
        self.viewAll()
        self.worlds[1][0].world_xmax=5000
        self.worlds[2][1].world_xmax=5000
        if self.canvas is not None:
            self.canvas.updateSize()
        self.update()


    def on_rectwin_activate_handler(self,*arg):
        self.windowfunction=0

    def on_barlettwin_activate_handler(self,*arg):
        self.windowfunction=1

    def on_hannwin_activate_handler(self,*arg):
        self.windowfunction=2

    def on_welchwin_activate_handler(self,*arg):
        self.windowfunction=3
    def on_show_vac_activate_handler(self,*arg):
        self.showtype=0
        self.updateGraph()
    def on_show_fft_activate_handler(self,*arg):
        self.showtype=1
        self.updateGraph()
    def on_show_vacfft_activate_handler(self,*arg):
        self.showtype=2
        self.updateGraph()

    def on_filter_button_toggled_handler(self,*arg):
        if self.xml.get_widget("wleft_entry").state==4:
            self.xml.get_widget("wleft_entry").set_sensitive(True)
            self.xml.get_widget("wright_entry").set_sensitive(True)
            self.xml.get_widget("wpolyn_entry").set_sensitive(True)
            self.xml.get_widget("wleft_lab").set_sensitive(True)
            self.xml.get_widget("wright_lab").set_sensitive(True)
            self.xml.get_widget("wpolyn_lab").set_sensitive(True)
        else:
            self.xml.get_widget("wleft_entry").set_sensitive(False)
            self.xml.get_widget("wright_entry").set_sensitive(False)
            self.xml.get_widget("wpolyn_entry").set_sensitive(False)
            self.xml.get_widget("wleft_lab").set_sensitive(False)
            self.xml.get_widget("wright_lab").set_sensitive(False)
            self.xml.get_widget("wpolyn_lab").set_sensitive(False)
    def on_multi_toggled_handler(self,*arg):
        self.multi=self.xml.get_widget("multi").get_active()

    def on_vac_button_clicked_handler(self, *arg):
        schedule(self.readVacGen())

    def on_fft_button_clicked_handler(self, *arg):
        schedule(self.fftGen())
    def fftGen(self):
        msg().status('Calculating window function')
        yield 1
        if self.windowfunction!=0:
            windowfunction=window_function(self.vac,self.windowfunction)
            vac=self.vac*windowfunction
        else: vac=self.vac*1
        self.freq=abs(fft(vac))
        yield 1
        if self.xml.get_widget("wleft_entry").state!=4:
            wleft=int(self.xml.get_widget("wleft_entry").get_text())
            wright=int(self.xml.get_widget("wright_entry").get_text())
            wpolyn=int(self.xml.get_widget("wpolyn_entry").get_text())
            scheduleFirst(self.savitzky_golay_filterGen(self.freq,wleft,wright,wpolyn))
            yield 1
        Wss=0
        for j in range(len(vac)):
            Wss+=(1-((j-0.5*len(vac))/(0.5*len(vac)))**2)
        Wss*=len(vac)
        self.Wss=Wss
        self.updateGraph()
        msg().status("OK")
    def savitzky_golay_filterGen(self,freq,nleft,nright,dimension):
        """digital filter in the time domain. window
        of dimension nleft+nright is moving along data.
        data in the window are fitted by polynom of
        dimension order.
        """
        if dimension>0:
            freq_=[]
            msg().status("Savitzky-Golay filtering")
            yield 1
            for i in range(len(freq)):
                msg().step(i,len(freq))
                yield 1
                if i>=nleft and i<=(len(freq)-nright):
                    data=freq[i-nleft:i+nright+1]
                    position=nleft
                elif i<nleft and i<=(len(freq)-nright):
                    data=freq[:i+nright+1]
                    position=len(data)-nright
                elif i>=nleft and i>(len(freq)-nright):
                    data=freq[i-nleft:]
                    position=nleft
                dimension_=dimension
                if len(data)<dimension:dimension_=len(data)
                regdat=savitzky_reg(data,position,dimension_)
                freq_.append(regdat)
            msg().step(i,len(freq))
            msg().step(0,1)
            self.freq=freq_
        else:
            self.freq=freq
#      msg().error("Invalid degree of the fitting polynomial.\nPolynomial must be >=1 !")


VACApplet.store_profile=AppletProfile(VACApplet,tagname="VAC")
