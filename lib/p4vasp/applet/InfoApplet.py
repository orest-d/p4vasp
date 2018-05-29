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


from p4vasp.util import ParseException
from p4vasp import *
from p4vasp.store import *
from p4vasp.applet.Applet import *
import gtk
import gobject
import pango


class InfoApplet(Applet):
    menupath=["Edit","Info"]
    def __init__(self):
        Applet.__init__(self)
        self.gladefile="info.glade"
        self.gladename="applet_frame"

    def updateSystem(self,x=None):
        import time
        p=self.system.DESCRIPTION
        if p is not None:
            p=str(p)
            self.description_textview.get_buffer().set_text(p)
        else:
            self.description_textview.get_buffer().set_text("")
        s=""
        if self.system.NAME is not None:
            s+="Name:%s\n"%str(self.system.NAME)
        else:
            s+="Unnamed.\n"
        if self.system.DATE is not None:
            s+="Date:%s\n"%str(time.strftime("%Y-%m-%d %H:%M:%S",self.system.DATE))
        if self.system.PROGRAM is not None:
            s+="Program:%s\n"%str(self.system.PROGRAM)
        if self.system.VERSION is not None:
            s+="Version:%s\n"%str(self.system.VERSION)
        if self.system.SUBVERSION is not None:
            s+="Subversion:%s\n"%str(self.system.SUBVERSION)
        if self.system.PLATFORM is not None:
            s+="Platform:%s\n"%str(self.system.PLATFORM)
        if self.system.KEYWORDS is not None:
            s+="Keywords:%s\n"%str(self.system.KEYWORDS)
        if self.system.URL is not None:
            s+="URL:%s\n"%str(self.system.URL)
        if self.system.PATH is not None:
            s+="Path:%s\n"%str(self.system.PATH)
        if self.system.FREE_ENERGY is not None:
            s+="Free energy:%s eV\n"%str(self.system.FREE_ENERGY)
        if self.system.E_FERMI is not None:
            s+="Fermi energy:%s eV\n"%str(self.system.E_FERMI)


        #self.label.set_markup(True)
        self.label.set_text(s)

    def initUI(self):
        self.label = self.xml.get_widget("info_label")
        self.description_textview=self.xml.get_widget("description_textview")

#BuilderApplet.store_profile=AppletProfile(BuilderApplet,tagname="Builder")
