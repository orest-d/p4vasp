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
 
#ifndef ODPDocument_h
#define ODPDocument_h

#include "Node.h"

class ODPNodeList;
class ODPText;
class ODPComment;
class ODPCDATASection;

class ODPElement;
class ODPAttr;
class ODPProcessingInstruction;
class ODPDocumentType;
class ODPEntityReference;
class ODPDocumentFragment;

class ODPDOMImplementation {
  public:
  int hasFeature(const char *feature, const char *version);
};


class ODPDocument : public ODPNode{
  static ODPDOMImplementation *dummy_implementation;
  
  public:
#ifndef SWIG  
  ODPDocument(const char *text,long len);
#endif

  ODPDocumentType       *getDoctype();
  ODPDOMImplementation  *getImplementation();
  ODPElement            *getDocumentElement();

  ODPElement            *createElement(const char *tagName);
  ODPDocumentFragment   *createDocumentFragment();
  ODPText               *createTextNode(const char *data);
  ODPComment            *createComment(const char *data);
  ODPCDATASection       *createCDATASection(const char *data);
  ODPProcessingInstruction *createProcessingInstruction(const char *target, 
                                                     const char *data);
  ODPAttr               *createAttribute(const char *name);
  ODPEntityReference    *createEntityReference(const char *name);  
  
  ODPNodeList           *getElementsByTagName(const char *tagname);  

#ifndef SWIG
  char *text;
  long len;
  
  char *_simpleSearchAfter(long pos, char c);
  int charAtPos(long p);
#endif
};

class ODPDocumentParent : public ODPDocument{
  public:
#ifndef SWIG  
  ODPDocumentParent(char *text,long len);
#endif  
  ~ODPDocumentParent();  
};
#endif
