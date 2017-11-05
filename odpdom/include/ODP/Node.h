/*
 * Copyright (C) 2003 Orest Dubay <odubay@users.sourceforge.net>
 *
 * This file is part of ODPdom, a free DOM XML parser library.
 * See http://sourceforge.net/projects/odpdom/ for updates.
 * 
 * ODPdom is free software; you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * ODPdom is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with ODPdom; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */
 
#ifndef ODPNode_h
#define ODPNode_h

class ODPDocument;
class ODPNodeList;
class ODPNamedNodeMap;


class ODPNode{
  public:

#ifndef SWIG
#endif
  ODPDocument *doc;
  long pos;

  ODPNode(ODPNode *node);
#ifndef SWIG  
  ODPNode(ODPNode &node);
  ODPNode(ODPDocument *document, long position);
  ODPNode();
#endif
    
  //ODPNode(const char *text,long pos);
  static const unsigned short      ELEMENT_NODE                   = 1;
  static const unsigned short      ATTRIBUTE_NODE                 = 2;
  static const unsigned short      TEXT_NODE                      = 3;
  static const unsigned short      CDATA_SECTION_NODE             = 4;
  static const unsigned short      ENTITY_REFERENCE_NODE          = 5;
  static const unsigned short      ENTITY_NODE                    = 6;
  static const unsigned short      PROCESSING_INSTRUCTION_NODE    = 7;
  static const unsigned short      COMMENT_NODE                   = 8;
  static const unsigned short      DOCUMENT_NODE                  = 9;
  static const unsigned short      DOCUMENT_TYPE_NODE             = 10;
  static const unsigned short      DOCUMENT_FRAGMENT_NODE         = 11;
  static const unsigned short      NOTATION_NODE                  = 12;

  char *getNodeName();
  char *getNodeValue();
  void setNodeValue(const char *v);

  unsigned short   getNodeType();
  ODPNode            *getParentNode();
  ODPNodeList        *getChildNodes();
  ODPNode            *getFirstChild();
  ODPNode            *getLastChild();
  ODPNode            *getPreviousSibling();
  ODPNode            *getNextSibling();
  ODPNamedNodeMap    *getAttributes();
  ODPDocument        *getOwnerDocument();
#ifndef SWIG  
  ODPNode            *insertBefore(ODPNode *newChild, ODPNode *refChild);
  ODPNode            *replaceChild(ODPNode *newChild, ODPNode *oldChild);
  ODPNode            *removeChild(ODPNode *oldChild);
  ODPNode            *appendChild(ODPNode *newChild);
#endif  
  int                hasChildNodes();
#ifndef SWIG  
  ODPNode            *cloneNode(int deep);
  
  int nextBlock();
#endif
  
  int up();
  int down();
  int next();
  int previous();
  
  int poschar();
};
 

#endif
