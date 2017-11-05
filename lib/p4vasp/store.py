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

"""
Store module handles configurable xml persistance - i.e. it makes possible
to store and retrieve python object into (from) xml files.
It is possible to customize the encoding of objects as well as to select xml tags
or attributes that are used for storing a particular object.
To store objects causing difficulties (e.g. python code) marshal and pickle
encoded in a hexadecimal form are used.

For convenience the functions *load*, *loads*, *dump*, *dumps* are defined,
that can be used the same way as the *load*, *loads*, *dump*, *dumps* in the *pickle*
module.

Here is a more advanced example:

  # Create example class
  class Test:
    def __init__(self,a=0):
      self.a=a
      self.b=2
      self.c=2.2
      self.d=[4,5]
      self.e=type(int)
    def __str__(self):
      return "Test(a=%s,b=%s,c=%s,d=%s,e=%s)"%(
      str(self.a),str(self.b),str(self.c),str(self.d),str(self.e))
    __repr__=__str__

  # Create list
  l=[1,2,3]
  # Now there will be circular references:
  l.append(Test(l))

  # Create the top-level store profile
  profile=Profile()

  # Create the store-profile for class Test:
  testprofile=Profile(Test,tagname="Test",attr_setup='''
  a
  int   B b
  float c
  list d
  ''')

  # Using addAttr and AttributeProfiles attributes can be configured
  # more precisely:
  testprofile.addAttr(HexPickleAttribute("e",tagattr=1))

  # Register the testprofile in the top-level store profile
  profile.addClass(testprofile)

  # Now dump ane load l using the profile:
  print l
  s = profile.dumps(l)
  print s
  print profile.loads(s)

Other examples can be found directly in the module source.

Variables:
INDENT - indentation unit; two spaced by default
"""

try:
    import p4vasp.ODPdom as dom
except ImportError:
    try:
        import ODPdom as dom
    except ImportError:
        import xml.dom.minidom as dom

from types import *
from string import *

from cStringIO import *
from sys import *
from UserList import UserList
from UserDict import UserDict
import marshal
import binascii
import pickle

INDENT="  "

def wo(f,x,indent,label,tag):
    """Write object *x* inclosed in tags *tag* to stream *f* indeted by *indent* units,
  optionally including label *label*.
    """
    if label:
        f.write('%s<%s label="%s">%s</%s>\n'%(indent*INDENT,tag,label,str(x),tag))
    else:
        f.write('%s<%s>%s</%s>\n'%(indent*INDENT,tag,str(x),tag))

def getRootNode(elem):
    """get root from the dom element"""
#  print "getRootNode(elem)",elem.nodeName
    while elem.parentNode is not None:
#    print "  :",elem.nodeName
        elem=elem.parentNode
    return elem

def findSubElementWithLabel(elem,label):
    """Find a dom element, with label attribute set to *label*.
  Element must not be a ref-node (reference to labeled node).
  It is searched between the element passed as argument (*elem*)
  and its children.
    """
    if elem is None:
        return None
    if elem.nodeType==elem.ELEMENT_NODE:
        if elem.nodeName!="ref" and elem.getAttribute("label")==label:
            return elem
    for x in elem.childNodes:
        ret=findSubElementWithLabel(x,label)
        if ret:
            return ret
    return None

def getTextFromElement(elem):
    """Extracts all texts and CDATA sections from the element *elem* and returns them
  joined as one string.
  Note: The returntype is the ordinary string, not unicode."""
    from string import join
    f=lambda x:x.nodeType in [x.TEXT_NODE,x.CDATA_SECTION_NODE]
    return join(map(lambda x:str(x.data),filter(f,elem.childNodes)),"")

class AttributeProfile:
    """General profile to define the storage of class attributes.
  There are several possiblilities, how the attributes can be stored:

  - Attribute can be either encoded in form of a string (encode=1)
  or as a DOM Node.

  - String-encoded attributes can be stored
  either as xml-attributes (if tagattr is true, e.g. attribute="value")
  or inside tags (<attribute>value</attribute>).

  -If the attribute is stored as a node, it can be enclosed in tags with its own name (if tag is true)
  or it will be stored as <attr name="name">value</attr>.

  Variable profile will point to the master-profile.
    """
    def __init__(self,name,attribute=None,encode=0,tag=0,tagattr=0):
        """Attribute profile constructor

             *name* - name, by which is the attribute identified in the xml file

             *attribute* - name, by which is the attribute identified in object (class attribute)
             If not specified, it is the same as name.

             *encode* - if true, the attribute will be string-encoded

             *tag* - if true, *name* will be used as a tag name

             *tagattr* - if true, information will be stored in form of a xml attribute
    """
        self.name=name
        if attribute is None:
            self.attribute=name
        else:
            self.attribute=attribute
        self.parent  = None
        self.encode   = encode
        self.tag      = tag
        self.tagattr  = tagattr

    def write(self,f,obj,indent=0,label=None):
        "Wrapper to profile.writeObj."
        self.parent.write(f,obj,indent,label)

    def retrieve(self,elem):
        "Wrapper to parent.retrieve"
        return self.parent.retrieve(elem)

    def getValue(self,obj):
        """Get attribute value from object. Normally this returns getattr(obj,self.attribute),
    but it can be overriden if other method of attribute getting is needed.
    """
        return getattr(obj,self.attribute)

    def setValue(self,obj,val):
        """Set attribute value for object. Normally the setattr(obj,self.attribute,val) is called,
    but it can be overriden if other method of attribute setting is needed.
    """
        setattr(obj,self.attribute,val)

    def getEncodedValue(self,obj):
        """Get attributed value from object encoded as a string.
    By default encoding using python str() function is used.
    """
        return str(self.getValue(obj))

    def setEncodedValue(self,obj,val):
        """Set attribute value from object encoded as a string.
    By default no decoding is defined, the string-encoded value is just passed.
    This is suitable for simple strings, but it needs to be overriden for other objects.
    """
        self.setValue(obj,val)

    def writeObj(self,f,obj,indent=0):
        """Write attribute of *obj* onto stream f. Called by the parent profile."""
        in0=indent*INDENT
        if self.encode:
            if self.tag:
                f.write('%s<%s>%s</%s>\n'%(in0,self.name,self.getEncodedValue(obj),self.name))
            else:
                f.write('%s<attr name="%s">%s</attr>\n'%(in0,self.name,self.getEncodedValue(obj)))
        else:
            if self.tag:
                f.write('%s<%s>\n'%(in0,self.name))
                self.write(f,self.getValue(obj),indent+1)
                f.write('%s</%s>\n'%(in0,self.name))
            else:
                f.write('%s<attr name="%s">\n'%(in0,self.name))
                self.write(f,self.getValue(obj),indent+1)
                f.write('%s</attr>\n'%(in0))

    def writeAsTagattr(self,f,obj):
        """Write attribute of *obj* as a xml attribute onto stream f. Called by the parent profile."""
