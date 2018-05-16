#!/usr/bin/python2
"""Slightly modified PIDDLE canvas implementations for PyGTK.

The real documentation is in piddleGTK.

"""
__author__ = "Fred L. Drake, Jr.  <fdrake@acm.org>"
__version__ = '$Revision: 1.1 $'

# Do this first so we only proceed if PyGTK is actually available:
import gtk
import gtk.gdk
import pango
import string
import p4vasp.piddle.piddle as piddle


_DEFAULT_FONT_FACE = "helvetica"


def _pixels_per_point():
  """Return the number of pixels for each typographer's point."""
  #
  # This is a function instead of a computed constant so that we
  # don't have to actually initialize _gkt, allowing the application 
  # to control that if needed.  It simply needs to be done before
  # this can be used.
  #
  return ((25.4 * gtk.gtk.gdk.screen_height())
          / gtk.gtk.gdk.screen_height_mm()) / 72.0


class DrawableCanvas(piddle.Canvas):
  def __init__(self, drawable):
    self.__color_cache={}
    self.backgroundColor = piddle.white
    self.drawable=drawable
    piddle.Canvas.__init__(self)
    self.gc = self.drawable.new_gc(foreground=None, background=None, font=None, 
    function=-1, fill=-1, tile=None,
    stipple=None, clip_mask=None, subwindow_mode=-1,
    ts_x_origin=-1, ts_y_origin=-1, clip_x_origin=-1,
    clip_y_origin=-1, graphics_exposures=-1,
    line_width=-1, line_style=-1, cap_style=-1,
    join_style=-1)

  def isInteractive(self):
    return 0

  def canUpdate(self):
    return 1

  def clear(self, background=None):
    if background is not None:
      self.backgroundColor = background	
    if self.backgroundColor == piddle.transparent:
      return
    
    self.gc.set_foreground(self.get_color(self.backgroundColor))
    w,h=self.drawable.get_size()
    
    self.drawable.draw_rectangle(self.gc,1,0,0,w,h)

  def flush(self):
    pass

  def drawLine(self, x1, y1, x2, y2, color=None, width=None):
    # We could just call drawLines(), or drawLines() could call here,
    # but that would just get slow.
#    print "drawLine", x1, y1, x2, y2, color, width
    if color is None:
      color = self.defaultLineColor
    if color == piddle.transparent:
      return
    if width is None:
        width = self.defaultLineWidth
    #buffer = self.__ensure_size(x2+width, y2+width)
    gc = self.gc
    gc.foreground = self.get_color(color)
    gc.line_width = width
#    print "drawable",self.drawable
    self.drawable.draw_line(gc, int(x1), int(y1), int(x2), int(y2))

  def drawLines(self, lineList, color=None, width=None):
    if color is None:
      color = self.defaultLineColor
    if color == piddle.transparent:
      return
    if width is None:
        width = self.defaultLineWidth
    # force everything to the nearest integer,
    # and make sure the canvas is big enough:
    #iwidth = iheight = 0
    ##for i in range(len(lineList)):
    ##    x1, y1, x2, y2 = map(int, map(round, lineList[i]))
    ##    iwidth = max(iwidth, x1, x2)
    ##    iheight = max(iheight, y1, y2)
    #
    ##buffer = self.__ensure_size(iwidth+width, iheight+width)

    gc = self.gc
    gc.foreground = self.get_color(color)
    gc.line_width = width
    self.drawable.draw_segments(gc, map(lambda x:tuple(map(int,x)),lineList))

  def drawPolygon(self, pointlist, edgeColor=None, edgeWidth=None,
                  fillColor=None, closed=0):
    if len(pointlist) < 3:
      raise ValueError, "too few points in the point list"
    # XXX lots more should be checked
    if edgeColor is None:
      edgeColor = self.defaultLineColor
    if edgeWidth is None:
      edgeWidth = self.defaultLineWidth
    if fillColor is None:
      fillColor = self.defaultFillColor
    # force everything to the nearest integer,
    # and make sure the canvas is big enough:
    iwidth = 0
    iheight= 0
    for i in range(len(pointlist)):
      x, y = pointlist[i]
      point = (int(round(x)), int(round(y)))
      x, y = point
      iwidth = max(iwidth, x)
      iheight = max(iheight, y)
      pointlist[i] = point
    #
    gc = self.gc
    if fillColor != piddle.transparent:
      filled = 1
      gc.foreground = self.get_color(fillColor)
      gc.line_width = 1
      self.drawable.draw_polygon(gc, 1, pointlist)
    if edgeColor != piddle.transparent:
      gc.foreground = self.get_color(edgeColor)
      gc.line_width = edgeWidth
      if closed:
        self.drawable.draw_polygon(gc, 0, pointlist)
      else:
        self.drawable.draw_lines(gc, pointlist)

  def drawRect(self, x1, y1, x2, y2, edgeColor=None, edgeWidth=None,
               fillColor=None):
    if edgeColor is None:
      edgeColor = self.defaultLineColor
    if edgeWidth is None:
      edgeWidth = self.defaultLineWidth
    if fillColor is None:
      fillColor = self.defaultFillColor
    w = max(x1 + edgeWidth, x2 + edgeWidth)
    h = max(y1 + edgeWidth, y2 + edgeWidth)
