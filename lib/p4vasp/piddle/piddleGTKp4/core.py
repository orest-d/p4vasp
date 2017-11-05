"""Slightly modified PIDDLE canvas implementations for PyGTK.

The real documentation is in piddleGTK.

"""
__author__ = "Fred L. Drake, Jr.  <fdrake@acm.org>"
__version__ = '$Revision: 1.1 $'

# Do this first so we only proceed if PyGTK is actually available:
import _gtk
import GDK

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
    return ((25.4 * _gtk.gdk_screen_height())
            / _gtk.gdk_screen_height_mm()) / 72.0


class BasicCanvas(piddle.Canvas):
    def __init__(self, area=None):
        if area is None:
            import gtk
            area = gtk.GtkDrawingArea()
        self.__area = area
        self.__setup = 0
        self.__color_cache = {}
        self.backgroundColor = piddle.white
        self.__buffer = None
        self.__buffer_size = (-1, -1)
        self.__background_buffer = None
        self.__background_buffer_size = (-1, -1)
        self.__area.connect("expose_event", self.__expose_event)
        self.__area.connect("configure_event", self.__configure_event)

        piddle.Canvas.__init__(self)

    def isInteractive(self):
        return 0

    def canUpdate(self):
        return 1

    def clear(self, background=None):
        if background is not None:
            self.backgroundColor = background
        if self.__buffer:
            width, height = self.__buffer_size
            self.__buffer_size = (-1, -1)
            self.__buffer = None
            buffer = self.__ensure_size(width, height)
            self.__area.draw_pixmap(self.__gc, buffer,
                                   0, 0, 0, 0, width, height)

    def flush(self):
        if self.__buffer:
            width, height = self.__buffer_size
            self.__area.draw_pixmap(self.__gc, self.__buffer,
                                    0, 0, 0, 0, width, height)

    def drawLine(self, x1, y1, x2, y2, color=None, width=None):
        # We could just call drawLines(), or drawLines() could call here,
        # but that would just get slow.
        if color == piddle.transparent:
            return
        if color is None:
            color = self.defaultLineColor
            if color == piddle.transparent:
                return
        if width is None:
            width = self.defaultLineWidth
        #buffer = self.__ensure_size(x2+width, y2+width)
        gc = self.__gc
        gc.foreground = self.__get_color(color)
        gc.line_width = width
        _gtk.gdk_draw_line(self.__buffer, gc, x1, y1, x2, y2)

    def drawLines(self, lineList, color=None, width=None):
        if color == piddle.transparent:
            return
        if color is None:
            color = self.defaultLineColor
            if color == piddle.transparent:
                return
        if width is None:
            width = self.defaultLineWidth
        # force everything to the nearest integer,
        # and make sure the canvas is big enough:
        iwidth = iheight = 0
        ##for i in range(len(lineList)):
        ##    x1, y1, x2, y2 = map(int, map(round, lineList[i]))
        ##    iwidth = max(iwidth, x1, x2)
        ##    iheight = max(iheight, y1, y2)
        #
        ##buffer = self.__ensure_size(iwidth+width, iheight+width)
        gc = self.__gc
        gc.foreground = self.__get_color(color)
        gc.line_width = width
        _gtk.gdk_draw_segments(self.__buffer, gc, lineList)

    def drawString(self, s, x, y, font=None, color=None, angle=0.0):
        if color == piddle.transparent:
            return
        if color is None:
            color = self.defaultLineColor
            if color == piddle.transparent:
                return
        if "\n" in s or "\r" in s:
            self.drawMultiLineString(s, x, y, font, color, angle)
            return
        angle = int(round(angle))
        if angle != 0:
            raise NotImplementedError, "rotated text not implemented"
        if font is None:
            font = self.defaultFont
        lines = string.split(s, "\n")
        gdk_font = _font_to_gdkfont(font)
        textwidth = gdk_font.measure(s)
        width = max(x, x + textwidth)
        height = max(y, y + gdk_font.descent)
        buffer = self.__ensure_size(width, height)
        gc = self.__gc
        gc.foreground = self.__get_color(color)
        #gc.font = gdk_font
        _gtk.gdk_draw_text(buffer, gdk_font, gc, x, y, s)
        if font.underline:
            gc.line_width = 1
            y = y + gdk_font.descent
            _gtk.gdk_draw_line(buffer, gc, x, y, x + textwidth, y)

    def fontHeight(self, font=None):
        if font is None:
            font = self.defaultFont
        return 1.2 * font.size

    def fontAscent(self, font=None):
        if font is None:
            font = self.defaultFont
        gdk_font = _font_to_gdkfont(font)
        return gdk_font.ascent

    def fontDescent(self, font=None):
        if font is None:
            font = self.defaultFont
        gdk_font = _font_to_gdkfont(font)
        return gdk_font.descent

    def stringWidth(self, s, font=None):
        if font is None:
            font = self.defaultFont
        return _font_to_gdkfont(font).measure(s)

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
        iwidth = iheight = 0
        for i in range(len(pointlist)):
            x, y = pointlist[i]
            point = (int(round(x)), int(round(y)))
            x, y = point
            iwidth = max(iwidth, x)
            iheight = max(iheight, y)
            pointlist[i] = point
        buffer = self.__ensure_size(iwidth+edgeWidth, iheight+edgeWidth)
        #
        gc = self.__gc
        if fillColor != piddle.transparent:
            filled = 1
            gc.foreground = self.__get_color(fillColor)
            gc.line_width = 1
            _gtk.gdk_draw_polygon(buffer, gc, 1, pointlist)
        if edgeColor != piddle.transparent:
            gc.foreground = self.__get_color(edgeColor)
            gc.line_width = edgeWidth
            if closed:
                _gtk.gdk_draw_polygon(buffer, gc, 0, pointlist)
            else:
                _gtk.gdk_draw_lines(buffer, gc, pointlist)

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
        buffer = self.__ensure_size(w, h)
        gc = self.__gc
        if fillColor != piddle.transparent:
            gc.foreground = self.__get_color(fillColor)
            gc.line_width = 1
            _gtk.gdk_draw_rectangle(buffer, gc, 1, x1, y1, x2-x1, y2-y1)
        if edgeColor != piddle.transparent:
            gc.foreground = self.__get_color(edgeColor)
            gc.line_width = edgeWidth
            _gtk.gdk_draw_rectangle(buffer, gc, 0, x1, y1, x2-x1, y2-y1)


    # Class-specific interfaces:

    def get_drawing_area(self):
        return self.__area

    def ensure_size(self, width, height):
        # like __ensure_size(), but doesn't return buffer
        if (width <= 0) or (height <= 0):
            raise ValueError, "width and height must both be positive"
        self.__ensure_size(width, height)


    # Interfaces for subclasses:

    def __ensure_size(self, width, height):
        if not (width and height):
            return
        old_width, old_height = self.__buffer_size
        width = max(width, old_width)
        height = max(height, old_height)
        if not self.__setup:
            w = self.__area.get_window()
            self.__gc = w.new_gc()
            self.__cmap = w.colormap
            self.__setup = 1
            # surely there's a better way to get this?
            self.__depth = 24
        if (width, height) != self.__buffer_size or not self.__buffer:
            new_pixmap = _gtk.gdk_pixmap_new(
                None, width, height, self.__depth)
            gc = self.__gc
            if self.backgroundColor == piddle.transparent:
                self.backgroundColor = piddle.white
            c = self.__get_color(self.backgroundColor)
            gc.foreground = c
            y = (height + 1) / 2
            gc.line_width = int(y * 2)
            _gtk.gdk_draw_line(new_pixmap, gc, 0, y, width, y)
            if self.__buffer:
                # copy from old buffer to new buffer
                _gtk.gdk_draw_pixmap(new_pixmap, gc, self.__buffer,
                                     0, 0, 0, 0, old_width, old_height)
            self.__buffer = new_pixmap
            self.__buffer_size = self.size = (width, height)
            return new_pixmap
        else:
            return self.__buffer

    def to_background_buffer(self):