#    print "writeAsTagattr",obj,self.name
        f.write(' %s="%s"'%(self.name,self.getEncodedValue(obj)))

    def retrieveObj(self,elem,obj):
        """retrieve the attribute value of *obj* from a DOM Element (Node or Attribute).
    """
        if elem.nodeType==elem.ELEMENT_NODE:
            if self.encode:
                self.setEncodedValue(obj,getTextFromElement(elem))
            else:
                for x in elem.childNodes:
                    if x.nodeType==x.ELEMENT_NODE:
                        self.setValue(obj,self.retrieve(x))
                        break
        elif elem.nodeType==elem.ATTRIBUTE_NODE:
            self.setEncodedValue(obj,elem.nodeValue)

class IntAttribute(AttributeProfile):
    """The AttributeProfile for storing integers."""
    def __init__(self,name,attribute=None,encode=1,tag=1,tagattr=0):
        AttributeProfile.__init__(self,name,attribute=attribute,encode=encode,tag=tag,tagattr=tagattr)

    def setEncodedValue(self,obj,val):
        self.setValue(obj,int(val))
    def getEncodedValue(self,obj):
        """Get attributed value from object encoded as a string.
    """
        return str(int(self.getValue(obj)))

class FloatAttribute(AttributeProfile):
    """The AttributeProfile for storing float."""
    def __init__(self,name,attribute=None,encode=1,tag=1,tagattr=0):
        AttributeProfile.__init__(self,name,attribute=attribute,encode=encode,tag=tag,tagattr=tagattr)

    def setEncodedValue(self,obj,val):
        self.setValue(obj,float(val))

class StringAttribute(AttributeProfile):
    """The AttributeProfile for storing string."""
    def __init__(self,name,attribute=None,encode=1,tag=1,tagattr=0):
        AttributeProfile.__init__(self,name,attribute=attribute,encode=encode,tag=tag,tagattr=tagattr)

    def setEncodedValue(self,obj,val):
        self.setValue(obj,str(val))

class IntListAttribute(AttributeProfile):
    """The AttributeProfile for storing a list of integers."""
    def __init__(self,name,attribute=None,encode=1,tag=1,tagattr=0):
        AttributeProfile.__init__(self,name,attribute=attribute,encode=encode,tag=tag,tagattr=tagattr)

    def setEncodedValue(self,obj,val):
        self.setValue(obj,map(int,split(str(val))))
    def getEncodedValue(self,obj):
        return join(map(str,self.getValue(obj)))

class ListAttribute(AttributeProfile):
    """The AttributeProfile for storing lists."""
    def __init__(self,name,attribute=None,encode=0,tag=1,tagattr=0):
        AttributeProfile.__init__(self,name,attribute=attribute,encode=encode,tag=tag,tagattr=tagattr)

    def writeObj(self,f,obj,indent=0):
        """Write attribute of *obj* onto stream f. Called by the parent profile."""
        in0=indent*INDENT
        l=self.getValue(obj)
        if self.tag:
            f.write('%s<%s>\n'%(in0,self.name))
            for x in l:
                self.write(f,x,indent+1)
            f.write('%s</%s>\n'%(in0,self.name))
        else:
            f.write('%s<attr name="%s">\n'%(in0,self.name))
            for x in l:
                self.write(f,x,indent+1)
            f.write('%s</attr>\n'%(in0))

    def retrieveObj(self,elem,obj):
        """retrieve the attribute value of *obj* from a DOM Element (Node or Attribute).
    """
        l=[]
        label=elem.getAttribute("label")
        if label:
            self.getRoot().retrieve_reftable[label]=l
        for x in elem.childNodes:
            if x.nodeType == x.ELEMENT_NODE:
                l.append(self.retrieve(x))
        self.setValue(obj,l)


class StringListAttribute(AttributeProfile):
    """The AttributeProfile for storing list of space-separated strings."""
    def __init__(self,name,attribute=None,encode=1,tag=1,tagattr=0):
        AttributeProfile.__init__(self,name,attribute=attribute,encode=encode,tag=tag,tagattr=tagattr)

    def setEncodedValue(self,obj,val):
        self.setValue(obj,map(intern,split(str(val))))
    def getEncodedValue(self,obj):
        return join(map(str,self.getValue(obj)))

class FloatListAttribute(AttributeProfile):
    """The AttributeProfile for storing a list of floats."""
    def __init__(self,name,attribute=None,encode=1,tag=1,tagattr=0):
        AttributeProfile.__init__(self,name,attribute=attribute,encode=encode,tag=tag,tagattr=tagattr)

    def setEncodedValue(self,obj,val):
        self.setValue(obj,map(float,split(str(val))))
    def getEncodedValue(self,obj):
        return join(map(str,self.getValue(obj)))


