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
 
#ifndef ODPExceptions_h
#define ODPExceptions_h
#include <stdio.h>
#include <exception>

using namespace std;

const unsigned short   INDEX_SIZE_ERR		    = 1;      
const unsigned short   DOMSTRING_SIZE_ERR	    = 2;      
const unsigned short   HIERARCHY_REQUEST_ERR	    = 3;      
const unsigned short   WRONG_DOCUMENT_ERR	    = 4;      
const unsigned short   INVALID_CHARACTER_ERR	    = 5;      
const unsigned short   NO_DATA_ALLOWED_ERR	    = 6;      
const unsigned short   NO_MODIFICATION_ALLOWED_ERR  = 7;      
const unsigned short   NOT_FOUND_ERR		    = 8;      
const unsigned short   NOT_SUPPORTED_ERR	    = 9;      
const unsigned short   INUSE_ATTRIBUTE_ERR	    = 10;     

class DOMException:public exception{
  char buff[256];
  public:
  unsigned short code;
#ifndef SWIG
  DOMException(unsigned short c, const char *s="");
#endif
  const char *what();
};

class ODPException:public exception{
  char buff[256];
  public:
#ifndef SWIG
  ODPException(const char *s="");
#endif
  const char *what();
};


#ifndef SWIG
#  ifdef NO_THROW
inline void THROW_DOMEXC(unsigned short c, const char *sb=""){
  switch (c){
    case INDEX_SIZE_ERR:
      fprintf(stderr, "DOMException INDEX_SIZE_ERR:\n%s\n",sb);
      exit(-1);
    case DOMSTRING_SIZE_ERR:
      fprintf(stderr, "DOMException DOMSTRING_SIZE_ERR:\n%s\n",sb);
      exit(-1);
    case HIERARCHY_REQUEST_ERR:
      fprintf(stderr, "DOMException HIERARCHY_REQUEST_ERR:\n%s\n",sb);
      exit(-1);
    case WRONG_DOCUMENT_ERR:
      fprintf(stderr, "DOMException WRONG_DOCUMENT_ERR:\n%s\n",sb);
      exit(-1);
    case INVALID_CHARACTER_ERR:
      fprintf(stderr, "DOMException INVALID_CHARACTER_ERR:\n%s\n",sb);
      exit(-1);
    case NO_DATA_ALLOWED_ERR:
      fprintf(stderr, "DOMException NO_DATA_ALLOWED_ERR:\n%s\n",sb);
      exit(-1);
    case NO_MODIFICATION_ALLOWED_ERR:
      fprintf(stderr, "DOMException NO_MODIFICATION_ALLOWED_ERR:\n%s\n",sb);
      exit(-1);
    case NOT_FOUND_ERR:
      fprintf(stderr, "DOMException NOT_FOUND_ERR:\n%s\n",sb);
      exit(-1);
    case NOT_SUPPORTED_ERR:
      fprintf(stderr, "DOMException NOT_SUPPORTED_ERR:\n%s\n",sb);
      exit(-1);
    case INUSE_ATTRIBUTE_ERR:
      fprintf(stderr, "DOMException INUSE_ATTRIBUTE_ERR:\n%s\n",sb);
      exit(-1);
  }
}
inline void THROW_ODPEXC(const char *s){
  fprintf(stderr, "ODPException: %s\n",s);
  exit(-1);
}
#  else
inline void THROW_DOMEXC(unsigned short c, const char *sb=""){
  throw DOMException(c,sb);
}
inline void THROW_ODPEXC(const char *s){
  throw ODPException(s);
}
#endif
#endif

#endif