#        print "to background"
        width, height = self.__buffer_size
        if not self.__setup:
            w = self.__area.get_window()
            self.__gc = w.new_gc()
            self.__cmap = w.colormap
            self.__setup = 1
            # surely there's a better way to get this?
            self.__depth = 24
        if self.__buffer:
            new_pixmap = _gtk.gdk_pixmap_new(
                None, width, height, self.__depth)
            gc = self.__gc
            _gtk.gdk_draw_pixmap(new_pixmap, gc, self.__buffer,
                                 0, 0, 0, 0, width, height)
            self.__background_buffer = new_pixmap
            self.__background_buffer_size = (width, height)
            return new_pixmap
        else:
            self.__background_buffer = None
            self.__background_buffer_size = (-1, -1)	
            return None
    
    def from_background_buffer(self):
#        print "from background"
        width,height=self.__background_buffer_size
        if not (width and height):
            return
        old_width, old_height = self.__buffer_size
        width = max(width, old_width)
        height = max(height, old_height)
        if not self.__setup:
            w = self.__area.get_window()
            self.__gc = w.new_gc()
            self.__cmap = w.colormap
            self.__setup = 1
            # surely there's a better way to get this?
            self.__depth = 24
        if (width, height) != self.__buffer_size:
            new_pixmap = _gtk.gdk_pixmap_new(
                None, width, height, self.__depth)
            gc = self.__gc
            if self.backgroundColor == piddle.transparent:
                self.backgroundColor = piddle.white
            c = self.__get_color(self.backgroundColor)
            gc.foreground = c
            y = (height + 1) / 2
            gc.line_width = int(y * 2)
            _gtk.gdk_draw_line(new_pixmap, gc, 0, y, width, y)
            if self.__background_buffer:
                # copy from old buffer to new buffer
                _gtk.gdk_draw_pixmap(new_pixmap, gc, self.__background_buffer,
                                     0, 0, 0, 0, old_width, old_height)
            self.__buffer = new_pixmap
            self.__buffer_size = self.size = (width, height)
