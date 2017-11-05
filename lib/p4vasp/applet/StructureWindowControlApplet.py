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
from p4vasp.graph import *
from p4vasp.store import *
from p4vasp.applet.Applet import *
import p4vasp.sellang
from p4vasp.StructureWindow import *
from p4vasp.util import getAtomtypes
import p4vasp.Selection
import p4vasp.applet.StructureWindowApplet

class SubtrSequence:
    def __init__(self,src,subtr,mul=1):
        self.src=src
        self.subtr=subtr
        self.mul=mul
    def __len__(self):
        return len(self.src.system.STRUCTURE_SEQUENCE_L)
    def __getitem__(self,key):
        l=[]
        s=self.src.system.STRUCTURE_SEQUENCE_L[key]
        sub=self.src.system[self.subtr].get()
        for i in range(len(s)):
            l.append(self.mul*(s[i]-sub[i]))
        return l

class StructureWindowControlApplet(Applet,p4vasp.Selection.SelectionListener):
    menupath=["Structure","Control"]
    def __init__(self):
        Applet.__init__(self)
        self.gladefile="swincontrol.glade"
        self.gladename="applet_frame"
        self.arrows_sequence=[]
        self.view_iso=None
        self.levelentry=None
        self.subtrentry=None
        self.subtr_density_fileselection=None
        self.charge_density_fileselection=None
        self.subtrchgcar=None
        self.chgcar=None
    def notifyAtomSelection(self, sel,origin):
        pass
##    self.atom_selection.set_text(sel.encode(self.structure))
#    sel=p4vasp.Selection.selection()
#    self.swin().removeSelectedAll()
#    for i,nx,ny,nz in sel:
#      self.swin().selectAtom(i,nx,ny,nz)

    def setSystem(self,s):
        self.system=s
        self.updateSystem()

    def updateSystem(self,x=None):
        s=self.system
        self.createMenuItems()


    def createMenuItems(self):
        omenu = self.xml.get_widget("structuremenu")
        if omenu is None:
            return None
        menu=gtk.Menu()
        omenu.set_menu(menu)
        omenu.show()
        swa=self.getSWinApplet()
        swsystem=swa.system

        if swsystem is not None:
            I=0
            if swsystem.INITIAL_STRUCTURE is not None:
                item=gtk.MenuItem("Initial positions")
                item.connect("activate",self.on_structureitem_clicked_handler,
                swa.INITIAL_SEQUENCE)
                menu.append(item)
                item.show()
                if swa.sequencetype==swa.INITIAL_SEQUENCE:
                    omenu.set_history(I)
                I+=1
            if swsystem.FINAL_STRUCTURE is not None:
                item=gtk.MenuItem("Final positions")
                item.connect("activate",self.on_structureitem_clicked_handler,
                swa.FINAL_SEQUENCE)
                menu.append(item)
                item.show()
                if swa.sequencetype==swa.FINAL_SEQUENCE:
                    omenu.set_history(I)
                I+=1
            if swsystem.PRIMITIVE_STRUCTURE is not None:
                item=gtk.MenuItem("Primitive cell")
                item.connect("activate",self.on_structureitem_clicked_handler,
                swa.PRIMITIVE_SEQUENCE)
                menu.append(item)
                item.show()
                if swa.sequencetype==swa.PRIMITIVE_SEQUENCE:
                    omenu.set_history(I)
                I+=1
            if swsystem.STRUCTURE_SEQUENCE_L is not None:
                item=gtk.MenuItem("Arbitrary Sequence")
                item.connect("activate",self.on_structureitem_clicked_handler,
                swa.UNDEFINED_SEQUENCE)
                menu.append(item)
                item.show()
                if swa.sequencetype==swa.UNDEFINED_SEQUENCE:
                    omenu.set_history(I)
                I+=1
            if swsystem.RELAXATION_SEQUENCE_L is not None:
                item=gtk.MenuItem("Relaxation")
                item.connect("activate",self.on_structureitem_clicked_handler,
                swa.RELAXATION_SEQUENCE)
                menu.append(item)
                item.show()
                if swa.sequencetype==swa.RELAXATION_SEQUENCE:
                    omenu.set_history(I)
                I+=1
            if swsystem.MD_SEQUENCE_L is not None:
                item=gtk.MenuItem("Molecular Dynamics")
                item.connect("activate",self.on_structureitem_clicked_handler,
                swa.MD_SEQUENCE)
                menu.append(item)
                item.show()
                if swa.sequencetype==swa.MD_SEQUENCE:
                    omenu.set_history(I)
                I+=1
