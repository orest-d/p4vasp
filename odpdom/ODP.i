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
 
%module cODP
%{
#include <exception>
#include <ODP/Exceptions.h>
#include <ODP/string.h>
#include <ODP/Node.h>
#include <ODP/NodeSequences.h>
#include <ODP/Document.h>
#include <ODP/Element.h>
#include <ODP/CharacterNodes.h>
#include <ODP/parse.h>
#include <ODP/pyDOMExc.h>

%}

%exception {
  try{
    $action
  }
  catch(DOMException &e){
    throwPythonDOMException(e.code,e.what());
    return NULL;
  }
  catch(exception &e){
    PyErr_SetString(PyExc_Exception,e.what());
    return NULL;
  }
}

%typemap(out) char * {
  if ($1==NULL){
    $result=Py_None;
    Py_INCREF($result);
  }
  else{
    $result=PyString_FromStringAndSize($1,ODP_strlen($1));
  }
}

%include <include/ODP/parse.h>
%include <include/ODP/Node.h>
%include <include/ODP/Document.h>
%include <include/ODP/Element.h>
%include <include/ODP/CharacterNodes.h>
%include <include/ODP/NodeSequences.h>
