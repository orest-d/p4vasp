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
import p4vasp.Selection
import gtk
import gobject
import pango

class StructureTreeModel(gtk.GenericTreeModel):
    def __init__(self,a):
        '''constructor for the model.'''
        gtk.GenericTreeModel.__init__(self)
        self.a=a
        self.struct=Structure()

    def getStructure(self):
        return self.a.getCurrentStructure()
#      return self.struct
    def setStructure(self,s=None):
        pass

    # the implementations for TreeModel methods are prefixed with on_
    def on_get_flags(self):
        '''returns the GtkTreeModelFlags for this particular type of model'''
        return gtk.TREE_MODEL_LIST_ONLY
    def on_get_n_columns(self):
        '''returns the number of columns in the model'''
        return 8
    def on_get_column_type(self, index):
        '''returns the type of a column in the model'''
        if index in [0,1]:
            return gobject.TYPE_STRING
        if index in [2,3,4]:
            return gobject.TYPE_FLOAT
        if index in [5,6,7]:
            return gobject.TYPE_BOOLEAN
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
#       print "get value",node,column
        s=self.getStructure()
        if s is None or len(s)==0 or node>=len(s):
            return None
        if column==0:
            return node+1
        elif column==1:
            try:
                e=s.getRecordForAtom(node).element
                if e not in [None,""]:
                    return s.getRecordForAtom(node).element
            except:
                pass
            return "#%d"%(s.speciesIndex(node)+1)

        elif column in [2,3,4]:
            return s[node][column-2]
        elif column in [5,6,7]:
            if s.isSelective():
                return s.selective[node][column-5]
            else:
                return None
        return "???"
    def on_iter_next(self, node):
        '''returns the next node at this level of the tree'''
        node+=1
        try:
            if node<len(self.getStructure()):
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

#    def update_all_cb(self,m,path,iter,l):
##      print "update",path
#      l1,l2=l
#      p=path[0]
#      if p<min(l1,l2):
#        print "changed", p
#        self.row_changed(path,iter)
#      else:
#        print "inserted", p
#        self.row_inserted(path,iter)
#
#    def update_all(self,l1,l2):
#      self.foreach(self.update_all_cb,(l1,l2))

class BuilderApplet(Applet):#p4vasp.Selection.SelectionListener
    menupath=["Edit","Builder"]
    def __init__(self):
        Applet.__init__(self)
        self.gladefile="builder.glade"
        self.gladename="applet_frame"
        self.noselflag=0
#    self.gladename="None"

#  def notifyAtomSelection(self,sel,origin):
#    if not self.noselflag:
#      print "notify",sel
#      self.treeselect.unselect_all()
#      for x in sel.getAtoms():
#        print "x",x
#        self.treeselect.select_path((x,))
    def updateSystem(self,x=None):
        self.updateStructure()
    def updateStructure(self):
#    print "update"
#    print "a"
#    print self.getCurrentStructure().basis
        s=self.getCurrentStructure()
        if s is not None:
            self.no_coord_upd=1
            if s.isCarthesian():
                self.carthesian_button.set_active(True)
            else:
                self.direct_button.set_active(True)
            if self.table_button.get_active():
                for i in range(3):
                    for j in range(3):
                        self.xml.get_widget("a%d%d"%(i+1,j+1)).set_text(str(s.basis[i][j]))
                self.treeview.set_model(StructureTreeModel(self))
                self.treeview.show_all()
#       self.model.setStructure(s)
            else:
                self.textview.get_buffer().set_text(s.toString())
        else:
            if self.table_button.get_active():
                for i in range(3):
                    for j in range(3):
                        self.xml.get_widget("a%d%d"%(i+1,j+1)).set_text("")
                self.treeview.set_model(StructureTreeModel(self))
                self.treeview.show_all()
#       self.model.setStructure(s)
            else:
                self.textview.get_buffer().set_text("")
#    systemlist().notifySystemChanged()
        self.no_coord_upd=0


    def getCurrentStructure(self):
        s=getCurrentSystemPM()
        if s is not None:
            return s.INITIAL_STRUCTURE

    def initUI(self):
        self.text_editor=self.xml.get_widget("text_editor")
        self.textview=self.xml.get_widget("textview")
        self.table_editor=self.xml.get_widget("table_editor")
        self.text_button=self.xml.get_widget("text_button")
        self.table_button=self.xml.get_widget("table_button")
        self.direct_button=self.xml.get_widget("direct_button")
        self.carthesian_button=self.xml.get_widget("carthesian_button")
        self.selective_button=self.xml.get_widget("selective_button")
        self.editor_frame=self.xml.get_widget("editor_frame")
        self.table_button.set_active(1)
        self.text_editor.hide()
        self.model=StructureTreeModel(self)
        self.treeview,self.treeviewscrolled=self.make_treeview(self.model,self.xml.get_widget("treeview"))
        self.table_editor.add(self.treeviewscrolled)
        self.textview.get_buffer().connect("changed",self.on_textbuff_changed_handler)
        for i in range(3):
            for j in range(3):
                self.xml.get_widget("a%d%d"%(i+1,j+1)).connect("activate",self.edited_b_h,i,j)
        self.updateStructure()
