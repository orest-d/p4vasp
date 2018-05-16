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

from __future__ import generators
from string import *
#import copy
#from p4vasp import *
import p4vasp.applet.Applet
from p4vasp.graph import *
from p4vasp.GraphPM import *
from p4vasp.GraphCanvas import *
import p4vasp.store
import p4vasp.util
import p4vasp.repository as repository
import p4vasp
import gtk
import os

class GraphWindowApplet(p4vasp.applet.Applet.Applet):
#  menupath=["Test","Graph"]
#  showmode=p4vasp.applet.Applet.Applet.EXTERNAL_MODE
    INTMODE_NONE =0
    INTMODE_ZOOM0=1
    INTMODE_ZOOM1=2
    INTMODE_MOVE0=3
    INTMODE_MOVE1=4
    INTMODE_PICK =5
    def __init__(self):
        p4vasp.applet.Applet.Applet.__init__(self)
        self.gladefile="graphwindowapplet.glade"
        self.gladename="applet_frame"
        self.world=None
        self.world_name="dos"
        self.canvas=None
        self.graphdata=[]
        self.required=[]
        self.area=None
        self.int_mode=self.INTMODE_NONE
        self.export=Export()
        self.menubar=None
        self.point0=(0,0)

    def clone(self):
        c=GraphWindowApplet()
        c.name=self.name
#    c.frame=self.frame
        c.appletnode=self.appletnode
        c.world=self.world.clone()
        c.graphdata=self.graphdata[:]
        return c

    def setWorld(self,w):
        self.world=w
        if self.canvas is not None:
            self.canvas.setWorld(w)
    def setWorldAndData(self,w,data=None):
        self.world=w
        self.graphdata=data
        if self.canvas is not None:
            self.canvas.setWorldAndData(w,data)

    def initUI(self):
#    print "initUI"
        self.cursorNone=None
        self.cursorZoom0=gtk.gdk.Cursor(gtk.gdk.DOTBOX)
#    self.cursorZoom1=gtk.gdk.Cursor(gtk.gdk.LR_ANGLE)
        self.cursorZoom1=gtk.gdk.Cursor(gtk.gdk.BOTTOM_RIGHT_CORNER)
        self.cursorMove0=gtk.gdk.Cursor(gtk.gdk.FLEUR)
        self.cursorMove1=gtk.gdk.Cursor(gtk.gdk.FLEUR)
        self.cursorMove1=gtk.gdk.Cursor(gtk.gdk.SB_RIGHT_ARROW)
        self.cursorPick =gtk.gdk.Cursor(gtk.gdk.CROSSHAIR)
        if self.world is None:
            if self.world_name is None:
                self.world=World()
            else:
                self.world=createGraph(self.world_name)

        self.graph_box=self.xml.get_widget("graph_box")
        self.menubar=self.xml.get_widget("menubar")


    def update(self):
        if self.canvas is not None:
            self.canvas.updateGraph()

    def viewAll(self):
        if self.canvas is not None:
            self.canvas.viewAll()
    def viewAllX(self):
        if self.canvas is not None:
            self.canvas.viewAllX()
    def viewAllY(self):
        if self.canvas is not None:
            self.canvas.viewAllY()

    def setSystem(self,system):
        if not self.pin_status:
            self.system=system
            if system is not None:
                self.system.require(self.required,self.updateSystem)
            self.updateSystem()
    #    self.viewAll()
            self.update()

       # def updateSystem(self,x=None):
       #   pass

    def destroy(self):
        pass
    def hide(self):
        self.canvas=None
        self.panel=None

#  def _canvas_motion_notify_handler(self,*arg):
#    if self.canvas is not None:
#      return apply(self.canvas._motion_notify_handler,arg)

    def button_press_event_Handler(self,w,e):
