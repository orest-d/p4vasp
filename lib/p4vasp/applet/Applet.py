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

from __future__ import generators
from string import split
import copy
from p4vasp import *
from p4vasp.applet import *
from p4vasp.graph import *
from p4vasp.GraphPM import *
from p4vasp.GraphCanvas import *
from p4vasp.store import *
import p4vasp.util
import p4vasp.repository as repository

#class VisibleAppletAttribute(AttributeProfile):
#  def __init__(self,name="visible",attribute=None,encode=1,tag=1,tagattr=0):
#    AttributeProfile.__init__(self,name,attribute=attribute,encode=encode,tag=tag,tagattr=tagattr)
#
#  def setEncodedValue(self,obj,val):
#    if upper(val[0]) in ["1","Y","T"]:
##      print "show applet",obj.name
##      obj.showApplet()
#      pass
#
#  def getEncodedValue(self,obj):
#    return str(obj.isVisible())

class Widgets:
    def __init__(self,parent):
      self.parent=parent
    def __getattr__(self,name):
      return self.parent.xml.get_widget(name)

class AppletProfile(Profile):
#  visible_attr=VisibleAppletAttribute(tagattr=1)
    def __init__(self,name=None,tagname=None, list_saving=0, dict_saving=0,disable_attr=1,attr_setup=None,attr_profiles=[],class_profiles=[]):
        if type(disable_attr) is ListType:
            disabled_attr.extend(["gladefile","frame","panel","gladename","system","xml","required"])
        Profile.__init__(self,name,tagname=tagname, list_saving=list_saving, dict_saving=dict_saving,disable_attr=disable_attr,attr_setup=attr_setup,attr_profiles=attr_profiles,class_profiles=class_profiles)
        self.default_class_tag="applet"
#    self.addAttr(self.visible_attr)
        self.setupAttributes("int applet_showmode showmode")

    def retrieveObj(self,elem,c=None):
        """retrieve class instance from a DOM Element *elem*.
    If the class instance is supplied as an argument *c*, then the class attributes will
    be loaded into it, otherwise, a new instance will be created.
    """
        if elem.nodeType == elem.ELEMENT_NODE:
            exclude=["label"]
            if c is None:
                if elem.nodeName==self.default_class_tag:
                    exclude.append("name")
                    name=elem.getAttribute("name")
#         print "class retrieve",name
                    c=createClassFromName(name)
##        if self.getRoot().frame is not None:
##          self.getRoot().frame.addApplet(c)
##        else:
##          msg().error("can't add applet, frame is missing")
                else:
                    c=self.createClass()
            else:
                name=getClassName(c)

            label=elem.getAttribute("label")
            if label:
                self.getRoot().retrieve_reftable[label]=c

            lm=self.retrieve_class_handlers
            attrib=elem.attributes
            if attrib is not None:
                for i in range(0,len(attrib)):
                    x=attrib.item(i)
                    key=x.nodeName
                    if key not in exclude:
                        if self.aprof_by_name.has_key(key):
                            self.aprof_by_name[key].setEncodedValue(c,x.nodeValue)
                        else:
                            msg().error('Unknown tagattr attribute for %s while retrieveing %s.'%(key,self.name))

            for x in elem.childNodes:
                if x.nodeType==x.ELEMENT_NODE:
                    if self.retrieve_class_handlers.has_key(x.nodeName):
                        apply(self.retrieve_class_handlers[x.nodeName],(x,c))
                    else:
                        msg().error('Unknown tag method for <%s>.'%(x.nodeName))

            return c

    def createClass(self,name=None):
#    print "create applet class"
        flag=1
        if name is None:
            if self.object is not None:
                cl=apply(self.object,())
                flag=0
            else:
                name=self.name
        if flag:
            v=split(name,".")
            module=join(v[:-1],".")
            cname=v[-1]
            cmd=""
            if len(module):
                cmd="import %s\n"%module
            cmd="%scl=%s()"%(cmd,name)
            exec cmd

##    if self.getRoot().frame is not None:
##      print "add applet"
##      self.getRoot().frame.addApplet(cl)
##    else:
##      msg().error("can't add applet, frame is missing")

        return cl

