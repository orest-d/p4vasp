#!/usr/bin/python
#
# HappyDoc:docStringFormat='ClassicStructuredText'
#
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


"""Property module provides a dictionary (PropertyManager)
of "properties".
These properties typically require some time to retirieve - e.g. they need
to be parsed. As soon as they are available, they will not change
(or they do not need to be reread), thus they can be cached.

Properties can be:

  - obtained as attributes of the property manager

  - requested - read in in the same or in a separate thread (if has_threading is true)
    Interested object can recieve notification when the property is available

  - read using a scheduler (generator needs to be specified)

  - tested for availability or error

  - cleared from the cache

"""
from UserDict import UserDict
from p4vasp import *
from types import *

try:
    import threading
    has_threading=1
except:
    has_threading=0
has_threading=0
print_exceptions=0

class Property:
    """This object encapsulates all the information about a certain property:

    - *name* - property name

    - *value* - property value if available, or *None*

    - *status* - can be one of

      Property.NOT_READY  - not read yet

      Property.READY      - property was read successfully and it is available

      Property.ERROR      - property reading failed for some reason

      Property.GENERATING - property is being generated using the *generator*

    - *manager* - parent PropertyManager

    - *thread* - running reading thread (if property was *required* and not yet *READY*)

    - *read_func* - reading function, if specified

    - *notify* - list of functions, that are called, when the property is available

    - *generator* - generator for generating property (if specified)

    """
    NOT_READY   =  0
    READY       =  1
    ERROR       = -1
    GENERATING  = -2

#  def __init__(self,name=None,value=None,manager=None,read=lambda x:None,generator=None):
    def __init__(self,name=None,value=None,manager=None,read=None,generator=None):
        """Create Property

          - *name* - property name

          - *value* - property value if available. If it is *None* (default),
            the value will be read using *read* function

          - *manager* - parent PropertyManager

          - *read* - reading function used for obtaining the property if specified.
          It takes one argument, that will contain a reference to the Property object.

          - *generator* - generator for generating property (if specified).
          This is a python iterator object which has to contain a *next()* method.
          This method is called as long as it does not throw *StopIteration*.
          (See the Iterators section of the Python tutorial.)

        """
        self.name        = name
        self.value       = value
        if value is None:
            self.status    = self.NOT_READY
        else:
            self.status    = self.READY

        self.manager     = manager
        self.thread      = None
        self.read_func   = read
        self.notify      = []
        self.generator   = generator

    def isPending(self):
        """Returns true if the property is being read in thread."""
        if self.thread is not None:
            return self.thread.isAlive()
        return 0

    def isGenerating(self):
        """Returns true if the property is being read using a generator."""
        return self.status==self.GENERATING

    def get(self):
        """Return the property value immediately."""
        import traceback
        if self.status == self.READY:
            return self.value
        elif self.status == self.ERROR:
            return None
        elif self.status == self.GENERATING:
            try:
                while 1:
                    self.generator.next()
            except StopIteration:
                pass
            for notify in self.notify:
                notify(self)
            self.notify=[]
            return self.value
        elif self.isPending():
            self.thread.join()
            if self.status == self.READY:
                return self.value
            elif self.status == self.ERROR:
                return None
        else:
            try:
                self.value=self.read()
                self.status=self.READY
                return self.value
            except:
                if print_exceptions:
                    traceback.print_exc()
                msg().error("Error reading property %s"%self.name)
                msg().exception()
                self.value=None
                self.status=self.ERROR

    def read(self):
        """Apply the read_func."""
        return apply(self.read_func,(self,))

    def _read(self):
        """This function is called in thread to obtain the property value."""
        import traceback
        try:
            self.value=self.read()
            self.status=self.READY
        except:
            if print_exceptions:
                traceback.print_exc()
            msg().error("Error reading property %s"%self.name)
            msg().exception()
            self.value=None
            self.status=self.ERROR
        self.thread=None
        for notify in self.notify:
            notify(self)
        self.notify=[]

    def require(self,notify=None):
        """Request the property.
    If the threading is permitted, then the read function will be started in a
    separate thread. Othervise the property is read immediately.
    The *notify* can contain a one or more (in a list) notify functions,
    that are called with a reference to the Property as an argument
    as soon as the property is available.
        """
        if self.status!=self.NOT_READY:
            return None
        self.addNotify(notify)
        if self.isPending():
            return None
        if has_threading:
            self.thread=threading.Thread(target=self._read)
            self.thread.start()
        else:
            self.get()
            for notify in self.notify:
                notify(self)
            self.notify=[]

    def addNotify(self,notify):
        """Add new notify function/functions. See *require()*."""
        if notify is not None:
            if type(notify)==type([]):
                self.notify.extend(notify)
            else:
                self.notify.append(notify)

    def release(self):
        """Release the property.
    The property *value* is cleared and status set to *NOT_READY*.
    Also the *notify* list is cleared.
        """
        if self.read_func is not None:
            self.value       = None
            self.status      = Property.NOT_READY
            self.thread      = None
            self.notify      = []

    def schedule(self,notify=None):
        """Schedule the property generator using the *p4vasp.schedule()*"""
        if self.status!=self.NOT_READY:
            return None
        self.addNotify(notify)
        if self.generator is None:
            self.get()
        else:
            schedule(self.generator)

    def scheduleFirst(self,notify=None):
        """Schedule the property generator on top of the queue
        using the *p4vasp.scheduleFirst()*"""
        if self.status!=self.NOT_READY:
            return None
        self.addNotify(notify)
        if self.generator is None:
            self.get()
        else:
            scheduleFirst(self.generator)

