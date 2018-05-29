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


from p4vasp.graph import *
import gtk

import p4vasp.piddle.piddle as piddle
import p4vasp.piddle.piddleGTK2p4 as piddleGTK2p4
import p4vasp.util

class Export:
    def __init__(self,world=None,data=None):
        self.window=None
        self.xml=None
        self.fileselection=None
        self.world=world
        self.data=data
        self.type=None
        self.file=None
        self.type_menu=None
        self.type_options=None
        self.options=["raw data (.dat, .data)",
                      "XmGrace (.agr)",
                      "Postscript (.ps)",
                      "Encapsulated Postscript (.eps)",
                      "Portable Document Format (.pdf)",
                      "XFig (.fig)",
                      "Scalable Vector Graphics (.svg)"
                      ]
        self.option_extensions={".data" :0,
                                ".dat"  :0,
                                ".txt"  :0,
                                ".agr"  :1,
                                ".ps"   :2,
                                ".eps"  :3,
                                ".pdf"  :4,
                                ".fig"  :5,
                                ".svg"  :6
                                }

    def show(self):
        if self.window is not None:
            self.window.destroy()
        xml=p4vasp.util.loadGlade("graphwindow.glade","exportdata_window")
        self.connect_signals(xml)
        self.xml=xml
        self.file_entry=xml.get_widget("file_entry")
        opt=xml.get_widget("type_optionmenu")
        menu=gtk.Menu()
        opt.set_menu(menu)
        self.type_menu=menu
        self.type_options=opt

        for i in range(len(self.options)):
            item=gtk.MenuItem(self.options[i])
            item.connect("activate",self._set_type,i)
            menu.append(item)
            item.show()
        opt.show()
        opt.set_history(0)

        self.window=xml.get_widget("exportdata_window")
        self.window.show()

    def _set_type(self,widget,num):
#    print "set type",num
        self.type=num

    def connect_signals(self,x):
        x.signal_connect("on_export",self._on_export)
        x.signal_connect("hide_widget",self._hide_widget)
        x.signal_connect("show_widget",self._show_widget)
        x.signal_connect("destroy_widget",self._destroy_widget)
        x.signal_connect("show_fileselection",self._show_fileselection)
        x.signal_connect("destroy_fileselection",self._destroy_fileselection)
        x.signal_connect("export_file_selected",self._export_file_selected)
        x.signal_connect("on_file_entry_changed",self._on_file_entry_changed)

    def _on_file_entry_changed(self,*arg):
        self.file=self.file_entry.get_text()
        for k,v in self.option_extensions.items():
            if self.file[-len(k):]==k:
                self.type_options.set_history(v)
                self.type=v

    def _on_export(self,*arg):
        self.export()

    def _export_file_selected(self,*arg):
        self.file_entry.set_text(self.fileselection.get_filename())
        self.fileselection.destroy()
        self.fileselection=None

    def _show_fileselection(self,*arg):
