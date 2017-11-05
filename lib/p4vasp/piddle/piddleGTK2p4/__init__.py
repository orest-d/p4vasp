"""PIDDLE implementation that uses a Gtk+ GtkDrawingArea object as the
  output device.

  This module offers four classes which support the piddle.Canvas
  interface, two of which provide the standard constructor signature.
  One serves as the standard interface for creating PIDDLE canvas
  objects, offering the full range of canvas attributes
  (interactivity, updatability, and an info line).

Classes
-------

Canvas
    Basic canvas class that offers all the display interfaces but
    doesn't provide support for interactivity (or the load required to
    fully support that aspect of the API).  The canvas uses double
    buffering to eliminate flicker, and supports arbitrary resizing.
    A gtk.GtkDrawingArea widget may be passed to the constructor.

InteractiveCanvas
    Subclass of Canvas which adds interactivity support for all three
    on*() methods.  This class makes a fair effort to reduce the
    required overhead of implementing the dynamic interface, but can't
    avoid too much of it.  Only use an interactive Canvas if you
    actually need one.  Requires that both the drawing area and the
    toplevel window (gtk.GtkWindow or gtk.GtkDialog) be passed to the
    constructor; the toplevel window is required in order to set up
    the event handlers properly.

DialogCanvas
    Sublass of InteractiveCanvas which supports the standard PIDDLE
    constructor signature in all but name.

GTKCanvas
    This is the 'standard' PIDDLE interface; it offers the standard
    constructor as well as the required name.  It provides a simple
    top-level window (gtk.GtkWindow) that contains nothing but the
    canvas's drawing area and a simple status bar at the bottom.  The
    status bar is used to support the piddle.Canvas setInfoLine()
    interface.  Once created, the creator must enter the Gtk+ main
    loop (or already be running the main loop).

Limitations
-----------

  The Canvas class doesn't yet support rotated text.  This will be
  added as time allows.  The basic functionality for all required
  fonts appears to be working for non-rotated text for the required
  fonts.  Eventually, I'd like to support alternative font management
  schemes through the piddle.Canvas interface, allowing the use of the
  Gtk+ native X font support for applications which don't need rotated
  text (allowing a simple and fast implementation), and offering t1lib
  and FreeType rendering for applications which need stronger text
  support.

  The .drawImage() API hasn't been implemented yet; this will come as
  I understand more about the image models offered with Gtk+ and have
  a chance to play with the recent versions of the Python Imaging
  Library.

"""
__author__ = "Fred L. Drake, Jr.  <fdrake@acm.org>"
__version__ = '$Revision: 1.1 $'

# These imports set up the namespace to be exactly what's needed for a
# PIDDLE backend implementation: everything from piddle, plus the
# exported names for the specific backend.

from p4vasp.piddle.piddle import *

from core import \
     BasicCanvas, \
     InteractiveCanvas, \
     InteractiveBoxCanvas, \
     GTKCanvas, \
     DialogCanvas
