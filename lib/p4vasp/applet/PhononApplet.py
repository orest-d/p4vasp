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
from p4vasp.Structure import *
from p4vasp.SystemPM import *
import p4vasp.Selection
import gtk
import gobject
import pango
from p4vasp.Dyna import Dyna,dynaPublisher

class KPathTreeModel(gtk.GenericTreeModel):
    def __init__(self,dyna):
        '''constructor for the model.'''
        gtk.GenericTreeModel.__init__(self)
        self.dyna=dyna

    # the implementations for TreeModel methods are prefixed with on_
    def on_get_flags(self):
        '''returns the GtkTreeModelFlags for this particular type of model'''
        return gtk.TREE_MODEL_LIST_ONLY
    def on_get_n_columns(self):
        '''returns the number of columns in the model'''
        return 8
    def on_get_column_type(self, index):
        '''returns the type of a column in the model'''
        if index == 0 or index == 4:
            return gobject.TYPE_STRING
        if index in [1,2,3,5,6,7]:
            return gobject.TYPE_FLOAT
        return gobject.TYPE_STRING

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
        if column==0:
            return self.dyna.labels[node][0]
        if column==4:
            return self.dyna.labels[node][1]
        if column in (1,2,3):
            return self.dyna.segments[node][0][column-1]
        if column in (5,6,7):
            return self.dyna.segments[node][1][column-5]
        return "???"
    def on_iter_next(self, node):
        '''returns the next node at this level of the tree'''
        node+=1

        try:
            if node<len(self.dyna.segments):
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
        if node is None:
          return len(self.dyna.segments)
        return 0
    def on_iter_n_children(self, node):
        '''returns the number of children of this node'''
        return 0
    def on_iter_nth_child(self, node, n):
        '''returns the nth child of this node'''
        if node is None:
          return n
        return None
    def on_iter_parent(self, node):
        '''returns the parent of this node'''
        return None

