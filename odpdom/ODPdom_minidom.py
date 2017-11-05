#
# Copyright (C) 2003 Orest Dubay <odubay@users.sourceforge.net>
#
# This file is part of ODPdom, a free DOM XML parser library.
# See http://sourceforge.net/projects/odpdom/ for updates.
#
# ODPdom is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ODPdom is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ODPdom; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
 
import _cODP

import xml.dom
from string import split,join
from types import StringType    

class Node(xml.dom.Node):
  def __init__(self,n):
    self.this = _cODP.new_ODPNode(n)
    self.thisown=1

  def __setattr__(self,attr,value):
    if (attr in ["nodeName",
                 "nodeType",
		 "parentNode",
		 "childNodes",
		 "firstChild",
		 "lastChild",
		 "previousSibling",
		 "nextSibling",
		 "attributes",
		 "ownerDocument"]):
      raise "Node.%s is read only"%attr
    if attr == "nodeValue":
      raise xml.dom.NoModificationAllowedErr,"Node.nodeValue is read only"
    self.__dict__[attr]=value

  _get_methods_={
    "nodeName"       :_cODP.ODPNode_getNodeName,
    "nodeValue"      :_cODP.ODPNode_getNodeValue,
    "nodeType"       :_cODP.ODPNode_getNodeType,
    "parentNode"     :lambda x:_ntype(_cODP.ODPNode_getParentNode(x)),
    "childNodes"     :lambda x: NodeList(_cODP.ODPNode_getChildNodes(x)),
    "firstChild"     :lambda x:_ntype(_cODP.ODPNode_getFirstChild(x)),
    "lastChild"      :lambda x:_ntype(_cODP.ODPNode_getLastChild(x)),
    "previousSibling":lambda x:_ntype(_cODP.ODPNode_getPreviousSibling(x)),
    "nextSibling"    :lambda x:_ntype(_cODP.ODPNode_getNextSibling(x)),
    "attributes"     :lambda x: AttributeList(_cODP.ODPNode_getAttributes(x)),
    "ownerDocument"  :lambda x:_ntype(_cODP.ODPNode_getOwnerDocument(x))
  }		   

  def __getattr__(self,name):
    method = self._get_methods_.get(name,None)
    if (method):
      return method(self.this)
    raise AttributeError,name

  def __nonzero__(self):
      return 1

  def insertBefore(self, newChild, refChild):
    raise xml.dom.NoModificationAllowedErr,"Node.insertBefore not supported"

  def appendChild(self, node):
    raise xml.dom.NoModificationAllowedErr,"Node.appendChild not supported"

  def replaceChild(self, newChild, oldChild):
    raise xml.dom.NoModificationAllowedErr,"Node.replaceChild not supported"

  def removeChild(self, oldChild):
    raise xml.dom.NoModificationAllowedErr,"Node.removeChild not supported"

  def cloneNode(self, deep):
    raise xml.dom.NotSupportedErr,"Node.cloneNode not supported"



class DocumentFragment(Node):
  nodeType = Node.DOCUMENT_FRAGMENT_NODE
  nodeName = "#document-fragment"
  nodeValue = None
  attributes = None
  parentNode = None
  childNodeTypes = (Node.ELEMENT_NODE,
                    Node.TEXT_NODE,
                    Node.CDATA_SECTION_NODE,
                    Node.ENTITY_REFERENCE_NODE,
                    Node.PROCESSING_INSTRUCTION_NODE,
                    Node.COMMENT_NODE,
                    Node.NOTATION_NODE)


