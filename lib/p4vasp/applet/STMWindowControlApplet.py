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

from __future__ import generators
import gtk
import gobject
from p4vasp import *
from p4vasp.store import *
from p4vasp.applet.Applet import *
import p4vasp.applet.STMWindowApplet
import cp4vasp

class STMWindowControlApplet(Applet):
    menupath=["Electronic","STM Control"]
    def __init__(self):
        Applet.__init__(self)
        self.gladefile="stmcontrol.glade"
        self.gladename="applet_frame"
        self.dir=2

    def setSystem(self,s):
        self.system=s
        self.updateSystem()

    def updateSystem(self,x=None):
        s=self.system


    def applet_activated(self,rep,a):
        if  isinstance(a,p4vasp.applet.STMWindowApplet.STMWindowApplet):
            self.pin_status=a.pin_status
            self.updatePinStatusImage()
            entry=self.xml.get_widget("lo_entry")
            if entry is not None:
                entry.set_text(str(a.lo))
            entry=self.xml.get_widget("hi_entry")
            if entry is not None:
                entry.set_text(str(a.hi))
            m=self.xml.get_widget("dirmenu")
            if m is not None:
                m.set_history(a.dir)
            b=self.xml.get_widget("inversebutton")
            if b is not None:
                if a.inv != b.get_active():
                    b.set_active(a.inv)
            if a.mode:
                m=self.xml.get_widget("currentmodebutton").set_active(1)
            else:
                m=self.xml.get_widget("heightmodebutton").set_active(1)
            if a.src:
                m=self.xml.get_widget("smoothsrcbutton").set_active(1)
            else:
                m=self.xml.get_widget("rawsrcbutton").set_active(1)
            if a.interpolation:
                m=self.xml.get_widget("cubicint").set_active(1)
            else:
                m=self.xml.get_widget("linearint").set_active(1)

            sd=a.sd
            if sd is not None:
                self.csadj1.value=float(sd.n1)
                self.csadj2.value=float(sd.n2)
            self.updatemode()
#      if self.getMode()==0:
#        self.psadj.set_all(a.n,0,a.getMaxN(),1,0,0)
#      else:
#        self.psadj.set_all(a.n,0,1000,1,0,0)

    def initUI(self):
        self.xml.get_widget("toolbar1").set_style(gtk.TOOLBAR_ICONS)

        cs1=self.xml.get_widget("cell_scale1")
        cs2=self.xml.get_widget("cell_scale2")
        self.csadj1=gtk.Adjustment(1,1,20,1,0,0)
        self.csadj2=gtk.Adjustment(1,1,20,1,0,0)
        cs1.set_adjustment(self.csadj1)
        cs2.set_adjustment(self.csadj2)
        self.csadj1.connect("value-changed",self.on_cell_scale_changed)
        self.csadj2.connect("value-changed",self.on_cell_scale_changed)
        ps=self.xml.get_widget("posscale")

#    self.padj=gtk.Adjustment(0,0,100,1,0,0)
        self.psadj=ps.get_adjustment()
        self.psadj.connect("value-changed",self.on_pos_scale_changed)

        applets().notify_on_activate.append(self.applet_activated)
        self.swin()

    def getSWinApplet(self):
        return applets().getActive(p4vasp.applet.STMWindowApplet.STMWindowApplet)

    def swin(self):
        return self.getSWinApplet()
    def sd(self):
        return self.swin().sd

    def on_front_button_clicked_handler(self,*arg):
        self.swin().navigator.setFrontView()
    def on_back_button_clicked_handler(self,*arg):
        self.swin().navigator.setBackView()
    def on_left_button_clicked_handler(self,*arg):
        self.swin().navigator.setLeftView()
    def on_right_button_clicked_handler(self,*arg):
        self.swin().navigator.setRightView()
    def on_top_button_clicked_handler(self,*arg):
        self.swin().navigator.setTopView()
    def on_bottom_button_clicked_handler(self,*arg):
        self.swin().navigator.setBottomView()
    def on_home_button_clicked_handler(self,*arg):
        self.swin().navigator.setHome()
    def on_zoom_11_button_clicked_handler(self,*arg):
        self.swin().navigator.setZoom(1.0)
    def on_zoom_in_button_clicked_handler(self,*arg):
        self.swin().navigator.mulZoom(1.1)
    def on_zoom_out_button_clicked_handler(self,*arg):
        self.swin().navigator.mulZoom(1.0/1.1)
    def on_ortho_button_clicked_handler(self,*arg):
        self.swin().navigator.setPerspective(0)
    def on_persp_button_clicked_handler(self,*arg):
        self.swin().navigator.setPerspective(1)
    def on_cell_scale_changed(self,*arg):
        w=self.swin()
        sd=w.sd
        if sd is not None:
            sd.n1=int(self.csadj1.value)
            sd.n2=int(self.csadj2.value)
            w.updateOrigin()
            w.redraw()
    def on_pos_scale_changed(self,*arg):
        w=self.swin()
        val=self.psadj.value
        if self.getMode()==0:
            w.setN(int(self.psadj.value))
            x=self.psadj.value*w.getMaxPos()/w.getMaxN()
            self.xml.get_widget("pos_entry").set_text(str(x))
            w.updatePlane()
        else:
            c=w.getCharge()
            if c is not None:
                Min=c.getMinimum()
                Max=c.getMaximum()
                sigma=c.getSigma()
