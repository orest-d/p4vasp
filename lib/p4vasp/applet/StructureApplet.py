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
from p4vasp import *
from p4vasp.graph import *
from p4vasp.store import *
from p4vasp.applet.Applet import *
import p4vasp.sellang
from p4vasp.StructureWindow import *
from p4vasp.util import getAtomtypes
import p4vasp.Selection

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

class Measure:
    def __init__(self,structure_applet):
        import p4vasp.util
        self.structure_applet=structure_applet
        self.gladefile="structuremeasure.glade"
        self.xml=p4vasp.util.loadGlade(self.gladefile)
        self.swin=self.xml.get_widget("window")
        self.output=self.xml.get_widget("output")
        self.xml.signal_connect("hide", self.hide)
        self.xml.signal_connect("on_append_button_clicked", self.on_append)
        self.hidden=0
        self.on_append()

    def position(self,struct,a):
        return struct[a.atom]+struct.basis[0]*a.nx+struct.basis[1]*a.ny+struct.basis[2]*a.nz

    def deleteText(self):
        self.output.set_point(0)
        self.output.forward_delete(self.output.get_length())
    def setText(self,s):
        self.deleteText()
        self.output.get_buffer().set_text(s)
    def getText(self):
        return self.output.get_text()
    def appendText(self,s):
        b=self.output.get_buffer()
        b.insert(b.get_end_iter(),s)

    def on_append(self,*arg):
        l=[]
        #struct=self.structure_applet.structure.clone()
        struct=self.structure_applet.structure
        struct.setCarthesian()
        for i in range(self.structure_applet.swin.getSelectedCount()):
            l.append(self.structure_applet.swin.getSelected(i))
        s ="\nMeasure:\n"
        s+="N:     cell:       length:   angle:     dihedral:\n"
        if len(l)>0:
            s+="%3d %3d %3d %3d   -           -             -\n"%(l[0].atom+1,l[0].nx,l[0].ny,l[0].nz)
        if len(l)>1:
            L=(self.position(struct,l[0])-self.position(struct,l[1])).length()
            s+="%3d %3d %3d %3d %7.4f     -            -\n"%(l[1].atom+1,l[1].nx,l[1].ny,l[1].nz,L)
        if len(l)>2:
            a=self.position(struct,l[0])
            b=self.position(struct,l[1])
            c=self.position(struct,l[2])
            L=(c-b).length()
            angle=(a-b).angle(c-b)*180.0/pi
            s+="%3d %3d %3d %3d %7.4f %+6.4f      -\n"%(l[2].atom+1,l[2].nx,l[2].ny,l[2].nz,L,angle)
        for i in range(3,len(l)):
            a=self.position(struct,l[i-3])
            b=self.position(struct,l[i-2])
            c=self.position(struct,l[i-1])
            d=self.position(struct,l[i])
            L=(d-c).length()
            angle=(b-c).angle(d-c)*180.0/pi
            dihedral=(c-b).cross(a-b).angle((b-c).cross(d-c))
            s+="%3d %3d %3d %3d %7.4f %+6.4f %+6.4f\n"%(l[i].atom+1,l[1].nx,l[1].ny,l[1].nz,L,angle,dihedral)

        s+="\n"

        self.appendText(s)

    def hide(self,*arg):
        self.swin.hide()
        self.hidden=1

    def show(self):
        self.swin.show()
        self.hidden=0

class StructureApplet(Applet,p4vasp.Selection.SelectionListener):
    menupath=["Structure","Show (old)"]
    def __init__(self):
        Applet.__init__(self)
        self.gladefile="structureapplet.glade"
        self.gladename="applet_frame"
        self.required=["NAME","INITIAL_STRUCTURE","FINAL_STRUCTURE","PRIMITIVE_STRUCTURE","STRUCTURE_SEQUENCE_L"]
        self.swin=None
        self.measure=None
        self.radius_factor=1.0
        self.cell_centering=0 #0:none, 1:to unit cel, 2:centered unit cel
        self.visible_atoms=None
        self.index=-1
        self.hidden=[]
        self.arrows_sequence=[]
        self.view_iso=None
        self.levelentry=None
        self.subtrentry=None
        self.subtr_density_fileselection=None
        self.subtrchgcar=None
        self.chgcar=None
    def notifyAtomSelection(self, sel,origin):