#        buffer = self.__ensure_size(w, h)
    gc = self.gc
    if fillColor != piddle.transparent:
      gc.foreground = self.get_color(fillColor)
      gc.line_width = 1
      self.drawable.draw_rectangle(gc, 1, int(x1), int(y1), int(x2-x1), int(y2-y1))
    if edgeColor != piddle.transparent:
      gc.foreground = self.get_color(edgeColor)
      gc.line_width = edgeWidth
      self.drawable.draw_rectangle(gc, 0, int(x1), int(y1), int(x2-x1), int(y2-y1))

  def get_color(self, color):
    try:
      return self.__color_cache[color]
    except KeyError:
      cmap=self.drawable.get_colormap()
      c=cmap.alloc_color(int(color.red * 0xffff),
                         int(color.green * 0xffff),
                         int(color.blue * 0xffff))
      self.__color_cache[color] = c
      return c

class DrawingAreaCanvas(DrawableCanvas):
  def __init__(self, area=None):    
    if area is None:
      area=gtk.DrawingArea()
    self.area=area
#    print "area       ",area
#    print "area.window",area.window
    DrawableCanvas.__init__(self,area.window)
    self.pango_context=None
    self.__font_cache={}

  def get_font_description(self,font):      
    s=font.face
    if s is None:
      s=""
    if s=="sansserif":
      s="sans"
    if font.bold:
      s+=" bold"
    if font.italic:
      s+=" italic"
    s+=" "+str(font.size)
    return s

  def getFontDescription(self,font):      
    return pango.FontDescription(self.get_font_description(font))

  def getFont(self, font):
    try:
      return self.__font_cache[font]
    except KeyError:
      if self.pango_context is None:
        self.pango_context=self.area.get_pango_context()      
      f=self.pango_context.load_font(self.getFontDescription(font))
      self.__font_cache[font] = f
      return f

  def createPangoMarkup(self, s,font=None, color=None):
    if color is None:	  
      color = self.defaultLineColor
      if color == piddle.transparent:
        return None
    cs="#%02x%02x%02x"%(int(255*color.red),int(255*color.green),int(255*color.blue))
    if font is None:
      font = self.defaultFont
    ms=s.replace("<","&lt;").replace(">","&gt;")
    fs=self.get_font_description(font)
    if font.underline:
      return '<span font_desc="%s" underline="single" foreground="%s">%s</span>'%(fs,cs,ms)
    else:
      return '<span font_desc="%s" underline="none" foreground="%s">%s</span>'%(fs,cs,ms)
  def drawString(self, s, x, y, font=None, color=None, angle=0.0):
    angle = int(round(angle))
    if angle != 0:
        raise NotImplementedError, "rotated text not implemented"
    gc = self.gc
    if self.pango_context is None:
      self.pango_context=self.area.get_pango_context()          
    layout=pango.Layout(self.pango_context)
    layout.set_markup(self.createPangoMarkup(s,font,color))
    w,h=layout.get_pixel_size()
    self.drawable.draw_layout(gc, int(x), int(y-h), layout)

  def fontHeight(self, font=None):
    if font is None:
        font = self.defaultFont
    return 1.2 * font.size

  def fontAscent(self, font=None):
    if font is None:
        font = self.defaultFont        
    return self.getFont(font).get_metrics().get_ascent()

  def fontDescent(self, font=None):
    if font is None:
        font = self.defaultFont
    return self.getFont(font).get_metrics().get_descent()

  def stringWidth(self, s, font=None):
    if font is None:
        font = self.defaultFont
    if self.pango_context is None:
      self.pango_context=self.area.get_pango_context()          	
    layout=pango.Layout(self.pango_context)
    layout.set_markup(self.createPangoMarkup(s,font))
    return layout.get_pixel_size()[0]
  def stringHeight(self, s, font=None):
    if font is None:
        font = self.defaultFont
    if self.pango_context is None:
      self.pango_context=self.area.get_pango_context()          	
    layout=pango.Layout(self.pango_context)
    layout.set_markup(self.createPangoMarkup(s,font))
    return layout.get_pixel_size()[1]
  def stringSize(self, s, font=None):
    if font is None:
        font = self.defaultFont
    if self.pango_context is None:
      self.pango_context=self.area.get_pango_context()
    layout=pango.Layout(self.pango_context)
    layout.set_markup(self.createPangoMarkup(s,font))
    return layout.get_pixel_size()
      
    