class Applet(AppletTag,p4vasp.SystemPM.SystemListListener):
##  frame=None
    store_profile=AppletProfile()
    prototype=None
#  menupath=split("Applet:test",":")
    menupath=None
    name="Applet"
    EMBEDDED_MODE=1
    EXTERNAL_MODE=2
    EMBEDDED_ONLY_MODE=-1
    EXTERNAL_ONLY_MODE=-2

    showmode=1

    def __init__(self):
        self.name=self.__class__.__name__
        self.gladefile="Applet.glade"
        self.gladename="Applet"
        self.panel=None
#    self.appletnode=None
        self.system=None
        self.xml=None
        self.required=[]
        self.visible=0
        self.window=None
        self.applet_ready=0
        self.destroysignal=None
        self.widgets=Widgets(self)

    def updatePinStatusImage(self):
#    return None
        b=self.xml.get_widget("pin_button")
        if b is not None:
            i=gtk.Image()
            if self.pin_status:
                i.set_from_pixbuf(self.pin_image.get_pixbuf())
            else:
                i.set_from_pixbuf(self.unpin_image.get_pixbuf())
            if hasattr(b,"set_icon_widget"):
                b.set_icon_widget(i)
            else:
                b.foreach(lambda x,b=b:b.remove(x))
                b.add(i)

            i.show()
            b.show()


    def on_pin_button_clicked_handler(self,*arg):
        self.pin_status=not self.pin_status
        self.updatePinStatusImage()

    def updateEmbeddedStatusImage(self):
        b=self.xml.get_widget("embedded_button")
        if b is not None:
            i=gtk.Image()
            if self.isEmbedded():
                i.set_from_pixbuf(self.external_image.get_pixbuf())
            else:
                i.set_from_pixbuf(self.embedded_image.get_pixbuf())
            if hasattr(b,"set_icon_widget"):
                b.set_icon_widget(i)
            else:
                b.foreach(lambda x,b=b:b.remove(x))
                b.add(i)
            i.show()
            b.show()

    def on_embedded_button_clicked_handler(self,*arg):
        if self.isEmbedded():
            self.setExternalMode()
        else:
            self.setEmbeddedMode()
        self.updateEmbeddedStatusImage()

    def create(self):
        return Applet()

    def initUI(self):
        pass

    def setExternalMode(self):
        if self.isEmbedded():
            self.showmode=self.EXTERNAL_MODE
            self.window = gtk.Window()
            event_mask=    (  gtk.gdk.BUTTON_PRESS_MASK
                            | gtk.gdk.BUTTON_RELEASE_MASK
                            | gtk.gdk.KEY_PRESS_MASK
                            | gtk.gdk.POINTER_MOTION_MASK
                            #| gtk.gdk.POINTER_MOTION_HINT_MASK
                            )
            self.window.set_events(event_mask)
            self.window.connect("focus_in_event", self.focus_in_event_Handler)
            try:
                self.window.connect("motion_notify_event", self.motion_notify_event_Handler)
            except:
                pass
            try:
                self.window.connect("button_press_event", self.button_press_event_Handler)
            except:
                pass
            try:
                self.window.connect("button_release_event", self.button_release_event_Handler)
            except:
                pass
            try:
                self.destroysignal=self.window.connect("destroy", self.close_applet_handler)
            except:
                pass
#      self.window.set_events(gtk.gdk.ALL_EVENTS_MASK)

            try:
                self.window.set_title("p4vasp - %s"%str(self.name))
            except TypeError:
                self.window.set_title("p4vasp")
            if self.panel is None:
                self.createPanel()
            if self.panel.get_parent() is None:
#        print "ADD"
                self.window.add(self.panel)
            else:
#        print "REPARENT"
                self.panel.reparent(self.window)

            self.window.show_all()
#      self.panel.realize()
            getAppletFrame().externalizeApplet(self)
            self.updateEmbeddedStatusImage()
            self.updatePinStatusImage()
    def focus_in_event_Handler(self,w,event):