class IntTupleAttribute(AttributeProfile):
    """The AttributeProfile for storing a tuple of integers."""
    def __init__(self,name,attribute=None,encode=1,tag=1,tagattr=0):
        AttributeProfile.__init__(self,name,attribute=attribute,encode=encode,tag=tag,tagattr=tagattr)

    def setEncodedValue(self,obj,val):
        self.setValue(obj,tuple(map(int,split(str(val)))))
    def getEncodedValue(self,obj):
        return join(map(str,self.getValue(obj)))

class FloatTupleAttribute(AttributeProfile):
    """The AttributeProfile for storing a tuple of floats."""
    def __init__(self,name,attribute=None,encode=1,tag=1,tagattr=0):
        AttributeProfile.__init__(self,name,attribute=attribute,encode=encode,tag=tag,tagattr=tagattr)

    def setEncodedValue(self,obj,val):
        self.setValue(obj,tuple(map(float,split(str(val)))))
    def getEncodedValue(self,obj):
        return join(map(str,self.getValue(obj)))

class HexPickleAttribute(AttributeProfile):
    """The AttributeProfile for storing pickled attributes."""
    def __init__(self,name,attribute=None,encode=1,tag=1,tagattr=0):
        AttributeProfile.__init__(self,name,attribute=attribute,encode=encode,tag=tag,tagattr=tagattr)

    def setEncodedValue(self,obj,val):
        self.setValue(obj,pickle.loads(binascii.unhexlify(str(val))))

    def getEncodedValue(self,obj):
        return binascii.hexlify(pickle.dumps(self.getValue(obj),1))

class HexMarshalAttribute(AttributeProfile):
    """The AttributeProfile for storing marshaled attributes."""
    def __init__(self,name,attribute=None,encode=1,tag=1,tagattr=0):
        AttributeProfile.__init__(self,name,attribute=attribute,encode=encode,tag=tag,tagattr=tagattr)

    def setEncodedValue(self,obj,val):
        self.setValue(obj,marshal.loads(binascii.unhexlify(str(val))))

    def getEncodedValue(self,obj):
        return binascii.hexlify(marshal.dumps(self.getValue(obj)))

class ClassAttribute(AttributeProfile):
    """The AttributeProfile for storing class-objects."""
    def __init__(self,name,attribute=None,encode=1,tag=1,tagattr=0):
        AttributeProfile.__init__(self,name,attribute=attribute,encode=encode,tag=tag,tagattr=tagattr)

    def setEncodedValue(self,obj,val):
        v=map(strip,split(val,"."))
        if len(v) and len(val):
            if len(v)==1:
                self.setValue(obj,eval(val))
            else:
                exec "import %s\no=%s\n"%(join(v[:-1],"."),val)
                self.setValue(obj,o)
        else:
            self.setValue(obj,None)

    def getEncodedValue(self,obj):
        c=self.getValue(obj)
        if c is None:
            return ""
        if c.__module__=="__main__":
            return c.__name__
        else:
            return c.__module__+"."+c.__name__

def writePickleHandler(f,x,indent=0,label=None):
    """Write handler using pickle.
  """
    o=binascii.hexlify(pickle.dumps(x,1))
    if label:
        f.write('%s<pickle label="%s">%s</pickle>\n'%(indent*INDENT,label,o))
    else:
        f.write('%s<pickle>%s</pickle>\n'%(indent*INDENT,o))

def writeMarshalHandler(f,x,indent=0,label=None):
    """Write handler using marshal. (This is used for python code.
    The writePickle method is probably more reliable.)"""
    o=binascii.hexlify(marshal.dumps(x))
    if label:
        f.write('%s<marshal label="%s">%s</marshal>\n'%(indent*INDENT,label,o))
    else:
        f.write('%s<marshal>%s</marshal>\n'%(indent*INDENT,o))

def getClassName(object):
    """Get class name handled by this Profile."""
    object=object.__class__
    if object.__module__=="__main__":
        return object.__name__
    else:
        return object.__module__+"."+object.__name__

def createClassFromName(name):
    """Create class instance from class name *name*."""
    v=split(name,".")
    module=join(v[:-1],".")
    cname=v[-1]
    cmd=""
    if len(module):
        cmd="import %s\n"%module
    cmd="%scl=%s()"%(cmd,name)
    exec cmd
    return cl

class IgnoreProfile:
    def __init__(self,name):
        if type(name) is InstanceType:
            name=name.__class__
        if type(name) is ClassType:
            self.object=name
            if name.__module__=="__main__":
                name=name.__name__
            else:
                name=name.__module__+"."+name.__name__

    def writeObj(self,f,x,i=0,l=None):
        pass

