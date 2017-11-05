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

from p4vasp import *
from p4vasp.SystemPM import *
from p4vasp.applet.Applet import *
import p4vasp.sellang
from string import *
import gtk
from p4vasp.graph import *
from p4vasp.GraphPM import *
from p4vasp.setutils import *
import p4vasp.Selection
from p4vasp.applet.ElectronicApplet import *


def hasSpinInfo(system):

    data=system.PARTIAL_DOS_L
    if data is None:
        return None
    return len(data[0])>1

def hasOrbital(system,o):
    data=system.PARTIAL_DOS_L
    if data is None:
        return None
    return o in data.field

class LDOSLineAttribute(AttributeProfile):
    def setValue(self,obj,val):
        for x in val:
            obj.addLine(x)

class ElectronicControlApplet(Applet,p4vasp.Selection.SelectionListener):
    menupath=["Electronic","Local DOS+bands control"]
    showmode=Applet.EXTERNAL_MODE
    def __init__(self):
        Applet.__init__(self)
        self.gladefile="elcontrolapplet.glade"
        self.gladename="applet_frame"
        self.active_line = None
        self.active_color=-1
        self.active_symbol=-1

    def lines(self):
        return self.getEApplet().lines

    def getEApplet(self):
#    return applets().getActive(p4vasp.applet.ElectronicApplet.ElectronicApplet,self.EXTERNAL_MODE)
        return applets().getActive(p4vasp.applet.ElectronicApplet.ElectronicApplet)


    def initUI(self):
        self.line_selection=self.xml.get_widget("line_selection")
        if self.line_selection is not None:
            self.line_menu=gtk.Menu()
            self.line_selection.set_menu(self.line_menu)
            self.line_selection.show()
        else:
            self.line_menu=None
        w=self.xml.get_widget("atom_selection")
        if w is not None:
            try:
                s=self.system.INITIAL_STRUCTURE
            except:
                s=None
            sel=w.set_text(p4vasp.Selection.selection().encode(s))

        self.colors=[
          "default",
          "white",
          "black",
          "red",
          "green",
          "blue",
          "yellow",
          "brown",
          "grey",
          "violet",
          "cyan",
          "magenta",
          "orange",
          "indigo",
          "maroon",
          "turquoise",
        ]
        self.symbol_names=[
          "default",
          "None",
          "Circle",
          "Square",
          "Diamond",
          "Triangle up",
          "Triangle left",
          "Triangle down",
          "Triangle right",
          "Plus",
          "X",
          "Star"
        ]

        self.color_optionmenu=self.xml.get_widget("color_optionmenu")
        m=gtk.Menu()
        self.color_optionmenu.set_menu(m)
        for i in range(len(self.colors)):
            item=gtk.MenuItem(self.colors[i])
            item.connect("activate",self._color_activate,i-1)
            m.append(item)
            item.show()
        self.color_optionmenu.set_history(0)
        self.color_optionmenu.show()

        self.symbol_optionmenu=self.xml.get_widget("symbol_optionmenu")
        m=gtk.Menu()
        self.symbol_optionmenu.set_menu(m)
        for i in range(len(self.symbol_names)):
            item=gtk.MenuItem(self.symbol_names[i])
            item.connect("activate",self._symbol_activate,i-1)
            m.append(item)
            item.show()
        self.symbol_optionmenu.set_history(0)
        self.symbol_optionmenu.show()

        applets().notify_on_activate.append(self.applet_activated)
        self.getEApplet()

    def notifyAtomSelection(self, sel,origin):
        w=self.xml.get_widget("atom_selection")
        if w is not None:
            try:
                s=self.system.INITIAL_STRUCTURE
            except:
                s=None
            w.set_text(p4vasp.Selection.selection().encode(s))

    def getNewSymbolNumber(self):
        numbers=map(lambda x:x.symbol,self.lines())
        if not len(numbers):
            return 0
        for i in range(max(numbers)+2):
            if i not in numbers:
                return i

    def createLine(self):
        orbital=[]
        for n in orbitals:
            w=self.xml.get_widget(n)
            if w is not None:
                if w.get_active():
                    orbital.append(n)
        spin=0
        if self.system is not None:
            if hasSpinInfo(self.system):
                w=self.xml.get_widget("u_spin")
                if w is not None:
                    if w.get_active():
                        spin=1
                w=self.xml.get_widget("d_spin")
                if w is not None:
                    if w.get_active():
                        spin=2
                w=self.xml.get_widget("ud_spin")
                if w is not None:
                    if w.get_active():
                        spin=3


        sel=""
        w=self.xml.get_widget("atom_selection")
        if w is not None:
            sel=w.get_text()

        name=None
        w=self.xml.get_widget("line_description")
        if w is not None:
            name=w.get_text()

        scale=1
        w=self.xml.get_widget("invertbutton")
        if w is not None:
            if w.get_active():
                scale=-scale

        symbol_size=1.0
        w=self.xml.get_widget("symbolsize_entry")
        if w is not None:
            try:
                symbol_size=float(w.get_text())
            except:
                pass

        firstband=0
        w=self.xml.get_widget("firstband")
        if w is not None:
            try:
                firstband=int(w.get_text())
            except:
                pass

        lastband=-1
        w=self.xml.get_widget("lastband")
        if w is not None:
            try:
                lastband=int(w.get_text())
            except:
                pass