class PropertyManager(UserDict):
    """PropertyManager is a dictionary of properties.
  It works as a dictionary of Property instances, but the properties are also available
  as attributes. The simplest way how to obtain property X from PropertyManager pm
  is to call value=pm.X, which is equivalent to value=pm["X"].get()
    """
    def __init__(self):
        UserDict.__init__(self)
        self.required_list=[]

    def add(self,property,value=None,read=None,generator=None):
        """Add new property.
        The *property* can be either a Property instance or a property name (string).
        Property *value*, *read* function and *generator* can be specified.
        (see the *Property* for details)
        """
        if type(property) is StringType:
            if generator is not None:
                p=Property(property,value=value, manager=self, read=read)
                p.generator=generator(p)
                self[property]=p
            else:
                self[property]=Property(property,value=value, manager=self, read=read)
        else:
            self[property.name]=property
            property.manager=self

    def schedule(self,names,notify=None):
        """Schedule the property (or property list) using *p4vasp.schedule()*.
    The notification function(s) can be specified in the *notify* argument.
        """
        if type(names) is StringType:
            names=[names]
        for n in names:
            if self.has_key(n):
                self[n].schedule(notify)

    def scheduleFirst(self,names,notify=None):
        """Schedule the property (or property list) on top of the queue
    using *p4vasp.scheduleFirst()*.
    The notification function(s) can be specified in the *notify* argument."""
        if type(names) is StringType:
            names=[names]
        for i in range(len(names)-1,-1,-1):
            n=names[i]
#    for n in names[::-1]:
            if self.has_key(n):
                self[n].scheduleFirst(notify)

    def require(self,names,notify=None):
        """Request the property (properties).
    They will be read in the separate thread if the threading is permitted.
    The notification function(s) can be specified in the *notify* argument."""
        if type(names) is StringType:
            names=[names]
        for n in names:
            if self.has_key(n):
                self[n].require(notify)

    def requireNow(self,names):
        """Request the property (properties).
    They will be read immediately.
    """
        if type(names) is StringType:
            names=[names]
        for n in names:
            if self.has_key(n):
                self[n].get()

    def requireAll(self,notify):
        """Request all properties.
    They will be read in the separate thread if the threading is permitted.
    The notification function(s) can be specified in the *notify* argument."""
        for p in self.values():
            p.require(notify)

    def requireAllNow(self):
        """Request all properties. They will be read immediately.
    """
        for p in self.values():
            p.get()

    def __getattr__(self,attr):
        if self.has_key(attr):
            return self[attr].get()
        else:
            return None

    def current(self,attr):
        """Return the current value of the property (if available) or None,
    if the property has not yet been read.
        """
        if self.has_key(attr):
            return self[attr].value
        else:
            return None

    def release(self):
        """Calls release on all properties. (Makes all properties NOT_READY.)"""
        for p in self.values():
            p.release()