#    self.atom_selection.set_text(sel.encode(self.structure))
        sel=p4vasp.Selection.selection()
        self.swin.removeSelectedAll()
        for i,nx,ny,nz in sel:
            self.swin.selectAtom(i,nx,ny,nz)


    def setSystem(self,s):
        self.system=s
        if s is not None:
            self.system.require(self.required,self.updateSystem)
        self.updateSystem()

    def updateSystem(self,x=None):
        s=self.system
        if s is not None:
#      structure=s.getCurrent("INITIAL_STRUCTURE")
            structure=s.INITIAL_STRUCTURE
            if structure is not None:
                self.showStructureWindow()
                self.setStructure(structure)
        self.createStructureItems()

    def setStructure(self,structure):
        self.structure=structure
        if self.cell_centering==1:
            self.structure.toCenteredUnitCell()
        elif self.cell_centering==2:
            self.structure.toUnitCell()


        self.swin.setStructure(structure)
        self.swin.structure_drawer.setRadiusFactor(0.5*self.radius_factor)

        info=self.swin.structure_drawer.info
        l=info.len()
        for i in self.hidden:
            if i>=0 and i<l:
                info.getRecord(i).hidden=1

    def showStructureWindow(self):
        if self.swin is None:
            self.swin=StructureWindow(title="p4vasp Structure",atomtypes=getAtomtypes())
            self.swin.structure_drawer.setRadiusFactor(0.5*self.radius_factor)
        self.swin.show()

    def createStructureItems(self):
        omenu = self.xml.get_widget("structuremenu")
        if omenu is None:
            return None
        menu=gtk.Menu()
        omenu.set_menu(menu)
        omenu.show()

        if self.system is not None:
            if self.system.current("INITIAL_STRUCTURE") is not None:
                item=gtk.MenuItem("Initial positions")
                item.connect("activate",self.on_structureitem_clicked_handler,-1)
                menu.append(item)
                item.show()
            if self.system.current("FINAL_STRUCTURE") is not None:
                item=gtk.MenuItem("Final positions")
                item.connect("activate",self.on_structureitem_clicked_handler,-2)
                menu.append(item)
                item.show()
            if self.system.current("PRIMITIVE_STRUCTURE") is not None:
                item=gtk.MenuItem("Primitive cell")
                item.connect("activate",self.on_structureitem_clicked_handler,-2)
                menu.append(item)
                item.show()
            seq=self.system.current("STRUCTURE_SEQUENCE_L")
            if seq is not None:
                for i in range(len(seq)):
                    item=gtk.MenuItem("step %3d"%(i+1))
                    item.connect("activate",self.on_structureitem_clicked_handler,i)
                    menu.append(item)
                    item.show()


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

        self.createStructureItems()

        amenu = self.xml.get_widget("arrowstypemenu")
        if amenu is not None:
            menu=gtk.Menu()
            amenu.set_menu(menu)
            amenu.show()

            item=gtk.MenuItem("None")
            item.connect("activate",self.on_none_arrows_clicked_handler,-1)
            menu.append(item)
            item.show()

            item=gtk.MenuItem("Forces")
            item.connect("activate",self.on_forces_arrows_clicked_handler,-1)
            menu.append(item)
            item.show()

            item=gtk.MenuItem("Step - Initial")
            item.connect("activate",self.on_SMI_arrows_clicked_handler,-1)
            menu.append(item)
            item.show()

            item=gtk.MenuItem("Final - Step")
            item.connect("activate",self.on_SMF_arrows_clicked_handler,-1)
            menu.append(item)
            item.show()

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


    def on_measure_button_clicked_handler(self,*arg):
        if self.measure is None:
            self.measure = Measure(self)
        else:
            self.measure.show()

    def on_front_button_clicked_handler(self,*arg):
        self.swin.navigator.setFrontView()
    def on_back_button_clicked_handler(self,*arg):
        self.swin.navigator.setBackView()
    def on_left_button_clicked_handler(self,*arg):
        self.swin.navigator.setLeftView()
    def on_right_button_clicked_handler(self,*arg):
        self.swin.navigator.setRightView()
    def on_top_button_clicked_handler(self,*arg):
        self.swin.navigator.setTopView()
    def on_bottom_button_clicked_handler(self,*arg):
        self.swin.navigator.setBottomView()
    def on_home_button_clicked_handler(self,*arg):
        self.swin.navigator.setHome()
    def on_zoom_11_button_clicked_handler(self,*arg):
        self.swin.navigator.setZoom(1.0)
    def on_zoom_in_button_clicked_handler(self,*arg):
        self.swin.navigator.mulZoom(1.1)
    def on_zoom_out_button_clicked_handler(self,*arg):
        self.swin.navigator.mulZoom(1.0/1.1)
    def on_ortho_button_clicked_handler(self,*arg):
        self.swin.navigator.setPerspective(0)
    def on_persp_button_clicked_handler(self,*arg):
        self.swin.navigator.setPerspective(1)
    def on_cuc_button_clicked_handler(self,*arg):
        self.cell_centering=1
        if self.structure is not None:
            self.setStructure(self.structure)
    def on_tuc_button_clicked_handler(self,*arg):
        self.cell_centering=2
        if self.structure is not None:
            self.setStructure(self.structure)
    def on_cell_scale_changed(self,*arg):
        self.swin.setMultiple(self.csadj1.value,self.csadj2.value,self.csadj3.value)
    def on_sphere_size_scale_changed(self,*arg):
        self.radius_factor=self.sss_adj.value
        self.swin.structure_drawer.setRadiusFactor(0.5*self.radius_factor)
    def on_arrows_size_scale_changed(self,*arg):
        self.swin.setArrowsScale(self.ass_adj.value)

    def on_show_button_clicked_handler(self,*arg):
        if self.system is not None:
            a=p4vasp.Selection.selection().getAtoms()
            info=self.swin.structure_drawer.info
            l=info.len()
            for i in a:
                if i>=0 and i<l:
                    info.getRecord(i).hidden=0
            self.hidden=filter(lambda i,f=info.getRecord:f(i).hidden,range(l))
        self.swin.updateStructure()

    def on_hide_button_clicked_handler(self,*arg):
        if self.system is not None:
            a=p4vasp.Selection.selection().getAtoms()
            info=self.swin.structure_drawer.info
            l=info.len()
            for i in a:
                if i>=0 and i<l:
                    info.getRecord(i).hidden=1
            self.hidden=filter(lambda i,f=info.getRecord:f(i).hidden,range(l))
        self.swin.updateStructure()

    def on_showonly_button_clicked_handler(self,*arg):
        if self.system is not None:
            a=p4vasp.Selection.selection().getAtoms()
            info=self.swin.structure_drawer.info
            l=info.len()
            for i in range(l):
                info.getRecord(i).hidden=1
            for i in a:
                if i>=0 and i<l:
                    info.getRecord(i).hidden=0
            self.hidden=filter(lambda i,f=info.getRecord:f(i).hidden,range(l))
        self.swin.updateStructure()

    def on_hideonly_button_clicked_handler(self,*arg):
        if self.system is not None:
            a=p4vasp.Selection.selection().getAtoms()
            info=self.swin.structure_drawer.info
            l=info.len()
            for i in range(l):
                info.getRecord(i).hidden=0
            for i in a:
                if i>=0 and i<l:
                    info.getRecord(i).hidden=1
            self.hidden=filter(lambda i,f=info.getRecord:f(i).hidden,range(l))
        self.swin.updateStructure()