#    style=self.textview.get_style()
#    fd=style.font_desc
#    fd.set_family("serif,monospaced")
#    fd.set_style(pango.STYLE_ITALIC)
#    self.textview.set_style(style)
        self.treeselect=self.treeview.get_selection()
        self.treeselect.set_mode(gtk.SELECTION_MULTIPLE)
        self.treeselect.connect("changed",self.treeselect_h)

    def treeselect_h(self,ts):
        self.noselflag=1
        l=[]
        ts.selected_foreach(lambda m,p,i,l:l.append(p[0]),l)
        try:
          newspec = self.getCurrentStructure().speciesIndex(max(l))+1
          self.xml.get_widget("specie_entry").set_text(str(newspec))
        except:
          pass
        p4vasp.Selection.selection().setSelection(l)
        p4vasp.Selection.selection().notify(self)
        self.noselflag=0
    def edited_b_h(self,w,i,j):
#    print "e",i,j
        s=self.model.getStructure()
        s.basis[i][j]=float(eval(w.get_text()))
        systemlist().notifySystemChanged()
    def edited_h(self,renderer,path,txt,model,column):
#    print "edited",path,txt,column
        s=model.getStructure()
        if s:
            s[int(path)][column]=float(eval(txt))
        systemlist().notifySystemChanged()
    def edited_spec_h(self,renderer,path,txt,model):
#    print "edited",path,txt,column
        s=model.getStructure()
        if txt is not None and len(strip(txt)) and strip(txt).isalpha():
            s.info.getRecordForAtom(int(path)).element=txt
        systemlist().notifySystemChanged()
    def toggled_h(self,renderer,path,model,column):
#    print "toggled",path,column
        s=model.getStructure()
        if s:
            if s.isSelective():
                s.selective[int(path)][column]=not s.selective[int(path)][column]

    def make_treeview(self,model,view):
        # Create the view itself.
        if view is None:
            view = gtk.TreeView(model)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("#", renderer, text=0)
        column.set_resizable(0)
        view.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Spec.", renderer, text=1)
        renderer.set_property("editable",1)
        renderer.connect("edited",self.edited_spec_h,model)
        column.set_resizable(0)
        view.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_property("editable",1)
        renderer.connect("edited",self.edited_h,model,0)
        column = gtk.TreeViewColumn("X", renderer, text=2)
        column.set_resizable(1)
        view.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_property("editable",1)
        renderer.connect("edited",self.edited_h,model,1)
        column = gtk.TreeViewColumn("Y", renderer, text=3)
        column.set_resizable(1)
        view.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_property("editable",1)
        renderer.connect("edited",self.edited_h,model,2)
        column = gtk.TreeViewColumn("Z", renderer, text=4)
#    column.set_property("sizing",gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_resizable(1)
        view.append_column(column)

        renderer = gtk.CellRendererToggle()
#    renderer.set_property("editable",1)
        renderer.set_property("activatable",True)
        renderer.set_property("xalign",0.0)
#    renderer.set_property("active",5)
        renderer.connect("toggled",self.toggled_h,model,0)
        column = gtk.TreeViewColumn("SX", renderer)
        column.set_resizable(False)
        column.add_attribute(renderer,"active",5)
        view.append_column(column)

        renderer = gtk.CellRendererToggle()
#    renderer.set_property("editable",1)
#    renderer.set_property("active",6)
        renderer.set_property("activatable",True)
        renderer.set_property("xalign",0.0)
        renderer.connect("toggled",self.toggled_h,model,1)
        column = gtk.TreeViewColumn("SY", renderer)
#   column.set_resizable(False)
        column.add_attribute(renderer,"active",6)
        view.append_column(column)

        renderer = gtk.CellRendererToggle()
#    renderer.set_property("editable",1)
        renderer.set_property("activatable",True)
        renderer.set_property("xalign",0.0)
        renderer.connect("toggled",self.toggled_h,model,2)
        column = gtk.TreeViewColumn("SZ", renderer)
#    column.set_property("fixed-width",20)
#    column.set_property("sizing",gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(False)
        column.add_attribute(renderer,"active",7)
        view.append_column(column)

        view.show()

        # Create scrollbars around the view.
        scrolled = gtk.ScrolledWindow()
        scrolled.add(view)
        scrolled.show()

        return view,scrolled

    def textview2struct(self):
