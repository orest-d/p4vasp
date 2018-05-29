#!/usr/bin/python2
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
This module contains various utilities and functions that do not fit
into other modules.
"""

from UserDict import *
from UserList import *
from string import *
from sys import *
from matrix import *
from p4vasp import *
from types import *

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    import p4vasp.ODPdom as ODPdom
    use_odpdom=2
except:
    try:
        import ODPdom
        use_odpdom=1
    except:
        try:
            import xml.dom.minidom
        except:
            print "There is neither ODPdom, nor xml.dom.minidom."
        use_odpdom=0
#use_odpdom=0

class XMLParseException:
    """This exception can be raised while parsing xml-document."""
    def __init__(self,val,node=None,exc_info=None):
        self.value = val
        self.node  = node
        if (exc_info is None):
            exc_info=sys.exc_info()
        self.exc_info = exc_info
    def __str__(self):
        return "%s (%s)"%(str(self.value),str(self.node))

class ParseException:
    "This exception is thrown when parsing-error occures."
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return self.value

class UnknownType:
    """This exception is raised when unknown an type is found.
    (Types are defined in p4vasp.)
    """
    def __init__(self,t):
        self.type=t
    def __str__(self):
        return "UnknownType: %s"%repr(self.type)

def indent(s,istring):
    """Intend *s* by *istring*.
    If istring is an iteger, istring is changed to istring*INDENT
    (INDENT contains two whitespaces by default).
    Then *istring* is added to the beginning of every line of *s*.
    """
    if type(istring) is IntType:
        istring=istring*INDENT
    return join(map(lambda x,i=istring:i+x, split(s,"\n")),"\n")


class Parseable:
    """Defines the *parse* method as a wrapper to *read*."""
    def parse(self,string):
        """
        Parse the *string*.
        The *read* method is used to parse the file-like object containing the *string*.
        """
        sio=StringIO(string)
        self.read(sio)
        sio.close()
    def read(self,f):
        raise "read() method not implemented"

class ToString:
    """Defines the *toString* method as a wrapper to *write*."""
    def toString(self):
        """
        Convert object to string.
        Output of the *write* method is returned as a string.
        """
        sio=StringIO()
        self.write(sio)
        s=sio.getvalue()
        sio.close()
        return s

def guessType(x):
    """Try to guess the type from the python type.
  This maps *float* to *FLOAT_TYPE*, *int* to *INT_TYPE* and everything else
  to *STRING_TYPE* .
    """
    if type(x) is FloatType:
        return FLOAT_TYPE
    if type(x) is IntType:
        return INT_TYPE
    return STRING_TYPE

def retype(x,t):
    """Return x converted to a scalar of
    type t.

    For *LOGICAL_TYPE*
    this converts

    * integers to (*x* != 0),

    * ".TRUE." and strings starting with "T, "1", "Y" to 1 (case insensitive),

    * other values to 0.
    """
    if t==FLOAT_TYPE:
        try:
            return float(x)
        except:
            return 0.0
    elif t==STRING_TYPE:
        return str(x)
    elif t==INT_TYPE:
        return int(x)
    elif t==LOGICAL_TYPE:
        if type(x) is IntType:
            return t!=0
        uv=upper(str(x))
        return (uv[0] in ["T","1","Y"]) or (uv==".TRUE.")
    else:
        raise UnknownType(t)

def retypeVec(x,t):
    """Return x converted to a vector of type t.
    This is the same as *retype()* function applied to all elements of *x*.
    """
    if t==FLOAT_TYPE:
        return map(float,x)
    elif t==STRING_TYPE:
        return map(str,x)
    elif t==INT_TYPE:
        return map(int,x)
    elif t==LOGICAL_TYPE:
        return map(lambda xx:(xx[0] in ["T","1","Y"]) or (xx==".TRUE."), map(upper,map(str,x)))
    else:
        raise UnknownType(t)

def xmlrepr(x,t=FLOAT_TYPE,format=None,float_format=None,string_format=None,logical_format=None,int_format=None):
    """Represent *x* of type *t* as a string using
    *format*, or if *format* is None, using default formats ( *xxx_format* )
    for particular type.
    If the *format* (or *xxx_format*) is *None*, *str()* function is used for converting.

    LOGICAL_TYPE is first converted
    to "T" or "F".

    If *x* is an array, the format is applied ao all elements
    and the result is joined using the whitespace as a separator.
    """
    if t == LOGICAL_TYPE:
        if isArray(x):
            xx=[]
            for a in x:
                if a:
                    xx.append("T")
                else:
                    xx.append("F")
            x=xx
        else:
            if x:
                x="T"
            else:
                x="F"
    if not format:
        if t == LOGICAL_TYPE:
            format=logical_format
        elif t == FLOAT_TYPE:
            format=float_format
        elif t == STRING_TYPE:
            format=string_format
        elif t == INT_TYPE:
            format=int_format
    if format:
        if isArray(x):
            l=map(lambda a,f=format:f%a,x)
            return join(l)
        return format%x
    else:
        if isArray(x):
            l=map(str,x)
            return join(l)
        return str(x)

def removeNewline(s):
    """Remove newlines and cr ("\\n","\\r") from string."""
    s = replace(s,"\n","")
    s = replace(s,"\r","")
    return s

def getChildrenByTagName(elem,tag,name=None):
    """
    Searches the children of *elem* for element nodes
    with the tagname *tag* and optionaly with the attribute "name"
    having the value *name*.
    """
    try:
        r=ODPdom.ChildrenByTagNameList(elem,tag)
        if name:
#      print "return filtered ODPdom.ChildrenByTagNameList"
            return filter(lambda x,name=name:x.getAttribute("name")==name,r)
        else:
            return r
    except:
#    print "ODPdom.ChildrenByTagNameList failed"
        if name:
            f=lambda x,tag=tag,name=name:(x.nodeName==tag) and\
                                         (x.nodeType==x.ELEMENT_NODE) and\
                                         (x.getAttribute("name")==name)
        else:
            f=lambda x,tag=tag:(x.nodeName==tag) and (x.nodeType==x.ELEMENT_NODE)
        return filter(f,elem.childNodes)

def getInheritedElementsByTagName(elem,tag,name=None):
    """
    Searches the children of *elem* and (direct) children of the predecesors
    until element nodes with the tagname *tag* and optionaly with the attribute "name"
    having the value *name* are is (are) found.
    """
    while elem:
        e=getChildrenByTagName(elem,tag,name)
        if len(e):
            return e
        elem=elem.parentNode
    return None

def getTextFromElement(elem):
    """Extracts all texts and CDATA sections from the element *elem* and returns them
  joined as one string.
  Note: The returntype is the ordinary string, not unicode."""
    f=lambda x:x.nodeType in [x.TEXT_NODE,x.CDATA_SECTION_NODE]
    return join(map(lambda x:str(x.data),filter(f,elem.childNodes)),"")

def getTypeFromElement(elem):
    """Extracts the type from "type" attribute of elem and returns the type:

    || **returned type** || **type attribute**             ||
    || INTEGER_TYPE      || "int", "integer"               ||
    || STRING_TYPE       || "string"                       ||
    || LOGICAL_TYPE      || "logical", "bollean", "bool"   ||
    || FLOAT_TYPE        || in other cases                 ||

    """
    try:
        t=lower(str(elem.getAttribute("type")))
    except:
        return FLOAT_TYPE
    if (t in ["int","integer"]):
        return INT_TYPE
    elif (t == "string"):
        return STRING_TYPE
    elif (t in ["logical","boolean","bool"]):
        return LOGICAL_TYPE
    else:
        return FLOAT_TYPE

def resolveItemElement(e):
    """Reads the <i> tag and returns a tuple containing ( *name* , *value* , *type* ),
  where the *value* is a scalar of type *type* ."""
    key=str(e.getAttribute("name"))
    value=getTextFromElement(e)
    t=getTypeFromElement(e)
    value=retype(value,t)

    return (key,value,t)

def resolveVectorElement(e,t=None):
    """Reads the <v> tag and returns a tuple containing ( *name* , *value* , *type* ),
  where the *value* is an array of type *type* ."""
    key=str(e.getAttribute("name"))
    value=split(getTextFromElement(e))
    if t is None:
        t=getTypeFromElement(e)
    value=retypeVec(value,t)
    return (key,value,t)

def isNumericArray(x):
    """Returns true if x is an *array* object from the *numpy* library."""
    try:
        from numpy import ndarray
        return type(x) is ndarray
    except ImportError:
        return 0

def isArray(x):
    """Returns true
    for

    * python *lists*,

    * *tuples*,

    * *UserList* instances,

    * *Vector* instances (from the matrix library),

    * *array* objects from the *numpy* library.

    """
    return (type(x) in (ListType, TupleType))\
            or isinstance(x,UserList)\
            or isinstance(x,Vector)\
            or isNumericArray(x)

def arrayShape(l):
    """Returns the *shape* (i.e. list of dimensions) of the array l.
    For *Numeric* array object this function simply returns array.shape.
    For other objects a tuple containing (len(l), len(l[0]), len(l[0][0]) ...)
    is returned.
    """
    sh=[]
    if isNumericArray(l):
        return l.shape
    elif isArray(l):
        sh.append(len(l))
        if len(l):
            sh.extend(arrayShape(l[0]))

    return tuple(sh)

class ToXMLHelper:
    """This class encapsulates the formating properties for basic types
    and some useful functions.

      Formating variables
      contain the format-string:

              || **type**       || **variable**   || **default** ||
              || *FLOAT_TYPE*   || float_format   || "%+14.10f"  ||
              || *INT_TYPE*     || int_format     || "%3d"       ||
              || *STRING_TYPE*  || string_format  || *None*      ||
              || *LOGICAL_TYPE* || logical_format || " %s "      ||


    If the value is None, python *str()* function is used to format the type.
    *LOGICAL_TYPE* is first transformed into "T" (for 1) or "F" (for 0) and then
    the format is applied.

    """
    float_format  ="%+14.10f"
    int_format    ="%3d"
    string_format =None
    logical_format=" %s "
    def toxml(self,indent=0):
        """
        Returns the xml representation of an object as a string.
        This is a wrapper to the *writexml* method.
        The content, that would be written by *writexml* to the file
        is returned as a string.
        """
        sio=StringIO()
        self.writexml(sio,indent)
        s=sio.getvalue()
        sio.close()
        return s
    def getDefaultFormat(self,t):
        """Returns the format string for type t."""
        if t==FLOAT_TYPE:
            return self.float_format
        elif t==INT_TYPE:
            return self.int_format
        elif t==LOGICAL_TYPE:
            return self.logical_format
        elif t==STRING_TYPE:
            return self.string_format
        else:
            raise UnknownType(t)
    def xmlrepr(self,x,t=FLOAT_TYPE,format=None):
        """
        Convert *x* of type *t* by using *format* (if is not *None*)
        or use the default format.
        If *x* is an array (see *isArray()*), *format* is applied to all
        elements and the result is joined using whitespace as a separator.
        """
        if not format:
            format=self.getDefaultFormat(t)
        return xmlrepr(x,t,format=format)

def parseXML(path):
    """
    Return DOM Document object for xml file given by path.

    This is a wrapper to parsing function for some DOM parser.
    ODPdom is used by default.
    Change parseXML and parseXMLString if you want to use a different DOM parser.
    """
    import os.path
    if not os.path.exists(path):
        raise IOError,"No such file or directory: '%s'"%path
    if use_odpdom:
        return ODPdom.parseFile(path)
    else:
        msg().message("WARNING: ODPdom is not working, using minidom.")
        return xml.dom.minidom.parse(path)

#  from xml.dom.ext.reader import PyExpat
#  return PyExpat.Reader().fromUri(path)

#  from xml.dom.ext.reader.Sax import FromXmlFile
#  return FromXmlFile(path)

def parseXMLString(txt):
    """
    Return DOM Document object for xml string *txt* .

    This is a wrapper to parsing function for some DOM parser.
    ODPdom is used by default.
    Change parseXML and parseXMLString if you want to use a different DOM parser.
    """
    if use_odpdom:
        return ODPdom.parseString(txt)
    else:
        msg().message("WARNING: ODPdom is not working, using minidom.")
        return xml.dom.minidom.parseString(txt)

def parseXMLfromURL(url):
    import urllib
    if ":" not in url:
        return parseXML(url)
    if url[:5]=="http:" or url[:4]=="ftp:":
        f=urllib.urlopen(url)
        s=f.read()
        f.close()
        return parseXMLString(s)
    elif url[:5]=="file:":
        return parseXML(url[5:])
    else:
        return parseXML(url)

def getDirFromURL(url):
    import urlparse
    import os.path
    import os
    if url[:5]=="http:" or url[:4]=="ftp:":
        scheme,address,path,param,query,fragment=urlparse.urlparse(url)
        return urlparse.urlunparse((scheme,address,join(split(path,"/")[:-1],"/")+"/","",""))
    else:
        s=os.path.dirname(url)
        if len(s)!=0:
            return s+os.sep
        return s

def loadGlade_old(path,name=None):
    import libglade
    import os
    path=p4vasp_home+"%sdata%sglade%s%s"%(os.sep,os.sep,os.sep,path)
    if name is None:
        return libglade.GladeXML(path)
    else:
        return libglade.GladeXML(path,name)

def loadGlade(path,name=None):
    import gtk.glade
    import os
    path=p4vasp_home+"%sdata%sglade2%s%s"%(os.sep,os.sep,os.sep,path)
    if name is None:
        return gtk.glade.XML(path)
    else:
        return gtk.glade.XML(path,name)

def getPathChain():
    import os.path
    from os import sep
    return [p4vasp_home+sep+"data",os.path.expanduser("~")+sep+".p4vasp",os.getcwd()]

atomtypes_=None

def getAtomtypes():
    import p4vasp.Structure
    from os import sep
    global atomtypes_
    if atomtypes_ is not None:
        return atomtypes_
    p=getPathChain()
    atomtypes_=p4vasp.Structure.AtomInfo()
    for x in p:
        try:
            a=p4vasp.Structure.AtomInfo(x+sep+"atomtypes.xml")
            atomtypes_.updateAttributes(a)
        except IOError:
            pass
    return atomtypes_
