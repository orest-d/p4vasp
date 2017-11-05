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


from p4vasp import *
from p4vasp.store import *
from p4vasp.applet.Applet import *
from p4vasp.Structure import *
from p4vasp.SystemPM import *
import gtk
import gobject


class NewApplet(Applet):
    menupath=["Edit","New"]
    def __init__(self):
        Applet.__init__(self)
        self.gladefile="new.glade"
        self.gladename="applet_frame"
        self.creation=SetupPM()
#    self.gladename="None"

    def updateSystem(self):
        self.step_menu=gtk.Menu()
        s=self.system
        pop=["Empty"]
        if s is not None:
            try:
                p=s["INITIAL_STRUCTURE"]
                if p.status != p.ERROR:
                    pop.append("Initial structure")
            except:
                pass
            try:
                p=s["FINAL_STRUCTURE"]
                if p.status != p.ERROR:
                    pop.append("Final structure")
            except:
                pass

            p=s.DESCRIPTION
            if p is not None:
                p=str(p)
                self.description_textview.get_buffer().set_text(p)

            p=s.STRUCTURE_SEQUENCE_L
            if p is not None and len(p):
#        pop.append("Step with minimal energy")
#        pop.append("Step with minimal force")
                for i in range(len(p)):
                    pop.append("%3d"%i)

        self.step_combo.set_popdown_strings(pop)
        self.step_combo.show()

    def updateImportDescription(self):
        t=""
        s=getCurrentSystemPM()
        if s.NAME is not None:
            t+="<tt>Import from:</tt>%s\n"%s.NAME
        if s.URL is not None:
            t+="<tt>URL:        </tt>%s\n"%s.URL
        se=strip(self.step_entry.get_text())
        try:
            n=int(se)
            t+="<tt>Step:       </tt>%d\n"%n
        except:
            if len(se):
                if upper(se[0])=="I":
                    t+="<tt>            </tt>Initial step\n"
                elif upper(se[0])=="F":
                    t+="<tt>            </tt>Final step\n"
#       elif upper(se).find("ENERGY")!=-1:
#          t+="<tt>            </tt>Step with minimal energy\n"
#       elif upper(se).find("FORCE")!=-1:
#          t+="<tt>            </tt>Step with minimal force\n"
        if len(t):
            t="<tt>Import from:</tt>\n"+t
        self.importlabel.set_markup(t)

    def updateCreation(self):
        s=getCurrentSystemPM()
        self.creation=SetupPM(s)
        name=self.nameentry.get_text()
        self.creation.INCAR["SYSTEM"]=name
        if self.import_button.get_active():
            self.creation=SetupPM(s)
            name=self.nameentry.get_text()
            self.creation.INCAR["SYSTEM"]=name
            self.updateImportDescription()
#      print "updateCreation",self.creation.NAME
            se=strip(self.step_entry.get_text())
            buff=self.description_textview.get_buffer()
            start=buff.get_start_iter()
            end=buff.get_end_iter()
            self.creation.DESCRIPTION=str(buff.get_text(start,end))
            try:
                n=int(se)
                try:
                    struct=s.STRUCTURE_SEQUENCE_L[n]
                    if n is not None:
                        self.creation.INITIAL_STRUCTURE.setStructure(struct)
                except:
                    msg().exception()
                    self.creation.INITIAL_STRUCTURE=Structure()
            except:
                if len(se):
                    if upper(se[0])=="I":
                        if s.INITIAL_STRUCTURE is not None:
                            self.creation.INITIAL_STRUCTURE.setStructure(s.INITIAL_STRUCTURE)
                        else:
                            self.creation.INITIAL_STRUCTURE=Structure()

                    elif upper(se[0])=="F":
                        if s.FINAL_STRUCTURE is not None:
                            self.creation.INITIAL_STRUCTURE.setStructure(s.FINAL_STRUCTURE)
                        else:
                            self.creation.INITIAL_STRUCTURE=Structure()
        else:
            self.creation=SetupPM()
            name=self.nameentry.get_text()
            self.creation.INCAR["SYSTEM"]=name

#         elif upper(se).find("ENERGY")!=-1:
#            t+="<tt>            </tt>Step with minimal energy\n"
#         elif upper(se).find("FORCE")!=-1:
#            t+="<tt>            </tt>Step with minimal force\n"



    def initUI(self):
        self.importlabel=self.xml.get_widget("importlabel")
        self.description_textview=self.xml.get_widget("description_textview")
        self.step_combo=self.xml.get_widget("step_combo")
        self.step_entry=self.xml.get_widget("step_entry")
        self.nameentry=self.xml.get_widget("nameentry")
        self.import_frame=self.xml.get_widget("import_frame")
        self.import_button=self.xml.get_widget("import_button")
        self.updateSystem()

#  def on_nameentry_activate_handler(self,w,*arg):
#    pass
##    print "name"
    def on_import_button_toggled_handler(self,w,*arg):
#    print "import"
        if self.import_button.get_active():
            self.import_frame.show()
        else:
            self.import_frame.hide()

    def on_new_button_clicked_handler(self,w,*arg):
        self.updateCreation()
        systemlist().activate(self.creation)
    def on_step_changed_handler(self,w,*arg):
#    print "step",arg
        self.updateImportDescription()

NewApplet.store_profile=AppletProfile(NewApplet,tagname="NewApplet")