#        x=0.0001*sigma*self.psadj.value
                x=sigma*exp(-0.15*self.psadj.value)
                w.value=x
                self.xml.get_widget("pos_entry").set_text(str(x))
                w.updatePlane()
        self.xml.get_widget("lo_entry").set_text(str(w.minimum))
        self.xml.get_widget("hi_entry").set_text(str(w.maximum))


    def on_pos_entry_activate_handler(self,*arg):
        entry=self.xml.get_widget("pos_entry")
#    print "Pos entry"
        w=self.swin()
        if self.getMode()==0:
            w.setN(entry.get_text())
            w.updatePlane()
        else:
            w.value=float(eval(entry.get_text()))
#      print "POS",w.value
            w.updatePlane()

    def on_xtip_activate_handler(self,*arg):
        w=self.swin()
        w.dir=0
        self.dir=0
        w.updatePlane()
#    self.updateAccuracy()
    def on_ytip_activate_handler(self,*arg):
        w=self.swin()
        w.dir=1
        self.dir=1
        w.updatePlane()
#    self.updateAccuracy()
    def on_ztip_activate_handler(self,*arg):
        w=self.swin()
        w.dir=2
        self.dir=2
        w.updatePlane()
#    self.updateAccuracy()
    def on_threshold_menu_activate_handler(self,*arg):
        w=self.swin()
        w.setClamp(w.CLAMP_THRESHOLD)
    def on_cos_menu_activate_handler(self,*arg):
        w=self.swin()
        w.setClamp(w.CLAMP_COS)
    def on_atan_menu_activate_handler(self,*arg):
        w=self.swin()
        w.setClamp(w.CLAMP_ATAN)
    def on_fermi_menu_activate_handler(self,*arg):
        w=self.swin()
        w.setClamp(w.CLAMP_FERMI)
    def on_min_button_clicked_handler(self,*arg):
        w=self.swin()
        self.xml.get_widget("lo_entry").set_text(str(w.minimum))
        w.lo=w.minimum
        w.redraw()
    def on_max_button_clicked_handler(self,*arg):
        w=self.swin()
        self.xml.get_widget("hi_entry").set_text(str(w.maximum))
        w.hi=w.maximum
        w.redraw()
    def on_lo_entry_activate_handler(self,*arg):
        w=self.swin()
        x=float(eval(self.xml.get_widget("lo_entry").get_text()))
        self.xml.get_widget("lo_entry").set_text(str(x))
        w.lo=x
        w.redraw()
    def on_hi_entry_activate_handler(self,*arg):
        w=self.swin()
        x=float(eval(self.xml.get_widget("hi_entry").get_text()))
        self.xml.get_widget("hi_entry").set_text(str(x))
        w.hi=x
        w.redraw()

    def on_limit_entry_activate_handler(self,*arg):
        self.updateAccuracy()
