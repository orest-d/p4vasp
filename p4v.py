#!/usr/bin/env python
# Copyright (C) 2003 Orest Dubay <orest.dubay@univie.ac.at>

from __future__ import generators


def get_gtk():
    print """You need to get version 2.0 (or later) of PyGTK for this to work. You
             can get source code from http://www.pygtk.org """
    raise SystemExit

try:
    import pygtk
    pygtk.require("2.0")
except ImportError:
    try:
        import gtk
        import gobject
    except ImportError:
        get_gtk()
    if not hasattr(gtk, "Window"): # renamed in version 2.0
        get_gtk()
except AssertionError:
    get_gtk()

import sys
from p4vasp import *
from   p4vasp.SystemPM import *
import p4vasp.piddle.piddleGTK2p4 as piddleGTK2p4
#import p4vasp.GraphPM
from   p4vasp.setupstore import * # dead module
import p4vasp.util
#import p4vasp.graph
#import p4vasp.Structure
import p4vasp.Selection
import p4vasp.message
from   p4vasp.applet import *
#from   p4vasp.applet.AppletTree import *
#import p4vasp.repository as repository
from   p4vasp.applet.SelectionApplet import *
import gtk
import gobject
import os.path
import os
import time

try:
    import _cp4vasp
    import cp4vasp
except:
    pass


class FrameMessageDriver(p4vasp.message.MessageDriver):
    def __init__(self,xml,logfile=p4vasp.message.DummyFile(),closeflag=0):
        p4vasp.message.MessageDriver.__init__(self,logfile,closeflag)
        self.progressbar          = xml.get_widget("progressbar")
        self.progressbar.set_pulse_step(0.1)
        self.statusbar            = xml.get_widget("statusbar")
        self.consoleout=0

    def status(self,txt):
        self.statusbar.set_text(txt)
        self.statusbar.show()
        self.logfile.write("STATUS:%s\n"%p4vasp.message.indent(txt,"       "))
        self.logfile.flush()

    def error(self,txt):
        self.statusbar.set_text("ERROR: %s"%txt)
        if (self.consoleout):
            stdout.write("ERROR : %s\n"%p4vasp.message.indent(txt,"       "))
            stdout.flush()
        self.logfile.write("ERROR : %s\n"%p4vasp.message.indent(txt,"       "))
        self.logfile.flush()

    def step(self, step=None,total=None):
        if (step is None) or (total is None) or (total<=0):
            self.progressbar.pulse()
            self.pstep+=1
        else:
            self.progressbar.set_fraction(float(step)/float(total))
            if step:
                self.progressbar.set_text("%s/%s"%(str(step),str(total)))
            else:
                self.progressbar.set_text("")

    def message(self,txt):
        if self.consoleout:
            print txt
        self.logfile.write("MSG   :%s\n"%p4vasp.message.indent(txt,"       "))
        self.logfile.flush()

    def confirm(self,txt):
        self.logfile.write("CMSG  :%s\n"%p4vasp.message.indent(txt,"       "))
        self.logfile.flush()
        dialog=gtk.MessageDialog(None,gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_INFO,gtk.BUTTONS_OK ,txt)
        dialog.run()
        dialog.destroy()

    def confirm_error(self,txt):
        print "Error:",txt
        self.logfile.write("CERR  :%s\n"%p4vasp.message.indent(txt,"       "))
        self.logfile.flush()
        dialog=gtk.MessageDialog(None,gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_ERROR,gtk.BUTTONS_CLOSE ,txt)
        dialog.run()
        dialog.destroy()

    def exception(self,etype=None,value=None,trace=None):
        if etype is None:
            etype,value,trace=sys.exc_info()
        if self.consoleout:
            traceback.print_exception(etype,value,trace)
        txt=join(traceback.format_exception(etype,value,trace))
        self.logfile.write("EXCEPT:%s\n"%p4vasp.message.indent(txt,"       "))
        self.logfile.flush()

    def __del__(self):
        self.logfile.flush()
        self.logfile.close()