#    print "Line",(name,sel,orbital,spin,self.getNewSymbolNumber(),scale)
#  Line(name=None,selection="",orbital=[],spin=3,symbol=0,scale=1,symbol_size=1.0,color=1,first_band=0,last_band=-1,showmode=3)

        l=Line(name,sel,orbital,spin,self.active_symbol,scale,symbol_size,self.active_color,firstband,lastband)
#    if (name is None) or (len(name)==0):
#      l.name=l.getAutoName()
#      w=self.xml.get_widget("line_description")
#      if w is not None:
#       w.set_text(l.getAutoName())
        return l

    def createMenu(self):
        self.line_menu=gtk.Menu()
        self.line_selection.set_menu(self.line_menu)
        for i in range(len(self.lines())):
            l=self.lines()[i]
            item=gtk.MenuItem(l.getAutoName())
            item.connect("activate",self._line_activate,l,i)
            self.line_menu.append(item)
            item.show()

        self.line_menu.show()
        self.line_selection.show()
        self.line_selection.set_history(len(self.lines())-1)

    def applet_activated(self,rep,a):
        if  isinstance(a,ElectronicApplet):
#      print "applet_activated",a
            self.createMenu()

    def addLine(self,l):
#    print "add",l.getName()
        li=len(self.lines())
        self.lines().append(l)
        item=gtk.MenuItem(l.getAutoName())
        item.connect("activate",self._line_activate,l,li)
        self.line_menu.append(item)
        item.show()
        self.line_selection.show()
        self.line_selection.set_history(len(self.lines())-1)
        item.activate()
        self.getEApplet().updateShow()

    def showLine(self,line=None):
        if line is None:
            for n in orbitals:
                w=self.xml.get_widget(n)
                if w is not None:
                    w.set_active(0)

            w=self.xml.get_widget("ud_spin")
            if w is not None:
                w.set_active(1)

            w=self.xml.get_widget("atom_selection")
            if w is not None:
                w.set_text("")
            w=self.xml.get_widget("line_description")
            if w is not None:
                w.set_text("")
        else:
            for n in orbitals:
                w=self.xml.get_widget(n)
                if w is not None:
                    if n in line.orbital:
                        w.set_active(1)
                    else:
                        w.set_active(0)
            if line.spin==1:
                w=self.xml.get_widget("u_spin")
                if w is not None:
                    w.set_active(1)
            elif line.spin==2:
                w=self.xml.get_widget("d_spin")
                if w is not None:
                    w.set_active(1)
            elif line.spin==3:
                w=self.xml.get_widget("ud_spin")
                if w is not None:
                    w.set_active(1)
            if line.scale>0:
                w=self.xml.get_widget("invertbutton")
                if w is not None:
                    w.set_active(0)
            else:
                w=self.xml.get_widget("invertbutton")
                if w is not None:
                    w.set_active(1)


            w=self.xml.get_widget("atom_selection")
            if w is not None:
                w.set_text(line.selection)
            w=self.xml.get_widget("line_description")
            if w is not None:
                if line.name is None:
                    w.set_text("")
                else:
                    w.set_text(line.name)

            self.color_optionmenu.set_history(line.color)
            self.symbol_optionmenu.set_history(line.symbol)
            w=self.xml.get_widget("symbolsize_entry")
            if w is not None:
                w.set_text(str(line.symbol_size))
            w=self.xml.get_widget("firstband")
            if w is not None:
                w.set_text(str(line.first_band))
            w=self.xml.get_widget("lastband")
            if w is not None:
                w.set_text(str(line.last_band))


    def removeLine(self,line):
        flag=(line==self.active_line)

        if line in self.lines():
            self.lines().remove(line)
        self.createMenu()
        self.line_selection.show()
        self.line_selection.set_history(len(self.lines())-1)
        self.line_menu.show()
        if len(self.lines()):
            line=self.lines()[-1]
            self.showLine(self.lines()[-1])
            if flag:
                self.active_line=self.lines()[-1]
        else:
            self.showLine(None)
            if flag:
                self.active_line=None
        self.getEApplet().updateShow()


    def changeLine(self,old,new):
        new.symbol=old.symbol
        self.removeLine(old)
        self.addLine(new)
        self.showLine(new)

    def on_remove_line_clicked_handler(self,*arg):
        if self.active_line is not None:
            self.removeLine(self.active_line)

    def on_change_line_clicked_handler(self,*arg):
        l=self.createLine()
        if self.active_line is None:
            self.addLine(l)
        else:
            self.changeLine(self.active_line,l)


    def on_add_line_clicked_handler(self,*arg):
        self.addLine(self.createLine())

    def _color_activate(self,widget,i):