class FilterPropertyManager(PropertyManager):
    """FilterPropertyManager is a Property manager with the ability to disable certain properties.
    """
    def __init__(self,pm,disabled=[]):
        UserDict.__init__(self)
        self.required_list=[]
        self.pm=pm
        self.disabled=disabled

    def schedule(self,names,notify=None):
        """Schedule the property (or property list) using *p4vasp.schedule()*.
    The notification function(s) can be specified in the *notify* argument.
        """
        if type(names) is StringType:
            names=[names]
        for n in names:
            if n not in self.disabled:
                if self.has_key(n):
                    self[n].schedule(notify)
                else:
                    self.pm.schedule(n,notity)

    def scheduleFirst(self,names,notify=None):
        """Schedule the property (or property list) on top of the queue
    using *p4vasp.scheduleFirst()*.
    The notification function(s) can be specified in the *notify* argument."""
        if type(names) is StringType:
            names=[names]
        for i in range(len(names)-1,-1,-1):
            n=names[i]
            if n not in self.disabled:
                if self.has_key(n):
                    self[n].scheduleFirst(notify)
                else:
                    self.pm.scheduleFirst(n,notify)

    def require(self,names,notify=None):
        """Request the property (properties).
    They will be read in the separate thread if the threading is permitted.
    The notification function(s) can be specified in the *notify* argument."""
        if type(names) is StringType:
            names=[names]
        for n in names:
            if n not in self.disabled:
                if self.has_key(n):
                    self[n].require(notify)
                else:
                    self.pm.require(n,notify)

    def requireNow(self,names):
        """Request the property (properties).
    They will be read immediately.
    """
        if type(names) is StringType:
            names=[names]
        for n in names:
            if n not in self.disabled:
                if self.has_key(n):
                    self[n].get()
                else:
                    self.pm.requireNow(n)

    def requireAll(self,notify):
        """Request all properties.
    They will be read in the separate thread if the threading is permitted.
    The notification function(s) can be specified in the *notify* argument."""
        for p in self.values():
            if p.name not in self.disabled:
                p.require(notify)
        for p in self.pm.values():
            if p.name not in self.disabled:
                p.require(notify)

    def requireAllNow(self):
        """Request all properties. They will be read immediately.
    """
        for p in self.values():
            if p.name not in self.disabled:
                p.get()
        for p in self.pm.values():
            if p.name not in self.disabled:
                p.get()

    def __getitem__(self,i):
        if i not in self.disabled:
            return self.data.get(i,self.pm[i])
        raise KeyError,i


    def __getattr__(self,attr):
        if self.has_key(attr):
            if attr not in self.disabled:
                return self[attr].get()
            else:
                return None
        elif self.pm.has_key(attr):
            if attr not in self.disabled:
                return self.pm[attr].get()
            else:
                return None
        else:
            return None

    def current(self,attr):
        """Return the current value of the property (if available) or None,
    if the property has not yet been read.
        """
        if self.has_key(attr):
            if attr not in self.disabled:
                return self[attr].value
            else:
                return None
        elif self.pm.has_key(attr):
            if attr not in self.disabled:
                return self.pm[attr].value
            else:
                return None
        else:
            return None

    def release(self):
        """Calls release on all properties. (Makes all properties NOT_READY.)"""
        for p in self.values():
            if p.name not in self.disabled:
                p.release()
        for p in self.pm.values():
            if p.name not in self.disabled:
                p.release()

def wtest(x):
    import time
    time.sleep(1)
    return "wtest"

def notify(x):
    print "notify"

if __name__=="__main__":
    import time
    pm=PropertyManager()
    p=Property("TEST",read=wtest)
    pm.add(p)
    pm.require("TEST",notify)
    for i in range(20):
        print pm.TEST
        time.sleep(0.1)