#      seq=swsystem.current("STRUCTURE_SEQUENCE_L")
#      if seq is not None:
#        for i in range(len(seq)):
#          item=gtk.MenuItem("step %3d"%(i+1))
#          item.connect("activate",self.on_structureitem_clicked_handler,i)
#          menu.append(item)
#          item.show()

        amenu = self.xml.get_widget("arrowstypemenu")
        if amenu is not None:
            menu=gtk.Menu()
            amenu.set_menu(menu)
            amenu.show()

            item=gtk.MenuItem("None")
            item.connect("activate",self.on_arrows_clicked_handler,swa.NONE_ARROWS)
            menu.append(item)
            item.show()
            I=0
            if swa.arrowstype==swa.NONE_ARROWS:
                amenu.set_history(I)
            I+=1

            if swsystem is not None:
                if swsystem.FORCES_SEQUENCE_L is not None:
                    item=gtk.MenuItem("Forces")
                    item.connect("activate",self.on_arrows_clicked_handler,swa.FORCES_ARROWS)
                    menu.append(item)
                    item.show()
                    if swa.arrowstype==swa.FORCES_ARROWS:
                        amenu.set_history(I)
                    I+=1
                if swsystem.INITIAL_STRUCTURE is not None:
                    item=gtk.MenuItem("Step - Initial")
                    item.connect("activate",self.on_arrows_clicked_handler,swa.DIFF_INITIAL_ARROWS)
                    menu.append(item)
                    item.show()
                    if swa.arrowstype==swa.DIFF_INITIAL_ARROWS:
                        amenu.set_history(I)
                    I+=1
                if swsystem.FINAL_STRUCTURE is not None:
                    item=gtk.MenuItem("Final - Step")
                    item.connect("activate",self.on_arrows_clicked_handler,swa.DIFF_FINAL_ARROWS)
                    menu.append(item)
                    item.show()
                    if swa.arrowstype==swa.DIFF_FINAL_ARROWS:
                        amenu.set_history(I)
                    I+=1
    def applet_activated(self,rep,a):
        if         isinstance(a,p4vasp.applet.StructureWindowApplet.StructureWindowApplet):
            self.pin_status=a.pin_status
            self.updatePinStatusImage()
            self.createMenuItems()
            entry=self.xml.get_widget("seq_entry")
            if entry is not None:
                entry.set_text(str(a.index))
            sw=a.swin
            if sw is not None:
                i,j,k=sw.getMultiple()
                self.csadj1.value=float(i)
                self.csadj2.value=float(j)
                self.csadj3.value=float(k)
                self.ass_adj.value=float(sw.getArrowsScale())
                self.sss_adj.value=float(sw.getRadiusFactor()*2.0)
            self.xml.get_widget("dsx_entry").set_text(str(sw.dsx))
            self.xml.get_widget("dsy_entry").set_text(str(sw.dsy))
            self.xml.get_widget("dsz_entry").set_text(str(sw.dsz))
    def mdstep(self):
        return int(self.xml.get_widget("speedspin").get_text())
    def initUI(self):
        self.xml.get_widget("toolbar1").set_style(gtk.TOOLBAR_ICONS)
        self.xml.get_widget("toolbar2").set_style(gtk.TOOLBAR_ICONS)

        cs1=self.xml.get_widget("cell_scale1")
        cs2=self.xml.get_widget("cell_scale2")
        cs3=self.xml.get_widget("cell_scale3")
        self.csadj1=gtk.Adjustment(1,1,10,1,0,0)
        self.csadj2=gtk.Adjustment(1,1,10,1,0,0)
        self.csadj3=gtk.Adjustment(1,1,10,1,0,0)
        cs1.set_adjustment(self.csadj1)
        cs2.set_adjustment(self.csadj2)
        cs3.set_adjustment(self.csadj3)
        self.csadj1.connect("value-changed",self.on_cell_scale_changed)
        self.csadj2.connect("value-changed",self.on_cell_scale_changed)
        self.csadj3.connect("value-changed",self.on_cell_scale_changed)

        self.sss_adj=gtk.Adjustment(1.0,0.1,5.0,0.1,0,0)
        sss=self.xml.get_widget("sphere_size_scale")
        self.levelentry=self.xml.get_widget("levelentry")
        self.subtrentry=self.xml.get_widget("subtrentry")
        sss.set_adjustment(self.sss_adj)
        self.sss_adj.connect("value-changed",self.on_sphere_size_scale_changed)

        self.ass_adj=gtk.Adjustment(1.0,0.1,20.0,0.1,0,0)
        ass=self.xml.get_widget("arrows_size_scale")
        ass.set_adjustment(self.ass_adj)
        self.ass_adj.connect("value-changed",self.on_arrows_size_scale_changed)

