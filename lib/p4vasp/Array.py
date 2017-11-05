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
This module contains two basic types
of arrays:

* **VArray** is a one dimensional array of vectors (one dimensional arrays),
  i.e. VArray is a two-dimensional array.
  All elements of VArray must have the same type.

* **Array** is an array with arbitrary many dimensions. Elements are records
  containing fields with various (scalar) types.

* TopArray is a parent of Array and VArray. This inherits from UserList,
  thus normal python list access can be used both for Array and VArray.

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


class LateList:
    """
    List of elements parsed on demand.
    """
    def __init__(self,plist):
        self.plist=plist
        self.data=[None]*len(plist)
        self.available=[]
    def __len__(self):
        return len(self.plist)

    def __getitem__(self,i):
        l=len(self)
        if i<0:
            i+=l
        if i in self.available:
            return self.data[i]
        if (i<0) or (i>=l):
            raise IndexError,"list index out of range; len=%s index=%s"%(str(l),str(i))
        self.data[i]=self.parse(self.plist[i])
        self.available.append(i)
        return self.data[i]


class TopArray(UserList,ToXMLHelper):
    """
    This is the parent of Array and VArray.
    """
    def convertToNumeric(self):
        """
        Converts the internal data ( *self.data* ) to the *numpy* array (if possible).
        Elements of array must be numerical or logical.

        Arrays can be stored  and handeled more efficiently this way.
        Most of the code should be inependent of the type of storage of *self.data* ,
        however, the way of soring the data can introduce some compatibility problems.

        Function return 1 if the conversion was successful,
        0 otherwise.
        """
        can_convert=0
        if self.type in [FLOAT_TYPE,INT_TYPE,LOGICAL_TYPE]:
            can_convert=1
        elif (type(self.type in (ListType,TupleType))) or isinstance(self.type,UserList):
            v=map(lambda x:x in [FLOAT_TYPE,INT_TYPE,LOGICAL_TYPE],self.type)
            if reduce(lambda x,y: x and y, v):
                can_convert=1

        if can_convert:
            try:
                from numpy import array
                self.data=array(self.data)
                return 1
            except ImportError:
                return 0
        else:
            return 0


    def shape(self):
        """Returns the shape of the array. Uses *arrayShape()*."""
        return arrayShape(self.data)


class VArray(TopArray):
    """
    One dimensional array of vectors (i.e. one-dimensional arrays).
    All elements of VArray must have the same type ( kept in variable *type* ).

    Variable *name* contains the name attribute
    and *element* (optionaly) contains the element from which the VArray was constructed.
    """
    def __init__(self,data=[],t=FLOAT_TYPE,name=None,fastflag=0):
        """Create the VArray.
        *data* can be a python list, *VArray*, *UserList* or *numpy* array instance,
        or XML element node.

        *name* can specify the name attribute.
        *t* can specify the type (FLOAT_TYPE by default).
        *fastflag* if true, *readFromNodeFast* is used to read from *data*
        """
        self.name=name
        self.element=None
        self.type=t
        if isinstance(data,VArray):
            self.name=data.name
            self.element=data.element
            self.type=data.type
        if isArray(data):
            UserList.__init__(self,data)
        else:
            UserList.__init__(self)
            if fastflag:
                self.readFromNodeFast(data)
            else:
                self.readFromNode(data)

    def readFromNode(self,data):
        """Read the vArray content from the XML element node.
        Old data are replaced by the new content.
        """
