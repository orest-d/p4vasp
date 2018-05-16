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

from __future__ import generators
import gtk
from p4vasp import *
from p4vasp.graph import *
from p4vasp.store import *
from p4vasp.applet.Applet import *
import p4vasp.sellang
from p4vasp.StructureWindow import *
from p4vasp.util import getAtomtypes
#import p4vasp.Selection
import p4vasp.applet.StructureWindowApplet

#,p4vasp.Selection.SelectionListener
class ShowHideControlApplet(Applet):
    menupath=["Structure","Show/hide atoms"]
    showmode=Applet.EXTERNAL_MODE
    def __init__(self):
        Applet.__init__(self)
        self.gladefile="showhidecontrol.glade"
        self.gladename="applet_frame"
#  def notifyAtomSelection(self, sel,origin):
#    pass
#    sel=p4vasp.Selection.selection()


#  def initUI(self):
#    self.xml.get_widget("toolbar1").set_style(gtk.TOOLBAR_ICONS)
#    self.xml.get_widget("toolbar2").set_style(gtk.TOOLBAR_ICONS)


    def getSWinApplet(self):
        return applets().getActive([p4vasp.applet.StructureWindowApplet.StructureWindowApplet,
                                    p4vasp.applet.STMWindowApplet.STMWindowApplet])

    def swin(self):
        w=self.getSWinApplet()
        if isinstance(w,p4vasp.applet.StructureWindowApplet.StructureWindowApplet):
            return w.swin
        else:
            return w


    def on_show_button_clicked_handler(self,*arg):
        a=p4vasp.Selection.selection().getAtoms()
        l=filter(lambda x,a=a:x not in a,self.swin().getHiddenAtoms())
        self.swin().setHiddenAtoms(l)

    def on_hide_button_clicked_handler(self,*arg):
        a=p4vasp.Selection.selection().getAtoms()
        l=self.swin().getHiddenAtoms()[:]
        for i in a:
            if i not in l:
                l.append(i)
        self.swin().setHiddenAtoms(l)

    def on_showonly_button_clicked_handler(self,*arg):
        a=p4vasp.Selection.selection().getAtoms()
        l=filter(lambda x,a=a:x not in a,range(len(self.swin().structure)))
        self.swin().setHiddenAtoms(l)

    def on_hideonly_button_clicked_handler(self,*arg):
        a=p4vasp.Selection.selection().getAtoms()
        self.swin().setHiddenAtoms(a)


ShowHideControlApplet.store_profile=AppletProfile(ShowHideControlApplet,tagname="swinShowHideControl")
#StructureApplet.config_profile=AppletProfile(StructureApplet,tagname="Structure")