#    self.atom_selection=self.xml.get_widget("atom_selection")

        self.createMenuItems()


        isomenu = self.xml.get_widget("isomenu")
        if isomenu is not None:
            menu=gtk.Menu()
            isomenu.set_menu(menu)
            isomenu.show()

            item=gtk.MenuItem("None")
            item.connect("activate",self.on_iso_clicked_handler,None)
            menu.append(item)
            item.show()

            item=gtk.MenuItem("Charge density (CHG)")
            item.connect("activate",self.on_iso_clicked_handler,"CHG")
            menu.append(item)
            item.show()

            item=gtk.MenuItem("Charge density (CHGCAR)")
            item.connect("activate",self.on_iso_clicked_handler,"CHGCAR")
            menu.append(item)
            item.show()

            item=gtk.MenuItem("ELF (ELFCAR)")
            item.connect("activate",self.on_iso_clicked_handler,"ELFCAR")
            menu.append(item)
            item.show()

            item=gtk.MenuItem("Local potential (LOCPOT)")
            item.connect("activate",self.on_iso_clicked_handler,"LOCPOT")
            menu.append(item)
            item.show()

            item=gtk.MenuItem("Partial charge (PARCHG)")
            item.connect("activate",self.on_iso_clicked_handler,"PARCHG")
            menu.append(item)
            item.show()

            item=gtk.MenuItem("Select file")
            item.connect("activate",self.on_selectisofile_handler)
            menu.append(item)
            item.show()
        applets().notify_on_activate.append(self.applet_activated)
        self.swin()

    def getSWinApplet(self):
        return applets().getActive([p4vasp.applet.StructureWindowApplet.StructureWindowApplet,
                                    p4vasp.applet.STMWindowApplet.STMWindowApplet])

    def swin(self):
        w=self.getSWinApplet()
        if isinstance(w,p4vasp.applet.StructureWindowApplet.StructureWindowApplet):
            return w.swin
        else:
            return w

    def on_sample111_clicked_handler(self,*arg):
        self.xml.get_widget("dsx_entry").set_text("1")
        self.xml.get_widget("dsy_entry").set_text("1")
        self.xml.get_widget("dsz_entry").set_text("1")
        schedule(self.updateIsosurfaceGen())
    def on_sample222_clicked_handler(self,*arg):
        self.xml.get_widget("dsx_entry").set_text("2")
        self.xml.get_widget("dsy_entry").set_text("2")
        self.xml.get_widget("dsz_entry").set_text("2")
        schedule(self.updateIsosurfaceGen())
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
    def on_cuc_button_clicked_handler(self,*arg):
        a=self.getSWinApplet()
        a.cell_centering=a.CELL_CENTERING_ZERO
        a.updateSeq()
    def on_tuc_button_clicked_handler(self,*arg):
        a=self.getSWinApplet()
        a.cell_centering=a.CELL_CENTERING_INSIDE
        a.updateSeq()
    def on_cell_scale_changed(self,*arg):
        self.swin().setMultiple(self.csadj1.value,self.csadj2.value,self.csadj3.value)
    def on_sphere_size_scale_changed(self,*arg):
        self.swin().setRadiusFactor(0.5*self.sss_adj.value)
    def on_arrows_size_scale_changed(self,*arg):
        self.swin().setArrowsScale(self.ass_adj.value)

    def on_show_button_clicked_handler(self,*arg):
        if self.system is not None:
            a=p4vasp.Selection.selection().getAtoms()
            info=self.swin().structure_drawer.info
            l=info.len()
            for i in a:
                if i>=0 and i<l:
                    info.getRecord(i).hidden=0
            self.hidden=filter(lambda i,f=info.getRecord:f(i).hidden,range(l))
        self.swin().updateStructure()

    def on_hide_button_clicked_handler(self,*arg):
        if self.system is not None:
            a=p4vasp.Selection.selection().getAtoms()
            info=self.swin().structure_drawer.info
            l=info.len()
            for i in a:
                if i>=0 and i<l:
                    info.getRecord(i).hidden=1
            self.hidden=filter(lambda i,f=info.getRecord:f(i).hidden,range(l))
        self.swin().updateStructure()

    def on_showonly_button_clicked_handler(self,*arg):
        if self.system is not None:
            a=p4vasp.Selection.selection().getAtoms()
            info=self.swin().structure_drawer.info
            l=info.len()
            for i in range(l):
                info.getRecord(i).hidden=1
            for i in a:
                if i>=0 and i<l:
                    info.getRecord(i).hidden=0
            self.hidden=filter(lambda i,f=info.getRecord:f(i).hidden,range(l))
        self.swin().updateStructure()

    def on_hideonly_button_clicked_handler(self,*arg):
        if self.system is not None:
            a=p4vasp.Selection.selection().getAtoms()
            info=self.swin().structure_drawer.info
            l=info.len()
            for i in range(l):
                info.getRecord(i).hidden=0
            for i in a:
                if i>=0 and i<l:
                    info.getRecord(i).hidden=1
            self.hidden=filter(lambda i,f=info.getRecord:f(i).hidden,range(l))
        self.swin().updateStructure()

    def on_showcell_button_clicked_handler(self,*arg):
        self.swin().showCell(1)
    def on_hidecell_button_clicked_handler(self,*arg):
        self.swin().showCell(0)