#    if self.window is not None:
#      self.window.destroy()
        xml=p4vasp.util.loadGlade("graphwindow.glade","exportdata_fileselection")
        self.connect_signals(xml)
        self.fileselection=xml.get_widget("exportdata_fileselection")
        self.fileselection.show()

    def _destroy_fileselection(self,*arg):
        if self.fileselection is not None:
            self.fileselection.destroy()
            self.fileselection=None

    def export(self):
        import string
        if self.type==0:
            f=open(self.file,"w")
            if self.data is None:
                data=self.world
            else:
                data=self.data
            for g in data:
                for s in g:
                    for l in s:
                        f.write(string.join(map(lambda x:"%12g"%x,l)))
                        f.write("\n");
                    f.write("\n")
                f.write("\n\n")
            f.close()
        else:
            w=self.world.clone()
            w.background_color=0
            w.page_size_x=792
            w.page_size_y=612
            if self.type==1:
                if self.data is None:
                    w.exportGrace(self.file)
                else:
                    w.exportGrace(self.file,data=self.data)
            elif self.type==2:
                self.exportPS(w,self.data)
            elif self.type==3:
                self.exportEPS(w,self.data)
            elif self.type==4:
                self.exportPDF(w,self.data)
            elif self.type==5:
                self.exportFIG(w,self.data)
            elif self.type==6:
                self.exportSVG(w,self.data)

    def exportPS(self,w,data=None):
        import p4vasp.piddle.piddlePS as piddlePS
        c=piddlePS.PSCanvas(size=(w.page_size_x,w.page_size_y))
        w.render(c,data)
        c.save(self.file)
    def exportEPS(self,w,data=None):
        import p4vasp.piddle.piddlePS as piddlePS
        c=piddlePS.PSCanvas(size=(w.page_size_x,w.page_size_y))
        w.render(c,data)
        c.save(self.file)
    def exportPDF(self,w,data=None):
        import p4vasp.piddle.piddlePDF as piddlePDF
        c=piddlePDF.PDFCanvas(size=(w.page_size_x,w.page_size_y))
        w.render(c,data)
        c.save(self.file)
    def exportFIG(self,w,data=None):
        import p4vasp.piddle.piddleFIG as piddleFIG
        c=piddleFIG.FIGCanvas(size=(w.page_size_x,w.page_size_y))
        w.render(c,data)
        c.save(self.file)
    def exportSVG(self,w,data=None):
        import p4vasp.piddle.piddleSVG.piddleSVG as piddleSVG
        c=piddleSVG.SVGCanvas(size=(w.page_size_x,w.page_size_y))
        w.render(c,data)
        c.save_(self.file)

    def hide(self):
        if self.window is not None:
            self.window.hide()
        if self.fileselection is not None:
            self.fileselection.hide()

    def destroy(self):
        if self.window is not None:
            self.window.destroy()
            self.window=None
        if self.fileselection is not None:
            self.fileselection.destroy()
            self.fileselection=None


    def _destroy_widget(self,widget):
        widget.destroy()

    def _hide_widget(self,widget):
        widget.hide()

    def _show_widget(self,widget):
        widget.show()

def show_exportdata(self,*arg):
    e=Export()
    e.show()

class GraphCanvas(piddleGTK2p4.InteractiveCanvas):
    def __init__(self, size=(500,400), name="p4VASP graph", infoline=None,drawing_area=None,top=None,world=None,graphdata=None):
        self.lastmotiontime=0
        width, height = (int(round(size[0])), int(round(size[1])))
        self.world=world
        if drawing_area is None:
            if top is None:
                top  = gtk.Window()
            vbox = gtk.VBox()
            da   = gtk.DrawingArea()

            top.add(vbox)
            vbox.pack_start(da)

            if infoline:
                sbar = self.__sbar = gtk.Statusbar()
                vbox.pack_end(sbar, expand=0)
                sbar.set_border_width(2)
            else:
                self.__sbar = None
        else:
            da=drawing_area
            if infoline is None:
                self.__sbar = None
            else:
                self.__sbar = infoline

        self.top=top
        self.__status = None
        self.world=world
        self.graphdata=graphdata
        self.point=-1,-1
        self.selected_begin=None
        piddleGTK2p4.InteractiveCanvas.__init__(self, da, top)
        self.onOver  = self.onOverCallback
        self.onClick = self.onClickCallback
        self.onKey   = self.onKeyCallback
#    top.set_wmclass("canvas", "Canvas")
        da.realize()
        da.set_size_request(width, height)
#    top.show_all()
#    top.set_icon_name(name)
#    top.set_title(name)
        self.ensure_size(width, height)

    def setGraphData(self,data=None):
        self.graphdata=data
        self.render()

    def setWorld(self,world):
        self.world=world
        self.render()

    def setWorldAndData(self,world,data=None):
        self.world=world
        self.graphdata=data
        self.render()

    def render(self,data=None):
        if self.world is None:
            self.clear()
            self.flush()
            self.to_background_buffer()
        else:
            self.world.autotick()
            if data is None:
                if self.graphdata is None:
                    self.world.render(self)
                else:
                    self.world.render(self,self.graphdata)
            else:
                self.world.render(self,data)

    def updateGraph(self):