class Profile:
    """Profile handles the storage and retrieval of arbitrary data.
  Data are stored to a stream in xml format.
  To read the data, it is necessary to create a DOM element, e.g. by xml.dom.minidom
  or ODPdom (http://sf.net/projects/odpdom).

  Handling of primitive objects is controlled by write and retrieve handlers (see later).
  They do not need to be modified, unless you are not happy with the defaults.
  The objects (classes) are handled using class profiles.

    Write and retrieve handlers:

      The reading and writing of primitive types is performed using write and retrieve handlers.
      The write-handlers control storing of primitive types *obj* to stream *s*.
      Write-handler is a function with four arguments: *s*, *obj*, *indentation* and *label*.
      Argument *indentation* is an integer containing the level of indentation,
      *label* contains the label, that is used to identify the object, if it is referenced on several places.

      The retrieve-handler controlls retrieving objects from DOM elements.
      It has a single argument containing the DOM Element.

      Write-handlers are stored in the write_handlers dictionary, where the
      object type is the key and write-handler is the value.
      Similarily, retrieve-handlers are stored in the retrieve_handlers dictionary,
      where the xml tag-name is the key and retrieve-handler is the value.

      If the write-handler is not found for the given object, the *defaultWriteHandler* handler is used.
  """
    def __init__(self,name=None,tagname=None, list_saving=0, dict_saving=0,disable_attr=0,attr_setup=None,attr_profiles=[],class_profiles=[]):
        """Create *Profile*.

    *name* - can be either class-name (string) containing module path,
    object of type InstanceType or ClassType. This argument identifies what kind of class instance is stored.

    *tagname* - tag-name used in xml to identify the class. If *None* (default),
    then *self.default_class_tag* is used("class").

    *list_saving* - if true, the elements of an array-like class are stored using the *writeItem* method.
    The *retrieveItem* method is used to retrieve items from the DOM Element.

    *dict_saving* - if true, the key/value pairs of a dictionary-like class are stored using the *writePair* method.
    The *retrievePair* method is used to retrieve key/value pairs from the DOM Element.

    *disable_attr* - Can contain list of attributes, that are not stored. If *disable_attr* is one,
    then no attributes are stored, if it is zero (default) then all attributes are stored.

    *attr_setup* - Quickly setup attributes. The *setupAttributes* method
    is called with this argument if it is not *None*.

    *attr_profiles* - A list of containing *AttributeProfile* elements.
    Each element is added using the *addAttr* method.

    *class_profiles* - A list of containing *Profile* elements.
    Each element is added using the *addClass* method.
    """
        if type(name) is InstanceType:
            name=name.__class__
        if type(name) is ClassType:
            self.object=name
            if name.__module__=="__main__":
                name=name.__name__
            else:
                name=name.__module__+"."+name.__name__
        else:
            self.object=None
        self.name=name
        self.tagname=tagname
        self.list_saving=list_saving
        self.dict_saving=dict_saving
        self.disable_attr=disable_attr
        self.retrieve_class_handlers={"attr":self.retrieveAttr,
                           "item":self.retrieveItem,
                           "pair":self.retrievePair,}

        self.aprof_list    =[]
        self.aprof_by_name ={}
        self.parent=None
        self.default_class_tag="class"

        self.class_profiles=[]
        self.default_class_profile=self
        self.write_handlers={
          IntType:         lambda f,x,i=0,l=None,I=INDENT:f.write("%s<int>%s</int>\n"%(i*I,str(x))),
          LongType:        lambda f,x,i=0,l=None,I=INDENT:f.write("%s<long>%s</long>\n"%(i*I,str(x))),
          FloatType:       lambda f,x,i=0,l=None,I=INDENT:f.write("%s<float>%s</float>\n"%(i*I,str(x))),
          ComplexType:     lambda f,x,i=0,l=None,I=INDENT:
                           f.write("%s<complex>%s %s</complex>\n"%(i*I,str(x.real),str(x.imag))),
          NoneType:        lambda f,x,i=0,l=None,I=INDENT:f.write("%s<None/>\n"%(i*I)),
          StringType:      lambda f,x,i=0,l=None:wo(f,x,i,l,"string"),
          UnicodeType:     lambda f,x,i=0,l=None:wo(f,x,i,l,"unicode"),
          ListType:        self.writeListHandler,
          TupleType:       self.writeTupleHandler,
          DictionaryType:  self.writeDictHandler,
          CodeType:        writePickleHandler,
          InstanceType:    self.writeInstanceHandler
        }
        self.retrieve_handlers={
          "int":           lambda x:int(getTextFromElement(x)),
          "long":          lambda x:long(getTextFromElement(x)),
          "float":         lambda x:float(getTextFromElement(x)),
          "complex":       lambda x:apply(complex,map(float,split(getTextFromElement(x)))),
          "string":        lambda x:str(getTextFromElement(x)),
          "unicode":       lambda x:unicode(getTextFromElement(x)),
          "None":          lambda x:None,
          "list":          self.retrieveListHandler,
          "tuple":         lambda x,s=self:s.rll(x,tuple(s.retrieveListHandler(x))),
          "dict":          self.retrieveDictHandler,
          "class":         lambda x,s=self:s.default_class_profile.retrieveObj(x),
          "ref":           self.retrieveRef,
          "pickle":        lambda x,s=self:s.rll(x,pickle.loads(binascii.unhexlify(getTextFromElement(x)))),
          "marshal":       lambda x,s=self:s.rll(x,marshal.loads(binascii.unhexlify(getTextFromElement(x)))),

        }
        self.retrieve_reftable={}
        self.nonref_types=[NoneType,IntType,LongType,FloatType,ComplexType,StringType,UnicodeType,TypeType]
        if attr_setup is not None:
            self.setupAttributes(attr_setup)

        for x in attr_profiles:
            self.addAttr(x)
        for x in class_profiles:
            self.addClass(x)