#    print "color",i
        self.active_color=i

    def _symbol_activate(self,widget,i):
#    print "symbol",i
        self.active_symbol=i

    def _line_activate(self,widget,line,line_index):
#    print "line activate",line
        self.active_line=line
        self.showLine(line)


    def on_select_all_button_clicked_handler(self,*arg):
        for n in orbitals:
            w=self.xml.get_widget(n)
            if w is not None:
                w.set_active(1)

    def on_select_p_button_clicked_handler(self,*arg):
        for n in orbitals_p:
            w=self.xml.get_widget(n)
            if w is not None:
                w.set_active(1)
    def on_select_d_button_clicked_handler(self,*arg):
        for n in orbitals_d:
            w=self.xml.get_widget(n)
            if w is not None:
                w.set_active(1)
    def on_select_f_button_clicked_handler(self,*arg):
        for n in orbitals_f:
            w=self.xml.get_widget(n)
            if w is not None:
                w.set_active(1)
    def on_deselect_all_button_clicked_handler(self,*arg):
        for n in orbitals:
            w=self.xml.get_widget(n)
            if w is not None:
                w.set_active(0)
    def on_deselect_p_button_clicked_handler(self,*arg):
        for n in orbitals_p:
            w=self.xml.get_widget(n)
            if w is not None:
                w.set_active(0)
    def on_deselect_d_button_clicked_handler(self,*arg):
        for n in orbitals_d:
            w=self.xml.get_widget(n)
            if w is not None:
                w.set_active(0)
    def on_deselect_f_button_clicked_handler(self,*arg):
        for n in orbitals_f:
            w=self.xml.get_widget(n)
            if w is not None:
                w.set_active(0)
    def on_p_toggled_handler(self,w):
        if self.system is not None:
            if hasOrbital(self.system,"p"):
                a=w.get_active()
                for n in orbitals_p:
                    w=self.xml.get_widget(n)
                    if w is not None:
                        w.set_active(a)
    def on_d_toggled_handler(self,w):
        if self.system is not None:
            if hasOrbital(self.system,"d"):
                a=w.get_active()
                for n in orbitals_d:
                    w=self.xml.get_widget(n)
                    if w is not None:
                        w.set_active(a)
    def on_f_toggled_handler(self,w):
        if self.system is not None:
            if hasOrbital(self.system,"f"):
                a=w.get_active()
                for n in orbitals_f:
                    w=self.xml.get_widget(n)
                    if w is not None:
                        w.set_active(a)




ElectronicControlApplet.store_profile=AppletProfile(ElectronicControlApplet,
    tagname="ElectronicControl"
  )