#    print "before tv2s",len(self.getCurrentStructure())
        try:
            b=self.textview.get_buffer()
            t=b.get_text(b.get_start_iter(),b.get_end_iter(),True)
            s=Structure()
            s.parse(t)
            self.getCurrentStructure().setStructure(s)

            self.no_coord_upd=1
            if s.isCarthesian():
                self.carthesian_button.set_active(True)
            else:
                self.direct_button.set_active(True)
#      systemlist().notifySystemChanged()
        except ParseException:
            msg().error(str(sys.exc_info()[1]))
        except:
            msg().exception()
        else:
            msg().status("OK")
        self.no_coord_upd=0
#    print "after tv2s",len(self.getCurrentStructure())

    def on_view_button_toggled_handler(self,w,*arg):
#    print "view",self.table_button.get_active(),self.text_button.get_active()
        if self.table_button.get_active():
            self.textview2struct()
            self.text_editor.hide()
            self.table_editor.show()
            self.updateStructure()
            systemlist().notifySystemChanged()
        else:
            self.text_editor.show()
            self.table_editor.hide()
        self.updateStructure()

    def on_coord_button_toggled_handler(self,w,*arg):
#    print "coord",self.direct_button.get_active(),self.carthesian_button.get_active()
        if not self.no_coord_upd:
            if self.direct_button.get_active():
                if self.text_button.get_active():
                    self.textview2struct()
                self.getCurrentStructure().setDirect()
            else:
                if self.text_button.get_active():
                    self.textview2struct()
                self.getCurrentStructure().setCarthesian()
            self.updateStructure()
    def on_selective_button_toggled_handler(self,w,*arg):
        if self.text_button.get_active():
            self.textview2struct()
        if self.selective_button.get_active():
            self.getCurrentStructure().setSelective(1)
        else:
            self.getCurrentStructure().setSelective(0)
        self.updateStructure()
#  def on_textview_update_handler(self,w,*arg):
#    print "upd"
#    self.textview2struct()
    def on_textbuff_changed_handler(self,w,*arg):
        self.textview2struct()

    def on_new_specie_button_clicked_handler(self,w,*arg):
        s=self.getCurrentStructure()
        s.appendAtomOfNewSpecie((0.0,0.0,0.0))
        self.updateStructure()
        systemlist().notifySystemChanged()

    def on_new_atom_button_clicked_handler(self,w,*arg):
        s=self.getCurrentStructure()
        spec=self.xml.get_widget("specie_entry").get_text()
        try:
            specie = int(spec)-1
        except:
            specie = len(s.info)-1
        specie=max(0,specie)
        s.appendAtom(specie,(0.0,0.0,0.0))
        self.updateStructure()
        systemlist().notifySystemChanged()

    def on_del_button_clicked_handler(self,w,*arg):
        s=self.getCurrentStructure()
        s.remove(p4vasp.Selection.selection().getAtoms())
        p4vasp.Selection.selection().setSelection([])
        p4vasp.Selection.selection().notify(self)
        self.updateStructure()
        systemlist().notifySystemChanged()

    def on_sel_button_clicked_handler(self,w,*arg):
        s=self.getCurrentStructure()
        s.setSelective()
        for i in p4vasp.Selection.selection().getAtoms():
            if i<len(s):
                s.selective[i]=(1,1,1)
        self.updateStructure()
        systemlist().notifySystemChanged()

    def on_unsel_button_clicked_handler(self,w,*arg):
        s=self.getCurrentStructure()
        s.setSelective()
        for i in p4vasp.Selection.selection().getAtoms():
            if i<len(s):
                s.selective[i]=(0,0,0)
        self.updateStructure()
        systemlist().notifySystemChanged()

    def on_rescale_button_clicked_handler(self,w,*arg):
        s=self.getCurrentStructure()
        s.correctScaling()
        self.updateStructure()
        systemlist().notifySystemChanged()

    def on_cuc_button_clicked_handler(self,w,*arg):
        s=self.getCurrentStructure()
        s.toCenteredUnitCell()
        self.updateStructure()
        systemlist().notifySystemChanged()

    def on_tuc_button_clicked_handler(self,w,*arg):
        s=self.getCurrentStructure()
        s.toUnitCell()
        self.updateStructure()
        systemlist().notifySystemChanged()

    def on_remove_duplicate_button_clicked_handler(self,w,*arg):
        s=self.getCurrentStructure()
        s.removeDuplicate()
        self.updateStructure()
        systemlist().notifySystemChanged()

BuilderApplet.store_profile=AppletProfile(BuilderApplet,tagname="Builder")