class BasicCanvas(DrawingAreaCanvas):
  def __init__(self, area=None):
    DrawingAreaCanvas.__init__(self,area)
#    self.area_drawable = self.drawable
    w,h=self.area_drawable().get_size()
    self.drawable=gtk.gdk.Pixmap(self.area.window,w,h)
    self.background_buffer = None
    if self.area is not None:
      self.area.connect("expose_event", self.__expose_event)
      self.area.connect("configure_event", self.__configure_event)

  def area_drawable(self):
    return self.area.window
  def isInteractive(self):
    return 0

  def canUpdate(self):
    return 1

  def flush(self):
    w,h=self.drawable.get_size()  
    self.area_drawable().draw_drawable(self.gc,self.drawable,0,0,0,0,w,h)

  def ensure_size(self, width, height):
    if not (width and height):
        return
    old_width, old_height = self.drawable.get_size()
    width = max(width, old_width)
    height = max(height, old_height)
    if (width, height) != self.drawable.get_size():
      new_pixmap = gtk.gdk.Pixmap(self.area.window, width, height)
      gc = self.gc
      if self.backgroundColor == piddle.transparent:
          self.backgroundColor = piddle.white
      c = self.get_color(self.backgroundColor)
      gc.foreground = c
      y = (height + 1) / 2
      gc.line_width = int(y * 2)
      new_pixmap.draw_line(gc, 0, y, width, y)
      new_pixmap.draw_drawable(gc, self.drawable,0, 0, 0, 0, old_width, old_height)
      self.drawable = new_pixmap
    return self.drawable

  def flush(self):
#    print "flush"
    width, height = self.drawable.get_size()
    self.area_drawable().draw_drawable(self.gc, self.drawable,0, 0, 0, 0, width, height)

  def to_background_buffer(self):
    width, height = self.drawable.get_size()
    if self.area.window is None:
      new_pixmap = gtk.gdk.Pixmap(None, width, height,24)
    else:
      new_pixmap = gtk.gdk.Pixmap(self.area.window, width, height)
    new_pixmap.draw_drawable(self.gc, self.drawable,0, 0, 0, 0, width, height)
    self.background_buffer = new_pixmap
    return new_pixmap


  def from_background_buffer(self):
    if self.background_buffer:
      width,height=self.background_buffer.get_size()
      if not (width and height):
          return
      self.drawable.draw_drawable(self.gc, self.background_buffer,0, 0, 0, 0, width, height)
      self.area_drawable().draw_drawable(self.gc, self.background_buffer,0, 0, 0, 0, width, height)


  def __configure_event(self, area, event):