class PhononApplet(Applet):
    menupath=["Mechanics","Phonons k-points path"]
    def __init__(self):
        Applet.__init__(self)
        self.gladefile="phonons.glade"
        self.gladename="applet_frame"
        self.selected=None
    def updateSystem(self,x=None):
        s=self.getCurrentStructure()
        s.updateRecipBasis()
        self.b11.set_text(str(s.rbasis[0][0]))
        self.b12.set_text(str(s.rbasis[0][1]))
        self.b13.set_text(str(s.rbasis[0][2]))
        self.b21.set_text(str(s.rbasis[1][0]))
        self.b22.set_text(str(s.rbasis[1][1]))
        self.b23.set_text(str(s.rbasis[1][2]))
        self.b31.set_text(str(s.rbasis[2][0]))
        self.b32.set_text(str(s.rbasis[2][1]))
        self.b33.set_text(str(s.rbasis[2][2]))
        s=getCurrentSystemPM()
        primitive_cell = s.PRIMITIVE_STRUCTURE

        dyna=s.DYNA
        if dyna is None:
            dyna=Dyna()
            dyna.addSegment()
        if primitive_cell is not None:
            dyna=dyna.withBasis(primitive_cell.basis).reciprocal()

        self.model = KPathTreeModel(dyna)
        self.stepsPerSegment.set_text(str(dyna.size))
        dynaPublisher().updateDyna(dyna)
        self.treeview.set_model(self.model)

    def getCurrentStructure(self):
        s=getCurrentSystemPM()
        if s is not None:
            return s.INITIAL_STRUCTURE if s.PRIMITIVE_STRUCTURE is None else s.PRIMITIVE_STRUCTURE

    def initUI(self):
        self.table_editor=self.xml.get_widget("table_editor")
        self.direct_button=self.xml.get_widget("direct_button")
        self.carthesian_button=self.xml.get_widget("carthesian_button")
        self.b11=self.xml.get_widget("b11")
        self.b12=self.xml.get_widget("b12")
        self.b13=self.xml.get_widget("b13")
        self.b21=self.xml.get_widget("b21")
        self.b22=self.xml.get_widget("b22")
        self.b23=self.xml.get_widget("b23")
        self.b31=self.xml.get_widget("b31")
        self.b32=self.xml.get_widget("b32")
        self.b33=self.xml.get_widget("b33")
        self.stepsPerSegment=self.xml.get_widget("stepsPerSegment")
        self.b11.set_editable(False)
        self.b12.set_editable(False)
        self.b13.set_editable(False)
        self.b21.set_editable(False)
        self.b22.set_editable(False)
        self.b23.set_editable(False)
        self.b31.set_editable(False)
        self.b32.set_editable(False)
        self.b33.set_editable(False)
        self.stepsPerSegment.set_editable(True)

        self.model=KPathTreeModel(Dyna())
        self.treeview,self.treeviewscrolled=self.make_treeview(self.model,self.xml.get_widget("treeview"))
        self.table_editor.add(self.treeviewscrolled)
        self.treeselect=self.treeview.get_selection()
        self.treeselect.set_mode(gtk.SELECTION_SINGLE)
        self.treeselect.connect("changed",self.treeselect_h)
    def treeselect_h(self,ts):
        l=[]
        ts.selected_foreach(lambda m,p,i,l:l.append(p[0]),l)
        self.selected=l[0] if len(l) else None

    def edited_h(self,renderer,path,txt,model,column):
        value = txt
        row=int(path)
        if column==0:
            self.model.dyna.labels[row][0]=value
        if column==4:
            self.model.dyna.labels[row][1]=value
        if column in (1,2,3):
            value= float(value.replace(",","."))
            newpoint=Vector(self.model.dyna.segments[row][0])
            newpoint[column-1]=float(str(value).replace(",","."))
            newsegment=(newpoint,self.model.dyna.segments[row][1])
            self.model.dyna.segments[row]=newsegment
        if column in (5,6,7):
            value= float(value.replace(",","."))
            newpoint=Vector(self.model.dyna.segments[row][1])
            newpoint[column-5]=float(str(value).replace(",","."))
            newsegment=(self.model.dyna.segments[row][0],newpoint)
            self.model.dyna.segments[row]=newsegment
        dynaPublisher().updateDyna(self.model.dyna)

    def make_treeview(self,model,view):
        # Create the view itself.
        if view is None:
            view = gtk.TreeView(model)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Label 1", renderer, text=0)
        renderer.set_property("editable",1)
        renderer.connect("edited",self.edited_h,model,0)
        column.set_resizable(0)
        view.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_property("editable",1)
        renderer.connect("edited",self.edited_h,model,1)
        column = gtk.TreeViewColumn("kx1", renderer, text=1)
        column.set_resizable(1)
        view.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_property("editable",1)
        renderer.connect("edited",self.edited_h,model,2)
        column = gtk.TreeViewColumn("ky1", renderer, text=2)
        column.set_resizable(1)
        view.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_property("editable",1)
        renderer.connect("edited",self.edited_h,model,3)
        column = gtk.TreeViewColumn("kz1", renderer, text=3)
        column.set_resizable(1)
        view.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Label 2", renderer, text=4)
        renderer.set_property("editable",1)
        renderer.connect("edited",self.edited_h,model,4)
        column.set_resizable(0)
        view.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_property("editable",1)
        renderer.connect("edited",self.edited_h,model,5)
        column = gtk.TreeViewColumn("kx2", renderer, text=5)
        column.set_resizable(1)
        view.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_property("editable",1)
        renderer.connect("edited",self.edited_h,model,6)
        column = gtk.TreeViewColumn("ky2", renderer, text=6)
        column.set_resizable(1)
        view.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_property("editable",1)
        renderer.connect("edited",self.edited_h,model,7)
        column = gtk.TreeViewColumn("kz2", renderer, text=7)
#    column.set_property("sizing",gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_resizable(1)
        view.append_column(column)

        view.show()

        # Create scrollbars around the view.
        scrolled = gtk.ScrolledWindow()
        scrolled.add(view)
        scrolled.show()

        return view,scrolled

    def on_stepsPerSegment_activate_handler(self,w,*arg):
        self.model.dyna.size=int(self.stepsPerSegment.get_text())
        dynaPublisher().updateDyna(self.model.dyna)
    def on_add_clicked_handler(self,w,*arg):
        if self.selected is not None:
            self.model.dyna.insertSegment(self.selected)
            p=str(self.selected)
            self.model.row_inserted(p,self.model.get_iter(p))
        else:
            self.model.dyna.addSegment()
            p=str(len(self.model.dyna.segments)-1)
            self.model.row_inserted(p,self.model.get_iter(p))
        dynaPublisher().updateDyna(self.model.dyna)
    def on_delete_clicked_handler(self,w,*arg):
        if self.selected is not None:
            self.model.dyna.deleteSegment(self.selected)
            self.model.row_deleted(str(self.selected))
        dynaPublisher().updateDyna(self.model.dyna)

PhononApplet.store_profile=AppletProfile(PhononApplet,tagname="Phonons")