class Attr(Node):
  def __init__(self,n):
    self.this = _cODP.new_ODPAttr(n)
    self.thisown=1

  _get_methods_={
    "nodeName"       :_cODP.ODPNode_getNodeName,
    "nodeValue"      :_cODP.ODPNode_getNodeValue,
    "nodeType"       :_cODP.ODPNode_getNodeType,
    "parentNode"     :lambda x:_ntype(_cODP.ODPNode_getParentNode(x)),
    "childNodes"     :lambda x: NodeList(_cODP.ODPNode_getChildNodes(x)),
    "firstChild"     :lambda x:_ntype(_cODP.ODPNode_getFirstChild(x)),
    "lastChild"      :lambda x:_ntype(_cODP.ODPNode_getLastChild(x)),
    "previousSibling":lambda x:_ntype(_cODP.ODPNode_getPreviousSibling(x)),
    "nextSibling"    :lambda x:_ntype(_cODP.ODPNode_getNextSibling(x)),
    "attributes"     :lambda x: AttributeList(_cODP.ODPNode_getAttributes(x)),
    "ownerDocument"  :lambda x:_ntype(_cODP.ODPNode_getOwnerDocument(x)),
    "name"           : _cODP.ODPAttr_getName,
    "specified"      : _cODP.ODPAttr_getSpecified,
    "value"          : _cODP.ODPAttr_getValue,
  }		   

  def __setattr__(self,attr,value):
    if (attr in ["name",
                 "specified",
                 "nodeName",
                 "nodeType",
		 "parentNode",
		 "childNodes",
		 "firstChild",
		 "lastChild",
		 "previousSibling",
		 "nextSibling",
		 "attributes",
		 "ownerDocument"]):
      raise "Attr.%s is read only"%attr
    if attr in ["nodeValue","value"]:
      raise xml.dom.NoModificationAllowedErr,"Attr.%s is read only"%attr
    self.__dict__[attr]=value

  def __getattr__(self,name):
    method = self._get_methods_.get(name,None)
    if (method):
      return method(self.this)
    raise AttributeError,name

class NodeList:
  def __init__(self,this):
    self.this=this
    self.thisown=1

  def __getattr__(self,name):
    if name == "length":
      return _cODP.ODPNodeList_getLength(self.this)
    raise AttributeError,name

  def __len__(self):
    return _cODP.ODPNodeList_getLength(self.this)
  
  def __setattr__(self,attr,value):
    if (attr == "length"):
      raise "NodeList.length is read only"
    self.__dict__[attr]=value
    
  def item(self,i):
    return _ntype(_cODP.ODPNodeList_item(self.this,i))

  def __getitem__(self,i):
#    if (i>=0) and (i<len(self)):
#      return self.item(i)
#    raise IndexError
    if i<0:
      i+=_cODP.ODPNodeList_getLength(self.this)
    if (i>=0) and (i<_cODP.ODPNodeList_getLength(self.this)):
      return _ntype(_cODP.ODPNodeList_item(self.this,i))
    raise IndexError

class NamedNodeMap:
  def __init__(self):
    self.this=_cODP.new_ODPNamedNodeMap()
    self.thisown=1

  def __getattr__(self,attr):
    if attr=="length":
      return _cODP.ODPNamedNodeMap_getLength(self.this)
    else:
      raise AttributeError,attr

  def item(self,i):
    return _ntype(_cODP.ODPNamedNodeMap_item(self.this,i))

  def items(self):
    L = []
    for i in range(0,len(self)):
      I=_cODP.ODPNamedNodeMap_item(self.this,i)
      L.append((_cODP.ODPNode_getNodeName(I),_cODP.ODPNode_getNodeValue(I)))
    return L

  def keys(self):
    L = []
    for i in range(0,len(self)):
      I=_cODP.ODPNamedNodeMap_item(self.this,i)
      L.append(_cODP.ODPNode_getNodeName(I))
    return L

  def values(self):
    L = []
    for i in range(0,len(self)):
      I=_cODP.ODPNamedNodeMap_item(self.this,i)
      L.append(_cODP.ODPNode_getNodeValue(I))
    return L

  def get(self, name, value = None):
    I=_cODP.ODPNamedNodeMap_getNamedItem(self.this,name)
    if I is None:
      return value
    return _cODP.ODPNode_getNodeValue(I)

  def __len__(self):
    return _cODP.ODPNamedNodeMap_getLength(self.this)

  def __getitem__(self, i):
    if type(i)==IntType:
      if (i>0) and (i<len(self)):
	return self.item(i)
      else:
	raise IndexError  
    return _cODP.ODPNode_getNodeValue(
      _cODP.ODPNamedNodeMap_getNamedItem(self.this,name))

  def __setitem__(self, attname, value):
    raise xml.dom.NoModificationAllowedErr,"NamedNodeMap.setNamedItem not supported"

  def getNamedItem(self, name):
    return _ntype(_cODP.ODPNamedNodeMap_getNamedItem(self.this,name))

  def setNamedItem(self, node):
    raise xml.dom.NoModificationAllowedErr,"NamedNodeMap.setNamedItem not supported"

  def removeNamedItem(self, node):
    raise xml.dom.NoModificationAllowedErr,"NamedNodeMap.removeNamedItem not supported"

  def __delitem__(self, node):
    self.removeNamedItem(node)