#    if self.object:
#      self.write_handlers[self.object]=self.writeObj
#      if self.tagname:
#        self.retrieve_handlers[self.tagname]=self.retrieveObj

    def load(self,f):
        """Load object from a stream *f*.
    Loaded object is returned.
    This is a convenience method that reads the dom document, calls *retrieve*
    and frees the reference tables."""
        self.cleanReftables()
        e=dom.parse(f).documentElement
        val=self.retrieve(e)
        self.cleanReftables()
        return val;

    def loads(self,s):
        """Load object from a string *s*.
    Loaded object is returned.
    This is a convenience method that reads the dom document, calls *retrieve*
    and frees the reference tables."""
        self.cleanReftables()
        e=dom.parseString(s).documentElement
        val=self.retrieve(e)
        self.cleanReftables()
        return val;

    def dump(self,o,f):
        """Dumps object *o* to a stream *f*.
    This is a convenience method that creates the reference tables,
    calls *write* and frees the reference tables again."""
        self.cleanReftables()
        self.createReftable(o)
        f.write('<?xml version="1.0" encoding="ASCII"?>\n')
        self.write(f,o)
        self.cleanReftables()

    def dumps(self,o):
        """Dumps object *o* to a string.
    The string representation of the object *o* is returned.
    This is a convenience method that calls *dump* with StringIO."""
        f=StringIO()
        self.dump(o,f)
        s=f.getvalue()
        f.close()
        return s

    def getRoot(self):
        """Get the Profile root."""
        p=self
        while p.parent is not None:
            p=p.parent
        return p

    def rll(self,elem,obj):
        "Register label/object pair during retrieve."
        label=elem.getAttribute("label")
        if label:
            self.getRoot().retrieve_reftable[label]=obj
#    print "rll ",label,obj
        return obj

    def addClass(self,c):
        "Add class profile."
        if isinstance(c,IgnoreProfile):
            self.class_profiles.append(c)
            self.write_handlers[c.object]=c.writeObj
            c.parent=self
        else:
            self.class_profiles.append(c)
            self.write_handlers[c.object]=c.writeObj
            c.parent=self
            if c.tagname:
                self.retrieve_handlers[c.tagname]=c.retrieveObj

    def addAttr(self,aprof):
        """Register AttributeProfile *aprof*."""
        name=aprof.name
        a=self.aprof_list
        for i in range(len(a)):
            if a[i].name==name:
                del a[i]
        a=self.aprof_by_name
        for key,value in a.items():
            if value.name==name:
                del a[key]
        aprof.parent=self
        self.aprof_list.append(aprof)
        self.aprof_by_name[aprof.name]=aprof
        if aprof.tag:
            self.retrieve_class_handlers[aprof.name]=aprof.retrieveObj

    def cleanReftables(self):
        """Clean tables containing both retrieve and write reference tables.
    This should be called after *write* or *retrieve* methods finished.
    """
        self.written_ids=[]
        self.write_reftable={}
        self.retrieve_reftable={}

    def createReftable(self,obj,ctab=None):
        """Create table of references. It is necessary to create this table
    before writing objects if the same object is referenced more than once.
    This table should be cleaned by the *cleanReftables* method,
    when it is not needed anymore.

    Table of references (self.write_reftable) is a dictionary, where
    the key is the id() of the object and value is the label (integer number).
    """
        self.getRoot().cleanReftables()
        if ctab is None:
            ctab=self.countObjects(obj,{})
        ref={}
        label=1
        for key,val in ctab.items():
            if val:
                ref[key]=label
                label=label+1
        self.getRoot().write_reftable=ref
#    print "REFTABLE CREATED",ref,self.getRoot().write_reftable
        return ref

    def defaultWriteHandler(self,f,x,indent=0,label=None):
        """Default write handler. This is used if no other write method
    for the given object is defined.
    First, it is tried self.parent.write, if this fails, then *writePickleHandler* is used.
    If even this fails, <None/> is stored.
    """
        p=self.parent
        while p is not None:
            if p.write_handlers.has_key(type(x)):
                return apply(p.write_handlers[type(x)],(f,x,indent,label))
            p=p.parent

        try:
            writePickleHandler(f,x,indent,label)
        except:
            print "Warning: can't encode",type(x),", encoded as <None/>"
            f.write('%s<None/><!-- encoding error -->\n'%(indent*INDENT))

    def defaultWriteAttrHandler(self,f,key,val,indent=0):
        """Default method for writing attributes."""
        in0=indent*INDENT
        f.write('%s<attr name="%s">\n'%(in0,key))
        self.write(f,val,indent+1)
        f.write('%s</attr>\n'%(in0))

    def retrieveListHandler(self,elem):
        "retrieve handler for lists."
        l=[]
        label=elem.getAttribute("label")
        if label:
            self.getRoot().retrieve_reftable[label]=l
        for x in elem.childNodes:
            if x.nodeType == x.ELEMENT_NODE:
                l.append(self.retrieve(x))
        return l

    def retrieveDictHandler(self,elem):
        "retrieve handler for dictionary."
        d={}
        for x in elem.childNodes:
            if x.nodeType==x.ELEMENT_NODE and x.nodeName == "pair":
                try:
                    sub=filter(lambda xx:xx.nodeType==xx.ELEMENT_NODE,x.childNodes)
                    key   = self.retrieve(sub[0])
                    value = self.retrieve(sub[1])
                    d[key]=value
                except:
                    print "Error reading dictionary pair."

        return self.rll(elem,d)

    def writeListHandler(self,f,obj,indent=0,label=None):
        """Write handler for lists."""
        in0=indent*INDENT
        if label:
            f.write('%s<list label="%s">\n'%(in0,label))
        else:
            f.write('%s<list>\n'%(in0))
        for x in obj:
            self.write(f,x,indent+1)
        f.write('%s</list>\n'%(in0))

    def writeTupleHandler(self,f,obj,indent=0,label=None):
        "Write handler for tuple."
        in0=indent*INDENT
        if label:
            f.write('%s<tuple label="%s">\n'%(in0,label))
        else:
            f.write('%s<tuple>\n'%(in0))
        for x in obj:
            self.write(f,x,indent+1)
        f.write('%s</tuple>\n'%(in0))

    def writeDictHandler(self,f,obj,indent=0,label=None):
        "Write handler for dictionary."
        in0=indent*INDENT
        in1=in0+INDENT
        if label:
            f.write('%s<dict label="%s">\n'%(in0,label))
        else:
            f.write('%s<dict>\n'%(in0))
        for key,val in obj.items():
            f.write("%s<pair>\n"%(in1))
            self.write(f,key,indent+2)
            self.write(f,val,indent+2)
            f.write("%s</pair>\n"%(in1))
        f.write('%s</dict>\n'%(in0))

    def writeItem(self,f,obj,indent=0):
        """Write array elements (of the class instance)."""
        in0=indent*INDENT
        f.write("%s<item>\n"%in0)
        self.write(f,obj,indent+1)
        f.write("%s</item>\n"%in0)

    def writePair(self,f,key,value,indent=0):
        """Write key/value pairs (of the class instance)."""
        in0=indent*INDENT
        f.write("%s<pair>\n"%in0)
        self.write(f,key,indent+1)
        self.write(f,value,indent+1)
        f.write("%s</pair>\n"%in0)

    def writeRef(self,f,label,indent=0):
        "Write reference to an object identified by *label*."
        f.write(indent*INDENT+'<ref label="%s"/>\n'%str(label))

    def retrieveRef(self,elem):
        "retrieve handler for references (written by writeRef)."
        label=elem.getAttribute("label")