class Frame(SystemListListener):
    def __init__(self):
        import os
        sep=os.sep
        self.gladefile="frame.glade"
        self.atomtypes=getAtomtypes()
        self.gladename="frame_box"
        self.xml=None
        self.applet_box=None
        self.embedded_applet=None
        self.menubar=None
        self.root_widget=None
        self.systemitems=[]
        self.load_system_fileselection=None
        self.init3d_flag=0
        self.last_system_path=""

    def init3d(self):
        if not self.init3d_flag:
            _cp4vasp.VisInit()
            if _cp4vasp.checkThreadsSupport():
                _cp4vasp.VisMainLoopInThread()
            else:
                gobject.idle_add(self.update3d)
            self.init3d_flag=1

    def update3d(self,*p):
        _cp4vasp.VisCheck()
        gobject.idle_add(self.update3d)

    def addSystem(self,ss):
#    print "addSystem",ss.URL
        systemlist().append(ss)
    def notifySystemListUpdated(self,l):
        self.updateSystemListMenu()
    def updateSystemListMenu(self):
        for x in self.systemitems:
            self.system_menu.remove(x)
            x.destroy()
        self.systemitems=[]
        #print "updateSystemListMenu"
        for ss in systemlist():
            name=ss.NAME
            if name is None:
                name="???"
            p=ss.URL
            if p is None:
                p=""
            else:
                p=" (%s)"%p
            name="%s%s"%(name,p)
            name=name.replace("_","__")
            item=gtk.MenuItem(name)
            item.connect("activate",self._system_activate,ss)
            self.system_menu.append(item)
            item.show()
#      item.activate()
            self.systemitems.append(item)

        self.system_options.show_all()
#    self.system_options.set_history(len(systemlist())-1)
#
        self.system_options.set_history(0)

    def _system_activate(self,menuitem,system):
#    print "activate system",system.NAME
#    self.current_system=system
        systemlist().activate(system)

#    for x in self.appletlist:
#    for x in applets():
#      if id(x.system)!=id(system):
#        x.setSystem(system)

    def button_press_event_Handler(self,w,e):
        if self.embedded_applet is not None:
            try:
                self.embedded_applet.button_press_event_Handler(w,e)
            except AttributeError:
                pass
            except:
                msg().exception()
    def button_release_event_Handler(self,w,e):
        if self.embedded_applet is not None:
            try:
                self.embedded_applet.button_release_event_Handler(w,e)
            except AttributeError:
                pass
            except:
                msg().exception()

    def motion_notify_event_Handler(self,w,e):
#    print "motion",e.type,e.x,e.y
        if self.embedded_applet is not None:
            try:
                self.embedded_applet.motion_notify_event_Handler(w,e)
            except AttributeError:
                pass
            except:
                msg().exception()
    def createFrame(self):
        try:
            xml=p4vasp.util.loadGlade(self.gladefile,self.gladename)
        except:
            msg().exception()
            msg().error("Unable to create Glade object from %s, %s"%(self.gladefile,self.gladename))
#      msg().error("Glade error in %s"%(self.name))
            return None
        self.xml=xml

        setMessageDriver(FrameMessageDriver(xml,"p4vasp.log"))

        self.connect_signals(xml)
#    self.notebook=xml.get_widget("notebook")
#    self.notebook.remove_page(0)
        self.applet_box=xml.get_widget("applet_box")
        self.root_widget=xml.get_widget(self.gladename)
        event_mask=    (  gtk.gdk.BUTTON_PRESS_MASK
                        | gtk.gdk.BUTTON_RELEASE_MASK
                        | gtk.gdk.KEY_PRESS_MASK
                        | gtk.gdk.POINTER_MOTION_MASK
                        #| gtk.gdk.POINTER_MOTION_HINT_MASK
                        )
        w=gtk.Window()
        w.set_events(event_mask)
        w.connect("destroy",self.quitNow)
        w.connect("motion_notify_event", self.motion_notify_event_Handler)
        w.connect("button_press_event", self.button_press_event_Handler)
        w.connect("button_release_event", self.button_release_event_Handler)
        w.connect("focus_in_event", self.focus_in_event_Handler)
        w.add(self.root_widget)
        self.root_window=w


#    self.createAppletTree()
        self.system_options=xml.get_widget("system_menu")
        self.selection_entry=xml.get_widget("selection_entry")
        self.selection_set=xml.get_widget("selection_set")
        self.selection_none=xml.get_widget("selection_none")
        self.system_menu=self.system_options.get_menu()
