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

class QueryTreeModel(gtk.GenericTreeModel):
    def __init__(self,query,column_type):
        '''constructor for the model.'''
        gtk.GenericTreeModel.__init__(self)
        self.query=query
        self.column_type=column_type
    # the implementations for TreeModel methods are prefixed with on_

    def on_get_flags(self):
        '''returns the GtkTreeModelFlags for this particular type of model'''
        return gtk.TREE_MODEL_LIST_ONLY
    def on_get_n_columns(self):
        '''returns the number of columns in the model'''
        return 4
    def on_get_column_type(self, index):
        '''returns the type of a column in the model'''
        return self.column_type[index]

    def on_get_path(self, node):
        '''returns the tree path (a tuple of indices at the various
        levels) for a particular node.'''
        return (node,)
    def on_get_iter(self, path):
        '''returns the node corresponding to the given path.  In our
        case, the node is the path'''
        return path[0]
    def on_get_value(self, node, column):
        '''returns the value stored in a particular column for the node'''
#       print "get value",node,column
#        print l,node,column,l[column],l[0],l[1]
        if column:
#         print self.query[node]
            di,q=self.query.get(node)
            if column==1:
                return self.query.container[di].name
            if q is not None:
                return q[column-1]
        else:
            return node+1

    def on_iter_next(self, node):
        '''returns the next node at this level of the tree'''
        node+=1
        try:
            if node<len(self.query):
                return node
        except:
            pass
        return None
    def on_iter_children(self, node):
        '''returns the first child of this node'''
        if node == None: # top of tree
            return 0
        return None
    def on_iter_has_child(self, node):
        '''returns true if this node has children'''
        return 0
    def on_iter_n_children(self, node):
        '''returns the number of children of this node'''
        return 0
    def on_iter_nth_child(self, node, n):
        '''returns the nth child of this node'''
        return None
    def on_iter_parent(self, node):
        '''returns the parent of this node'''
        return None

class DBApplet(Applet):
    menupath=["Database","Query"]
    column_dbvariable="#CALC.id, #USERINFO.username, #CALC.name, #CALC.cdatetime, #CALC.keywords"
    column_type      =[gobject.TYPE_INT,gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING, gobject.TYPE_STRING,gobject.TYPE_STRING]
    column_label     =[("#",0),("DB",1),("user",1),("name",1),("date",1),("keywords",1)]
    def __init__(self):
        Applet.__init__(self)
        self.gladefile="db.glade"
        self.gladename="applet_frame"
        self.noselflag=0
        self.database=getDatabase()
        self.selected_id =None
        self.selected_dbi=None
        if self.database is not None:
            self.database.connect()
        else:
            msg().error("Can't get the database, please check the configuration.")
#    self.gladename="None"

    def updateSystem(self,x=None):
        pass

    def updateDB(self,q=None):
        if q is None:
            q=self.getQuery()
        self.model=QueryTreeModel(self.database.query(*q),self.column_type)
        self.treeview.set_model(self.model)
        self.treeview.show_all()

    def initUI(self):
        self.query=self.xml.get_widget("query_entry")
        self.model=QueryTreeModel(self.database.query(*self.getQuery("")),self.column_type)
        self.treeview,self.treeviewscrolled=self.make_treeview(self.model,self.xml.get_widget("treeview"))
#    style=self.textview.get_style()
#    fd=style.font_desc
#    fd.set_family("serif,monospaced")
#    fd.set_style(pango.STYLE_ITALIC)
#    self.textview.set_style(style)
        self.treeview.set_model(self.model)
        self.treeview.show_all()
        self.treeselect=self.treeview.get_selection()
        self.treeselect.set_mode(gtk.SELECTION_MULTIPLE)
        self.treeselect.connect("changed",self.treeselect_h)

    def treeselect_h(self,ts):
        l=[]
        self.selected_id =None
        self.selected_dbi=None
        ts.selected_foreach(lambda m,p,i,l:l.append(p[0]),l)
        if len(l):
            di,rec=self.model.query.get(l[0])
            dbi=self.model.query.container[di]
            Id=rec[0]
            print "selected",Id,dbi.name,di,rec
            systemlist().setTemporaryActive(SQLSystemPM(dbi,Id))
            self.selected_id =Id
            self.selected_dbi=dbi
            self.xml.get_widget("deleteButton").set_sensitive(self.canDeleteSelected())


    def make_treeview(self,model,view):
        # Create the view itself.
        if view is None:
            view = gtk.TreeView(model)
        for i in xrange(len(self.column_label)):
            label,resizable=self.column_label[i]
            renderer = gtk.CellRendererText()
            column = gtk.TreeViewColumn(label, renderer, text=i)
            column.set_resizable(resizable)
            view.append_column(column)

        view.show()

        # Create scrollbars around the view.
        scrolled = gtk.ScrolledWindow()
        scrolled.add(view)
        scrolled.show()

        return view,scrolled

    def getQuery(self,qs=None):
        if qs is None:
            qs=self.query.get_text()
        keys=split(qs)
#    keys=split(self.xml.get_widget("key_entry").get_text())
        l=[]
        for k in keys:
            l.append('((#CALC.keywords LIKE "%%%s%%") OR (#CALC.name LIKE "%%%s%%") OR (#USERINFO.username LIKE "%%%s%%"))'%(k,k,k))
        s=join(l," AND ")

        s=strip(s)
        if len(s):
            s="WHERE "+s

        return self.column_dbvariable,"FROM #CALC JOIN #USERINFO ON #CALC.user_id=#USERINFO.id",s
    def on_query_entry_activate_handler(self,*argv):
        self.updateDB()
    def on_key_entry_activate_handler(self,*argv):
        self.updateDB()
    def on_searchButton_clicked_handler(self,*argv):
        self.updateDB()

    def canDeleteSelected(self):
        if self.selected_id is not None:
            try:
                user_id=self.selected_dbi.fetchvalue("SELECT user_id FROM #CALC WHERE id=%d"%self.selected_id)
            except:
                return 0
            if user_id is not None and user_id==self.selected_dbi.getUserID():
                return 1
        return 0


    def on_deleteButton_clicked_handler(self,*argv):
        if self.selected_id is not None:
            if not self.canDeleteSelected():
                msg().confirm_error("Not allowed to delete this database entry.")
            else:
                name,user=self.selected_dbi.fetchone(
                "SELECT #CALC.name, #USERINFO.username FROM #CALC JOIN #USERINFO ON #CALC.user_id=#USERINFO.id WHERE #CALC.id=%d"%self.selected_id)
                dialog=gtk.MessageDialog(None,gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_INFO,gtk.BUTTONS_OK_CANCEL ,"Delete %s from the database %s ?"%(name,self.selected_dbi.name))
                if dialog.run() == gtk.RESPONSE_OK:
                    self.selected_dbi.removeCalculation(self.selected_id)
                    self.updateDB()
                dialog.destroy()

#BuilderApplet.store_profile=AppletProfile(BuilderApplet,tagname="Builder")