#    return self.getRoot().retrieve_reftable[label]
        if self.getRoot().retrieve_reftable.has_key(label):
            return self.getRoot().retrieve_reftable[label]
        else:
            root =getRootNode(elem)
            e=findSubElementWithLabel(root,label)
            if e is not None:
                return self.retrieve(e)
        return None

    def write(self,f,obj,indent=0,label=None):
        """Write the xml reprezentation of object *obj* to a stream *f*.

    If *obj* contains objects, that are referenced more than once,
    call the *createReftable(obj)* method before *write*.
        """
        if label is not None:
            print "Warning, label %s in Profile.write."%str(label)
        wh=self.write_handlers
        iobj=id(obj)
        flag=1
        wreft=self.getRoot().write_reftable
        wrids=self.getRoot().written_ids
        if iobj in wrids:
            flag=0
            if wreft.has_key(iobj):
                self.writeRef(f,wreft[iobj],indent)
            else:
                print "Object referenced more than once without label.",iobj,obj
                flag=1

        if flag:
            flag=1
            if type(obj) in self.nonref_types:
                flag=0
            elif type(obj) is InstanceType:
                if obj.__class__ in  self.nonref_types:
                    flag=0
            if flag:
                wrids.append(iobj)
            if wreft.has_key(iobj):
                label=wreft[iobj]
            else:
                if label is not None:
                    if label in self.wreft.values():
                        label=None

            if wh.has_key(type(obj)):
                apply(wh[type(obj)],(f,obj,indent,label))
            else:
                self.defaultWriteHandler(f,obj,indent,label)

    def writeInstanceHandler(self,f,obj,indent=0,label=None):
        "Write handler for writing class instances."
#    print "writeInstanceHandler self",self
#    print "writeInstanceHandler obj ",repr(obj)
#    print "writeInstanceHandler name",self.name

        wh=self.write_handlers
#    print "  handlers:",wh.keys()
        if wh.has_key(obj.__class__):
            apply(wh[obj.__class__],(f,obj,indent,label))
        else:
            cp=self.class_profiles
            for i in range(len(cp)-1,-1,-1):
                if cp[i].object is not None:
                    if isinstance(obj,cp[i].object):
                        cp[i].write(f,obj,indent,label)
                        return
            if self.parent is not None:
                self.parent.writeInstanceHandler(f,obj,indent,label)
            else:
                self.default_class_profile.writeObj(f,obj,indent,label)

    def retrieve(self,elem):
        "Retrieve object from a DOM Element *elem*."
        if elem.nodeType == elem.ELEMENT_NODE:
            if self.retrieve_handlers.has_key(elem.nodeName):
                return apply(self.retrieve_handlers[elem.nodeName],(elem,))
            else:
                if self.parent is not None:
                    return self.parent.retrieve(elem)
                else:
                    raise "Unknown tag: %s"%elem.nodeName
        else:
            raise "Not a DOM Element node in Profile.retrieve"


    def countObjects(self,obj,ctab={}):
        """Count how many times is the object referenced.
    Returns table containing id(obj) as key and number of references (within the object tree)
    as a value. This is used in createReftable.
        """
        if type(obj) in self.nonref_types:
            return ctab
        if type(obj) is InstanceType:
            if obj.__class__ in self.nonref_types:
                return ctab
        iobj=id(obj)
        if ctab.has_key(iobj):
            ctab[iobj]=ctab[iobj]+1
            return ctab
        else:
            ctab[iobj]=0
            if type(obj) is InstanceType:
                cp=self.class_profiles
                for i in range(len(cp)-1,-1,-1):
                    if cp[i].object is not None:
                        if isinstance(obj,cp[i].object):
                            try:
                                return cp[i].countObjectsObj(obj,ctab)
                            except:
                                pass
                for x in obj.__dict__.values():
                    self.countObjects(x,ctab)
            elif type(obj) in [TupleType,ListType]:
                for x in obj:
                    self.countObjects(x,ctab)
            elif type(obj) is DictionaryType:
                for key,val in obj.items():
                    self.countObjects(key,ctab)
                    self.countObjects(val,ctab)
            return ctab

    def countObjectsObj(self,obj,ctab={}):
        """Count how many times is the object (class instance) referenced.
    Returns table containing id(obj) as key and number of references (within the object tree)
    as a value. This is used in *countObjects* to count objects in class instances.
        """
        attr=self.aprof_list[:]
        dattr=[]
        if self.disable_attr!=1:
            d=obj.__dict__.keys()
            try:
                d.remove("__doc__")
            except:
                pass
            try:
                d.remove("__module__")
            except:
                pass
            dd=map(lambda x:x.attribute,attr)
            dattr=filter(lambda x,dd=dd:x not in dd,d)

        if type(self.disable_attr) is not IntType:
            attr =filter(lambda x,l=self.disable_attr:x.name not in l,attr)
            dattr=filter(lambda x,l=self.disable_attr:x not in l,dattr)

        for a in attr:
            self.parent.countObjects(a.getValue(obj),ctab)
        for a in dattr:
            self.parent.countObjects(getattr(obj,a),ctab)
        return ctab


    def writeObj(self,f,obj,indent=0,label=None):
        """Write class instance *obj* to the stream *f*.
    This is used as a handler for storing class instances in *Profile*.
    """