#    self.element=data
        self.name=data.getAttribute("name")
        self.type=getTypeFromElement(data)
        self.data=[]

        for e in getChildrenByTagName(data,"v"):
            key,value,t=resolveVectorElement(e,self.type)
            self.append(value)

    def readFromNodeFast(self,data):
        """Read the vArray content from the XML element node.
        Old data are replaced by the new content.
        The content is parsed in C++, using *readFromNode* as a fallback.
        This procedure can be used for reading vArray of float 3d vectors only.
        The vectors are stored as cmatrix Vectors.
        """
        try:
            import p4vasp.FArray as fa
            a=fa.FArray2D(elem=data.this,tag="v")
            self.name=data.getAttribute("name")
            self.type=getTypeFromElement(data)
            self.data=[]
            for i in range(len(a)):
                self.data.append(a.getVector(i))
        except ImportError:
            self.readFromNode(data)


    def __str__(self):
        """Represents VArray as a string.
        All values are included, so this can be a quite long string...
        """
        s="%s[%d] %s:\n"%(self.type,len(self),self.name)
        for i in range(0,len(self)):
            s+="  %3d:"%(i+1)
            for x in self[i]:
                s+=" "+str(x)
            s+="\n"
        return s

    def writexml(self,f,indent=0):
        """Write in xml format to file *f* indentet by *indent* (integer).
        """
        in0  =indent*INDENT
        in1 =(indent+1)*INDENT
        if self.name in [None, ""]:
            if self.type == FLOAT_TYPE:
                f.write('%s<varray>\n'%(in0))
            else:
                f.write('%s<varray type="%s">\n'%(in0,self.type))
        else:
            if self.type == FLOAT_TYPE:
                f.write('%s<varray name="%s">\n'%(in0,self.name))
            else:
                f.write('%s<varray name="%s" type="%s">\n'%(in0,self.name,self.type))

        for i in range(0,len(self)):
            f.write('%s<v>'%(in1))
            for x in self[i]:
                f.write(" %s"%self.xmlrepr(x,self.type))
            f.write('</v>\n')
        f.write("%s</varray>\n"%(in0))

    def convertToVector(self):
        """Convert vectors to Vector. This allows more convenient vector handling."""
        if (self.shape()[-1]==3) and (self.type==FLOAT_TYPE):
            for i in range(0,len(self)):
                self[i]=Vector(self[i])
        else:
            return 0

class ArrayRecord:
    """A wrapper class to the Array record, that allows a more convenient handling
    of records.
    It is returned by *Array.getRecord()* .

    Array is stored in *self.array_* and record in *self.record* ,
    however, the use *getArray()* and *getRecord()* is recomended.

    Array fields can be acessed
    using:

    a. dictionary convention (e.g. rec["field"]),

    b. list convention (by field numbers) (e.g. rec[1])

    c. as attributes (e.g. rec.field) .

    """
    def __init__(self,array,record=None):
        """Create a ArrayRecord from array and (optionaly) a record.
        when the *record* parameter is missing or *None* ,  a new record is created.
        as a list.
        """
        self.array_=array
        if record:
            self.record_=record
        else:
            l=[]
            for x in array.type:
                if x==FLOAT_TYPE:
                    l.append(0.0)
                elif x in [INT_TYPE,LOGICAL_TYPE]:
                    l.append(0)
                elif x==STRING_TYPE:
                    l.append("")
                else:
                    raise UnknownType(x)
            self.record_=l

    def __len__(self):return len(self.record_)

    def __getitem__(self,i):
        if (type(i) is IntType):
            return self.record_[i]
#    print "Array.getitem",i
#    print "  field:",self.array_.field
        return self.record_[self.array_.field.index(i)]

    def __setitem__(self,i,value):
        if (type(i) is IntType):
            self.record_[i]=value
        else:
            self.record_[self.array_.field.index(i)]=value

    def __getattr__(self,attr):
        if attr in self.array_.field:
            return self.record_[self.array_.field.index(attr)]
        else:
            raise AttributeError(attr)

    def __setattr__(self,attr,value):
        if (attr in ["record_","array_"]):
            self.__dict__[attr]=value
        elif attr in self.array_.field:
            self.__dict__["record_"][self.array_.field.index(attr)]=value

    def __str__(self):
        s="Record{\n"
        for i in range(0,len(self.array_.field)):
            s+="  %-10s %-10s = %s\n"%(self.array_.type[i],self.array_.field[i],self.record_[i])
        s+="}\n"
        return s
    def __repr__(self):
        return repr(self.record_)

    def getFields(self):
        "Return the list of fields (the *Array.field* attribute)."
        return self.array_.field
    def getArray(self):
        "Return *Array* object containing for this record."
        return self.array_
    def getRecord(self):
        "Return the record (list of field values)."
        return self.record_


class rRecordSetLateList(LateList):
    def __init__(self,plist,array):
        LateList.__init__(self,plist)
        self.array=array
    def parse(self,e):
        return self.array.resolveRecordElement(e)

class rcRecordSetLateList(LateList):
    def __init__(self,plist,array):
        LateList.__init__(self,plist)
        self.array=array
    def parse(self,e):
        return self.array.resolveRecordColumnedElement(e)

class SetLateList(LateList):
    def __init__(self,plist,array,level,fastflag):
        LateList.__init__(self,plist)
        self.array=array
        self.level=level
        self.fastflag=fastflag
    def parse(self,e):
        if self.level==0:
            if self.fastflag:
                return self.array.resolveRecordSet_F(e)
            else:
                return self.array.resolveRecordSet_L(e)
        else:
            rec=getChildrenByTagName(e,"set")