class AttributeList(NamedNodeMap):
  def __init__(self,this):
    self.this=this
    self.thisown=1

  def __getattr__(self,attr):
    if attr=="length":
      return _cODP.ODPNamedNodeMap_getLength(self.this)
    else:
      raise AttributeError,attr

  def item(self,i):
    return _ntype(_cODP.ODPNamedNodeMap_item(self.this,i))

  def items(self):
    L = []
    for i in range(0,len(self)):
      I=_cODP.ODPNamedNodeMap_item(self.this,i)
      L.append((_cODP.ODPNode_getNodeName(I),_cODP.ODPNode_getNodeValue(I)))
    return L

  def keys(self):
    L = []
    for i in range(0,len(self)):
      I=_cODP.ODPNamedNodeMap_item(self.this,i)
      L.append(_cODP.ODPNode_getNodeName(I))
    return L

  def values(self):
    L = []
    for i in range(0,len(self)):
      I=_cODP.ODPNamedNodeMap_item(self.this,i)
      L.append(_cODP.ODPNode_getNodeValue(I))
    return L

  def get(self, name, value = None):
    a=self.getAttribute(name)
    if a is None:
      return value

#  def __len__(self):
#    return _cODP.ODPAttributeMap_getLength(self.this)

  def __getitem__(self, i):
    if type(i)==IntType:
      if (i>0) and (i<len(self)):
	return self.item(i)
      else:
	raise IndexError
    a=self.getAttribute(i)
    if a is None:
      raise KeyError
    return a	

  def __setitem__(self, attname, value):
    raise xml.dom.NoModificationAllowedErr,"NamedNodeMap.setNamedItem not supported"

  def getNamedItem(self, name):
    return _ntype(_cODP.ODPNamedNodeMap_getNamedItem(self.this,name))

  def setNamedItem(self, node):
    raise xml.dom.NoModificationAllowedErr,"NamedNodeMap.setNamedItem not supported"

  def removeNamedItem(self, node):
    raise xml.dom.NoModificationAllowedErr,"NamedNodeMap.removeNamedItem not supported"

  def __delitem__(self, node):
    self.removeNamedItem(node)


