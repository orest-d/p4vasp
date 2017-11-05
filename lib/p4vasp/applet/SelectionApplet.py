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

import p4vasp.applet.Applet
import p4vasp.store
from p4vasp.applet import *
from p4vasp.Selection import *
from p4vasp.SystemPM import *

class SelectionApplet(p4vasp.applet.Applet.Applet,SelectionListener):
    def __init__(self,entry,set,setnone):
        p4vasp.applet.Applet.Applet.__init__(self)
        self.entry=entry
        self.set=set
        self.setnone=setnone
    def setExternalMode(self):
        raise "SelectionApplet.setExternalMode() not supported"
    def createPanel(self):
        raise "SelectionApplet.createPanel not supported"
    def isVisible(self):
        return 1

    def initUI(self):
        self.entry.connect("activate",self.on_selection_entry_activate_handler)
        self.entry.connect("changed",self.on_selection_entry_changed_handler)
        self.set.connect("clicked",self.on_selection_set_clicked_handler)
        self.setnone.connect("clicked",self.on_selection_none_clicked_handler)

    def setSelection(self, sel):
        if type(sel) is not type(""):
            sel=Selection(sel)
            s=getCurrentSystemPM()
            if s is not None:
                s=s.INITIAL_STRUCTURE
            sel=sel.encode(s)

        self.entry.set_text(sel)

    def on_selection_entry_activate_handler(self,*arg):
        selection().setSelection(self.getSelection())
        selection().notify(self)
    def on_selection_entry_changed_handler(self,*arg):
        selection().setSelection(self.getSelection())
        selection().notify(self)
    def on_selection_set_clicked_handler(self,*arg):
        selection().setSelection(self.getSelection())
        selection().toSet()
        self.setSelection(selection())
        selection().notify(self)
    def on_selection_none_clicked_handler(self,*arg):
        selection().setSelection([])
        self.setSelection(selection())
        selection().notify(self)

    def getSelectionText(self):
        return self.entry.get_text(sel)

    def notifyAtomSelection(self,sel,origin):
#    print "notifyAtomSelection",sel.encodeSimple()
        self.setSelection(sel)

    def getSelection(self):
        s=getCurrentSystemPM()
        if s is not None:
            s=s.INITIAL_STRUCTURE
        return Selection(self.entry.get_text(),s)

#SelectionApplet.store_profile=p4vasp.applet.Applet.AppletProfile(SelectionApplet,tagname="SelectionApplet")
SelectionApplet.store_profile=p4vasp.store.IgnoreProfile(SelectionApplet)