#    print "writeObj",obj,"by",self.name
        in0=indent*INDENT
        in1=in0+INDENT

        attr=self.aprof_list[:]
        dattr=[]
        if self.disable_attr!=1:
            d=obj.__dict__.keys()
            try:
                d.remove("__doc__")
            except:
                pass
            try:
                d.remove("__module__")
            except:
                pass
            dd=map(lambda x:x.attribute,attr)
            dattr=filter(lambda x,dd=dd:x not in dd,d)

        if type(self.disable_attr) is not IntType:
            attr =filter(lambda x,l=self.disable_attr:x.name not in l,attr)
            dattr=filter(lambda x,l=self.disable_attr:x not in l,dattr)


        if self.tagname is None:
            f.write('%s<%s name="%s"'%(in0,self.default_class_tag,getClassName(obj)))
        else:
            f.write('%s<%s'%(in0,self.tagname))

        if label:
            f.write(' label="%s"'%label)

        for a in attr:
            if a.tagattr:
                a.writeAsTagattr(f,obj)

        f.write(">\n")
        for a in attr:
            if not a.tagattr:
                a.writeObj(f,obj,indent+1)
        for a in dattr:
            self.defaultWriteAttrHandler(f,a,getattr(obj,a),indent+1)

        if self.list_saving:
            for x in obj:
                self.writeItem(f,x,indent+1)

        if self.dict_saving:
            for key,val in obj.items():
                self.writePair(f,key,value,indent+1)

        if self.tagname is None:
            f.write("%s</%s>\n"%(in0,self.default_class_tag))
        else:
            f.write("%s</%s>\n"%(in0,self.tagname))

    def createClass(self):
        """Create class instance of the class handled by this Profile."""
        if self.object is not None:
            return apply(self.object,())
        else:
            name=self.name
            v=split(name,".")
            module=join(v[:-1],".")
            cname=v[-1]
            cmd=""
            if len(module):
                cmd="import %s\n"%module
            cmd="%scl=%s()"%(cmd,name)
            exec cmd
            return cl

    def retrieveAttr(self,elem,c):
        """retrieve attribute of class instance *c* from DOM Element *elem*."""
        name=elem.getAttribute("name")
        if self.aprof_by_name.has_key(name):
            p=self.aprof_by_name[name]
            p.retrieveObj(elem,c)
        else:
            for x in elem.childNodes:
                if x.nodeType == x.ELEMENT_NODE:
                    setattr(c,name,self.retrieve(x))

    def retrieveItem(self,elem,c):
        """retrieve array item of the class instance *c* from the DOM Element *elem*."""
        for x in elem.childNodes:
            if x.nodeType == x.ELEMENT_NODE:
                val=self.retrieve(x)
                c.append(val)
                return
        c.append(getTextFromElement(elem))

    def retrievePair(self,elem,c):
        """retrieve key/value pair of the class instance *c* from the DOM Element *elem*."""
        p=[]
        for x in elem.childNodes:
            if x.nodeType == x.ELEMENT_NODE:
                p.append(self.retrieve(x))
                if len(p) == 2:
                    break
        c[p[0]]=p[1]

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
                            print 'Unknown tagattr attribute for %s while retrieveing %s.'%(key,name)

            for x in elem.childNodes:
                if x.nodeType==x.ELEMENT_NODE:
                    if self.retrieve_class_handlers.has_key(x.nodeName):
                        apply(self.retrieve_class_handlers[x.nodeName],(x,c))
                    else:
                        print 'Unknown tag method for <%s>.'%(x.nodeName)

            self.afterRetrieveObj(c,elem)
            return c

    def afterRetrieveObj(self,c,elem):
        """Called before *retrieveObj* returns - i.e. when the object was retrieved.
    The arguments contain the retrieved objects (*c*) and the source DOM element (*elem*).
    This can be used to to something after the object is retrieved - initialization,
    maintenance, whatever...
    """
        pass

    def setupAttributes(self,l):
        """Simple setup of attributes.
    Argument *l* is either a list of lists or a string.
    Each line of *l* (element of *l*) contains one, two or three strings:

      - name

      - type name

      - type xml-alias name

    For each (nonempty) line an attribute is added (with *addAttr*),
    optionally setting up the type and xml-alias (the attribute name used in the
    xml document).
    Supported types are:

      int - integer number (IntType)

      string - string (StringType)

      float - float number (FloatType)

      list - list (ListType)

      intlist - list of integers

      stringlist - list of strings separated by whitespace

      floatlist -list of float numbers

      pickle - pickled value

      marshal - marshaled value

      class - class (ClassType)
    """
        if type(l) is StringType:
            l=map(split,split(l,"\n"))
        for x in l:
            if len(x):
                if len(x)==1:
                    if x[0]!="attr":
                        self.addAttr(AttributeProfile(x[0],tag=1))
                    else:
                        raise "'attr' attribute not allowed"
                elif len(x)==2:
                    t=x[0]
                    a=x[1]
                    if a=="label":
                        raise "'label' attribute not allowed"
                    if t=="int":
                        self.addAttr(IntAttribute(a,tag=1,tagattr=1))
                    elif t=="string":
                        self.addAttr(StringAttribute(a,tag=1,tagattr=0))
                    elif t=="float":
                        self.addAttr(FloatAttribute(a,tag=1,tagattr=1))
                    elif t=="list":
                        self.addAttr(ListAttribute(a,tag=1,tagattr=0))
                    elif t=="intlist":
                        self.addAttr(IntListAttribute(a,tag=1,tagattr=0))
                    elif t=="stringlist":
                        self.addAttr(StringListAttribute(a,tag=1,tagattr=0))
                    elif t=="floatlist":
                        self.addAttr(FloatListAttribute(a,tag=1,tagattr=0))
                    elif t=="pickle":
                        self.addAttr(HexPickleAttribute(a,tag=1,tagattr=0))
                    elif t=="marshal":
                        self.addAttr(HexMarshalAttribute(a,tag=1,tagattr=0))
                    elif t=="class":
                        self.addAttr(ClassAttribute(a,tag=1,tagattr=0))
                    else:
                        self.addAttr(AttributeProfile(a,tag=1,tagattr=0))
                else:
                    t=x[0]
                    n=x[1]
                    a=x[2]
                    if n=="label":
                        raise "'label' attribute not allowed"
                    if t=="int":
                        self.addAttr(IntAttribute(n,attribute=a,tag=1,tagattr=1))
                    elif t=="string":
                        self.addAttr(StringAttribute(n,attribute=a,tag=1,tagattr=0))
                    elif t=="float":
                        self.addAttr(FloatAttribute(n,attribute=a,tag=1,tagattr=1))
                    elif t=="list":
                        self.addAttr(ListAttribute(n,attribute=a,tag=1,tagattr=0))
                    elif t=="intlist":
                        self.addAttr(IntListAttribute(n,attribute=a,tag=1,tagattr=0))
                    elif t=="stringlist":
                        self.addAttr(StringListAttribute(n,attribute=a,tag=1,tagattr=0))
                    elif t=="floatlist":
                        self.addAttr(FloatListAttribute(n,attribute=a,tag=1,tagattr=0))
                    elif t=="pickle":
                        self.addAttr(HexPickleAttribute(n,attribute=a,tag=1,tagattr=0))
                    elif t=="marshal":
                        self.addAttr(HexMarshalAttribute(n,attribute=a,tag=1,tagattr=0))
                    elif t=="class":
                        self.addAttr(ClassAttribute(n,attribute=a,tag=1,tagattr=0))
                    else:
                        self.addAttr(AttributeProfile(n,attribute=a,tag=1,tagattr=0))