#    print "focus",event.type
        applets().activate(self)

    def isEmbedded(self):
        return self.window is None

    def setEmbeddedMode(self):
        self.showmode=self.EMBEDDED_MODE
        getAppletFrame().embedApplet(self)
        if self.destroysignal is not None:
            self.window.disconnect(self.destroysignal)
        self.window.destroy()
        self.window=None
        self.updateEmbeddedStatusImage()
        self.updatePinStatusImage()

    def setSystem(self,s):
        if not self.pin_status:
            self.system=s
            if s is not None:
                self.system.require(self.required,self.updateSystem)
            self.updateSystem()


    def notifySystemActivated(self,l,s):
#    print "system activated in applet",s.URL
        self.setSystem(s)
    def notifySystemListUpdated(self,l):
#    print "system activated in applet",s.URL
        self.updateSystemList()

    def updateSystem(self,x=None):
        pass
    def updateSystemList(self):
        pass

    def clone(self):
        a=copy.copy(self)
        a.panel=None
        return a


    def destroyApplet(self):
        applets().remove(self)
        if self.panel is not None:
            self.panel.destroy()
        self.panel=None
#    self.hide()
        if self.window is not None:
            self.window.destroy()
        self.destroy()

    def isVisible(self):
        return self.panel is not None

    def close_applet_handler(self,*arg):
        self.destroyApplet()

    def destroy(self):
        pass

    def hide(self):
        pass

    def show(self):
        pass

    def autoConnectSignals(self):
        xml=self.xml
        for x in dir(self):
            if x[-8:]=="_handler":
                try:
#         print "HANDLER:",self.name,x
                    xml.signal_connect(x[:-8],eval("self.%s"%x))
                except:
                    msg().exception()

    def createPanel(self):
#    print "%s.createPanel()"%self.__class__.__name__
        try:
            xml=p4vasp.util.loadGlade(self.gladefile,self.gladename)
        except:
            msg().error("Unable to create Glade object from %s, %s"%(self.gladefile,self.gladename))
            msg().error("Glade error in %s"%(self.name))
            return None
#    if self.gladename is not None:
#      xml=p4vasp.util.loadGlade(self.gladefile,self.gladename)
#    else:
#      xml=p4vasp.util.loadGlade(self.gladefile)
        panel=xml.get_widget(self.gladename)
        self.xml=xml
        self.panel=panel
        self.autoConnectSignals()
        self.updatePinStatusImage()
        self.updateEmbeddedStatusImage()
        return panel
    def getWindowPtr(self):
        return None

path=p4vasp.p4vasp_home+"%sdata%sglade2%s%s"%(os.sep,os.sep,os.sep,"pin_i.png")
Applet.pin_image=gtk.Image()
Applet.pin_image.set_from_file(path)
path=p4vasp.p4vasp_home+"%sdata%sglade2%s%s"%(os.sep,os.sep,os.sep,"unpin_i.png")
Applet.unpin_image=gtk.Image()
Applet.unpin_image.set_from_file(path)
Applet.pin_status=0
path=p4vasp.p4vasp_home+"%sdata%sglade2%s%s"%(os.sep,os.sep,os.sep,"Embedded_i.png")
Applet.embedded_image=gtk.Image()
Applet.embedded_image.set_from_file(path)
path=p4vasp.p4vasp_home+"%sdata%sglade2%s%s"%(os.sep,os.sep,os.sep,"External_i.png")
Applet.external_image=gtk.Image()
Applet.external_image.set_from_file(path)
Applet.embedded_status=0

#class Applet1(Applet):
#  def __init__(self):
#    Applet.__init__(self)
#    self.gladefile="applet1.glade"
#    self.gladename="applet_frame"
#
#class Applet2(Applet):
#  def __init__(self):
#    Applet.__init__(self)
#    self.gladefile="applet2.glade"
#    self.gladename="applet_frame"
#
#class Applet3(Applet):
#  def __init__(self):
#    Applet.__init__(self)
#    self.gladefile="applet1.glade"
#    self.gladename="applet_frame"

