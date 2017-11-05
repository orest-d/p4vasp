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
 
#include <stdio.h>
#include <ODP/Document.h>
#include <ODP/Element.h>
#include <ODP/Exceptions.h>
#include <ODP/mark.h>

#define NSE(x) THROW_DOMEXC(NOT_SUPPORTED_ERR,x)

int ODPDOMImplementation::hasFeature(const char *feature, const char *version){
  return 0;
}

ODPDOMImplementation *ODPDocument::dummy_implementation = 
                       new ODPDOMImplementation();

ODPDocument::ODPDocument(const char *text,long len){
  this->text=(char *)text;
  this->len =len;
  pos=ODP_DOCUMENT_NODE;
  doc=this;
}

ODPDocumentType *ODPDocument::getDoctype(){
  return NULL;
}

ODPDOMImplementation *ODPDocument::getImplementation(){
  return dummy_implementation;
}

ODPElement *ODPDocument::getDocumentElement(){
  ODPElement *node = new ODPElement(this);
  for (node->pos=0; node->pos<len; node->pos++){
    if (node->poschar()==ODP_MARK_NODE_BEGIN){
      node->refreshAttr();
      return node;
    }
  }
  delete node;
  return NULL;  
}

ODPElement *ODPDocument::createElement(const char *tagName){
  NSE("Document.createElement is not supported.");
}

ODPDocumentFragment *ODPDocument::createDocumentFragment(){
  NSE("Document.createDocumentFragment is not supported.");
}

ODPText *ODPDocument::createTextNode(const char *data){
  NSE("Document.createTextNode is not supported.");
}

ODPComment *ODPDocument::createComment(const char *data){
  NSE("Document.createComment is not supported.");
}

ODPCDATASection *ODPDocument::createCDATASection(const char *data){
  NSE("Document.createCDATASection is not supported.");
}

ODPProcessingInstruction *ODPDocument::createProcessingInstruction(const char *target,
                                                   const char *data){
  NSE("Document.createProcessingInstruction is not supported.");
}

ODPAttr *ODPDocument::createAttribute(const char *name){
  NSE("Document.createAttribute is not supported.");
}

ODPEntityReference *ODPDocument::createEntityReference(const char *name){
  NSE("Document.createProcessingInstruction is not supported.");
}

ODPNodeList *ODPDocument::getElementsByTagName(const char *tagname){
  return new ODPElementsByTagNameList(this,tagname);
}

char *ODPDocument::_simpleSearchAfter(long p, char c){
  long l=len-1;
  for(;p<l ; p++){
    if (text[p]==c){
      return &text[p+1];
    }
  }
  return NULL;
}

int ODPDocument::charAtPos(long p){
#if CHECK>1
  if (p<0){
    THROW_ODPEXC("Position negative in Document.charAtPos(p)");
  }
  if (p>=len){
    THROW_ODPEXC("Position out of range in Document.charAtPos(p)");
  }
#endif  
  return text[p];
}

ODPDocumentParent::ODPDocumentParent(char *text,long len):ODPDocument(text,len){;}

ODPDocumentParent::~ODPDocumentParent(){
  printf("ODPDocumentParent::~ODPDocumentParent()\n");
  delete text;
  text=NULL;
}