#      print "configure event",event.type
#      print "event:   ",event.x,event.y,event.width,event.height
#      print "area:    ",area
#      print "drawable:",self.drawable.get_size()
      b = self.ensure_size(event.x + event.width, event.y + event.height)
      width, height = self.drawable.get_size()
      if hasattr(self,"resizeCallback"):
	self.resizeCallback(event.width,event.height)

  def __expose_event(self, area, event):
#      print "expose event"
      x, y, width, height = event.area
      b = self.ensure_size(width, height)
      self.area_drawable().draw_drawable(self.gc, b, x, y, x, y, width, height)


class InteractiveCanvas(BasicCanvas):
    def __init__(self, area, window):
        BasicCanvas.__init__(self, area)
	window=area.get_toplevel()
	self.window=window
        # XXX set up the event handlers
	
#        self.initEvents()
#        self.area.connect("event", self.__event)
        self.__get_allocation = area.get_allocation
	self.__button=0

    def initEvents(self):
      event_mask=    (  gtk.gdk.BUTTON_PRESS_MASK
                      | gtk.gdk.BUTTON_RELEASE_MASK
                      | gtk.gdk.KEY_PRESS_MASK
                      | gtk.gdk.POINTER_MOTION_MASK
                      #| gtk.gdk.POINTER_MOTION_HINT_MASK
		      )
#      x=self.area
      x=self.area.get_toplevel()
      x.set_events(event_mask)
      x.connect("event", self.__event)
      x.connect("motion_notify_event", self.__event)
      x=self.area
      x.set_events(event_mask)
#      print "initEvents:"
#      while x is not None:
#        print "  ",x
#	x.realize()
#        x.set_events(gtk.gdk.ALL_EVENTS_MASK)
#	x=x.get_parent()
	
    def isInteractive(self):
        return 1

    def __event(self, widget, event):
        print "EVENT",event.type
        if event.type == gtk.gdk.ENTER_NOTIFY:
            x, y, ok = self.__check_coords(event.x, event.y)
            if ok:
                self.onOver(self, x, y,self.__button)
        elif event.type == gtk.gdk.MOTION_NOTIFY:
            x, y = widget.get_pointer()
            x, y, ok = self.__check_coords(x, y)
            if ok:
                self.onOver(self, x, y, self.__button)
        elif event.type == gtk.gdk.BUTTON_PRESS:
	    self.__button=event.button
            x, y = widget.get_pointer()
            x, y, ok = self.__check_coords(x, y)
            if ok:
                self.onOver(self, x, y,event.button)
        elif (event.type in [gtk.gdk.BUTTON_RELEASE]):
	    self.__button=0
            x, y, ok = self.__check_coords(event.x, event.y)
            if ok:
                self.onClick(self, x, y, event.button)
        elif event.type == gtk.gdk.KEY_PRESS:
#	    print "key pressed"
#	    print "keyval",event.keyval,gtk.gdk.keyval_name(event.keyval)
#	    print "string",event.string
            key = self.__get_key_string(event.keyval, event.string)
            if key:
                # Get as much milage as possible from the modifiers
                # computation:
#		print "key:",key
                try:
                    modifiers = self.__modifier_map[event.state]
#		    print "modifiers:",modifiers
                except KeyError:
                    modifiers = 0
                    state = event.state
                    if (state & gtk.gdk.SHIFT_MASK) == gtk.gdk.SHIFT_MASK:
                        modifiers = piddle.modShift
                    if (state & gtk.gdk.CONTROL_MASK) == gtk.gdk.CONTROL_MASK:
                        modifiers = modifiers | piddle.modControl
                    self.__modifier_map[state] = modifiers