#  def setStructure(self,s):
#    print "setStructure"

    def setSeqIndex(self,index):
        self.getSWinApplet().setIndex(index)
        index=self.getSWinApplet().index
        entry=self.xml.get_widget("seq_entry")
        if entry is not None:
            entry.set_text(str(index))


    def on_seq_first_clicked_handler(self,w):
        self.setSeqIndex(0)

    def on_seq_last_clicked_handler(self,w):
        self.setSeqIndex("last")

    def on_seq_back_clicked_handler(self,w):
        self.setSeqIndex(self.getSWinApplet().index-1)

    def on_play_clicked_handler(self,w):
        index=self.getSWinApplet().index
        self.play_flag=1
        self.play_id=gtk.timeout_add(200,self.play_callback)

    def play_callback(self):
        index=self.getSWinApplet().index
#    print "play",index
        self.setSeqIndex(index+self.mdstep())
        if index==self.getSWinApplet().index:
            self.play_flag=0
            return False
        self.swin().win.redraw()
        return True

    def on_stop_clicked_handler(self,w):
#    print "stop"
        if self.play_flag:
            gobject.source_remove(self.play_id)
            self.play_flag=0

    def on_seq_forward_clicked_handler(self,w):
#    print "A",self.getSWinApplet(),self.getSWinApplet().index
        self.setSeqIndex(self.getSWinApplet().index+1)
