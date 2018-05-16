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


from p4vasp import *
from p4vasp.store import *
from p4vasp.applet.Applet import *
from p4vasp.Structure import *
from p4vasp.SystemPM import *
import gtk
import gobject


class MultiplyCellApplet(Applet):
    menupath=["Edit","Multiply cell"]
    showmode=Applet.EXTERNAL_ONLY_MODE
    def __init__(self):
        Applet.__init__(self)
        self.gladefile="multcell.glade"
        self.gladename="applet_frame"
        self.creation=SetupPM()
#    self.gladename="None"

    def updateSystem(self):
        pass

    def initUI(self):
        self.simplemultiply   = self.xml.get_widget("simplemultiply")
        self.advancedmultiply = self.xml.get_widget("advancedmultiply")
        self.simple_button    = self.xml.get_widget("simple_button")
        self.advanced_button  = self.xml.get_widget("advanced_button")
        self.advancedmultiply.hide()
        self.n1e  = self.xml.get_widget("n1entry")
        self.n2e  = self.xml.get_widget("n2entry")
        self.n3e  = self.xml.get_widget("n3entry")
        self.n11e  = self.xml.get_widget("n11entry")
        self.n12e  = self.xml.get_widget("n12entry")
        self.n13e  = self.xml.get_widget("n13entry")
        self.n21e  = self.xml.get_widget("n21entry")
        self.n22e  = self.xml.get_widget("n22entry")
        self.n23e  = self.xml.get_widget("n23entry")
        self.n31e  = self.xml.get_widget("n31entry")
        self.n32e  = self.xml.get_widget("n32entry")
        self.n33e  = self.xml.get_widget("n33entry")
        self.n1e.set_text("1")
        self.n2e.set_text("1")
        self.n3e.set_text("1")
        self.n11e.set_text("1")
        self.n12e.set_text("0")
        self.n13e.set_text("0")
        self.n21e.set_text("0")
        self.n22e.set_text("1")
        self.n23e.set_text("0")
        self.n31e.set_text("0")
        self.n32e.set_text("0")
        self.n33e.set_text("1")

        self.simplemultiply.show()
        self.updateSystem()

#  def on_nameentry_activate_handler(self,w,*arg):
#    pass
##    print "name"

    def on_simple_button_toggled_handler(self,w,*arg):
        if self.simple_button.get_active():
            self.advancedmultiply.hide()
            self.simplemultiply.show()
        else:
            self.advancedmultiply.show()
            self.simplemultiply.hide()

    def on_simplemultiply_button_clicked_handler(self,w,*arg):
#    print "simplemultiply"
#    print self.n1e.get_text(),self.n2e.get_text(),self.n3e.get_text()
        try:
            n1=int(self.n1e.get_text())
            n2=int(self.n2e.get_text())
            n3=int(self.n3e.get_text())
        except:
            msg().exception()
        s=getCurrentSystemPM()
        if s is None:
            msg().error("No valid system was selected.")
            return
        s=s.INITIAL_STRUCTURE
        if s is None:
            msg().error("The selected system does not contain a valid initial structure.")
            return
        s.setCarthesian()
        s.replicateCell(n1,n2,n3)
        systemlist().notifySystemChanged()
    def on_advancedmultiply_button_clicked_handler(self,w,*arg):
#    print "advancedmultiply"
#    print self.n11e.get_text(),self.n12e.get_text(),self.n13e.get_text()
#    print self.n21e.get_text(),self.n22e.get_text(),self.n23e.get_text()
#    print self.n31e.get_text(),self.n32e.get_text(),self.n33e.get_text()
        try:
            n11=int(self.n11e.get_text())
            n21=int(self.n21e.get_text())
            n31=int(self.n31e.get_text())
            n12=int(self.n12e.get_text())
            n22=int(self.n22e.get_text())
            n32=int(self.n32e.get_text())
            n13=int(self.n13e.get_text())
            n23=int(self.n23e.get_text())
            n33=int(self.n33e.get_text())
        except:
            msg().exception()
        s=getCurrentSystemPM()
        if s is None:
            msg().error("No valid system was selected.")
            return
        s=s.INITIAL_STRUCTURE
        if s is None:
            msg().error("The selected system does not contain a valid initial structure.")
            return
        ns=s.createMultiplied(n11,n12,n13,n21,n22,n23,n31,n32,n33)
        s.setStructure(ns)
        systemlist().notifySystemChanged()
MultiplyCellApplet.store_profile=AppletProfile(MultiplyCellApplet,tagname="MultiplyCell")