#    self.system_options.set_menu(menu)
        self.system_options.show()
        self.menubar=xml.get_widget("menubar")
        self.toolbar=xml.get_widget("toolbar")

        setMessageDriver(FrameMessageDriver(xml,"p4vasp.log"))
        w.show_all()
        systemlist().addSystemListListener(self)
        return self.root_widget

    def connect_signals(self,x):
        x.signal_connect('quit_now',             self.quitNow)
        x.signal_connect('hide_widget',          self.hide_widget)
        x.signal_connect('show_widget',          self.show_widget)
        x.signal_connect('show_about_dialog',    self.show_about_dialog)
        x.signal_connect('show_license_dialog',  self.show_license_dialog)
        x.signal_connect('show_load_system_fileselection',
                                              self.show_load_system_fileselection)
        x.signal_connect('show_save_system_fileselection',
                                              self.show_save_system_fileselection)
        x.signal_connect('load_system_selected', self.load_system_selected)
        x.signal_connect('save_system_selected', self.save_system_selected)
        x.signal_connect('on_save_setup',        self.on_save_setup)
        x.signal_connect('on_reload_activate',   self.on_reload_activate)
        x.signal_connect('show_applet',          self.on_show_applet)
        x.signal_connect('ext_applet',           self.on_ext_applet)
        x.signal_connect('on_commitbutton_clicked',self.quickCommit)

    def focus_in_event_Handler(self,w,event):
#    print "focus",event.type
        if self.embedded_applet is not None:
            applets().activate(self.embedded_applet)

    def on_show_applet(self,*arg):
        print "on_show_applet",arg
    def on_ext_applet(self,*arg):
        print "on_ext_applet",arg

    def createSubmenus(self,l):
        i=gtk.MenuItem(l[0])
        i.set_name(l[0])
        if len(l)>1:
            menu=gtk.Menu()
            menu.show()
            i.set_submenu(menu)
            menu.add(self.createSubmenus(l[1:]))
        i.show()
        return i

    def getMenuItem(self,l,m=None):
        if m is None:
            m=self.menubar
        if len(l) == 0:
            return None
        ch=m.get_children()
        for x in ch:
            if x.get_name()==l[0]:
                if len(l)>1:
                    return self.getMenuItem(l[1:],x.get_submenu())
                else:
                    return x
        m.add(self.createSubmenus(l))
        return self.getMenuItem(l,m)

    def createHelpMenu(self):
        helpitem=gtk.MenuItem("Help")
        helpitem.set_right_justified(1)
        helpmenu=gtk.Menu()
        about=gtk.MenuItem("About")
        lic=gtk.MenuItem("License agreement")
        self.menubar.add(helpitem)
        helpitem.set_submenu(helpmenu)
        helpmenu.add(about)
        helpmenu.add(lic)
        about.connect("activate",self.show_about_dialog)
        lic.connect("activate",self.show_license_dialog)
        helpitem.show_all()


    def saveSetup(self,f="setup.xml",closeflag=0,obj=None):
        if obj is None:
            obj=[systemlist(),applets()]
        if type(f) is StringType:
            f=open(f,"w")
            closeflag=1
        sp=SetupProfile()
        sp.dump(obj,f)
        if closeflag:
            f.close()

#  def loadSetup(self,url="setup.xml"):
#    dom=p4vasp.util.parseXMLfromURL(url)
#    sp=SetupProfile()
#    sp.frame=self
#    obj=sp.retrieve(dom.documentElement)
#    sp.cleanReftables()
#    print obj
#    if len(obj):
#      msg().message("Open systems:")
#      for s in obj[0]:
#        if s.URL != "vasprun.xml":
#         msg().message("  "+s.URL)
#          self.addSystem(s)
#    if len(obj)>0:
#      msg().message("Loading applets:")
#      aa=obj[1]
#      for i in range(len(aa)-1,-1,-1):
#        a=aa[i]
#       msg().message("  "+a.name)
#        applets().activate(a)
#
#    msg().status("Setup %s loaded."%url)

    def loadSetupGen(self,url="setup.xml"):
        msg().step()
        try:
            dom=p4vasp.util.parseXMLfromURL(url)
        except:
            msg().error("Can not read %s"%url)
            return

        sp=SetupProfile()
        sp.frame=self
        msg().step()
        yield 1
        obj=sp.retrieve(dom.documentElement)
        sp.cleanReftables()
        msg().step()
        yield 1
        if len(obj):
            for s in obj[0]:
                if s.URL != "vasprun.xml":
                    msg().status("Open %s"%s.URL)
                    msg().step()
                    yield 1
                    self.addSystem(s)

        if len(obj)>0:
            msg().message("Loading applets:")
            yield 1
            aa=obj[1]
            for i in range(len(aa)-1,-1,-1):
                a=aa[i]
                msg().message("  "+a.name)
                msg().step()
                yield 1
                applets().activate(a)