class Element(Node):
  def __init__(self, node):
    self.this    = _cODP.new_ODPElement(node)
    self.thisown = 1

  _get_methods_={
    "nodeName"       :_cODP.ODPNode_getNodeName,
    "nodeValue"      :_cODP.ODPNode_getNodeValue,
    "nodeType"       :_cODP.ODPNode_getNodeType,
    "parentNode"     :lambda x:_ntype(_cODP.ODPNode_getParentNode(x)),
    "childNodes"     :lambda x: NodeList(_cODP.ODPNode_getChildNodes(x)),
    "firstChild"     :lambda x:_ntype(_cODP.ODPNode_getFirstChild(x)),
    "lastChild"      :lambda x:_ntype(_cODP.ODPNode_getLastChild(x)),
    "previousSibling":lambda x:_ntype(_cODP.ODPNode_getPreviousSibling(x)),
    "nextSibling"    :lambda x:_ntype(_cODP.ODPNode_getNextSibling(x)),
    "attributes"     :lambda x: AttributeList(_cODP.ODPNode_getAttributes(x)),
    "ownerDocument"  :lambda x:_ntype(_cODP.ODPNode_getOwnerDocument(x)),
    "tagName"        :_cODP.ODPElement_getTagName,
  }		   

  def __setattr__(self,attr,value):
    if (attr in ["tagName",
                 "nodeName",
                 "nodeType",
		 "parentNode",
		 "childNodes",
		 "firstChild",
		 "lastChild",
		 "previousSibling",
		 "nextSibling",
		 "attributes",
		 "ownerDocument"]):
      raise "Element.%s is read only"%attr
    if attr == "nodeValue":
      raise xml.dom.NoModificationAllowedErr,"Element.nodeValue is read only"
    self.__dict__[attr]=value

  def __getattr__(self,name):
    method = self._get_methods_.get(name,None)
    if (method):
      return method(self.this)
    raise AttributeError,name

  def cloneNode(self, deep):
    raise xml.dom.NotSupportedErr,"Element.cloneNode not supported"

  def getAttribute(self, attrname):
    return _cODP.ODPElement_getAttribute(self.this,attrname)

  def setAttribute(self, attname, value):
    raise xml.dom.NoModificationAllowedErr,"Element.setAttribute not supported"

  def getAttributeNode(self, attrname):
    return _ntype(_cODP.ODPElement_getAttributeNode(self.this,attrname))

  def setAttributeNode(self, attr):
    raise xml.dom.NoModificationAllowedErr,"Element.setAttributeNode not supported"

  def removeAttribute(self, name):
    raise xml.dom.NoModificationAllowedErr,"Element.removeAttribute not supported"

  def removeAttributeNode(self, node):
    raise xml.dom.NoModificationAllowedErr,"Element.removeAttributeNode not supported"

  def hasAttribute(self, name):
    return _cODP.ODPElement_getAttribute(self.this,name) is not None

  def getElementsByTagName(self, name):
    return NodeList(_cODP.ODPElement_getElementsByTagName(self.this,name))

  def __repr__(self):
      return "<DOM Element: %s at %s>" % (self.tagName, id(self))

  def hasAttributes(self):
    raise "write me!"

class CharacterData(Node):
  def __init__(self, node):
    self.this    = _cODP.new_ODPCharacterData(node)
    self.thisown = 1

  _get_methods_={
    "nodeName"       :_cODP.ODPNode_getNodeName,
    "nodeValue"      :_cODP.ODPNode_getNodeValue,
    "nodeType"       :_cODP.ODPNode_getNodeType,
    "parentNode"     :lambda x:_ntype(_cODP.ODPNode_getParentNode(x)),
    "childNodes"     :lambda x: NodeList(_cODP.ODPNode_getChildNodes(x)),
    "firstChild"     :lambda x:_ntype(_cODP.ODPNode_getFirstChild(x)),
    "lastChild"      :lambda x:_ntype(_cODP.ODPNode_getLastChild(x)),
    "previousSibling":lambda x:_ntype(_cODP.ODPNode_getPreviousSibling(x)),
    "nextSibling"    :lambda x:_ntype(_cODP.ODPNode_getNextSibling(x)),
    "attributes"     :lambda x: AttributeList(_cODP.ODPNode_getAttributes(x)),
    "ownerDocument"  :lambda x:_ntype(_cODP.ODPNode_getOwnerDocument(x)),
    "length"         :_cODP.ODPCharacterData_getLength,
    "data"           :_cODP.ODPCharacterData_getData,
  }		   

  def __repr__(self):
    return "<DOM %s node>" % (self.__class__.__name__)

  def __setattr__(self,attr,value):
    if (attr in ["length"
                 "nodeName",
                 "nodeType",
		 "parentNode",
		 "childNodes",
		 "firstChild",
		 "lastChild",
		 "previousSibling",
		 "nextSibling",
		 "attributes",
		 "ownerDocument"]):
      raise "Node.%s is read only"%attr
    if attr in ["nodeValue","data"]:
      raise xml.dom.NoModificationAllowedErr,"CharacterData.%s is read only"%attr
    self.__dict__[attr]=value

  def __getattr__(self,name):
    method = self._get_methods_.get(name,None)
    if (method):
      return method(self.this)
    raise AttributeError,name


  def __len__(self):
    return _cODP.ODPCharacterData_getLength(self.this)

  def __str__(self):
    return _cODP.ODPCharacterData_getData(self.this)

  def substringData(self, offset, count):
    if offset < 0:
      raise xml.dom.IndexSizeErr("offset is negative")
    if offset >= len(self):
      raise xml.dom.IndexSizeErr("offset out of range")
    if count < 0:
      raise xml.dom.IndexSizeErr("count is negative")
    return _cODP.ODPCharacterData_substringData(self.this,offset,count)

  def appendData(self, arg):
    raise xml.dom.NoModificationAllowedErr,"CharacterData.appendData not supported"

  def insertData(self, offset, arg):
    raise xml.dom.NoModificationAllowedErr,"CharacterData.insertData not supported"

  def deleteData(self, offset, count):
    raise xml.dom.NoModificationAllowedErr,"CharacterData.deleteData not supported"

  def replaceData(self, offset, count, arg):
    raise xml.dom.NoModificationAllowedErr,"CharacterData.replaceData not supported"