#    print "Press",e.type,e.x,e.y
#    print "local",self.area.get_pointer()
        if self.int_mode==self.INTMODE_ZOOM0:
            self.int_mode=self.INTMODE_ZOOM1
            self.point0=self.area.get_pointer()
            self.area.window.set_cursor(self.cursorZoom1)
        elif self.int_mode==self.INTMODE_MOVE0:
            self.area.window.set_cursor(self.cursorMove1)
            self.int_mode=self.INTMODE_MOVE1
            self.point0=self.area.get_pointer()

    def zoomAtPoint(self,x,y,f):
        self.canvas.zoomAtPoint(x,y,f)
    def zoomTo(self,x1,y1,x2,y2):
        self.canvas.zoomTo(x1,y1,x2,y2)
    def move(self,x1,y1,x2,y2):
        g=self.canvas.world.identifyGraph(x1,y1)
        if g is not None:
            x1=g.screen2worldX(x1)
            y1=g.screen2worldY(y1)
            x2=g.screen2worldX(x2)
            y2=g.screen2worldY(y2)
            dx=x2-x1
            dy=y2-y1
            g.world_xmin-=dx
            g.world_xmax-=dx
            g.world_ymin-=dy
            g.world_ymax-=dy
            self.canvas.updateGraph()


    def button_release_event_Handler(self,w,e):
#    print "local",self.area.get_pointer()
        x,y=self.area.get_pointer()
        if self.int_mode==self.INTMODE_ZOOM1:
            self.int_mode=self.INTMODE_ZOOM0
            self.area.window.set_cursor(self.cursorZoom0)
#      self.int_mode=self.INTMODE_NONE
            self.canvas.from_background_buffer()
            self.canvas.flush()
            x1=min(x,self.point0[0])
            x2=max(x,self.point0[0])
            y1=min(y,self.point0[1])
            y2=max(y,self.point0[1])
            if abs(x1-x2)<=1 or abs(y1-y2)<=1:
#        print "a"
                if e.button==1:
                    self.zoomAtPoint(x1,y1,1.0/1.2)
                else:
                    self.zoomAtPoint(x1,y1,1.2)
            else:
                self.zoomTo(x1,y1,x2,y2)
            self.canvas.flush()
        elif self.int_mode==self.INTMODE_MOVE1:
            self.int_mode=self.INTMODE_MOVE0
            self.area.window.set_cursor(self.cursorMove0)
#      self.int_mode=self.INTMODE_NONE
            self.point1=self.area.get_pointer()
            self.canvas.from_background_buffer()
            self.canvas.flush()
            self.move(self.point0[0],self.point0[1],x,y)
    def motion_notify_event_Handler(self,w,e):
#    print "Motion",e.type,e.x,e.y
#    print "local",self.area.get_pointer()
        try:
            x,y=self.area.get_pointer()
            if self.int_mode==self.INTMODE_ZOOM1:
    #      print x,y
                self.canvas.from_background_buffer()
                x1=min(x,self.point0[0])
                x2=max(x,self.point0[0])
                y1=min(y,self.point0[1])
                y2=max(y,self.point0[1])
                self.canvas.drawRect(x1,y1,x2,y2)
                self.canvas.flush()
            elif self.int_mode==self.INTMODE_MOVE1:
    #      print x,y
                self.canvas.from_background_buffer()
                self.canvas.drawLine(self.point0[0],self.point0[1],x,y)
                self.canvas.flush()
            elif self.int_mode==self.INTMODE_PICK:
                w=self.canvas.world
                info=""
                xx,yy=self.point0
                if x!=xx or y!=yy:
                    self.point0=(x,y)
                    self.canvas.from_background_buffer()
                    if w is not None:
                        gi=w.identifyGraphIndex(x,y)
                        if gi is not None:
                            info+="G"+str(gi)
                            g=w[gi]
                            info+=" [%f, %f]"%(g.screen2worldX(x),g.screen2worldY(y))
                            if self.canvas.graphdata is None:
                                i,j=g.identifySetPointVisible(x,y)
                                gd=g
                            else:
                                gd=self.graphdata[gi]
                                i,j=g.identifySetPointVisible(x,y,gd)
                            if i is not None:
                                info+=" set %d: point %d, [%f, %f]"%(i,j,gd[i][j][0],gd[i][j][1])
                                xx=g.world2screenX(gd[i][j][0])
                                yy=g.world2screenY(gd[i][j][1])

                                msg().status(info)
                                self.canvas.drawEllipse(xx-3,yy-3,xx+3,yy+3,red,2)
                                self.canvas.flush()
                        else:
                            info+="%3d %3d"%(x,y)
                            msg().status(info)
        except:
            msg().exception()