class TextApplet(Applet):
    def __init__(self):
        Applet.__init__(self)
        self.gladefile="textapplet.glade"
        self.gladename="applet_frame"
        self.isinit=0
        self.system=None
        self.required=["NAME","INITIAL_STRUCTURE"]

    def initUI(self):
        self.lframe = self.xml.get_widget("frame")
        self.text  = self.xml.get_widget("text")
        self.isinit=1
        self.setSystem(self.system)

    def setLabel(self,label):
        self.lframe.set_label(label)
    def deleteText(self):
        self.text.set_point(0)
        self.text.forward_delete(self.text.get_length())
    def setText(self,text):
        self.deleteText()
        self.text.get_buffer().insert(None,None,None,text)

    def updateSystem(self,x=None):
#    print "TextApplet update System"
        system=self.system
        if self.isinit:
            if system is not None:
                self.setLabel(str(system.NAME))
                struct=system.current("INITIAL_STRUCTURE")
                if struct:
                    self.setText(str(struct.toxml()))
            else:
                self.setLabel("-")
                self.setText("")

def handler(*arg):
    print "HANDLER",arg

class GraphApplet(Applet):
    def __init__(self):
        Applet.__init__(self)
        self.gladefile="graphapplet.glade"
        self.gladename="applet_frame"
        self.world=None
        self.world_name=None
        self.canvas=None
        self.graphdata=[]
        self.window_canvas=None
        self.window_world=None
        self.required=[]

    def clone(self):
        c=GraphApplet()
        c.name=self.name
#    c.frame=self.frame
        c.appletnode=self.appletnode
        c.world=self.world.clone()
        c.graphdata=self.graphdata[:]
        return c

    def initUI(self):
#    print "initUI"
        if self.world is None:
            if self.world_name is None:
                self.world=World()
            else:
                self.world=createGraph(self.world_name)
            self.window_world=self.world.clone()

        self.xml.signal_connect("open_external_window",self._open_external_window_handler)
        self.graph_area=self.xml.get_widget("graph")
        if self.graph_area is not None:
            self.graph_area.connect("motion-notify-event",self._canvas_motion_notify_handler)
#    print "initUI end"

    def _open_external_window_handler(self,*arg):
        if self.window_canvas is None:
            self.window_canvas=GraphCanvasWindow(world=self.window_world)
        else:
            if self.window_canvas.is_open:
                self.window_canvas.show()
            else:
                self.window_canvas.close()
                self.window_canvas=GraphCanvasWindow(world=self.window_world)
        self.setGraphData(self.graphdata)
        self.update()

    def setGraphData(self,data):
        self.graphdata=data
        if self.canvas is not None:
            self.canvas.setGraphData(data)
        if self.window_canvas is not None:
            self.window_canvas.setGraphData(data)

    def update(self):
        if self.canvas is not None:
            self.canvas.updateGraph()
        if self.window_canvas is not None:
            self.window_canvas.updateGraph()

    def viewAll(self):
        if self.canvas is not None:
            self.canvas.viewAll()
        if self.window_canvas is not None:
            self.window_canvas.viewAll()

    def setSystem(self,system):
        self.system=system
        if system is not None:
            self.system.require(self.required,self.updateSystem)
        self.updateSystem()
        self.viewAll()
        self.update()

    def updateSystem(self,x=None):
        pass

    def destroy(self):
#    print "destroy",self.appletnode
        if self.window_canvas is not None:
            self.window_canvas.close()
            self.window_canvas=None
    def hide(self):
#    print "hide",self.appletnode
        if self.window_canvas is not None:
            self.window_canvas.hide()
        self.canvas=None
        self.panel=None

    def _canvas_motion_notify_handler(self,*arg):
        if self.canvas is not None:
            return apply(self.canvas._motion_notify_handler,arg)

    def show(self):
        if self.window_canvas is not None:
            if self.window_canvas.is_open:
                self.window_canvas.show()
        area=self.graph_area
        if area is not None:
            self.canvas=GraphCanvas(drawing_area=area,
      #       top=self.panel.get_parent_window(),
              top=None,
              world=self.world)
            self.world.setupFonts(self.canvas)
        else:
            self.canvas=None
        self.updateSystem()