#  def on_put_selection_button_clicked_handler(self,*arg):
#    if self.system is not None:
#      sel=self.atom_selection.get_text()
#      a=p4vasp.sellang.decode(sel,self.system.INITIAL_STRUCTURE)
#      self.swin.removeSelectedAll()
#      for i in a:
#        self.swin.selectAtom(i)
#    #self.swin.updateStructure()
#
#  def on_get_selection_button_clicked_handler(self,*arg):
#    if self.system is not None:
#      sel=[]
#      for i in range(self.swin.getSelectedCount()):
#        sel.append(self.swin.getSelected(i).atom)
#      a=p4vasp.sellang.encode(sel,self.system.INITIAL_STRUCTURE)
#      sel=self.atom_selection.set_text(a)
#    #self.swin.updateStructure()

    def destroy(self):
        print "destroy"
        if self.swin is not None:
#      print "hide"
#      self.swin.hide()
#      print "<-None"
            self.swin=None
            print "done"

    def hide(self):
        if self.swin is not None:
            self.swin.hide()

    def show(self):
        if self.swin is not None:
            self.swin.show()
        self.updateSystem()

    def setSeqIndex(self,index):
        if index<-2:
            index=-1
        else:
            if self.system.current("STRUCTURE_SEQUENCE_L") is not None:
                if index>=len(self.system.STRUCTURE_SEQUENCE_L):
                    index=-2
        self.index=index

        try:
            if index==-1:
                self.setStructure(self.system.INITIAL_STRUCTURE)
                self.swin.setArrows([])
            elif index==-2:
                self.setStructure(self.system.FINAL_STRUCTURE)
                self.swin.setArrows([])
            else:
                self.setStructure(self.system.STRUCTURE_SEQUENCE_L[index])
                if index<len(self.arrows_sequence):
                    self.swin.setArrows(self.arrows_sequence[index])
                else:
                    self.swin.setArrows([])

            error=0
        except:
            msg().exception()
            error=1

        entry=self.xml.get_widget("seq_entry")
        if entry is not None:
            if index==-1:
                if error:
                    entry.set_text("ERR (Init. pos.)")
                else:
                    entry.set_text("Initial pos.")
            elif index==-2:
                if error:
                    entry.set_text("ERR (Final pos.)")
                else:
                    entry.set_text("Final pos.")
            else:
                if error:
                    entry.set_text("ERR "+str(index))
                else:
                    entry.set_text(str(index))


    def on_seq_first_clicked_handler(self,w):
        self.setSeqIndex(-1)

    def on_seq_last_clicked_handler(self,w):
        self.setSeqIndex(-2)

    def on_seq_back_clicked_handler(self,w):
        if self.index==-2:
            self.setSeqIndex(len(self.system.STRUCTURE_SEQUENCE_L)-1)
        else:
            self.setSeqIndex(self.index-1)

    def on_seq_forward_clicked_handler(self,w):
        self.setSeqIndex(self.index+1)

    def on_structureitem_clicked_handler(self,w,index):
        self.setSeqIndex(index)

    def on_none_arrows_clicked_handler(self,*arg):
        self.arrows_sequence=[]
        self.setSeqIndex(self.index)

    def on_forces_arrows_clicked_handler(self,*arg):
        self.arrows_sequence=self.system.FORCES_SEQUENCE_L
        self.setSeqIndex(self.index)

    def on_SMI_arrows_clicked_handler(self,*arg):
        self.arrows_sequence=SubtrSequence(self,"INITIAL_STRUCTURE",1)
        self.setSeqIndex(self.index)
    def on_SMF_arrows_clicked_handler(self,*arg):
        self.arrows_sequence=SubtrSequence(self,"FINAL_STRUCTURE",-1)
        self.setSeqIndex(self.index)

    def updateIsosurface(self):
        if self.view_iso is None:
            self.swin.setChgcar(None)
        else:
            if self.system[self.view_iso] is not None:
                c=self.system[self.view_iso].get().clone()
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

                self.swin.setChgcar(None)
                try:
                    msg().message("Isosurface Level: %s"%self.levelentry.get_text())
                    l=float(self.levelentry.get_text())
                    self.swin.setIsosurfaceLevel(l)
                except:
                    pass
                self.swin.setChgcar(c)

    def updateIsosurfaceGen(self):
        if self.view_iso is None:
            self.swin.setChgcar(None)
            msg().message("isosurface off")
        else:
            msg().message("view isosurface of %s"%self.view_iso)
            if self.system[self.view_iso] is not None:
                self.system.scheduleFirst(self.view_iso)
                yield 1
                c=self.system[self.view_iso].get().clone()
                yield 1
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

                self.swin.setChgcar(None)
                try:
                    msg().message("Isosurface Level: %s"%self.levelentry.get_text())
                    l=float(self.levelentry.get_text())
                    self.swin.setIsosurfaceLevel(l)
                except:
                    pass
                msg().status("Creating isosurface")
                yield 1
                self.swin.setChgcar(c)
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
            xml.signal_connect('hide_widget',                    self.hide_widget_handler)
            xml.signal_connect('show_widget',                    self.show_widget_handler)
            xml.signal_connect("on_subtr_density_ok_clicked",    self.on_subtr_density_ok_clicked_handler)
            self.subtr_density_fileselection=xml.get_widget("subtr_density_fileselection")
        self.subtr_density_fileselection.show()