#  def __event(self,w,e):
#    print "EVENT",e
    def show(self):
        box=self.graph_box
        if self.area is None:
            area=gtk.DrawingArea()
            box.pack_start(area)
            box.show_all()
            self.area=area
            event_mask=    (  gtk.gdk.BUTTON_PRESS_MASK
                            | gtk.gdk.BUTTON_RELEASE_MASK
                            | gtk.gdk.KEY_PRESS_MASK
                            | gtk.gdk.POINTER_MOTION_MASK
                            | gtk.gdk.POINTER_MOTION_HINT_MASK)
            x=self.area
            x.set_events(event_mask)
#      x.connect("event", self.__event)

        if box is not None:
#      self.canvas=GraphBoxCanvas(box=box,world=self.world)
            self.canvas=GraphCanvas(drawing_area=self.area,top=self.area.get_toplevel(),world=self.world)
            self.world.setupFonts(self.canvas)
        else:
            self.canvas=None
#    self.updateSystem()

    def setGraphData(self,data):
        self.graphdata=data
        if self.canvas is not None:
            self.canvas.setGraphData(data)

    def updateSystem(self,x=None):
        pass

    def zoomFactor(self,factor):
        if self.canvas is not None:
            w=self.canvas.world
            for g in w:
                d=g.world_xmax-g.world_xmin
                g.world_xmin=g.world_xmin-0.5*(factor-1.0)*d
                g.world_xmax=g.world_xmin+factor*d
                d=g.world_ymax-g.world_ymin
                g.world_ymin=g.world_ymin-0.5*(factor-1.0)*d
                g.world_ymax=g.world_ymin+factor*d
        self.update()

    def on_autoscale_button_clicked_handler(self,*arg):
        self.viewAll()
        self.update()
    def on_autoscale_x_button_clicked_handler(self,*arg):
        self.viewAllX()
        self.update()
    def on_autoscale_y_button_clicked_handler(self,*arg):
        self.viewAllY()
        self.update()
    def on_zoomp_button_clicked_handler(self,*arg):
        self.zoomFactor(1.0/1.2)
    def on_zoomm_button_clicked_handler(self,*arg):
        self.zoomFactor(1.2)
    def on_zoom_button_clicked_handler(self,*arg):
        self.canvas.from_background_buffer()
        self.area.window.set_cursor(self.cursorZoom0)
        self.int_mode=self.INTMODE_ZOOM0

    def on_move_button_clicked_handler(self,*arg):
#    print "move"
        self.canvas.from_background_buffer()
        self.area.window.set_cursor(self.cursorMove0)
        self.int_mode=self.INTMODE_MOVE0
    def on_pick_button_clicked_handler(self,*arg):
#    print "pick"
        self.canvas.from_background_buffer()
        self.area.window.set_cursor(self.cursorPick)
        self.int_mode=self.INTMODE_PICK
#    self.canvas.initEvents()
#    self.canvas.drawLine(0,0,50,50)
##    self.canvas.render()
#    self.canvas.flush()
#    self.viewAll()
    def on_quick_export_button_clicked_handler(self,*arg):
        import os.path
        if self.export is not None:
            file=self.export.file
            et=self.export.type
            if file is None:
                file="graph"
            f,e=os.path.splitext(file)
            self.export.world=self.world
            self.export.data=self.graphdata
            if e=="":
                i=1
                while 1:
                    for e in [".ps",".agr",".dat"]:
                        if os.path.exists("%s%04d%s"%(f,i,e)):
                            i+=1
                            continue
                    break
                for t,e in [(0,".dat"),(1,".agr"),(2,".ps")]:
                    self.export.type=t
                    self.export.file="%s%04d%s"%(f,i,e)
                    self.export.export()
            else:
                self.export.type=self.export.option_extensions[lower(e)]
                i=1
                while os.path.exists("%s%04d%s"%(f,i,e)):
                    i+=1
                self.export.file="%s%04d%s"%(f,i,e)
                self.export.export()
            self.export.file=file
            self.export.type=et


    def show_export_handler(self,*arg):
        self.export.world=self.world
        self.export.data=self.graphdata
        self.export.show()

GraphWindowApplet.store_profile=p4vasp.applet.Applet.AppletProfile(GraphWindowApplet,tagname="Graph")