#      print "%ssub len=%d"%("  "*(5-self.level),len(rec))
            return SetLateList(getChildrenByTagName(e,"set"),self.array,self.level-1,self.fastflag)

class Array(TopArray):
    """
    Arbitrary (reasonably :-) dimensional array of
    records.

    Records are defined by *field* and *type* attributes.
    The *self.field* is a list of field names, while *self.type* is a list of
    field types.
    The *self.format* attribute is a list of formats for all fields.
    The Array can be acessed as a multidimensional python array
    (use a[i][j][k], a[i,j,k] only works if converted to *numpy* array.)
    The records are just lists of values ordered the same way as the *field* list is.
    The more convenient way to access records is to use *getRecord()* method,
    where the field can be acessed this way: my_array.getRecord(i,j,k).my_field.

    The *dimension* attribute is a list of names
    for every dimension (axis).

    Variable *name* contains the name attribute
    and *element* (optionaly) contains the element from which the VArray was constructed.

    When the attribute *rcmode* is true, the Array will be exported to xml
    by using the <rc> convention, <r> convention is used otherwise.

    Configure new Array example:

      # Create array:
      a=Array(name='example')
      # Description of every dimension is required:
      a.dimension=['point']
      # Create fields x and y with types and formats:
      a.setupFields(['x','y'],[INT_TYPE,FLOAT_TYPE],['%3d','%+14.10f'])
      # Append new record:
      a.append([0,0.5])
      # Append new record using ArrayRecord:
      r=ArrayRecord(a)
      r.x=1
      r.y=5.6
      a.append(r.getRecord())
      # print array:
      print a
      # Print array in xml representation:
      print a.toxml()

    """
    def __init__(self,data=[],name=None,fastflag=0):
        """Create the Array.
        *data* can be a python list, *Array*, *UserList* or *numpy* array instance,
        or XML element node.

        *name* can specify the name attribute.
        """
        if isinstance(data,Array):
            self.name      = data.name
            self.element   = data.element
            self.field     = map(intern,data.field)
            self.type      = map(intern,data.type)
            self.format    = data.format[:]
            self.dimension = data.dimension[:]
            self.rcmode    = data.rcmode

        self.name=name
        self.element=None
        self.field=[]
        self.type=[]
        self.format=[]
        self.dimension=[]
        self.rcmode=0

        if isArray(data):
            UserList.__init__(self,data)
        else:
            UserList.__init__(self)
            self.readFromNode(data,fastflag)

    def readFromNode(self,data,late=-1,fastflag=0):
        """Read the Array content from the XML element node.
        Old data are replaced by the new content.

        *late* attribute controlls the level of parsing:
        If *late* = -1 (default) everything is parsed after immediately.
        If late has non-negative value, *late* outer dimmensions are parsed immediately and the rest dimmensions
        are accessed through the *LateLists* .
        If *fastflag* is true, then nodes are parsed using FArray2D. the innermost set has to contain
        only <r> nodes with float numbers.
        """
        #self.element=data
        self.name=data.getAttribute("name")
        self.type=[]
        self.field=[]

        self.dimension =map(getTextFromElement,getChildrenByTagName(data,"dimension"))
        self.field     =map(lambda x:intern(strip(getTextFromElement(x))),getChildrenByTagName(data,"field"))
        self.type=map(getTypeFromElement,getChildrenByTagName(data,"field"))
        self.defaultFormat()

        self.data=self.resolveSet(data,len(self.dimension),late,fastflag)[0]

    def defaultFormat(self):
        """Reset *format* to default formats for particular types."""
        self.format=map(self.getDefaultFormat,self.type)

    def fieldIndex(self,field):
        """Get index of *field* in record or *None* if not in *self.field* ."""
        if field in self.field:
            return self.field.index(field)
        else:
            return None
    def getFieldType(self,field):
        """Return the type of *field*  or *None* if not in *self.field* ."""
        i=self.fieldIndex(field)
        if i:
            return self.type[i]
        else:
            return None
    def getFormatForField(self,field):
        """Return the format for *field*  or *None* if not in *self.field* ."""
        i=self.fieldIndex(field)
        if i:
            return self.format[i]
        else:
            return None


    def setFormatForField(self,field,format):
        """Set the format for *field* ."""
        i=self.fieldIndex(field)
        if i:
            self.format[i]=format

    def resolveSet(self,e,level=0,late=-1,fastflag=0):
        "Internal function used for parsing a <set> node *e* of level *level* ."