class Comment(CharacterData):
  pass

class Text(CharacterData):
  def splitText(self, offset):
    raise xml.dom.NoModificationAllowedErr,"Text.splitText not supported"

class CDATASection(Text):
  pass
    
class ProcessingInstruction(Node):
  def __init__(self, node):
    self.this    = _cODP.new_ODPProcessingInstruction(node)
    self.thisown = 1

  _get_methods_={
    "nodeName"       :_cODP.ODPNode_getNodeName,
    "nodeValue"      :_cODP.ODPNode_getNodeValue,
    "nodeType"       :_cODP.ODPNode_getNodeType,
    "parentNode"     :lambda x:_ntype(_cODP.ODPNode_getParentNode(x)),
    "childNodes"     :lambda x: NodeList(_cODP.ODPNode_getChildNodes(x)),
    "firstChild"     :lambda x:_ntype(_cODP.ODPNode_getFirstChild(x)),
    "lastChild"      :lambda x:_ntype(_cODP.ODPNode_getLastChild(x)),
    "previousSibling":lambda x:_ntype(_cODP.ODPNode_getPreviousSibling(x)),
    "nextSibling"    :lambda x:_ntype(_cODP.ODPNode_getNextSibling(x)),
    "attributes"     :lambda x: AttributeList(_cODP.ODPNode_getAttributes(x)),
    "ownerDocument"  :lambda x:_ntype(_cODP.ODPNode_getOwnerDocument(x)),
    "length"         :_cODP.ODPCharacterData_getLength,
    "target"         :lambda x:split(x.getNodeName())[0],
    "data"           :lambda x:join(split(x.getNodeName())[1:])
  }		   

  def __setattr__(self,attr,value):
    if (attr in ["target",
                 "nodeName",
                 "nodeType",
		 "parentNode",
		 "childNodes",
		 "firstChild",
		 "lastChild",
		 "previousSibling",
		 "nextSibling",
		 "attributes",
		 "ownerDocument"]):
      raise "ProcessingInstruction.%s is read only"%attr
    if attr in ["nodeValue","data"]:
      raise xml.dom.NoModificationAllowedErr,"ProcessingInstruction.%s is read only"%attr
    self.__dict__[attr]=value

  def __getattr__(self,name):
    method = self._get_methods_.get(name,None)
    if (method):
      return method(self.this)
    raise AttributeError,name


class DOMImplementation:
  def hasFeature(self, feature, version):
    if version not in ("1.0", "2.0"):
      return 0
    feature = _string.lower(feature)
    return feature == "core"