def load(f):
    """Load object from stream *f*.
  This is equivalent to Profile().load(f).
  """
    p=Profile()
    return p.load(f)

def loads(s):
    """Load object from string *s*.
  This is equivalent to Profile().loads(s).
  """
    p=Profile()
    return p.loads(s)

def dump(x,f):
    """Dump object *x* to a stream *f*.
  This is equivalent to Profile().dump(x,f).
  """
    p=Profile()
    return p.dump(x,f)

def dumps(x):
    """Dump object *x* to a string.
  This is equivalent to Profile().dumps(x).
  Returns string representation of *x*.
  """
    p=Profile()
    return p.dumps(s)


if __name__=="__main__":
    class Test:
        bb=1
        def __init__(self,a=0):
            self.a=a
            self.b=2
            self.c=2.2
            self.d="xxx"
        def set_c(self,c):
            self.c=c
        def get_c(self):
            return self.c
        def repare():
            print "repare Test class"
        def __str__(self):
            return "Test(a=%s,b=%s,c=%s,d=%s,bb=%s)"%(str(self.a),str(self.b),str(self.c),str(self.d),str(self.bb))
        __repr__=__str__

    sp=Profile()
    cp=Profile(Test,tagname="Test",disable_attr=0,list_saving=0,dict_saving=0)
    cp.addAttr(AttributeProfile("AAA","a",tag=1))
    cp.addAttr(IntAttribute("BBB","b",tagattr=1))
    cp.addAttr(FloatAttribute("CCC","c"))
    sp.addClass(cp)
    cp=Profile(UserList,disable_attr=["data"],list_saving=1)
    sp.addClass(cp)

    l1=[1,2,3]
    l1.append(l1)
    tt=Test(l1)
    l1.append(tt)
    test=Test("test")
    l=[2+1j,None,tt,(1,2,"a"),{1:2,"a":2.2},UserList([1,2,3]),Test("tes")]
#  f=StringIO()
#  sp.createReftable(l)
#  sp.write(f,l)
#  s=f.getvalue()
#  f.close()
    s=sp.dumps(l)

    print s

#  e=dom.parseString(s).documentElement
#  print "element parsed"
#  val=sp.retrieve(e)
#  print "retrieved"
    val=sp.loads(s)
    print l,type(l)
    print val,type(val)
    for i in range(len(val)):
        print i,":",type(val[i]),val[i]

    print
    print

    class Test:
        def __init__(self,a=0):
            self.a=a
            self.b=2
            self.c=2.2
            self.d=[4,5]
            self.e=type(int)
            self.Class=UserList
        def __str__(self):
            return "Test(a=%s,b=%s,c=%s,d=%s,e=%s,Class=%s)"%(str(self.a),str(self.b),str(self.c),str(self.d),str(self.e),str(self.Class))
        __repr__=__str__

    l=[1,2,3,type(1)]
    l.append(Test(l))

    profile=Profile()
    testprofile=Profile(Test,tagname="Test",attr_setup="""
    a
    int   B b
    float c
    list d
    class Class
    """)
    testprofile.addAttr(HexPickleAttribute("e",tagattr=1))
    profile.addClass(testprofile)

    print l
    s = profile.dumps(l)
    print s
    print profile.loads(s)