#   	    win=self.__area.get_window()
#	    self.__area.draw((0,0,win.width,win.height))
            return new_pixmap
        else:
            gc = self.__gc
            if self.__background_buffer:
                # copy from old buffer to new buffer
                _gtk.gdk_draw_pixmap(self.__buffer, gc, self.__background_buffer,
                                     0, 0, 0, 0, old_width, old_height)
#   	    win=self.__area.get_window()
#	    self.__area.draw((0,0,win.width,win.height))

            return self.__buffer
    

    # Internal interfaces:

    def __get_color(self, color):
        try:
            return self.__color_cache[color]
        except KeyError:
            _int = int
            c = self.__cmap.alloc(_int(color.red * 0xffff),
                                  _int(color.green * 0xffff),
                                  _int(color.blue * 0xffff))
            self.__color_cache[color] = c
            return c

    def __configure_event(self, area, event):
#        print "configure event",event.type
        buffer = self.__ensure_size(event.x + event.width,
                                   event.y + event.height)
        width, height = self.__buffer_size
        if (width > 0) and (height > 0):
            self.__area.draw_pixmap(self.__gc, buffer, 0, 0, 0, 0,
                                    width, height)
        self.size = self.__area.get_allocation()[2:]
	if hasattr(self,"resizeCallback"):
	  self.resizeCallback(self.size[0],self.size[1])

    def __expose_event(self, area, event):
#        print "expose event"
        x, y, width, height = event.area
        buffer = self.__ensure_size(width, height)
        self.__area.draw_pixmap(self.__gc, buffer, x, y, x, y,
                                width, height)


def _font_to_gdkfont(font):
    key = _font_to_key(font)
    xlfd = _fontkey_to_xlfd(key)
    try:
        return _xlfd_to_gdkfont(xlfd)
    except RuntimeError:
#        print "failed to load", xlfd
        raise