#    print "B",self.getSWinApplet(),self.getSWinApplet().index

    def on_structureitem_clicked_handler(self,w,t):
        self.getSWinApplet().setSequenceType(t)

    def on_arrows_clicked_handler(self,w,t):
        self.getSWinApplet().setArrowsType(t)

    def updateIsosurface(self):
        if self.view_iso is None:
            self.swin().setChgcar(None)
        else:
            c=None
            if type(self.view_iso)==type([]):
                if len(self.view_iso[0]):
                    c=cp4vasp.Chgcar()
                    c.read(self.view_iso[0])
            elif self.system[self.view_iso] is not None:
                c=self.system[self.view_iso].get().clone()
            if c is not None:
                if self.subtrchgcar is None:
                    s=strip(self.subtrentry.get_text())
                    if len(s):
                        self.subtrchgcar=cp4vasp.Chgcar()
                        self.subtrchgcar.read(s)
                        if self.subtrchgcar is not None:
                            try:
                                c.subtractChgcar(self.subtrchgcar)
                            except:
                                self.subtrchgcar=None
                self.swin().setChgcar(None)
                try:
                    msg().message("Isosurface Level: %s"%self.levelentry.get_text())
                    l=float(self.levelentry.get_text())
                    self.swin().setIsosurfaceLevel(l)
                except:
                    pass
            self.swin().setChgcar(c)

    def updateIsosurfaceGen(self):
        sw=self.swin()
        try:
            sw.dsx=int(self.xml.get_widget("dsx_entry").get_text())
        except:
            msg().error("Invalid downsample value x")
        try:
            sw.dsy=int(self.xml.get_widget("dsy_entry").get_text())
        except:
            msg().error("Invalid downsample value x")
        try:
            sw.dsz=int(self.xml.get_widget("dsz_entry").get_text())
        except:
            msg().error("Invalid downsample value x")

        if self.view_iso is None:
            sw.setChgcar(None)
            msg().message("isosurface off")
        else:
            if type(self.view_iso)==type([]):
                s=self.view_iso[0]
                if len(s):
                    c=cp4vasp.Chgcar()
                    g=c.createReadProcess(s)
                    yield 1
                    while g.next():
                        st=g.error()
                        if st is not None:
                            msg().error(st)
                        st=g.status()
                        if s is not None:
                            msg().status(st)
                        msg().step(g.step(),g.total())
                        yield 1
                    s=g.error()
                    if s is not None:
                        msg().error(s)
                    s=g.status()
                    if s is not None:
                        msg().status(s)
                    msg().step(g.step(),g.total())
                    msg().step(0,1)
                else:
                    c=None
            else:

                msg().message("view isosurface of %s"%self.view_iso)

                if self.system[self.view_iso] is not None:
                    self.system.scheduleFirst(self.view_iso)
                    yield 1
                    c=self.system[self.view_iso].get().clone()
                    yield 1

            if c is not None:
                if self.subtrchgcar is None:
                    s=strip(self.subtrentry.get_text())
                    if len(s):
                        msg().status("Read %s for subtraction"%s)
                        self.subtrchgcar=cp4vasp.Chgcar()
                        g=self.subtrchgcar.createReadProcess(s)
                        yield 1
                        while g.next():
                            st=g.error()
                            if st is not None:
                                msg().error(st)
                            st=g.status()
                            if s is not None:
                                msg().status(st)
                            msg().step(g.step(),g.total())
                            yield 1
                        s=g.error()
                        if s is not None:
                            msg().error(s)
                        s=g.status()
                        if s is not None:
                            msg().status(s)
                        msg().step(g.step(),g.total())
                        msg().step(0,1)

                    if self.subtrchgcar is not None:
                        try:
                            msg().status("Chgcar subtraction")
                            yield 1
                            c.subtractChgcar(self.subtrchgcar)
                            yield 1
                        except:
                            self.subtrchgcar=None

                    sw.setChgcar(None)
                    try:
                        msg().message("Isosurface Level: %s"%self.levelentry.get_text())
                        l=float(self.levelentry.get_text())
                        sw.setIsosurfaceLevel(l)
                    except:
                        pass
                    msg().status("Creating isosurface")
                    yield 1
            sw.setChgcar(c)
            msg().status("OK")

    def on_iso_clicked_handler(self,w,iso):
        self.view_iso=iso
#    self.updateIsosurface()
        schedule(self.updateIsosurfaceGen())

#  def on_levelentry_changed(self,*arg):
#    print "on_levelentry_changed"

    def on_selectsubtr_clicked_handler(self,*arg):
        if self.subtr_density_fileselection is None:
            xml=p4vasp.util.loadGlade(self.gladefile,"subtr_density_fileselection")
            xml.signal_connect('hide_widget',                     self.hide_widget_handler)
            xml.signal_connect('show_widget',                     self.show_widget_handler)
            xml.signal_connect("on_subtr_density_ok_clicked",     self.on_subtr_density_ok_clicked_handler)
            xml.signal_connect("on_subtr_density_cancel_clicked", self.on_subtr_density_cancel_clicked_handler)
            self.subtr_density_fileselection=xml.get_widget("subtr_density_fileselection")
        self.subtr_density_fileselection.show()

    def on_selectisofile_handler(self,*arg):
        if self.charge_density_fileselection is None:
            xml=p4vasp.util.loadGlade(self.gladefile,"charge_density_fileselection")
            xml.signal_connect('hide_widget',                     self.hide_widget_handler)
            xml.signal_connect('show_widget',                     self.show_widget_handler)
            xml.signal_connect("on_charge_density_ok_clicked",    self.on_charge_density_ok_clicked_handler)
            xml.signal_connect("on_charge_density_cancel_clicked",self.on_charge_density_cancel_clicked_handler)
            self.charge_density_fileselection=xml.get_widget("charge_density_fileselection")
        self.charge_density_fileselection.show()

#  def on_subtrentry_changed(self,*arg):
#    print "on_subtrentry_changed"

    def on_updateisobutton_clicked_handler(self,*arg):