#    print "update graph"
        self.render()
        self.flush()
        self.to_background_buffer()

    def viewAll(self,data=None):
        if data is None:
            if self.graphdata is None:
                self.world.viewAll()
            else:
                self.world.viewAll(self.graphdata)
        else:
            self.world.viewAll(data)
    def viewAllX(self,data=None):
        if data is None:
            if self.graphdata is None:
                self.world.viewAllX()
            else:
                self.world.viewAllX(self.graphdata)
        else:
            self.world.viewAllX(data)
    def viewAllY(self,data=None):
        if data is None:
            if self.graphdata is None:
                self.world.viewAllY()
            else:
                self.world.viewAllY(self.graphdata)
        else:
            self.world.viewAllY(data)

    def setInfoLine(self, s):
        if self.__sbar:
            if self.__status:
                self.__sbar.pop(1)
            if s:
                self.__sbar.push(1, str(s))
            self.__status = s

    def onKeyCallback(self,canvas,key,m):
#    print "onKeyCallback",repr(key),repr(m)
        x,y=self.point
#    print "point",x,y
        if len(self.world)==1:
            gi=0
        else:
            gi=self.world.identifyGraphIndex(x,y)
        if x==-1 and y==-1:
            x,y=self.area.window.get_size()
            x/=2
            y/=2
#    print "gi",gi
        if gi is not None:
            g=self.world[gi]
            if key=='+':
                self.zoomAtPoint(x,y,1.0/1.2)
            elif key=='-':
                self.zoomAtPoint(x,y,1.2)
            elif key==keyRight:
                dx=(g.world_xmax-g.world_xmin)*0.1
                g.world_xmin+=dx
                g.world_xmax+=dx
                self.updateGraph()
            elif key==keyLeft:
                dx=(g.world_xmax-g.world_xmin)*0.1
                g.world_xmin-=dx
                g.world_xmax-=dx
                self.updateGraph()
            elif key==keyUp:
                dy=(g.world_ymax-g.world_ymin)*0.1
                g.world_ymin+=dy
                g.world_ymax+=dy
                self.updateGraph()
            elif key==keyDown:
                dy=(g.world_ymax-g.world_ymin)*0.1
                g.world_ymin-=dy
                g.world_ymax-=dy
                self.updateGraph()
            elif key==keyHome:
                if self.graphdata is None:
                    g.viewAll()
                    self.updateGraph()
                else:
                    if len(self.graphdata)>gi:
                        g.viewAll(self.graphdata[gi])
                        self.updateGraph()


    def resizeCallback(self,x,y):
#    print "resizeCallback(%d,%d)"%(x,y)
        flag=0
        if self.world.page_size_x!=x:
            flag=1
            self.world.page_size_x=x
        if self.world.page_size_y!=y:
            flag=1
            self.world.page_size_y=y

        self.updateGraph()

    def updateSize(self):
        x,y=self.area_drawable().get_size()
