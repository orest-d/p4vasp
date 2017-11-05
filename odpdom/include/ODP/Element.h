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
 
#ifndef ODPElement_h
#define ODPElement_h


#include "Document.h"
#include "Node.h"
#include "NodeSequences.h"

class ODPElement : public ODPNode {
  ODPAttributeMap attr;
  public:

  ODPElement(ODPNode *node);
#ifndef SWIG  
  ODPElement(ODPDocument *document, long position);
  ODPElement();
  ODPElement(ODPNode &node);
#endif  
  
  char        *getTagName();
  char        *getAttribute(const char *name);
  void         setAttribute(const char *name, const char *value);	    
  void         removeAttribute(const char *name);		   
  ODPAttr     *getAttributeNode(const char *name);		   
  ODPAttr     *setAttributeNode(ODPAttr *newAttr);	   
  ODPAttr     *removeAttributeNode(ODPAttr *oldAttr);	  	   
  ODPNodeList *getElementsByTagName(const char *name);	           
  void         normalize(); 			           
  
  void refreshAttr();
};

#endif