#  def on_sv_entry_activate_handler(self,*arg):
#    self.updateAccuracy()
#  def on_sh_entry_activate_handler(self,*arg):
#    self.updateAccuracy()
    def updateAccuracy(self,*arg):
        try:
            limit=float(eval(self.xml.get_widget("limit_entry").get_text()))
            self.xml.get_widget("limit_entry").set_text(str(limit))
        except:
            msg().error("Error parsing accuracy")
            return None
        try:
            sh=float(eval(self.xml.get_widget("sh_entry").get_text()))
            self.xml.get_widget("sh_entry").set_text(str(sh))
        except:
            msg().error("Error parsing sigma-horizontal")
            return None
        try:
            sv=float(eval(self.xml.get_widget("sv_entry").get_text()))
            self.xml.get_widget("sv_entry").set_text(str(sv))
        except:
            msg().error("Error parsing sigma-vertical")
            return None
        w=self.swin()
        if (w.structure is not None) and (w.charge is not None):
            lx=w.structure.basis[0].length()
            ly=w.structure.basis[1].length()
            lz=w.structure.basis[2].length()
            nx=w.charge.nx
            ny=w.charge.ny
            nz=w.charge.nz
            fx= lx*lx/(nx*nx*2.0)
            fy= ly*ly/(ny*ny*2.0)
            fz= lz*lz/(nz*nz*2.0)
            try:
                svf=-sv*sv*log(limit*sv*sqrt(2*pi))
            except:
                svf=0
            try:
                shf=-sh*sh*log(limit*sh*sqrt(2*pi))
            except:
                shf=0
            if self.dir==0:
                n1=int(sqrt(svf/fx)+0.5)
                n2=int(sqrt(shf/fy)+0.5)
                n3=int(sqrt(shf/fz)+0.5)
            elif self.dir==1:
                n1=int(sqrt(shf/fx)+0.5)
                n2=int(sqrt(svf/fy)+0.5)
                n3=int(sqrt(shf/fz)+0.5)
            else:
                n1=int(sqrt(shf/fx)+0.5)
                n2=int(sqrt(shf/fy)+0.5)
                n3=int(sqrt(svf/fz)+0.5)
            self.xml.get_widget("n1_entry").set_text(str(n1))
            self.xml.get_widget("n2_entry").set_text(str(n2))
            self.xml.get_widget("n3_entry").set_text(str(n3))

#    if self.dir==0:



    def on_inversebutton_toggled_handler(self,*arg):
        w=self.swin()
        w.inv=self.xml.get_widget("inversebutton").get_active()
        w.redraw()

    def getMode(self):
        return self.xml.get_widget("currentmodebutton").get_active()

    def updatemode(self):
        m=self.getMode()
        w=self.swin()
        if (m):
            c=w.getCharge()
            self.psadj.set_all(self.psadj.value,0,100,1,0,0)
            self.xml.get_widget("poslabel").set_text("Isos. density:")
            w.mode=1
        else:
            self.psadj.set_all(w.n,0,w.getMaxN(),1,0,0)
            self.xml.get_widget("poslabel").set_text("Tip position:")
            w.mode=0

    def on_heightmodebutton_toggled_handler(self,*arg):
        self.updatemode()
        self.swin().updatePlane()
    def on_currentmodebutton_toggled_handler(self,*arg):
        self.updatemode()
        self.swin().updatePlane()

    def on_rawsrcbutton_toggled_handler(self,*arg):
        w=self.swin()
        w.src=0
        w.updatePlane()
    def on_smoothsrcbutton_toggled_handler(self,*arg):
        w=self.swin()
        w.src=1
        w.updatePlane()
    def on_linearint_toggled_handler(self,*arg):
        w=self.swin()
        w.interpolation=0
        w.updatePlane()
    def on_cubicint_toggled_handler(self,*arg):
        w=self.swin()
        w.interpolation=1
        w.updatePlane()
    def on_interpolation_entry_changed_handler(self,*arg):
        w=self.swin()
        try:
            w.postinterpolation=int(eval(self.xml.get_widget("interpolation_entry").get_text()))
        except:
            msg().error("Parse error in Postprocessing - Interpolation entry")
            msg().exception()
    def on_postsigma_entry_changed_handler(self,*arg):
        w=self.swin()
        try:
            w.postsigma=float(eval(self.xml.get_widget("postsigma_entry").get_text()))
        except:
            msg().error("Parse error in Postprocessing - sigma entry")
    def on_postn_entry_changed_handler(self,*arg):
        w=self.swin()
        try:
            w.postn=float(eval(self.xml.get_widget("postn_entry").get_text()))
        except:
            msg().error("Parse error in Postprocessing - N entry")

    def on_interpolation_entry_activate_handler(self,*arg):
        w=self.swin()
        try:
            w.postinterpolation=int(eval(self.xml.get_widget("interpolation_entry").get_text()))
            w.updatePlane()
        except:
            msg().error("Parse error in Postprocessing - Interpolation entry")
    def on_postsigma_entry_activate_handler(self,*arg):
        w=self.swin()
        try:
            w.postsigma=float(eval(self.xml.get_widget("postsigma_entry").get_text()))
            w.updatePlane()
        except:
            msg().error("Parse error in Postprocessing - sigma entry")
    def on_postn_entry_activate_handler(self,*arg):
        w=self.swin()
        try:
            w.postn=float(eval(self.xml.get_widget("postn_entry").get_text()))
            w.updatePlane()
        except:
            msg().error("Parse error in Postprocessing - N entry")



    def on_smooth_button_clicked_handler(self,*arg):
        try:
            sh=float(eval(self.xml.get_widget("sh_entry").get_text()))
            self.xml.get_widget("sh_entry").set_text(str(sh))
        except:
            msg().error("Error parsing sigma-horizontal")
            return None
        try:
            sv=float(eval(self.xml.get_widget("sv_entry").get_text()))
            self.xml.get_widget("sv_entry").set_text(str(sv))
        except:
            msg().error("Error parsing sigma-vertical")
            return None
        try:
            n1=int(eval(self.xml.get_widget("n1_entry").get_text()))
            self.xml.get_widget("n1_entry").set_text(str(n1))
        except:
            msg().error("Error parsing n1")
            return None
        try:
            n2=int(eval(self.xml.get_widget("n2_entry").get_text()))
            self.xml.get_widget("n2_entry").set_text(str(n2))
        except:
            msg().error("Error parsing n2")
            return None
        try:
            n3=int(eval(self.xml.get_widget("n3_entry").get_text()))
            self.xml.get_widget("n3_entry").set_text(str(n3))
        except:
            msg().error("Error parsing n3")
            return None

        w=self.swin()
        w.sv=sv
        w.sh=sh
        w.dir=self.dir
        w.n1=n1
        w.n2=n2
        w.n3=n3
        schedule(w.updateSmoothGen())