#    print "updateSize(%d,%d)"%(x,y)
        s=self.area
        flag=0
        if self.world.page_size_x!=x:
            flag=1
            self.world.page_size_x=x
        if self.world.page_size_y!=y:
            flag=1
            self.world.page_size_y=y

        self.updateGraph()


    def _button_press_handler(self,widget,event,data=None):
        self.onOverCallback(self,event.x,event.y,event.button)
        self.onClickCallback(self,event.x,event.y,event.button)
    def _button_release_handler(self,widget,event,data=None):
        self.onOverCallback(self,event.x,event.y,event.button)
        self.onClickCallback(self,event.x,event.y,event.button)
    def _motion_notify_handler(self,widget,event,data=None):
        print "_motion_notify_handler",event.x,event.y
        self.point=event.x,event.y
        self.onOverCallback(self,event.x,event.y)
    def onClickCallback(self,canvas,x,y,button=1):
        print "onClickCallback",x,y,button
        if button==4:
            self.zoomAtPoint(x,y,1.0/1.2)
        elif button==5:
            self.zoomAtPoint(x,y,1.2)
        elif button in [0,1]:
            self.onOverCallback(self,x,y,button)

    def onOverCallback(self,canvas,x,y,button=0):
        print "onOverCallback",x,y,button
        if (self.selected_begin is None) and (button==1):
            self.selected_begin=(x,y)

        if self.point[0]==int(x):
            if self.point[1]==int(y):
                return
        self.point=int(x),int(y)
        self.from_background_buffer()
        if self.selected_begin is not None:
            x1=min(self.selected_begin[0],x)
            x2=max(self.selected_begin[0],x)
            y1=min(self.selected_begin[1],y)
            y2=max(self.selected_begin[1],y)
            self.drawRect(x1,y1,x2,y2)
            if button==0:
                self.zoomTo(x1,y1,x2,y2)
                self.selected_begin=None
                return
        info=""
        if self.world:
            gi=self.world.identifyGraphIndex(x,y)
            if gi is not None:
                info+="G"+str(gi)
                g=self.world[gi]
                info+=" [%f, %f]"%(g.screen2worldX(x),g.screen2worldY(y))
                if self.graphdata is None:
                    i,j=g.identifySetPointVisible(x,y)
                    gd=g
                else:
                    gd=self.graphdata[gi]
                    i,j=g.identifySetPointVisible(x,y,gd)
                if i is not None:
                    info+=" set %d: point %d, [%f, %f]"%(i,j,gd[i][j][0],gd[i][j][1])
                    xx=g.world2screenX(gd[i][j][0])
                    yy=g.world2screenY(gd[i][j][1])

                    self.drawEllipse(xx-3,yy-3,xx+3,yy+3,red,2)
                    self.flush()
        canvas.setInfoLine(info)

    def zoomAtPoint(self,x,y,factor):
        g=self.world.identifyGraph(x,y)
#    print "zoomAtPoint",x,y,g
        if g is not None:
            x=g.screen2worldX(x)
            y=g.screen2worldY(y)
#      x=(g.world_xmin+g.world_xmax)/2
#      y=(g.world_ymin+g.world_ymax)/2
            g.world_xmin=x+(g.world_xmin-x)*factor
            g.world_xmax=x+(g.world_xmax-x)*factor
            g.world_ymin=y+(g.world_ymin-y)*factor
            g.world_ymax=y+(g.world_ymax-y)*factor
            #self.clear()
            self.updateGraph()

    def zoomTo(self,x1,y1,x2,y2):
        g=self.world.identifyGraph(x1,y1)
#    print "zoomTo",x1,y1,x2,y2,g
        if g is not None:
            x1=g.screen2worldX(x1)
            y1=g.screen2worldY(y1)
            x2=g.screen2worldX(x2)
            y2=g.screen2worldY(y2)
#      print "screen",x1,y1,x2,y2
            g.world_xmin=min(x1,x2)
            g.world_xmax=max(x1,x2)
            g.world_ymin=min(y1,y2)
            g.world_ymax=max(y1,y2)
            #self.clear()
            self.updateGraph()



class GraphCanvasWindow(GraphCanvas):
    def __init__(self, size=(500,400), name="p4VASP graph", gladefile="graphwindow.glade",gladename="window1",world=None,graphdata=None):
        self.xml=p4vasp.util.loadGlade(gladefile)
        GraphCanvas.__init__(self,
          size         = size,
          drawing_area = self.xml.get_widget("graph"),
          infoline     = self.xml.get_widget("infoline"),
          top          = self.xml.get_widget(gladename),
          world        = world,
          graphdata    = graphdata
        )