#    ind="  "*(4-level)
        if level==0:
            if late==-2 or fastflag:
                return self.resolveRecordSet_F(e)
            else:
                return self.resolveRecordSet(e)

        if late==0:
            return SetLateList(getChildrenByTagName(e,"set"),self,level-1,fastflag)
        else:
            if late>0:
                late-=1
            sets=[]
            for x in getChildrenByTagName(e,"set"):
                sets.append(self.resolveSet(x,level-1,late,fastflag))
            return sets


    def resolveRecordSet(self,e):
        """Internal function used for parsing a <set> node *e* containing <r> or <rc> nodes .
        <r> and <rc> nodes must not be mixed !
        """
        records=getChildrenByTagName(e,"r")
        if len(records):
            self.rcmode=0
            return map(self.resolveRecordElement,records)
        else:
            self.rcmode=1
            records=getChildrenByTagName(e,"rc")
            return map(self.resolveRecordColumnedElement,records)

    def resolveRecordSet_F(self,e):
        """Internal function used for parsing a <set> node *e* containing <r> or <rc> nodes .
        This function parses the set into FArray2D. It is only able to parse <r> nodes containing
        float numbers. The *resolveRecordSet* is used as fallback.
        """
        try:
            import p4vasp.FArray as fa
            return fa.FArray2D(elem=e.this,tag="r")
        except ImportError:
            return self.resolveRecordSet(e)

    def resolveRecordSet_L(self,e):
        """Internal function used for parsing a <set> node *e* containing <r> or <rc> nodes .
        <r> and <rc> nodes must not be mixed !
        (LateList version)
        """
        records=getChildrenByTagName(e,"r")
        if len(records):
            self.rcmode=0
            return rRecordSetLateList(records,self)
        else:
            self.rcmode=1
            records=getChildrenByTagName(e,"rc")
            return rcRecordSetLateList(records,self)

    def resolveRecordElement(self,e):
        """Internal function used for parsing a <r> node *e* ."""
        return self.retypeRecord(split(getTextFromElement(e)))
    def resolveRecordColumnedElement(self,e):
        """Internal function used for parsing a <rc> node *e* ."""
        r=map(getTextFromElement,getChildrenByTagName(e,"c"))
        return self.retypeRecord(r)

    def getRecord(self,*arg):
        """Gets a record specified by index(es) (or a list of indexes)
        as a *ArrayRecord*, which is a more convenient way of accessing records.
        """
        if len(arg):
            if isArray(arg[0]):
                arg=arg[0]
        return ArrayRecord(self,self.getRecordFromSet(self.data,arg))

    def getRecordFromSet(self,set,path):
        "Internal function used by *getRecord()* to get to the right record."
        if len(path):
            return self.getRecordFromSet(set[path[0]],path[1:])
        else:
            return set

    def retypeRecord(self,r):
        "Retype record *r* to have the types as in *self.type* ."
        l=[]
        for i in range(0,len(self.type)):
            l.append(retype(r[i],self.type[i]))
        return l


    def __str__(self):
        """Represents VArray as a string.
        All values are included, so this can be a quite long string...
        """
        n=self.name
        if n is None:
            n=""
        s="Array %s:{\n"%str(n)
        s+="  dimension(%s)\n"%join(self.dimension,", ")
        for i in range(0,len(self.field)):
            x=self.field[i]
            s+="  %s %s\n"%(self.type[i],x)
        s+="}\n"+str(self.data)
        return s

    def writeSetTag(self,f,set,level,indent,rcmode=None):
        "Internal function used to write a <set> node. Used in *writexml()* ."
        if rcmode is None:
            rcmode=self.rcmode
        in0  =indent*INDENT
        in1  =(indent+1)*INDENT
        f.write(in0)
        f.write('<set>\n')
        if level:
            for x in set:
                self.writeSetTag(f,x,level-1,indent+1)
        else:
            if rcmode:
                for x in set:
                    f.write(in1)
                    f.write('<rc>')
                    for i in range(0,len(self.field)):
                        f.write('<c>%s</c>'%xmlrepr(x[i],self.type[i],self.format[i]))
                    f.write('</rc>\n')
            else:
                for x in set:
                    f.write(in1)
                    f.write('<r>')
                    for i in range(0,len(self.field)):
                        f.write(' %s'%xmlrepr(x[i],self.type[i],self.format[i]))
                    f.write('</r>\n')
        f.write(in0)
        f.write('</set>\n')

    def writexml(self,f,indent=0,rcmode=None):
        """Write in xml format to file *f* indentet by *indent* (integer).
        If rcmode is true, <rc> convention will be used.
        If it is *None*, *self.rcmode* value will be used.
        """
        if rcmode is None:
            rcmode=self.rcmode
        in0  =indent*INDENT
        in1 =(indent+1)*INDENT

        if self.name in [None, ""]:
            f.write(in0)
            f.write('<array>\n')
        else:
            f.write('%s<array name="%s">\n'%(in0,self.name))

        for x in self.dimension:
            f.write('%s<dimension>%s</dimension>\n'%(in1,x))

        for i in range(0,len(self.field)):
            x=self.field[i]
            t=self.type[i]
            if t==FLOAT_TYPE:
                f.write('%s<field>%s</field>\n'%(in1,x))
            else:
                f.write('%s<field type="%s">%s</field>\n'%(in1,t,x))

        self.writeSetTag(f,self.data,len(self.dimension)-1,indent+1,rcmode=rcmode)
        f.write(in0)
        f.write("</array>\n")


    def addFieldIntoSet(self,set,value,level):
        "Internal function used to add a field into set. Uset by *addField()* ."
        if level>1:
            return map(lambda x,s=self,v=value,l=level-1:s.addFieldIntoSet(x,v,l),set)
        elif level==1:
            v=map(list,set)
            for x in v:
                x.append(value)
            return v
        elif level==0:
            v=list(set)
            v.append(value)
            return v
        else:
            raise "Illegal level :%s"%str(level)

    def addField(self,field,t=FLOAT_TYPE,format=None,value=None):
        """Add a new *field* of type *t* (optional).
        Optionaly a *format* for this type can be specified as well as the initial *value* .
        """
        if field not in self.field:
            if value is None:
                if t==FLOAT_TYPE:
                    value=0.0
                elif t in[INT_TYPE,LOGICAL_TYPE]:
                    value=0
                elif t==STRING_TYPE:
                    value=""
                else:
                    raise UnknownType(t)

            self.data=self.addFieldIntoSet(self.data,value,len(self.dimension))
            self.field.append(field)
            self.type.append(t)
            if not format:
                format=self.getDefaultFormat(t)
            self.format.append(format)

    def arrangeSet(self,set,indexes,level):
        """Internal function for reordering fields in set. Used by *removeFields()* ,
        *removeFields()* ,*removeField()* and *setupFields()* .
        """
        if level>0:
            return map(lambda x,s=self,i=indexes,l=level-1:s.arrangeSet(x,i,l),set)
        elif level==0:
            return map(lambda x,r=set:r[x],indexes)
        else:
            raise "Illegal level :%s"%str(level)


    def removeFields(self,fields):
        "Remove fields *fields* (list of field names). "
        indexes=[]
        for i in range(0,len(self.field)):
            if self.field[i] not in fields:
                indexes.append(i)
        self.data=self.arrangeSet(self.data,indexes,len(self.dimension))

        for f in fields:
            f=fields[0]
            if f in self.field:
                i=self.field.index(f)
                del self.field[i]
                del self.type[i]
                del self.format[i]

    def removeField(self,field):
        "Remove field *field* (field name). "
        self.removeFields([field])

    def setupFields(self,fields,types=None,formats=None,values=None):
        """This function can be used for rearanging the ordering of fields,
        as well as for adding and removing of fields.

        Parameter *fields* contains the new *field*
        list.

        Parameter *types* are the field types (optional, float by default).
        The *types* will not change the old type.

        The *formats* parameter can specify the format. If not specified,
        the old format (or default format) will be used.

        The *values* can be used the initial values of new fields.

        """
        if types is None:
            types=[FLOAT_TYPE]*len(fields)
        for i in range(0,len(fields)):
            if (fields[i] in self.field):
                fldindex=self.field.index(fields[i])
                types[i]  =self.type[fldindex]
        if formats is None:
            formats=map(self.getDefaultFormat,types)
            for i in range(0,len(fields)):
                if (fields[i] in self.field):
                    fldindex=self.field.index(fields[i])
                    formats[i]=self.format[fldindex]
        if values is None:
            values=[]
            for t in types:
                if t==FLOAT_TYPE:
                    values.append(0.0)
                elif t in[INT_TYPE,LOGICAL_TYPE]:
                    values.append(0)
                elif t==STRING_TYPE:
                    values.append("")
                else:
                    raise UnknownType(t)
        indexes=[]
        for i in range(0,len(fields)):
            if fields[i] not in self.field:
                self.addField(fields[i],types[i],values[i])
            indexes.append(self.field.index(fields[i]))
        self.data   = self.arrangeSet(self.data,indexes,len(self.dimension))
        self.field  = fields
        self.type   = types
        self.format = formats