def _font_to_key(font):
    face = _DEFAULT_FONT_FACE
    if type(font.face) is type(''):
        try:
            face = _get_font_face(font.face)
        except KeyError:
            pass
    elif font.face is None:
        # we should use the default face
        pass
    else:
        for f in font.face:
            try:
                face = _get_font_face(f)
            except KeyError:
                pass
            else:
                break
    # weight & shaping attributes
    weight = _face_weight_map.get(face,
                                  ("medium", "bold"))[font.bold and 1 or 0]
    slant = _face_slant_map.get(face, ("r", "o"))[font.italic and 1 or 0]
    width = _face_width_map.get(face, "*")
    # If a scalable font isn't available, we might need to choose the
    # best fit from what's available:
    pixels = int(round(font.size * _pixels_per_point()))
    # 'charset' includes both registry and encoding
    if face == "symbol":
        charset = "adobe-fontspecific"
    else:
        charset = "*"
    return (face, weight, slant, width, pixels, charset)

_face_weight_map = {
    # face: (normal, bold)
    "courier": ("medium", "bold"),
    "helvetica": ("medium", "bold"),
    "symbol": ("medium", "medium"),
    "times": ("medium", "bold"),
    "avantgarde": ("book", "demibold"),
    "bookman": ("light", "demibold"),
    "charter": ("medium", "bold"),
    }
_face_slant_map = {
    # face: (normal, italic)
    "courier": ("r", "i"),
    "helvetica": ("r", "o"),
    "symbol": ("r", "r"),
    "times": ("r", "i"),
    "avantgarde": ("r", "o"),
    "bookman": ("r", "i"),
    "charter": ("r", "i"),
    "gothic": ("r", "o"),
    }
_face_width_map = {
    # face: normal-width-specifier
    "courier": "normal",
    "helvetica": "normal",
    "symbol": "normal",
    "times": "normal",
    "avantgarde": "normal",
    }


def _get_font_face(face):
    try:
        return _font_face_map[face]
    except KeyError:
        lface = string.lower(face)
        nface = _font_face_map.get(lface, lface)
        _font_face_map[lface] = nface
        return face

_font_face_map = {
    "courier": "courier",
    "monospaced": "courier",
    "helvetica": "helvetica",
    "sansserif": "helvetica",
    "serif": "times",
    "symbol": "symbol",
    "times": "times",
    }


def _fontkey_to_xlfd(key):
    return "-*-%s-%s-%s-%s-*-%s-*-*-*-*-*-%s" % key


def _xlfd_to_gdkfont(xlfd, cache={}):
    # This can raise RuntimeError if the font isn't actually available.
    try:
        return cache[xlfd]
    except KeyError:
        gdkfont = _gtk.gdk_font_load(xlfd)
        cache[xlfd] = gdkfont
        return gdkfont


class InteractiveCanvas(BasicCanvas):
    def __init__(self, area, window):
        # XXX set up the event handlers
	if window is not None:
          window.set_events(GDK.BUTTON1_MOTION_MASK
	                  | GDK.BUTTON2_MOTION_MASK
	                  | GDK.BUTTON3_MOTION_MASK
                          | GDK.BUTTON_PRESS_MASK
                          | GDK.BUTTON_RELEASE_MASK
                          | GDK.KEY_PRESS_MASK
                          | GDK.POINTER_MOTION_MASK
                          | GDK.POINTER_MOTION_HINT_MASK)
          window.connect("event", self.__event)
        self.__get_allocation = area.get_allocation
	self.__button=0
        BasicCanvas.__init__(self, area)

    def isInteractive(self):
        return 1

    def __event(self, widget, event):