#       if id(a.system) != id(getCurrentSystemPM()):
#         a.setSystem(getCurrentSystemPM())
        msg().step(0,1)
        msg().status("Setup %s loaded."%url)
    def on_save_setup(self,*arg):
        self.saveSetup()

    def load_system_selected(self,*arg):
        w=self.load_system_fileselection
        self.last_system_path=w.get_filename()
        systemlist().activate(getSystem(self.last_system_path))
        w.hide()

    def save_system_selected(self,*arg):
        w=self.save_system_fileselection
        p=w.get_filename()
        self.last_system_path=p
        s=getCurrentSystemPM()
        if s is not None:
            if os.path.isdir(p):
                try:
    #       print p,"->",os.path.join(p,"POSCAR")
                    s.INITIAL_STRUCTURE.write(os.path.join(p,"POSCAR"))
                except:
                    msg().exception()
                    msg().error("Can not write POSCAR. Check the p4vasp.log for details.")
                try:
    #       print s.INCAR.toxml()
                    s.INCAR.write(os.path.join(p,"INCAR"))
                except:
                    msg().exception()
                    msg().error("Can not write INCAR. Check the p4vasp.log for details.")
                try:
                    f=open(os.path.join(p,"KPOINTS"),"w")
                    f.write(s.KPOINTS_TEXT)
                    f.close()
                except:
                    msg().exception()
                    msg().error("Can not write KPOINTS. Check the p4vasp.log for details.")
                try:
                    f=open(os.path.join(p,"DESCRIPTION"),"w")
                    d=s.DESCRIPTION
                    if d is None:
                        d=s.NAME
                    if d is None:
                        d="No description."
                    f.write(d)
                    f.close()
                except:
                    msg().exception()
                    msg().error("Can not write DESCRIPTION. Check the p4vasp.log for details.")

            else:
                try:
                    s.INITIAL_STRUCTURE.write(p)
                except:
                    msg().exception()
                    msg().error("Can not write POSCAR. Check the p4vasp.log for details.")
        else:
            msg().error("System is None, nothing to write.")
        w.hide()

    def show_load_system_fileselection(self,*arg):
        xml=p4vasp.util.loadGlade(self.gladefile,"load_system_fileselection")
        self.connect_signals(xml)
        self.load_system_fileselection=xml.get_widget("load_system_fileselection")
        self.load_system_fileselection.set_filename(self.last_system_path)
        self.load_system_fileselection.show()
    def show_save_system_fileselection(self,*arg):
        xml=p4vasp.util.loadGlade(self.gladefile,"save_system_fileselection")
        self.connect_signals(xml)
        self.save_system_fileselection=xml.get_widget("save_system_fileselection")
        self.save_system_fileselection.set_filename(self.last_system_path)
        self.save_system_fileselection.show()
    def show_about_dialog(self,*arg):
        import p4vasp
        xml=p4vasp.util.loadGlade(self.gladefile,"about_dialog")
        self.connect_signals(xml)
        about=xml.get_widget("about_dialog")
        about_label=xml.get_widget("about_label")
        try:
            about_label.set_markup("""<big><b>%s <i>v%sr%s</i></b></big>

       Build:%s
       Homepage: <span foreground="blue">http://www.p4vasp.at</span>
       P4vasp home directory:%s

       P4vasp, Copyright (C) 2003,2004 Orest Dubay &lt;dubay@danubiananotech.com&gt;
       P4vasp comes with <u>ABSOLUTELY NO WARRANTY</u>.
       This is free software, and you are welcome to redistribute it
       under certain conditions; see Help/License agreement for details.
      """%(p4vasp.name,p4vasp.version,p4vasp.release,p4vasp.build_date,p4vasp.p4vasp_home))
        except:
            about_label.set_markup("""<big><b>P4vasp <span foreground="red"><i>development version</i></span></b></big>

       Homepage: <span foreground="blue">http://www.p4vasp.at</span>
       P4vasp home directory:%s

       P4vasp, Copyright (C) 2003,2004 Orest Dubay &lt;dubay@danubiananotech.com&gt;
       P4vasp comes with <u>ABSOLUTELY NO WARRANTY</u>.
       This is free software, and you are welcome to redistribute it
       under certain conditions; see Help/License agreement for details.
      """%(p4vasp.p4vasp_home))

        about.show()
    def show_license_dialog(self,*arg):
        xml=p4vasp.util.loadGlade(self.gladefile,"license_dialog")
        self.connect_signals(xml)
        about=xml.get_widget("license_dialog")
        about.show()

    def hide_widget(self,widget):
        widget.hide()

    def show_widget(self,widget):
        widget.show()


    def quitNow(self,x):
        gtk.main_quit()

    def initToolbarAppletButtons(self):
        for x in self.toolbar.get_children():