#    self.updateIsosurface()
        schedule(self.updateIsosurfaceGen())

    def on_minlevelbutton_clicked_handler(self,*arg):
        c=self.swin().chgcar
        if c is not None:
            self.levelentry.set_text(str(c.getMinimum()))
    #    self.updateIsosurface()
            schedule(self.updateIsosurfaceGen())

    def on_maxlevelbutton_clicked_handler(self,*arg):
        c=self.swin().chgcar
        if c is not None:
            self.levelentry.set_text(str(c.getMaximum()))
    #    self.updateIsosurface()
            schedule(self.updateIsosurfaceGen())

    def on_avglevelbutton_clicked_handler(self,*arg):
        c=self.swin().chgcar
        if c is not None:
            self.levelentry.set_text(str(c.getAverage()))
    #    self.updateIsosurface()
            schedule(self.updateIsosurfaceGen())

    def hide_widget_handler(self,widget):
        widget.hide()

    def show_widget_handler(self,widget):
        widget.show()

    def on_subtr_density_ok_clicked_handler(self,*arg):
        self.subtrentry.set_text(self.subtr_density_fileselection.get_filename())
        self.subtr_density_fileselection.hide()
        self.subtrchgcar=None
#    self.updateIsosurface()
        schedule(self.updateIsosurfaceGen())
    def on_subtr_density_cancel_clicked_handler(self,*arg):
        self.subtr_density_fileselection.hide()


    def on_charge_density_ok_clicked_handler(self,*arg):
#    self.subtrentry.set_text(self.subtr_density_fileselection.get_filename())
#    self.subtr_density_fileselection.hide()
#    self.subtrchgcar=None
#    self.updateIsosurface()
        self.view_iso=[self.charge_density_fileselection.get_filename()]
        schedule(self.updateIsosurfaceGen())
        self.charge_density_fileselection.hide()

    def on_charge_density_cancel_clicked_handler(self,*arg):
        self.charge_density_fileselection.hide()


    def on_foto_button_clicked_handler(self,*arg):
        import os.path
        i=1
        sw=self.swin()
        while os.path.exists("p4vasp%04d.tga"%i):
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
        sw.win.saveScreenshot("p4vasp%04d.tga"%i)

    def saveanim(self):
        import cp4vasp
        seq=self.system.STRUCTURE_SEQUENCE_L
        index=self.getSWinApplet().index
#    msg().status("Save picture of the initial structure")
#    yield 1
#    self.setSeqIndex(-1)
#    self.swin().win.redraw()
#    cp4vasp.VisCheck()
#    self.swin().win.saveScreenshot("p4vasp_initial.tga")
#    msg().status("Save picture of the final structure")
#    yield 1
#    self.setSeqIndex(")
#    self.swin().win.redraw()
#    cp4vasp.VisCheck()
#    self.swin().win.saveScreenshot("p4vasp_final.tga")
        sw=self.swin()
        x=sw.win.x
        y=sw.win.y
        w=sw.win.w
        h=sw.win.h
        w1=w+(4-w%4)%4
        if w!=w1:
            sw.win.resize(x,y,w1,h)
        for i in range(len(seq)):
            msg().step(i+1,len(seq))
            msg().status("Save step %d"%i)
            yield 1
            self.setSeqIndex(i)
            sw.win.redraw()
            cp4vasp.VisCheck()
            sw.win.saveScreenshot("p4vasp_step%03d.tga"%(i+1))
        self.setSeqIndex(index)
        sw.win.redraw()
        cp4vasp.VisCheck()
        msg().status("OK")
        msg().step(0,1)

    def on_anim_button_clicked_handler(self,*arg):
        schedule(self.saveanim())
    def on_bw_button_clicked_handler(self,*arg):
        self.swin().setBackground(0,0,0)
        self.swin().setCellColor(1,1,1)
    def on_wb_button_clicked_handler(self,*arg):
        self.swin().setBackground(1,1,1)
        self.swin().setCellColor(0,0,0)

    def on_pin_button_clicked_handler(self,*arg):
        self.pin_status=not self.pin_status
        self.updatePinStatusImage()
        self.getSWinApplet().pin_status=self.pin_status

    def on_drawaspoints_toggled_handler(self,*arg):
        self.swin().setDrawIsosurfaceAsPoints(self.xml.get_widget("drawAsPointsButton").get_active())
        self.swin().redraw()

    def destroy(self):
        applets().notify_on_activate.remove(self.applet_activated)

#  def on_structuremenu_clicked_handler(self,*arg):
#    print "structure changed",arg

StructureWindowControlApplet.store_profile=AppletProfile(StructureWindowControlApplet,tagname="swinControl")
#StructureApplet.config_profile=AppletProfile(StructureApplet,tagname="Structure")
