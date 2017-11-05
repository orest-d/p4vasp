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
Dictionary module
contains classes for dictionary-like objects:

  * **Dictionary ** - the basic dictionary object,
    it can be created from arbitrary xml element node containing
    <i> (item) and <v> (vector) nodes with specified "name" attribute.
    *Dictionary* has the interface of python dictionary.

  * **StructuredDictionary** inherits from *Dictionary*, adds the
    support for nested dictionaries (specified by the <separator> nodes
    in xml.)

  * **Incar** inherits from *StructuredDictionary*, adds the support
    for reading and writing of the INCAR file.

"""

from UserDict import *
from UserList import *
from string import *
from sys import *
from p4vasp.matrix import *
from p4vasp import *
from p4vasp.util import *
from types import *

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class Dictionary(UserDict,ToXMLHelper):
    """The basic dictionary object,
  it can be created from arbitrary xml element node containing
  <i> (item) and <v> (vector) nodes with specified "name" attribute.
  The type of the dictionary (usually a tag-name, e.g. "incar")
  is stored in the variable "name".

  XML element node from which the *Dictionary* was constructed is stored in the
  *element* attribute.

  Dictionary behaves
  like ordinary python dictionary (inherits from UserDict).

  Types of values are kept in the *self.type* dictionary,
  but *getFieldType()* and *setFieldType()* should be used instead of direct access.
  """
    def __init__(self,data={},name=None):
        """Create *Dictionary*,
    this can be created from other *Dictionary*, python dictionary, *UserDict*
    or the xml element node. The tagname of the element is stored in *name* attribute.
    It can be specified by the *name* parameter.

    When the type of value is not known, it is guessed
    using *util.guessType()* .
    """
        self.element=None
        self.type={}
        if isinstance(data,Dictionary):
            self.name=data.name
            self.type=data.type.copy()
        if name:
            self.name=name
        if (type(data) is DictionaryType) or isinstance(data,UserDict):
            UserDict.__init__(self,data)
            for k,v in data.items():
                if not self.type.has_key(k):
                    self.type[k]=guessType(v)
        else:
            UserDict.__init__(self)
            self.readFromNode(data)
        if not self.type:
            self.type={}


    def readFromNode(self,data):
        """Read the *Dictionary* content from the XML element node.
    Old data are replaced by the new content.
    """
        self.data={}
        self.type={}
        self.name=data.tagName
        self.element=data
#    for e in data.getElementsByTagName("i"):
        for e in getChildrenByTagName(data,"i"):
            key,value,t=resolveItemElement(e)
            self.type[key]=t
            self[key]=value
#    for e in data.getElementsByTagName("v"):
        for e in getChildrenByTagName(data,"v"):
            key,value,t=resolveVectorElement(e)
            self.type[key]=t
            self[key]=value

    def __str__(self):
        """String representation."""
        s="Dictionary %s:\n"%self.name
        for k in self.keys():
            s+="  %-10s %-10s = %s\n"%(self.getFieldType(k),k,str(self[k]))
        return s

    def writexml(self,f,indent=0):
        """Write in xml format to file *f* indentet by *indent* (integer).
        """
        in0  =indent*INDENT
        in1 =(indent+1)*INDENT
        f.write("%s<%s>\n"%(in0,self.name))
        for key in self.keys():
            value=self[key]
            t=self.getFieldType(key)
            if isArray(value):
                f.write('%s<v name="%s"'%(in1,key))
                if t != FLOAT_TYPE:
                    f.write(' type="%s"'%t)
                f.write('>%s</v>\n'%self.xmlrepr(value,t))
            else:
                f.write('%s<i name="%s"'%(in1,key))
                if t != FLOAT_TYPE:
                    f.write(' type="%s"'%t)
                f.write('>%s</i>\n'%self.xmlrepr(value,t))
        f.write("%s</%s>\n"%(in0,self.name))

    def getFieldType(self,key):
        "Gets the type of the field *key* ."
        try:
            return self.type[key]
        except KeyError:
            try:
                return guessType(self[key])
            except:
                return STRING_TYPE
    def setFieldType(self,key,t):
        "Sets the type of the field *key* ."
        self.type[key]=t

class StructuredDictionary(Dictionary,ToXMLHelper):
    """Structured dictionary object,
  it can be created from arbitrary xml element node containing
  <i> (item) and <v> (vector) nodes with specified "name" attribute.
  The type of the dictionary (usually a tag-name, e.g. "incar")
  is stored in the variable "name".

  The element nodes <separator> are treated as subgroups:
  Their content is stored in the separate dictionary.
  All (direct) subgroups are kept in *self.subgroup* .
  The subgroup name is in *self.groupname* .
  All subgroups are constructed as StructuredDictionary, thus they can alse have
  subgroups. The parent group behaves like it would have key-value
  pairs (and types) from subgroups too.

  If the group and subgroup contains common key, the results
  are undefined.

  XML element node from which the *StructuredDictionary* was constructed is stored in the
  *element* attribute.

  Types of values of the group are kept in the *self.type* dictionary,
  but not the types of values of subgroups.
  Use *getFieldType()* and *setFieldType()* to get/set the type of field
  (including subgroups).
  """
    def __init__(self,data={},name=None):
        """Create *StructuredDictionary*,
    this can be created from other *Dictionary*, *StructuredDictionary*, python dictionary, *UserDict*
    or the xml element node. The tagname of the element is stored in *name* attribute.
    It can be specified by the *name* parameter.

    When the type of value is not known, it is guessed
    using *util.guessType()* .
    """
        self.subgroup=[]
        self.groupname=None
        if (type(data) is DictionaryType) or isinstance(data,UserDict):
            if isinstance(data,StructuredDictionary):
                if not name:
                    try:
                        name=data.name
                    except:
                        name="???"
                Dictionary.__init__(self,data.data,name=name)
                self.type=data.type.copy()
                self.subgroup=map(lambda x:StructuredDictionary(x),data.subgroup)
                self.groupname=data.groupname
            else:
                Dictionary.__init__(self,data,name=name)

        else:
            Dictionary.__init__(self,name=name)
            self.readFromNode(data)

    def readFromNode(self,data):
        """Read the *StructuredDictionary* content from the XML element node.
    Old data are replaced by the new content.
    """
        self.data={}
        self.type={}
        self.subgroup=[]
        Dictionary.readFromNode(self,data)
        self.groupname=data.getAttribute("name")
        sub=getChildrenByTagName(data,"separator")
        for x in sub:
            self.subgroup.append(StructuredDictionary(x))

    def __str__(self):
        n=self.groupname
        if n is None:
            n=""
        s="StructuredDictionary <%s> %s:\n"%(self.name,n)
        for k in self.keys():
            s+="  %-10s %-10s = %s\n"%(self.getFieldType(k),k,str(self[k]))
        for x in self.subgroup:
            s+="  group %s\n"%x
            s+=indent(str(x),1)
        return s

    def writexml(self,f,indent=0):
        """Write in xml format to file *f* indentet by *indent* (integer).
        """
        in0  =indent*INDENT
        in1 =(indent+1)*INDENT
        if self.groupname in ["",None]:
            f.write('%s<%s>\n'%(in0,self.name))
        else:
            f.write('%s<%s name="%s">\n'%(in0,self.name,self.groupname))
        for key in self.data.keys():
            value=self.data[key]
            t=self.getFieldType(key)
            if isArray(value):
                f.write('%s<v name="%s"'%(in1,key))
                if t != FLOAT_TYPE:
                    f.write(' type="%s"'%t)
                f.write('>%s</v>\n'%self.xmlrepr(value,t))
            else:
                f.write('%s<i name="%s"'%(in1,key))
                if t != FLOAT_TYPE:
                    f.write(' type="%s"'%t)
                f.write('>%s</i>\n'%self.xmlrepr(value,t))
        for x in self.subgroup:
            x.writexml(f,indent+1)
        f.write("%s</%s>\n"%(in0,self.name))

    def getAllData(self):
        "Get all data in this group and the subgroups as a python dictionary."
        d=self.data.copy()
        for x in self.subgroup:
            d.update(x.getAllData())
        return d
    def getAllTypes(self):
        "Get all data in this group and the subgroups as a python dictionary."
        d=self.types.copy()
        for x in self.subgroup:
            try:
                d[k]=x.update(x.getAllTypes())
            except AttributeError:
                pass
        return d

    def getSubgroupForKey(self,key):
        "Get subgroup containing the *key* directly."
        if key in self.data.keys():
            return self
        for x in self.subgroup:
            try:
                return x.getSubgroupForKey(key)
            except KeyError:
                pass
        raise KeyError(key)

    def __cmp__(self,dict):
        if isinstance(dict,StructuredDictionary):
            return cmp(self.getAllData(),dict.getAllData())
        elif isinstance(dict,UserDict):
            return cmp(self.getAllData(),dict.data)
        else:
            return cmp(self.getAllData(),dict)
    def __len__(self):
        l=map(len,self.subgroup)
        return len(self.data)+reduce(lambda x,y:x+y,l)

    def __getitem__(self,key):
        if self.data.has_key(key):
            return self.data[key]
        for x in self.subgroup:
            try:
                return x[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __setitem__(self,key,value):
        try:
            s=self.getSubgroupForKey(key)
            s.data[key]=value
        except KeyError:
            self.data[key]=value

    def __delitem__(self,key):
        f=1
        try:
            del self.data[key]
            f=0
        except KeyError:
            pass
        for x in self.subgroup:
            try:
                del x[key]
                f=0
            except KeyError:
                pass
        if f:
            raise KeyError(key)

    def keys(self):
        k=self.data.keys()
        for x in self.subgroup:
            k.extend(filter(lambda x,k=k:x not in k,x.keys()))
        return k

    def values(self):
        k=self.data.values()
        for x in self.subgroup:
            k.extend(x.values())
        return k

    def items(self):
        return self.getAllData().items()

    def iteritems(self):
        raise "Not implemented yet."
    def iterkeys(self):
        raise "Not implemented yet."
    def itervalues(self):
        raise "Not implemented yet."

    def has_key(self,key):
        if self.data.has_key(key):
            return 1
        for x in self.subgroup:
            if x.has_key(key):
                return 1
        return 0

    def update(self,dict):
        for k,v in dict.items():
            self[k]=v

    def popitem(self):
        raise "Not implemented yet."

    def __contains__(self,key):
        if key in self.data:
            return 1
        for x in self.subgroup:
            if key in x:
                return 1
        return 0

    def getFieldType(self,key):
        "Gets the type of the field *key* ."
        try:
            if self.data.has_key(key):
                return self.type[key]
            for x in self.subgroup:
                if x.has_key(key):
                    return x.getFieldType(key)
        except KeyError:
            try:
                return guessType(self[key])
            except:
                return STRING_TYPE
    def setFieldType(self,key,t):
        "Sets the type of the field *key* ."
        if self.data.has_key(key):
            self.type[key]=t
        for x in self.subgroup:
            if x.has_key(key):
                x.setFieldType(key,t)

class Incar(StructuredDictionary,Parseable,ToString):
    """Special dictionary for holding INCAR.
  Inherits from StructuredDictionary.
  Methods for reading and writing INCAR files
  and producing automatic comments are added.
    """
    def __init__(self,data={},name="incar"):
        """Creates new Incar object.
    *Incar* can be created by specifiing data, which can be different types of dictionaries,
    xml element nodes, file object or path to INCAR file.
        """
        self.float_format="%+10.8f"
        if (type(data) is DictionaryType) or isinstance(data,UserDict):
            StructuredDictionary.__init__(self,data,name=name)
        elif type(data) in StringTypes:
            StructuredDictionary.__init__(self)
            self.read(data)
        else:
            StructuredDictionary.__init__(self,name=name)
            self.readFromNode(data)

    def readFromNode(self,data):
        """Read the *Incar* content from the XML element node.
    Old data are replaced by the new content.
    """
        self.data={}
        self.type={}
        self.subgroup=[]
        Dictionary.readFromNode(self,data)
        self.groupname=data.getAttribute("name")
        sub=getChildrenByTagName(data,"separator")
        for x in sub:
            self.subgroup.append(Incar(x))

    def read(self,f="INCAR",closeflag=0):
        """Read the incar from file *f* . This can be a reader object (file)
    or a string conaining the path"""
        if (type(f) == type("")):
            f = open(f,"r")
            closeflag = 1

        from shlex import shlex
        lex = shlex(f)
        lex.wordchars=lex.wordchars+".${}+-*()[]"
        lex.whitespace="#!\n;"
        lex.whitespace_split=True
        lex.commenters = "#!"

        x = lex.get_token()
        while ((x != "") and (x is not None)):
            v=split(x,"=")
            x = lex.get_token()
            if len(v)>=2:
                key=strip(v[0])
                val=strip(v[1])
                self[key]=val
                self.setFieldType(key,STRING_TYPE)
                if len(v)>2:
                    print "Warning: more than one = :",x
            if len(v)==1:
                print "Warning: no = :",x


        if (closeflag):
            f.close()

    def autocomment(self,key,value=None):
        """Returns the comment to *key* - *value* (optional) pair in this *Incar* .
    This can depend on the context - i.e. values of other fields.
    If comment is not available, *None* is returned."""

        if value is None:
            if self.has_key(key):
                value=self[key]

        if key=="IBRION":
            try:
                value=int(value)
            except ValueError:
                return None
            d={-1:"no update",
                0:"standart molecular dynamics - Verlet algorithm",
                1:"relaxation - quasi Newton (RMM-DIIS)",
                2:"relaxation - conjugate-gradient",
                3:"damped molecular dynamics (Verlet algorithm)",
                5:"finite differences"}
            try:
                return d[value]
            except KeyError:
                return None

        if key=="NSW":
            try:
                ibrion=int(self["IBRION"])

                d={-1:"outer loops",
                    0:"number of ionic steps",
                    1:None,
                    2:"number of ionic steps",
                    3:"number of ionic steps",
                    5:"not used, just needs to be positive"}
                return d[ibrion]
            except KeyError:
                return None

        if key=="NFREE":
            try:
                ibrion=int(self["IBRION"])
                if ibrion == 1:
                    return "iteration history",
                elif ibrion==5:
                    d={1:"one displacement per degree of freedom",
                       2:"two displacements (central differences)",
                       4:"four displacements per degree of freedom"}
                    return d[ibrion]
            except KeyError:
                return None

        if key=="POTIM":
            try:
                ibrion=int(self["IBRION"])

                d={-1:None,
                    0:"timestep",
                    1:"timestep",
                    2:"timestep",
                    3:"timestep",
                    5:"displacement length"}
                return d[ibrion]
            except KeyError:
                return None

        d={"ENCUT":"energy cutoff",
           "PREC":"precission",
           "EDIFF":"stopping-criterion for electronic upd."
           }

        try:
            return d[key]
        except KeyError:
            return None

        return None

    def write(self,f="INCAR",closeflag=0):
        """Write INCAR to file *f* . This can be a writer object (file)
    or a string conaining the path"""
        if (type(f) == type("")):
            f = open(f,"w+")
            closeflag = 1
        written=[]

        if self.groupname not in ["",None]:
            f.write("\n# %s\n#########################################\n\n"%str(self.groupname))

        fields=["IBRION",
                "NSW",
                "NFREE",
                "POTIM",
                "SMASS",
                "EDIFFG",
                "ENCUT",
                "PREC",
                "EDIFF",
                "LREAL",
                "ROPT",
                "ISMEAR",
                "SIGMA",
                "ISYM",
                "NSIM",
                "ALGO",
                "IALGO",
                "AMIX",
                "BMIX",
                "LWAVE",
                "LCHARG",
                "LVTOT"]

        ff=filter(lambda x,k=self.data.keys(): x in k,fields)

        for i in range(0,len(ff)):
            key     = ff[i]
            value   = self.xmlrepr(self[key],self.getFieldType(key))
            comment = self.autocomment(key)
            if comment:
                f.write("%-8s = %15s # %s\n"%(key,value,comment))
            else:
                f.write("%-8s = %15s\n"%(key,value))


        for key in self.data.keys():
            if (key not in ff):
                value   = self.xmlrepr(self[key],self.getFieldType(key))
                comment = self.autocomment(key)
                if comment:
                    f.write("%-8s = %15s # %s\n"%(key,value,comment))
                else:
                    f.write("%-8s = %15s\n"%(key,value))

        for x in self.subgroup:
            x.write(f)

        if (closeflag):
            f.close()
