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
from p4vasp.db import *
from p4vasp.SystemPM import *
from p4vasp.SQLSystemPM import *
from p4vasp.db import *
import p4vasp.Selection
import gtk
import gobject
import pango


class CommitApplet(Applet):
    menupath=["Database","Commit"]
    def __init__(self):
        Applet.__init__(self)
        self.gladefile="commit.glade"
        self.gladename="applet_frame"
        self.database=getDatabase()
        if self.database is not None:
            self.database.connect()
        else:
            msg().error("Can't get the database, please check the configuration.")
#    self.gladename="None"

    def updateSystem(self,x=None):
        import time
        self.calcname_entry.set_text(str(self.system.NAME))
        self.keywords_entry.set_text(str(self.system.KEYWORDS))
        d=self.system.DATE
        if d is None:
            d=time.localtime()
        self.date_entry.set_text(time.strftime("%Y-%m-%d %H:%M:%S",d))

        d=self.system.DESCRIPTION
        if d is not None:
            d=str(d)
        else:
            d=""
        self.description_textview.get_buffer().set_text(d)

    def createDBOpt(self):
        self.dbi_index=None
        omenu = self.xml.get_widget("db_opt")
        if omenu is None:
            return None
        menu=gtk.Menu()
        omenu.set_menu(menu)
        omenu.show()
        I=0
        for di in xrange(len(self.database)):
            d=self.database[di]
            if d.canCommit():
                item=gtk.MenuItem(d.name)
                item.connect("activate",self.on_dbitem_clicked_handler,di)
                if not d.isConnected():
                    item.set_sensitive(False)
                menu.append(item)
                item.show()
                if d.getDefaultCommit():
                    omenu.set_history(I)
                    self.on_dbitem_clicked_handler(None,di)
                I+=1

    def initUI(self):
        self.username_entry = self.xml.get_widget("username_entry")
        self.uid_entry      = self.xml.get_widget("uid_entry")
        self.calcname_entry = self.xml.get_widget("calcname_entry")
        self.keywords_entry = self.xml.get_widget("keywords_entry")
        self.description_textview =self.xml.get_widget("description_textview")
        self.date_entry     =self.xml.get_widget("date_entry")

        self.createDBOpt()

    def canDeleteSelected(self):
        if self.selected_id is not None:
            try:
                user_id=self.selected_dbi.fetchvalue("SELECT user_id FROM #CALC WHERE id=%d"%self.selected_id)
            except:
                return 0
            if user_id is not None and user_id==self.selected_dbi.getUserID():
                return 1
        return 0


    def storeGen(self):
        from p4vasp.Property import FilterPropertyManager
        d=self.database[self.dbi_index]
        name=self.calcname_entry.get_text()
        keywords=self.keywords_entry.get_text()

        buff=self.description_textview.get_buffer()
        start=buff.get_start_iter()
        end=buff.get_end_iter()
        description=str(buff.get_text(start,end))

        date=self.date_entry.get_text()

        disable=[]
        if not self.xml.get_widget("sequence_checkbutton").get_active():
            disable.append("STRUCTURE_SEQUENCE")
            disable.append("STRUCTURE_SEQUENCE_L")
        if not self.xml.get_widget("forces_checkbutton").get_active():
            disable.append("FORCES_SEQUENCE")
            disable.append("FORCES_SEQUENCE_L")
        if not self.xml.get_widget("dos_checkbutton").get_active():
            disable.append("TOTAL_DOS")
        if not self.xml.get_widget("ldos_checkbutton").get_active():
            disable.append("PARTIAL_DOS")
            disable.append("PARTIAL_DOS_L")

        try:
            d.addUser()
            fsystem=FilterPropertyManager(self.system,disable)
            g=d.storePMgen(fsystem,name=name,keywords=keywords,date=date,description=description)
            try:
                while 1:
                    g.next()
                    yield 1
            except StopIteration:
                pass

            msg().confirm("The calculation '%s' has been comitted to the database '%s'"%(name,d.name))
        except Exception, e:
            msg().confirm_error("Commit exception: %s"%str(e))
            msg().exception()

    def on_commit_button_clicked_handler(self,*argv):
        scheduler().schedule(self.storeGen())


    def on_dbitem_clicked_handler(self,dummy_item,di):
        self.dbi_index=di
        if di is not None:
            self.uid_entry.set_text(self.database[di].getUserUID())
            self.username_entry.set_text(self.database[di].getUserName())
        else:
            self.uid_entry.set_text("")
            self.username_entry.set_text("")

#BuilderApplet.store_profile=AppletProfile(BuilderApplet,tagname="Builder")