#        print "EVENT",event.type
        if event.type == GDK.ENTER_NOTIFY:
            x, y, ok = self.__check_coords(event.x, event.y)
            if ok:
                self.onOver(self, x, y,self.__button)
        elif event.type == GDK.MOTION_NOTIFY:
            x, y = widget.get_pointer()
            x, y, ok = self.__check_coords(x, y)
            if ok:
                self.onOver(self, x, y, self.__button)
        elif event.type == GDK.BUTTON_PRESS:
	    self.__button=event.button
            x, y = widget.get_pointer()
            x, y, ok = self.__check_coords(x, y)
            if ok:
                self.onOver(self, x, y,event.button)
        elif (event.type in [GDK.BUTTON_RELEASE]):
	    self.__button=0
            x, y, ok = self.__check_coords(event.x, event.y)
            if ok:
                self.onClick(self, x, y, event.button)
        elif event.type == GDK.KEY_PRESS:
            key = self.__get_key_string(event.keyval, event.string)
            if key:
                # Get as much milage as possible from the modifiers
                # computation:
                try:
                    modifiers = self.__modifier_map[event.state]
                except KeyError:
                    modifiers = 0
                    state = event.state
                    if (state & GDK.SHIFT_MASK) == GDK.SHIFT_MASK:
                        modifiers = piddle.modShift
                    if (state & GDK.CONTROL_MASK) == GDK.CONTROL_MASK:
                        modifiers = modifiers | piddle.modControl
                    self.__modifier_map[state] = modifiers
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

    __get_key_string = {
        GDK.Left: piddle.keyLeft,
        GDK.Right: piddle.keyRight,
        GDK.Up: piddle.keyUp,
        GDK.Down: piddle.keyDown,
        GDK.Prior: piddle.keyPgUp,
        GDK.Next: piddle.keyPgDn,
        GDK.Home: piddle.keyHome,
        GDK.End: piddle.keyEnd,
        }.get

    # This covers most cases, but may be extended by __event().
    __modifier_map = {
        0: 0,
        GDK.SHIFT_MASK: piddle.modShift,
        GDK.CONTROL_MASK: piddle.modControl,
        GDK.SHIFT_MASK | GDK.CONTROL_MASK: (
            piddle.modShift | piddle.modControl),
        }


class DialogCanvas(InteractiveCanvas):
    def __init__(self, size=(300,300), name="Piddle-GTK"):
        import gtk
        #
        width, height = (int(round(size[0])), int(round(size[1])))
        top = self.__top = gtk.GtkDialog()
        vbox = top.vbox
        frame = self.__frame = gtk.GtkFrame()
        frame.set_shadow_type(gtk.SHADOW_IN)
        da = gtk.GtkDrawingArea()
        button = gtk.GtkButton("Dismiss")
        button.connect("clicked",
                       lambda button, top=top: top.destroy())
        frame.set_border_width(10)
        bbox = self.__bbox = gtk.GtkHButtonBox()
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
        """Return the gtk.GtkDialog which contains the canvas."""
        return self.__top

    def get_frame(self):
        """Return the gtk.GtkFrame that directly surrounds the canvas and
        provides the visual relief around it."""
        return self.__frame

    def get_buttonbox(self):
        """Return the gtk.GtkHButtonBox that holds the buttons in the
        dialog's action area."""
        return self.__bbox


class GTKCanvas(InteractiveCanvas):
    """Very simple interactive canvas with no decoration."""

    def __init__(self, size=(300,300), name="Piddle-GTK", infoline=1):
        """Initialize the canvas and minimal supporting widgets.

        If |infoline| is true (the default), a status bar will be
        included at the bottom of the window to support the
        ,setInfoLine() method.  If false, no statusbar will be used.

        """
        import  gtk
        #
        width, height = (int(round(size[0])), int(round(size[1])))
        #
        top = self.__top = gtk.GtkWindow()
        vbox = self.__vbox = gtk.GtkVBox()
        da = gtk.GtkDrawingArea()
        #
        top.add(vbox)
        vbox.pack_start(da)
        if infoline:
            sbar = self.__sbar = gtk.GtkStatusbar()
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
        """Return the gtk.GtkWindow which contains the canvas."""
        return self.__top

    def get_statusbar(self):
        """Return the gtk.GtkStatusbar that implements the info line, or None.
        """
        return self.__sbar

    def get_vbox(self):
        """Return the gtk.GtkVBox that the canvas widget and optional status
        bar are packed in."""
        return self.__vbox