#      print "toolbar:",x.get_name()
            v=split(x.get_name())
            if len(v)==2:
                if v[0]=="astart":
                    x.connect("clicked",startApplet,v[1],self)

    def showApplet(self,applet):
        if not applet.applet_ready:
            if applet.showmode in [applet.EMBEDDED_MODE,applet.EMBEDDED_ONLY_MODE]:
                if self.embedded_applet is not None:
                    self.embedded_applet.destroyApplet()
        #    self.addApplet(applet)
                panel=applet.createPanel()
        #      self.notebook.append_page(panel,gtk.Label(applet.name))
                if panel is None:
                    msg().confirm_error("Can not start applet %s"%applet.name)
                    return None
                self.applet_box.add(panel)
                panel.show()
#       panel.realize()
        #      page=self.notebook.page_num(panel)
        #      self.notebook.set_current_page(page)
                applet.initUI()

                applet.show()
                self.embedded_applet=applet
                applet.applet_ready=1
                if id(applet.system) != id(getCurrentSystemPM()):
                    applet.setSystem(getCurrentSystemPM())
            else:
                panel=applet.createPanel()
                applet.setExternalMode()
                if panel is not None:
                    panel.show()
#          panel.realize()
        #      page=self.notebook.page_num(panel)
        #      self.notebook.set_current_page(page)
                applet.initUI()

                applet.show()
                applet.applet_ready=1
                if id(applet.system) != id(getCurrentSystemPM()):
                    applet.setSystem(getCurrentSystemPM())
        else:
            applet.show()

    def quickCommit(self,*arg):
        import p4vasp.db as db
        s=getCurrentSystemPM()
        if s is not None:
            d=db.getDatabase()
            d.connect()
            for dd in d:
                if dd.getDefaultCommit():
                    dd.addUser()
                    dd.storePM(s)

    def reload_gen(self):
        for s in systemlist():
            msg().status("Invalidating system %s"%str(s.NAME))
            s.release()
            yield 1
        for a in applets():
            msg().status("Notifying %s"%str(a.name))
            a.updateSystem()
            yield 1
        msg().status("OK")

    def on_reload_activate(self,*arg):
        schedule(self.reload_gen())
    def externalizeApplet(self,applet):
        if id(applet) == id(self.embedded_applet):
            self.embedded_applet=None
    def embedApplet(self,applet):
        if not applet.applet_ready:
            self.showApplet(applet)
        if not applet.isEmbedded():
            panel=applet.panel
            if panel is None:
                msg().error("Can not embed applet %s"%applet.name)
                return None
            if self.embedded_applet is not None:
                self.embedded_applet.destroyApplet()
            if panel.get_parent() is None:
                self.applet_box.add(panel)
            else:
                panel.reparent(self.applet_box)
            self.applet_box.show_all()
#      panel.show()
#      panel.realize()
            applet.show()
            self.embedded_applet=applet
            applet.applet_ready=1