#		print "onKey(self, %s, %s)"%(repr(key),repr(modifiers))
                self.onKey(self, key, modifiers)

    def __check_coords(self, x, y):
            xoff, yoff, width, height = self.__get_allocation()
            _int = int
            _round = round
            x = _int(_round(x)) - xoff
            y = _int(_round(y)) - yoff
            if x < 0 or y < 0 or x >= width or y >= height:
                return x, y, 0
            return x, y, 1
#    def __get_key_string(self,k,v):
#      print "get_key_string ",k,gtk.gdk.keyval_name(k),v
#      print "get_key_string_",repr(self.__get_key_string_.get(k,v))
#      print self.__get_key_string_
#      return self.__get_key_string_.get(k,v)
    __get_key_string = {
        gtk.gdk.keyval_from_name("Left"): piddle.keyLeft,
        gtk.gdk.keyval_from_name("Right"): piddle.keyRight,
        gtk.gdk.keyval_from_name("Up"): piddle.keyUp,
        gtk.gdk.keyval_from_name("Down"): piddle.keyDown,
        gtk.gdk.keyval_from_name("Prior"): piddle.keyPgUp,
        gtk.gdk.keyval_from_name("Next"): piddle.keyPgDn,
        gtk.gdk.keyval_from_name("Home"): piddle.keyHome,
        gtk.gdk.keyval_from_name("End"): piddle.keyEnd,
        }.get

    # This covers most cases, but may be extended by __event().
    __modifier_map = {
        0: 0,
        gtk.gdk.SHIFT_MASK: piddle.modShift,
        gtk.gdk.CONTROL_MASK: piddle.modControl,
        gtk.gdk.SHIFT_MASK | gtk.gdk.CONTROL_MASK: (
            piddle.modShift | piddle.modControl),
        }

class InteractiveBoxCanvas(BasicCanvas):
    def __init__(self, box):
#	self.i=0
        self.box=box
	self.area=None
        self.initEvents()	
        BasicCanvas.__init__(self, self.area)
#	window=area.get_toplevel()
#	self.window=window
#        self.area.connect("event", self.__event)
        self.__get_allocation = self.area.get_allocation
	self.__button=0

    def initEvents(self):
      print "initEvents"
      if self.area is not None:
        self.area.destroy()
#        self.box.remove(self.area)
      self.area=gtk.DrawingArea()
#      self.area=gtk.Label("test"+str(self.i))
      self.__get_allocation = self.area.get_allocation
#      self.i+=1
      self.box.pack_start(self.area)
      self.box.show_all()
      w,h=self.area_drawable().get_size()
      self.drawable=gtk.gdk.Pixmap(self.area.window,w,h)
      self.background_buffer = None
      self.pango_context=None
      self.__font_cache={}

#      event_mask=    (  gtk.gdk.BUTTON_PRESS_MASK
#                      | gtk.gdk.BUTTON_RELEASE_MASK
#                      | gtk.gdk.KEY_PRESS_MASK
#                      | gtk.gdk.POINTER_MOTION_MASK
#                      | gtk.gdk.POINTER_MOTION_HINT_MASK)
#      x=self.area
#      x.set_events(event_mask)
#      x.connect("event", self.__event)
##      x.connect("motion_notify_event", self.__event)
 
	
    def isInteractive(self):
        return 1

    def __event(self, widget, event):
        print "EVENT",event.type
        if event.type == gtk.gdk.ENTER_NOTIFY:
            x, y, ok = self.__check_coords(event.x, event.y)
            if ok:
                self.onOver(self, x, y,self.__button)
        elif event.type == gtk.gdk.MOTION_NOTIFY:
            x, y = widget.get_pointer()
            x, y, ok = self.__check_coords(x, y)
            if ok:
                self.onOver(self, x, y, self.__button)
        elif event.type == gtk.gdk.BUTTON_PRESS:
	    self.__button=event.button
            x, y = widget.get_pointer()
            x, y, ok = self.__check_coords(x, y)
            if ok:
                self.onOver(self, x, y,event.button)
        elif (event.type in [gtk.gdk.BUTTON_RELEASE]):
	    self.__button=0
            x, y, ok = self.__check_coords(event.x, event.y)
            if ok:
                self.onClick(self, x, y, event.button)
        elif event.type == gtk.gdk.KEY_PRESS:
