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

class AppletNode(UserList):
    frame=None
    def __init__(self,name="?",classname=""):
        UserList.__init__(self)
        self.name=name
        self.classname=classname
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
        cl.frame=self.frame
        cl.appletnode=self
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
        if applet.appletnode is None:
            c=applet.__class__
            if self.classname==c.__module__+"."+c.__name__:
                return 1
        else:
            if id(applet.appletnode) == id(self):
                return 1

        for x in self:
            if x.isGroupMember(applet):
                return 1
        return 0

class AppletTree(AppletNode):
    def __init__(self,name="?",classname=""):
        AppletNode.__init__(self,name,classname)
    def __str__(self):
        return "AppletTree(name='%s', classname='%s')"%(self.name,self.classname)

    def createGtkTree(self,win):
        tree=gtk.Tree()
        win.add(tree)
        item=self.createGtkTreeItem(tree)
        item.expand()
        item.collapse()
        item.expand()
        tree.show()
        return tree

class AppletTreeStoreProfile(Profile):
    def __init__(self):
        Profile.__init__(self)
        cp=Profile(UserList,tagname="List",disable_attr=["data"],list_saving=1)
        self.addClass(cp)
        cp=Profile(AppletNode,tagname="Applet",disable_attr=["data"],list_saving=1,
        attr_setup="""string name
        string classname""")
        self.addClass(cp)
        cp=Profile(AppletTree,tagname="Tree",disable_attr=["data"],list_saving=1)
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
    win.connect("destroy",mainquit)
    win.show()

    tree1.createGtkTree(win)
#  mainloop()

if __name__=="__main__":
    test()