#    schedule(w.setSmoothPlaneNGen())
    def updateMinMax(self,w):
        wmin=w.minimum
        wmax=w.maximum
        dmm=wmax-wmin
        ds =4*w.sigma
        d=min(ds,dmm)
        Min=w.average-2*d*(w.brightness-0.5)-w.contrast*d
        Max=w.average-2*d*(w.brightness-0.5)+w.contrast*d
        Min=max(Min,wmin-0.5*dmm)
        Max=min(Max,wmax+0.5*dmm)
        self.xml.get_widget("lo_entry").set_text(str(Min))
        self.xml.get_widget("hi_entry").set_text(str(Max))
        w.lo=Min
        w.hi=Max
        w.redraw()

    def on_colorscale_value_changed_handler(self,*arg):
        s=float(self.xml.get_widget("colorscale").get_value())
        w=self.swin()
        w.contrast=s*0.01
        self.updateMinMax(w)

    def on_brightscale_value_changed_handler(self,*arg):
        s=float(self.xml.get_widget("brightscale").get_value())
        w=self.swin()
        w.brightness=s*0.01
        self.updateMinMax(w)

    def on_foto_button_clicked_handler(self,*arg):
        import os.path
        i=1
        sw=self.swin()
        while os.path.exists("p4vasp_STM_%04d.tga"%i):
            i+=1

        x=sw.win.x
        y=sw.win.y
        w=sw.win.w
        h=sw.win.h
        w1=w+(4-w%4)%4
        if w!=w1:
            sw.win.resize(x,y,w1,h)
        cp4vasp.VisCheck()
        sw.win.redraw()
        cp4vasp.VisCheck()
        cp4vasp.VisSync()
        sw.win.saveScreenshot("p4vasp_STM_%04d.tga"%i)

    def on_view_structure_button_toggled_handler(self,*argv):
        if self.xml.get_widget("view_structure_button").get_active():
            self.swin().setStructure(self.system.INITIAL_STRUCTURE)
        else:
            self.swin().setStructure(None)

    def on_structure_offset_entry_activate_handler(self,*argv):
        try:
            v=float(self.xml.get_widget("structure_offset_entry").get_text())
        except:
            msg().error("Float expected in 'Structure offset'")
        sw=self.swin()
        sw.structure_offset=v
        sw.updateOrigin()
        sw.redraw()

    def on_pin_button_clicked_handler(self,*arg):
        self.pin_status=not self.pin_status
        self.updatePinStatusImage()
        self.getSWinApplet().pin_status=self.pin_status

    def destroy(self):
        applets().notify_on_activate.remove(self.applet_activated)

#  def on_structuremenu_clicked_handler(self,*arg):
#    print "structure changed",arg

STMWindowControlApplet.store_profile=AppletProfile(STMWindowControlApplet,tagname="STMControl")
#StructureApplet.config_profile=AppletProfile(StructureApplet,tagname="Structure")