#  def on_subtrentry_changed(self,*arg):
#    print "on_subtrentry_changed"

    def on_updateisobutton_clicked_handler(self,*arg):
#    self.updateIsosurface()
        schedule(self.updateIsosurfaceGen())

    def on_minlevelbutton_clicked_handler(self,*arg):
        c=self.swin.chgcar
        self.levelentry.set_text(str(c.getMinimum()))
#    self.updateIsosurface()
        schedule(self.updateIsosurfaceGen())

    def on_maxlevelbutton_clicked_handler(self,*arg):
        c=self.swin.chgcar
        self.levelentry.set_text(str(c.getMaximum()))
#    self.updateIsosurface()
        schedule(self.updateIsosurfaceGen())

    def on_avglevelbutton_clicked_handler(self,*arg):
        c=self.swin.chgcar
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
    def on_foto_button_clicked_handler(self,*arg):
        import os.path
        i=1
        while os.path.exists("p4vasp%04d.tga"%i):
            i+=1
        self.swin.win.saveScreenshot("p4vasp%04d.tga"%i)

    def saveanim(self):
        import cp4vasp
        seq=self.system.STRUCTURE_SEQUENCE_L
        index=self.index
        msg().status("Save picture of the initial structure")
        yield 1
        self.setSeqIndex(-1)
        cp4vasp.VisCheck()
        self.swin.win.saveScreenshot("p4vasp_initial.tga")
        msg().status("Save picture of the final structure")
        yield 1
        self.setSeqIndex(-2)
        cp4vasp.VisCheck()
        self.swin.win.saveScreenshot("p4vasp_final.tga")
        for i in range(len(seq)):
            msg().step(i+1,len(seq))
            msg().status("Save step %d"%i)
            yield 1
            self.setSeqIndex(i)
            cp4vasp.VisCheck()
            self.swin.win.saveScreenshot("p4vasp_step%03d.tga"%(i+1))
        self.setSeqIndex(index)
        msg().status("OK")
        msg().step(0,1)

    def on_anim_button_clicked_handler(self,*arg):
        schedule(self.saveanim())


#  def on_structuremenu_clicked_handler(self,*arg):
#    print "structure changed",arg

StructureApplet.store_profile=AppletProfile(StructureApplet,tagname="Structure",
attr_setup="""
float radius_factor
int   cell_centering
visible_atoms
int   index
hidden
""")
#StructureApplet.config_profile=AppletProfile(StructureApplet,tagname="Structure")