class Document(Node):
  doctype=None
  implementation=DOMImplementation()

  def __init__(self,n):
    self.this = n
    self.thisown=1

  _get_methods_={
    "nodeName"         :_cODP.ODPNode_getNodeName,
    "nodeValue"        :_cODP.ODPNode_getNodeValue,
    "nodeType"         :_cODP.ODPNode_getNodeType,
    "parentNode"       :lambda x:_ntype(_cODP.ODPNode_getParentNode(x)),
    "childNodes"       :lambda x: NodeList(_cODP.ODPNode_getChildNodes(x)),
    "firstChild"       :lambda x:_ntype(_cODP.ODPNode_getFirstChild(x)),
    "lastChild"        :lambda x:_ntype(_cODP.ODPNode_getLastChild(x)),
    "previousSibling"  :lambda x:_ntype(_cODP.ODPNode_getPreviousSibling(x)),
    "nextSibling"      :lambda x:_ntype(_cODP.ODPNode_getNextSibling(x)),
    "attributes"       :lambda x: AttributeList(_cODP.ODPNode_getAttributes(x)),
    "ownerDocument"    :lambda x:_ntype(_cODP.ODPNode_getOwnerDocument(x)),
    "documentElement"  :lambda x:_ntype(_cODP.ODPDocument_getDocumentElement(x)),
  }		   

  def __setattr__(self,attr,value):
    if (attr in ["documentElement"
                 "nodeName",
                 "nodeType",
		 "parentNode",
		 "childNodes",
		 "firstChild",
		 "lastChild",
		 "previousSibling",
		 "nextSibling",
		 "attributes",
		 "ownerDocument"]):
      raise "Document.%s is read only"%attr
    if attr == "nodeValue":
      raise xml.dom.NoModificationAllowedErr,"Node.nodeValue is read only"
    self.__dict__[attr]=value

  def __getattr__(self,name):
    method = self._get_methods_.get(name,None)
    if (method):
      return method(self.this)
    raise AttributeError,name

  def createDocumentFragment(self):
    raise xml.dom.NotSupportedErr,"Document.createDocumentFragment not supported"

  def createElement(self, tagName):
    raise xml.dom.NotSupportedErr,"Document.createElement not supported"

  def createTextNode(self, data):
    raise xml.dom.NotSupportedErr,"Document.createTextNode not supported"

  def createCDATASection(self, data):
    raise xml.dom.NotSupportedErr,"Document.createCDATASection not supported"

  def createComment(self, data):
    raise xml.dom.NotSupportedErr,"Document.createComment not supported"

  def createProcessingInstruction(self, target, data):
    raise xml.dom.NotSupportedErr,"Document.createProcessingInstruction not supported"

  def createAttribute(self, qName):
    raise xml.dom.NotSupportedErr,"Document.createAttribute not supported"

  def getElementsByTagName(self, name):
    return NodeList(_cODP.ODPDocument_getElementsByTagName(self.this,name))


def parseString(doc):
  return Document(_cODP.ODP_parseString(doc))

def parseFile(f):
  if type(f) is StringType:
    return Document(_cODP.ODP_parseFile(f))
  else:
    doc=f.read()
    return Document(_cODP.ODP_parseString(doc))
    
def getDOMImplementation():
    return Document.implementation


_ntype_table={
  xml.dom.Node.ELEMENT_NODE:                     Element,
  xml.dom.Node.ATTRIBUTE_NODE:                   Attr,
  xml.dom.Node.TEXT_NODE:                        Text,
  xml.dom.Node.CDATA_SECTION_NODE:               CDATASection,
  xml.dom.Node.PROCESSING_INSTRUCTION_NODE:      ProcessingInstruction,
  xml.dom.Node.COMMENT_NODE:                     Comment,
  xml.dom.Node.DOCUMENT_NODE:                    Document,
  xml.dom.Node.DOCUMENT_FRAGMENT_NODE:           DocumentFragment}

class ChildrenByTagNameList(NodeList):
  def __init__(self,node,tag):
    NodeList.__init__(self,_cODP.new_ODPChildrenByTagNameList(node,tag))
    
  
def _ntype(node):
  try:
    node = node.this
  except:
    pass
  if node:
    a=apply(_ntype_table[_cODP.ODPNode_getNodeType(node)],(node,))
    _cODP.delete_ODPNode(node)
    return a
  else:
    return None  
