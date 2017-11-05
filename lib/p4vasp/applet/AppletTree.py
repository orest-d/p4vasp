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



from p4vasp.store import *
from UserList import UserList
from types import *
from string import *
import gtk
import gobject

class AppletNode(UserList):
    frame=None
    def __init__(self,name="?",classname="",parent=None):
        UserList.__init__(self)
        self.name=name
        self.classname=classname
        self.parent=parent

    def __str__(self):
        return "AppletNode(name='%s', classname='%s')"%(self.name,self.classname)

    def selected(self,*arg):
#    print "selected",self.name,self.classname
        if self.frame:
            self.frame.showAppletNode(self)

    def createApplet(self):
#    print "createApplet",self.classname,self.name
        if self.classname in ["",None]:
            return None
        module=join(split(self.classname,".")[:-1],".")
        if len(module):
            cmd="import %s\ncl=%s()"%(module,self.classname)
        else:
            cmd="cl=%s()"%(self.classname)
        exec cmd
#    cl.frame=self.frame
#    cl.appletnode=self
        cl.name=self.name
        return cl

    def createGtkTreeItem(self,parent):
#    print "create item      name=",self.name,type(self.name)
#    print "create item classname=",self.classname,type(self.classname)
        item=gtk.TreeItem(self.name)
        item.signal_connect("select", self.selected)
        parent.append(item)
        item.show()
        parent.show()

        if len(self):
            tree=gtk.Tree()
            item.set_subtree(tree)
            for x in self:
                subitem=x.createGtkTreeItem(tree)
                subitem.expand()
                subitem.collapse()
        return item

    def isGroupMember(self,applet):
#    if applet.appletnode is None:
        c=applet.__class__
        if self.classname==c.__module__+"."+c.__name__:
            return 1
#    else:
#      if id(applet.appletnode) == id(self):
#       return 1

        for x in self:
            if x.isGroupMember(applet):
                return 1
        return 0

    def fillParentInChildren(self):
        for x in self.data:
            x.parent=self
            x.fillParentInChildren()

    def getPath(self):
        if self.parent is not None:
            l=self.parent.getPath()
            l.append(map(id,self.parent).index(id(self)))
#      l.append(self.parent.index(self))
            return l
        else:
            return []

    def getNodeForPath(self,path):
        x=self
        for p in path:
            x=x[p]
        return x

class AppletTreeModel(gtk.GenericTreeModel):
    def __init__(self,root):
        gtk.GenericTreeModel.__init__(self)
        self.root=root

    def on_get_flags(self):
        return 0
    def on_get_n_columns(self):
        return 1
    def on_get_column_type(self, index):
        """returns the type of a column in the model"""
        return gobject.TYPE_STRING
    def on_get_path(self, node):
        """returns the tree path (a tuple of indices at the various
        levels) for a particular node."""
#       print "on_get_path",node
        return tuple(node.getPath())
    def on_get_iter(self, path):
        '''returns the node corresponding to the given path.  In our
        case, the node is the path'''
#       print "on_get_iter",path
        return self.root.getNodeForPath(path)
    def on_get_value(self, node, column):
        '''returns the value stored in a particular column for the node'''
        assert column == 0
#       print "on_get_value",node,column
        return node.name
    def on_iter_next(self, node):
        '''returns the next node at this level of the tree'''
#       print "on_iter_next",node
        p=node.getPath()
#       print "original path",p
        p[-1]=p[-1]+1
#       print "next path",p
        try:
            return self.root.getNodeForPath(p)
        except IndexError:
            return None
    def on_iter_children(self, node):
        '''returns the first child of this node'''
        if node == None: # top of tree
            return self.root[0]
        if len(node):
            return node[0]
        return None
    def on_iter_has_child(self, node):
        '''returns true if this node has children'''
        return len(node)>0
    def on_iter_n_children(self, node):
        '''returns the number of children of this node'''
        return len(node)
    def on_iter_nth_child(self, node, n):
        '''returns the nth child of this node'''
        if node is None:
            return None
        try:
#         print type(node),node
            return node[n]
        except IndexError,TypeError:
            return None
    def on_iter_parent(self, node):
        '''returns the parent of this node'''
        return node.parent

class AppletTree(AppletNode):
    def __init__(self,name="?",classname=""):
        AppletNode.__init__(self,name,classname)
    def __str__(self):
        return "AppletTree(name='%s', classname='%s')"%(self.name,self.classname)

#  def createGtkTree_old(self,win):
#    tree=gtk.Tree()
#    win.add(tree)
#    item=self.createGtkTreeItem(tree)
#    item.expand()
#    item.collapse()
#    item.expand()
#    tree.show()
#    return tree
    def createGtkTree(self,win):
        self.fillParentInChildren()
        model = AppletTreeModel(self)
        tree_view = gtk.TreeView(model)
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Applets", cell, text=0)
        tree_view.append_column(column)
        win.add(tree_view)
        win.show_all()
        return tree_view


class AppletTreeStoreProfile(Profile):
    def __init__(self):
        Profile.__init__(self)
        cp=Profile(UserList,tagname="List",disable_attr=["data","parent"],list_saving=1)
        self.addClass(cp)
        cp=Profile(AppletNode,tagname="Applet",disable_attr=["data","parent"],list_saving=1)
        cp.addAttr(StringAttribute("name",tagattr=1))
        cp.addAttr(StringAttribute("classname",tagattr=1))
        self.addClass(cp)
        cp=Profile(AppletTree,tagname="Tree",disable_attr=["data","parent"],list_saving=1)
        cp.addAttr(StringAttribute("name",tagattr=1))
        cp.addAttr(StringAttribute("classname",tagattr=1))
        self.addClass(cp)

    def writeAll(self,f,obj,closeflag=0):
        if type(f) is StringType:
            f=open(f,"w")
            closeflag=1
        self.dump(obj,f)
        if closeflag:
            f.close()

    def loadAll(self,path):
        import p4vasp.util
        self.cleanReftables()
        dom=p4vasp.util.parseXML(path)
        r=self.retrieve(dom.documentElement)
        self.cleanReftables()
        r.fillParentInChildren()
        return r

def test():
    tree=AppletTree("Test")
    node1=AppletNode("node 1","appletmodule.applet1")
    node2=AppletNode("node 2","appletmodule.applet2")
    tree.append(node1)
    node1.append(node2)

    sp=AppletTreeStoreProfile()
    sp.writeAll("applettree-test.xml",tree)

    tree1=sp.loadAll("applettree-test.xml")
    sp.writeAll("applettree-test1.xml",tree)
    for x in tree1:
        print x,tree1.index(x),x.getPath(),id(x)
#  raise SystemExit
    print "tree:"
    print tree
    for x in tree:
        print x

    print "tree1:"
    print tree1
    for x in tree1:
        print x


    win=gtk.Window()
    win.set_title("tree test 1")
    win.connect("destroy",gtk.mainquit)
    win.show()

    tree1.createGtkTree(win)
    gtk.mainloop()

if __name__=="__main__":
    test()