#	    print "key pressed"
#	    print "keyval",event.keyval,gtk.gdk.keyval_name(event.keyval)
#	    print "string",event.string
            key = self.__get_key_string(event.keyval, event.string)
            if key:
                # Get as much milage as possible from the modifiers
                # computation:
#		print "key:",key
                try:
                    modifiers = self.__modifier_map[event.state]
#		    print "modifiers:",modifiers
                except KeyError:
                    modifiers = 0
                    state = event.state
                    if (state & gtk.gdk.SHIFT_MASK) == gtk.gdk.SHIFT_MASK:
                        modifiers = piddle.modShift
                    if (state & gtk.gdk.CONTROL_MASK) == gtk.gdk.CONTROL_MASK:
                        modifiers = modifiers | piddle.modControl
                    self.__modifier_map[state] = modifiers
#		print "onKey(self, %s, %s)"%(repr(key),repr(modifiers))
                self.onKey(self, key, modifiers)

    def __check_coords(self, x, y):
            xoff, yoff, width, height = self.__get_allocation()
            _int = int
            _round = round
            x = _int(_round(x)) - xoff
            y = _int(_round(y)) - yoff
            if x < 0 or y < 0 or x >= width or y >= height:
                return x, y, 0
            return x, y, 1
#    def __get_key_string(self,k,v):
#      print "get_key_string ",k,gtk.gdk.keyval_name(k),v
#      print "get_key_string_",repr(self.__get_key_string_.get(k,v))
#      print self.__get_key_string_
#      return self.__get_key_string_.get(k,v)
    __get_key_string = {
        gtk.gdk.keyval_from_name("Left"): piddle.keyLeft,
        gtk.gdk.keyval_from_name("Right"): piddle.keyRight,
        gtk.gdk.keyval_from_name("Up"): piddle.keyUp,
        gtk.gdk.keyval_from_name("Down"): piddle.keyDown,
        gtk.gdk.keyval_from_name("Prior"): piddle.keyPgUp,
        gtk.gdk.keyval_from_name("Next"): piddle.keyPgDn,
        gtk.gdk.keyval_from_name("Home"): piddle.keyHome,
        gtk.gdk.keyval_from_name("End"): piddle.keyEnd,
        }.get

    # This covers most cases, but may be extended by __event().
    __modifier_map = {
        0: 0,
        gtk.gdk.SHIFT_MASK: piddle.modShift,
        gtk.gdk.CONTROL_MASK: piddle.modControl,
        gtk.gdk.SHIFT_MASK | gtk.gdk.CONTROL_MASK: (
            piddle.modShift | piddle.modControl),
        }


class DialogCanvas(InteractiveCanvas):
    def __init__(self, size=(300,300), name="Piddle-GTK"):
      #
      width, height = (int(round(size[0])), int(round(size[1])))
      top = self.__top = gtk.Dialog()
      vbox = top.vbox
      frame = self.__frame = gtk.Frame()
      frame.set_shadow_type(gtk.SHADOW_IN)
      da = gtk.DrawingArea()
      da.set_size_request(size[0],size[1])
      button = gtk.Button("Dismiss")
      button.connect("clicked",
                     lambda button, top=top: top.destroy())
      frame.set_border_width(10)
      bbox = self.__bbox = gtk.HButtonBox()
      bbox.set_layout(gtk.BUTTONBOX_END)
      bbox.pack_end(button)
      top.action_area.pack_end(bbox)
      frame.add(da)
      vbox.pack_start(frame)
      InteractiveCanvas.__init__(self, da, top)
      top.set_wmclass("canvas", "Canvas")
      da.realize()
      da.set_usize(width, height)
      top.show_all()
      top.set_icon_name(name)
      top.set_title(name)
      self.ensure_size(width, height)


    # Class-specific interfaces (.get_drawing_area() provided by Canvas):

    def get_toplevel(self):
      """Return the gtk.Dialog which contains the canvas."""
      return self.__top

    def get_frame(self):
      """Return the gtk.Frame that directly surrounds the canvas and
      provides the visual relief around it."""
      return self.__frame

    def get_buttonbox(self):
      """Return the gtk.HButtonBox that holds the buttons in the
      dialog's action area."""
      return self.__bbox