#    print "GRAPH CANVAS WINDOW"
#    self.top.set_events(gtk.gdk.ALL_EVENTS_MASK)
#    self.area.set_events(gtk.gdk.ALL_EVENTS_MASK)
#    self.area.window.set_events(gtk.gdk.ALL_EVENTS_MASK)
        self.export=Export(world,graphdata)
        self.xml.signal_connect("close_window",  self._close_window_handler)
        self.xml.signal_connect("hide_window",   self._hide_window_handler)
#    self.xml.signal_connect("destroy_window",self._destroy_window_handler)
        self.xml.signal_connect("show_window",   self._show_window_handler)
        self.xml.signal_connect('hide_widget',   self._hide_widget_handler)
        self.xml.signal_connect('show_widget',   self._show_widget_handler)
        self.xml.signal_connect('show_export',   self._show_export_handler)
        self.is_open=1
        self.is_visible=0

    def _close_window_handler(self,*arg):
        self.close()
    def _hide_window_handler(self,*arg):
        self.hide()
    def _destroy_window_handler(self,*arg):
        self.hide()

    def _show_window_handler(self,*arg):
        self.show()
    def _show_export_handler(self,*arg):
        self.export.world=self.world
        self.export.data=self.graphdata
        self.export.show()
    def _hide_widget_handler(self,widget):
        widget.hide()
    def _show_widget_handler(self,widget):
        widget.show()

    def close(self):
        self.is_open=0
        self.world=None
        self.top.destroy()
        self.export.destroy()

    def hide(self):
        self.is_visible=0
        self.top.hide()
        self.export.destroy()


    def show(self):
        self.is_visible=1
        self.top.show()

    def _motion_notify_handler(self,widget,event,data=None):
        self.point=event.x,event.y
        self.onOverCallback(self,event.x,event.y)

if __name__=="__main__":
    import p4vasp.util
    import p4vasp.Dictionary
    import p4vasp.Array

    world=World()
    world.parseGrace("total_dos_param.agr")
    root = p4vasp.util.loadGlade("graph.glade")
    root.connect("quit_now",gtk.mainquit)
    canvas=GraphCanvas(drawing_area=root.get_widget("graph"),
                       infoline=root.get_widget("statusbar"),
                       top=root.get_widget("window1"),
                       world=world)
    world.setupFonts(canvas)


    print "Read dom"
    dom=p4vasp.util.parseXML("vasprun1.xml")
    print "OK"
    incar=p4vasp.Dictionary.Incar(dom.getElementsByTagName("incar")[0])
    print "Incar resolved"
    dos=dom.getElementsByTagName("dos")[0]
    total=dos.getElementsByTagName("total")[0]
    total_array=p4vasp.Array.Array(total.getElementsByTagName("array")[0])
    print "Total dos resolved"
    partial=dos.getElementsByTagName("partial")[0]
    partial_array=p4vasp.Array.Array(partial.getElementsByTagName("array")[0])
    print "Partial dos resolved"

    total_dos_set=map(lambda x:(x[0],x[1]),total_array[0])
    int_total_dos_set=map(lambda x:(x[0],x[2]),total_array[0])
    ion0_dos     =map(lambda x:(x[0],x[1]+x[2]+x[3]+x[4]+x[5]+x[6]+x[7]+x[8]+x[9]),
                   partial_array[0][0])

#  print "Datasets extracted"
#  world=World()
#  world.parseGrace("total_dos_param.agr")
#  print "Graph prototype (grace) read"


    ion0set = Set(data=ion0_dos)
    ion0set.line_color=3
    ion0set.symbol=0
    ion0set.symbol_size=0.6
    ion0set.symbol_color=blue
    ion0set.symbol_fill_color=yellow
    ion0set.legend="ion 0 dos"

    world[0].subtitle="(%s)"%incar["SYSTEM"]

    set=total_dos_set
    world[0][0].data=set
    world[1][0].data=int_total_dos_set

    world[0].append(ion0set)

    world.viewAll()

    print "World created"

    world.render(canvas)
    canvas.to_background_buffer()

    gtk.mainloop()
