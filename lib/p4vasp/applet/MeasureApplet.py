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
from p4vasp.Structure import *
from p4vasp.SystemPM import *
import gtk
import gobject
import pango
from p4vasp.Selection import selection, SelectionListener

class DistanceTreeModel(gtk.GenericTreeModel):
    def __init__(self,s,sel):
        '''constructor for the model.'''
        gtk.GenericTreeModel.__init__(self)
        self.s=s
        self.sel=sel

    # the implementations for TreeModel methods are prefixed with on_
    def on_get_flags(self):
        '''returns the GtkTreeModelFlags for this particular type of model'''
        return gtk.TREE_MODEL_LIST_ONLY
    def on_get_n_columns(self):
        return len(self.sel)+1
    def on_get_column_type(self, index):
        '''returns the type of a column in the model'''
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
        if node>=len(self.sel) or column>len(self.sel):
            return "<span background=\"#ffffff\" foreground=\"#333333\">?</span>"
        if column>0:
            i,nx,ny,nz=self.sel[node]
            v1=self.s[i]+self.s.basis[0]*nx+self.s.basis[1]*ny+self.s.basis[2]*nz
#         print "from %3d (%3d %3d %3d)\n  %s\n  %s"%(i,nx,ny,nz,str(self.s[i]),str(v1))
            i,nx,ny,nz=self.sel[column-1]
            v2=self.s[i]+self.s.basis[0]*nx+self.s.basis[1]*ny+self.s.basis[2]*nz
#         print "to   %3d (%3d %3d %3d)\n  %s\n  %s"%(i,nx,ny,nz,str(self.s[i]),str(v2))
            l=(v1-v2).length()
#         print "     length=%+14.8f delta=%s"%(l,str(v1-v2))
            if l==0:
                return "<span background=\"#ffffce\" foreground=\"#0000ff\"><tt>    0       </tt></span>"
            elif l<=3.0:
                return "<span background=\"#ffffce\" foreground=\"#000000\"><tt>%12.6f</tt></span>"%l
            else:
                return "<span background=\"#ffffff\" foreground=\"#000000\"><tt>%12.6f</tt></span>"%l

        else:
            i,nx,ny,nz=self.sel[node]
            return "<b>%d</b> (%d %d %d)"%(i+1,nx,ny,nz)
    def on_iter_next(self, node):
        '''returns the next node at this level of the tree'''
        node+=1
        if node<len(self.sel):
            return node
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

class ZMatTreeModel(DistanceTreeModel):
    def on_get_n_columns(self):
        return 4
    def on_get_value(self, node, column):
        '''returns the value stored in a particular column for the node'''
#        print "zmat",node,column,len(self.s)
        if node>=len(self.sel) or column>len(self.sel):
            return "<span background=\"#ffffff\" foreground=\"#333333\">?</span>"
        if column>0:
            if node==0:
                return ""
            elif node==1 and column==1:
                try:
                    i,nx,ny,nz=self.sel[0]
                    v1=self.s[i]+self.s.basis[0]*nx+self.s.basis[1]*ny+self.s.basis[2]*nz
                    i,nx,ny,nz=self.sel[1]
                    v2=self.s[i]+self.s.basis[0]*nx+self.s.basis[1]*ny+self.s.basis[2]*nz
                    l=(v1-v2).length()
                    return "%12.6f"%l
                except:
                    msg().exception()
                    return "<span foreground=\"red\">???</span>"

            elif node==1 and column==2:
                return ""
            elif node==1 and column==3:
                return ""
            elif node==2 and column==1:
                try:
                    i,nx,ny,nz=self.sel[1]
                    v1=self.s[i]+self.s.basis[0]*nx+self.s.basis[1]*ny+self.s.basis[2]*nz
                    i,nx,ny,nz=self.sel[2]
                    v2=self.s[i]+self.s.basis[0]*nx+self.s.basis[1]*ny+self.s.basis[2]*nz
                    l=(v1-v2).length()
                    return "%12.6f"%l
                except:
                    msg().exception()
                    return "<span foreground=\"red\">???</span>"
            elif node==2 and column==2:
                try:
                    i,nx,ny,nz=self.sel[0]
                    a=self.s[i]+self.s.basis[0]*nx+self.s.basis[1]*ny+self.s.basis[2]*nz
                    i,nx,ny,nz=self.sel[1]
                    b=self.s[i]+self.s.basis[0]*nx+self.s.basis[1]*ny+self.s.basis[2]*nz
                    i,nx,ny,nz=self.sel[2]
                    c=self.s[i]+self.s.basis[0]*nx+self.s.basis[1]*ny+self.s.basis[2]*nz
                except:
                    msg().exception()
                    return "<span foreground=\"red\">???</span>"
                try:
                    angle=(a-b).angle(c-b)*180.0/pi
                    return "%+5.2f"%angle
                except:
                    return "<i>undef.</i>"
            elif node==2 and column==3:
                return ""
            else:
                try:
                    i,nx,ny,nz=self.sel[node-3]
                    a=self.s[i]+self.s.basis[0]*nx+self.s.basis[1]*ny+self.s.basis[2]*nz
                    i,nx,ny,nz=self.sel[node-2]
                    b=self.s[i]+self.s.basis[0]*nx+self.s.basis[1]*ny+self.s.basis[2]*nz
                    i,nx,ny,nz=self.sel[node-1]
                    c=self.s[i]+self.s.basis[0]*nx+self.s.basis[1]*ny+self.s.basis[2]*nz
                    i,nx,ny,nz=self.sel[node]
                    d=self.s[i]+self.s.basis[0]*nx+self.s.basis[1]*ny+self.s.basis[2]*nz
                except:
                    msg().exception()
                    return "<span foreground=\"red\">???</span>"
                if column==1:
                    l=(d-c).length()
                    return "%12.6f"%l
                elif column==2:
                    try:
                        angle=(b-c).angle(d-c)*180.0/pi
                        return "%+5.2f"%angle
                    except:
                        return "<i>undef.</i>"
                else:
                    try:
                        dihedral=(c-b).cross(a-b).angle((b-c).cross(d-c))
                        return "%+5.2f"%(dihedral*180.0/pi)
                    except:
                        return "<i>undef.</i>"
        else:
            i,nx,ny,nz=self.sel[node]
            return "<b>%d</b> (%d %d %d)"%(i+1,nx,ny,nz)


