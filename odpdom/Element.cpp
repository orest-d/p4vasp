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
 
#include <ODP/Exceptions.h>

#define NMAE(x) THROW_DOMEXC(NO_MODIFICATION_ALLOWED_ERR,x)

#include <ODP/Element.h>
#include <ODP/mark.h>

ODPElement::ODPElement(ODPDocument *document, long position){
  doc=document;
  pos=position;
  attr.setNode(this);
}

ODPElement::ODPElement(){
  doc=NULL;
  pos=ODP_INVALID_NODE;
  attr.setNode(this);
}

ODPElement::ODPElement(ODPNode *node){
//  printf("ODPElement::ODPElement(ODPNode *node)\n");
//  printf("doc:%p\n",node->doc);
  this->doc=node->doc;
//  printf("a\n");
  this->pos=node->pos;
//  printf("b\n");
  attr.setNode(this);
//  printf("ODPElement::ODPElement(ODPNode *node) -\n");
}

ODPElement::ODPElement(ODPNode &node){
  this->doc=node.doc;
  this->pos=node.pos;
  attr.setNode(this);
}

void ODPElement::refreshAttr(){
  attr.setNode(this);
}

char *ODPElement::getTagName(){
  return &doc->text[pos+1];
}

char *ODPElement::getAttribute(const char *name){  
//  printf("ODPElement::getAttribute(%s)\n",name);
  return attr.getAttribute(name);
}

void ODPElement::setAttribute(const char *name, const char *value){
  NMAE("in Element.setAttribute.");
}

void ODPElement::removeAttribute(const char *name){
  NMAE("in Element.removeAttribute");
}

ODPAttr *ODPElement::getAttributeNode(const char *name){
  return (ODPAttr *)attr.getNamedItem(name);
}

ODPAttr *ODPElement::setAttributeNode(ODPAttr *newAttr){
  NMAE("in Element.setAttributeNode");
}

ODPAttr *ODPElement::removeAttributeNode(ODPAttr *oldAttr){
  NMAE("in Element.removeAttributeNode");
}

ODPNodeList *ODPElement::getElementsByTagName(const char *name){
  return new ODPElementsByTagNameList(this,name);
}

void ODPElement::normalize(){
}