class GTKCanvas(InteractiveCanvas):
    """Very simple interactive canvas with no decoration."""

    def __init__(self, size=(300,300), name="Piddle-GTK2", infoline=1):
        """Initialize the canvas and minimal supporting widgets.

        If |infoline| is true (the default), a status bar will be
        included at the bottom of the window to support the
        ,setInfoLine() method.  If false, no statusbar will be used.

        """
        width, height = (int(round(size[0])), int(round(size[1])))
        #
        top = self.__top = gtk.Window()
        vbox = self.__vbox = gtk.VBox()
        da = gtk.DrawingArea()
        #
        top.add(vbox)
        vbox.pack_start(da)
        if infoline:
            sbar = self.__sbar = gtk.Statusbar()
            vbox.pack_end(sbar, expand=0)
            sbar.set_border_width(2)
        else:
            self.__sbar = None
        InteractiveCanvas.__init__(self, da, top)
        top.set_wmclass("canvas", "Canvas")
        da.realize()
        da.set_usize(width, height)
        top.show_all()
        top.set_icon_name(name)
        top.set_title(name)
        self.ensure_size(width, height)
        self.__status = None

    def setInfoLine(self, s):
        """If the canvas was constructed with a status bar, set the message."""
        if self.__sbar:
            if self.__status:
                self.__sbar.pop(1)
            if s:
                self.__sbar.push(1, str(s))
            self.__status = s


    # Class-specific interfaces (.get_drawing_area() provided by Canvas):

    def get_toplevel(self):
        """Return the gtk.Window which contains the canvas."""
        return self.__top

    def get_statusbar(self):
        """Return the gtk.Statusbar that implements the info line, or None.
        """
        return self.__sbar

    def get_vbox(self):
        """Return the gtk.VBox that the canvas widget and optional status
        bar are packed in."""
        return self.__vbox

def test():
  canvas=GTKCanvas()
  return gtk.FALSE
def test1():
  global d
  gc = d.window.new_gc(foreground=None, background=None, font=None, 
                            function=-1, fill=-1, tile=None,
                            stipple=None, clip_mask=None, subwindow_mode=-1,
                            ts_x_origin=-1, ts_y_origin=-1, clip_x_origin=-1,
                            clip_y_origin=-1, graphics_exposures=-1,
                            line_width=-1, line_style=-1, cap_style=-1,
                            join_style=-1)
  d.window.draw_line(gc,0,0,100,100)			  
  return gtk.FALSE
def test2():
  global c
  c.drawLine(10,10,90,80)
  c.drawLine(10,10,90,90)
  c.drawLine(10,10,90,100)
  c.drawString("xxx",20,20)
  c.flush()
  return gtk.FALSE
if __name__=="__main__":
  win=gtk.Window()
  box=gtk.VBox()
  win.add(box)
  button=gtk.Button("Quit")
  win.connect("destroy",gtk.mainquit)
  button.connect("clicked",gtk.mainquit)
  box.add(button)
  #gtk.idle_add(test)
  win.show_all()
  d=gtk.DrawingArea()
  d.set_size_request(200,200)
  box.add(d)
  c=BasicCanvas(d)
  win.show_all()
  gc = d.window.new_gc(foreground=None, background=None, font=None, 
                            function=-1, fill=-1, tile=None,
                            stipple=None, clip_mask=None, subwindow_mode=-1,
                            ts_x_origin=-1, ts_y_origin=-1, clip_x_origin=-1,
                            clip_y_origin=-1, graphics_exposures=-1,
                            line_width=-1, line_style=-1, cap_style=-1,
                            join_style=-1)
  #d.window.draw_line(gc,0,0,100,100)			  
  win.show_all()
  gtk.idle_add(test2)
  gtk.main()