class MeasureApplet(Applet,SelectionListener):
    menupath=["Structure","Measure"]

    ZMAT_TYPE=1
    DIST_TYPE=2

    def __init__(self):
        Applet.__init__(self)
        self.gladefile="measure.glade"
        self.gladename="applet_frame"
#    self.gladename="None"
        self.showtype=self.ZMAT_TYPE
        self.step=None


    def notifyAtomSelection(self, sel,origin):
        self.updateSystem()

    def setSystem(self,s):
#    print "setSystem"
#    if s is not None:
#      print "URL",s.URL
        self.system=s
        if s is not None:
            self.system.require(self.required,self.updateSystem)
        self.updateSystem()

    def updateSystem(self,x=None):
#    print "updateSystem"
#    if self.system is not None:
#      print "URL",self.system.URL
        self.createStructureItems()
        self.updateTable()

    def updateTable(self,x=None):
        if self.showtype==self.DIST_TYPE:
            self.showDistances(self.getCurrentStructure(),selection())
        else:
            self.showZMat(self.getCurrentStructure(),selection())

    def createStructureItems(self):
        omenu = self.structureopt
        if omenu is None:
            return None
        menu=gtk.Menu()
        omenu.set_menu(menu)
        omenu.show()
        self.step=-1

        if self.system is not None:
            if self.system.INITIAL_STRUCTURE is not None:
                item=gtk.MenuItem("Initial positions")
                item.connect("activate",self.on_structureitem_clicked_handler,-1)
                menu.append(item)
                item.show()
#       print "initial"
            if self.system.FINAL_STRUCTURE is not None:
                item=gtk.MenuItem("Final positions")
                item.connect("activate",self.on_structureitem_clicked_handler,-2)
                menu.append(item)
                item.show()
#       print "final"
            seq=self.system.STRUCTURE_SEQUENCE_L
            if seq is not None:
                for i in range(len(seq)):
                    item=gtk.MenuItem("step %3d"%(i+1))
                    item.connect("activate",self.on_structureitem_clicked_handler,i)
                    menu.append(item)
                    item.show()
#          print "step",i
        else:
            msg().status("No system")

    def showDistances(self,s,sel):
        view=self.treeview
        s=Structure(s)
        s.setCarthesian()
        view.set_model(DistanceTreeModel(s,sel))
        for x in self.treeview.get_columns():
            view.remove_column(x)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("#", renderer, markup=0)
        view.append_column(column)
        renderer = gtk.CellRendererText()
        for i in range(len(sel)):
            n,nx,ny,nz=sel[i]
            column = gtk.TreeViewColumn("%d (%d %d %d)"%(n+1,nx,ny,nz), renderer, markup=i+1)
            view.append_column(column)
        view.show()

    def showZMat(self,s,sel):
        view=self.treeview
        s=Structure(s)
        s.setCarthesian()
        view.set_model(ZMatTreeModel(s,sel))
        for x in self.treeview.get_columns():
            view.remove_column(x)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("#", renderer, markup=0)
        view.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("distance", renderer, markup=1)
        view.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("angle", renderer, markup=2)
        view.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("dihedral", renderer, markup=3)
        view.append_column(column)

        view.show()

    def getCurrentStructure(self):
        if self.step == -1:
            return getCurrentSystemPM().INITIAL_STRUCTURE
        elif self.step == -2:
            return getCurrentSystemPM().FINAL_STRUCTURE
        elif self.step is None:
            return None
        else:
            return getCurrentSystemPM().STRUCTURE_SEQUENCE_L[self.step]


    def initUI(self):
        self.view_box=self.xml.get_widget("view_box")
        self.model=DistanceTreeModel(self.getCurrentStructure(),selection())
        self.treeview,self.treeviewscrolled=self.make_treeview(self.model,self.xml.get_widget("treeview"))
        self.view_box.add(self.treeviewscrolled)
        self.zmat_button=self.xml.get_widget("zmat_button")
        self.dist_button=self.xml.get_widget("dist_button")

        self.structureopt=self.xml.get_widget("structureopt")
        if self.zmat_button.get_active():
            self.showtype=self.ZMAT_TYPE
        if self.dist_button.get_active():
            self.showtype=self.DIST_TYPE

        self.updateSystem()

    def on_structureitem_clicked_handler(self,item,step):
        if step != self.step:
            self.step=step
            self.updateTable()

    def on_show_toggled_handler(self,*arg):
        if self.zmat_button.get_active():
            self.showtype=self.ZMAT_TYPE
        if self.dist_button.get_active():
            self.showtype=self.DIST_TYPE
        self.updateTable()

    def make_treeview(self,model,view):
        # Create the view itself.
        if view is None:
            view = gtk.TreeView(model)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("#", renderer, text=0)
        column.set_resizable(0)
        view.append_column(column)

        view.show()

        # Create scrollbars around the view.
        scrolled = gtk.ScrolledWindow()
        scrolled.add(view)
        scrolled.show()

        return view,scrolled


MeasureApplet.store_profile=AppletProfile(MeasureApplet,tagname="Measure")