vbequeue=_cp4vasp.VisBackEventQueue_get()

def getSelectionFromVisStructureDrawer(d):
    s=p4vasp.Selection.Selection()
    for i in range(d.getSelectedCount()):
        a=d.getSelected(i)
#    print i,(a.atom,a.nx,a.ny,a.nz)
        s.append((a.atom,a.nx,a.ny,a.nz))
    return s

def idle_func():
    global vbequeue
    scheduler().next()
    selection_types=(cp4vasp.BE_SELECTED,cp4vasp.BE_DESELECTED)
    time.sleep(0.005)
    while vbequeue.current() is not None:
        c=vbequeue.current()
#    print c
#    print "vbe",c.type,c.index,c.nx,c.ny,c.nz

        if c.type in selection_types:
            sd=c.getStructureDrawer()
            if sd is not None:
                sel=getSelectionFromVisStructureDrawer(sd)
    #      print "selected",sel.encodeSimple()
                p4vasp.Selection.selection().setSelection(sel)
                p4vasp.Selection.selection().notify(sd)
        elif c.type == cp4vasp.BE_WIN_CLOSE:
            w=c.getWindow()
            if w is not None:
                if w.this is not None:
                    try:
                        x=filter(lambda x,s=w.this:x.getWindowPtr()==s,applets())[0]
                        x.destroyApplet()
                    except:
                        msg().exception()
        elif c.type == cp4vasp.BE_WIN_ACTIVATE:
            w=c.getWindow()
            w.redraw()
            wp=w.this
#      print "ACTIVATE",wp
            if wp is not None:
                a=applets()
                for x in a:
                    p=x.getWindowPtr()
                    if p == wp:
#           print "activate",x
                        a.activate(x)
                        break

        vbequeue.pop()
    return True

def startApplet(widget,applet,frame):
#  print "start",applet
#  a=appletfactory().create(applet)
#  frame.showApplet(a)
#  applets().getActive(applet)
    applets().activate(applets().factory.create(applet))

def init():
#  msg().message("p4vasp init:")
#  yield 1
    frame=Frame()
#  msg().message("  frame constr.")
#  yield 1
    try:
        frame.init3d()
#    msg().message("  3d initialized")
        yield 1
    except:
        msg().error("Error initialising 3d visualisation.")
        yield 1

    frame.createFrame()
    msg().status("Searching for applets")
    yield 1
    appletfactory().registerApplets()
    msg().status("Creating menu items")
    yield 1
    for x in appletfactory().sortedvalues:
        m=x.Class.menupath
        if m is not None:
            msg().message("Add menu "+join(m,"::"))
            item=frame.getMenuItem(m)
            item.connect("activate",startApplet,x.Class,frame)

    msg().status("Initializing toolbar buttons")
    yield 1
    frame.initToolbarAppletButtons()

    msg().status("Initializing selection applet")
    yield 1

    setAppletFrame(frame)

    frame.createHelpMenu()
#  frame.xml.get_widget("help_item").set_right_justified(1)
    frame.selection_applet=SelectionApplet(frame.selection_entry,frame.selection_set,frame.selection_none)
    applets().append(frame.selection_applet)
    frame.selection_applet.initUI()
    yield 1
    applets().notify_on_append.append(lambda x,y,f=frame.showApplet:f(y))
    for i in range(1,len(sys.argv)):
        s=sys.argv[i]
        msg().status("reading %s"%s)
        yield 1
        frame.addSystem(getSystem(s))

    applets().activate(applets().factory.create("p4vasp.applet.InfoApplet.InfoApplet"))
    try:
        msg().status("loading setup")
        yield 1
        scheduleFirst(frame.loadSetupGen("setup.xml"))
        yield 1
        msg().status("setup loaded")
        yield 1
    except:
        pass

    msg().status("reading vasprun.xml")
    yield 1
    frame.addSystem(XMLSystemPM("vasprun.xml"))
    msg().status("reading vasprun.xml OK")
    yield 1

    msg().status("OK")
    msg().step(0,1)
    #  import traceback
    #  traceback.print_exc()
    #  print "Loading setup failed."


schedule(init())
gobject.idle_add(idle_func)
gtk.main()
