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
 
#ifndef ODPCharacterNodes_h
#define ODPCharacterNodes_h

#include "Node.h"

class ODPCharacterData : public ODPNode {
  public:
  char *getData();
  void setData(char *s);

  ODPCharacterData(ODPNode *node);
    
  unsigned long getLength();
#ifdef SWIG
%typemap(out) char * {
  if ($1==NULL){
    $result=Py_None;
  }
  else{
    $result=PyString_FromString($1);
    delete $1;
  }
}
#endif
  char *substringData(unsigned long offset, unsigned long count);
#ifdef SWIG
%typemap(out) char * {
  if ($1==NULL){
    $result=Py_None;
  }
  else{
    $result=PyString_FromStringAndSize($1,ODP_strlen($1));
  }
}
#endif

  void  appendData(char *arg);
  void  insertData(unsigned long offset, char *arg);
  void  deleteData(unsigned long offset, unsigned long count);
  void  replaceData(unsigned long offset, unsigned long count, char *arg);
};

class ODPText : public ODPCharacterData {
  public:
  ODPText(ODPNode *node);
  ODPText *splitText(unsigned long offset);
};

class ODPComment : public ODPCharacterData {
  public:
  ODPComment(ODPNode *node);
};

class ODPCDATASection : public ODPText {
  public:
  ODPCDATASection(ODPNode *node);
};

#endif
