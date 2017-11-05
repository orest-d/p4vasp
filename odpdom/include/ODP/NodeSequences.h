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
 
#ifndef ODPNodeSequences_h
#define ODPNodeSequences_h

#include "Node.h"

class ODPNodeList {
  public:
  virtual ODPNode *item(unsigned long index);
  virtual unsigned long getLength();
};

class ODPChildList : public ODPNodeList {
  ODPNode node;
  long len;
#ifndef NO_POS_CACHE  
  long pos_cache;
  unsigned long index_cache;
#endif
  public:
  ODPChildList(ODPNode *node);
#ifndef SWIG  
  ODPChildList(ODPNode &node);
#endif  
  virtual ODPNode *item(unsigned long index);
  virtual unsigned long getLength();
};

class ODPElementsByTagNameList : public ODPNodeList {
  ODPNode node;
  long len;
  char *tag;
#ifndef NO_POS_CACHE  
  long pos_cache;
  unsigned long index_cache;
  long level_cache;
#endif
  
  public:
  ODPElementsByTagNameList(ODPNode *node, const char *tag);
#ifndef SWIG  
  ODPElementsByTagNameList(ODPNode &node, const char *tag);
#endif  
  virtual ~ODPElementsByTagNameList();
  
  virtual ODPNode *item(unsigned long index);
  virtual unsigned long getLength();
};

class ODPChildrenByTagNameList : public ODPNodeList {
  ODPNode node;
  long len;
  char *tag;
#ifndef NO_POS_CACHE  
  long pos_cache;
  unsigned long index_cache;
#endif
  
  public:
  ODPChildrenByTagNameList(ODPNode *node, const char *tag);
#ifndef SWIG  
  ODPChildrenByTagNameList(ODPNode &node, const char *tag);
#endif  
  virtual ~ODPChildrenByTagNameList();
  
  virtual ODPNode *item(unsigned long index);
  virtual unsigned long getLength();
};

class ODPNamedNodeMap {
  public:
  virtual ODPNode  *getNamedItem(const char *name);
  virtual ODPNode  *setNamedItem(ODPNode *arg);
  virtual ODPNode  *removeNamedItem(const char *name);
  virtual ODPNode  *item(unsigned long index);
  virtual unsigned long getLength();
};

class ODPAttributeMap : public ODPNamedNodeMap{
  long len;
  ODPNode node;
  public:
  ODPAttributeMap(ODPNode *node);
#ifndef SWIG  
  ODPAttributeMap();
  ODPAttributeMap(ODPNode &node);
#endif

  void setNode(ODPNode *node);
#ifndef SWIG  
  void setNode(ODPNode &node);
#endif
  
  char *getAttribute(const char *name);
  virtual ODPNode  *getNamedItem(const char *name);
  virtual ODPNode  *item(unsigned long index);
  virtual unsigned long getLength();
};

class ODPAttr : public ODPNode {
  public:
  ODPAttr(ODPNode *node);
#ifndef SWIG  
  ODPAttr();
  ODPAttr(ODPNode &node);
#endif
  
  char *getName();
  int   getSpecified();
  char *getValue();
  void  setValue(const char *s);
};

#endif
