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
 
#include <string.h>
#include <ODP/CharacterNodes.h>
#include <ODP/string.h>
#include <ODP/Exceptions.h>
#include <ODP/mark.h>

#define NMAE(x) THROW_DOMEXC(NO_MODIFICATION_ALLOWED_ERR,x)

ODPCharacterData::ODPCharacterData(ODPNode *node) : ODPNode(node){;}

ODPText::ODPText(ODPNode *node) : ODPCharacterData(node){;}

ODPComment::ODPComment(ODPNode *node) : ODPCharacterData(node){;}

ODPCDATASection::ODPCDATASection(ODPNode *node) : ODPText(node){;}

char *ODPCharacterData::getData(){
  return getNodeValue();
}

void ODPCharacterData::setData(char *s){
  NMAE("in CharacterData.setData");
}

  
unsigned long ODPCharacterData::getLength(){
  return (unsigned long)ODP_strlen(getNodeValue());
}

char *ODPCharacterData::substringData(unsigned long offset, unsigned long
count){
  long l=ODP_strlen(getNodeValue());
  if (offset<0){
    THROW_DOMEXC(INDEX_SIZE_ERR,"offset negative"
    " in CharacterData.substringData()");
  }
  if (offset>=l){
    THROW_DOMEXC(INDEX_SIZE_ERR,"offset exceeds length"
    " in CharacterData.substringData()");
  }
  if (count<0){
    THROW_DOMEXC(INDEX_SIZE_ERR,"count is negative"
    " in CharacterData.substringData()");
  }
  if ((l-offset) < count){
    count=l-offset;
  }

  char *d = new char[count+1];
  char *s = getNodeValue() ;
  memcpy(d,&s[offset],count);
  d[count]='\0';
  return d;
}

void  ODPCharacterData::appendData(char *arg){
  NMAE("in CharacterData.appendData");
}

void  ODPCharacterData::insertData(unsigned long offset, char *arg){
  NMAE("in CharacterData.insertData");
}

void  ODPCharacterData::deleteData(unsigned long offset, unsigned long count){
  NMAE("in CharacterData.deleteData");
}

void  ODPCharacterData::replaceData(unsigned long offset, unsigned long count,
char *arg){
  NMAE("in CharacterData.replaceData");
}


ODPText *ODPText::splitText(unsigned long offset){
  NMAE("in Text.splitText");
}
