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
 
#include <ODP/Node.h>
#include <ODP/Element.h>
#include <ODP/NodeSequences.h>
#include <ODP/Document.h>
#include <ODP/Exceptions.h>
#include <ODP/mark.h>
#include <ODP/string.h>

#define NMAE(x) THROW_DOMEXC(NO_MODIFICATION_ALLOWED_ERR,x)

ODPNode *ODPNodeList::item(unsigned long index){
  return NULL;
}

unsigned long ODPNodeList::getLength(){
  return 0;
}

ODPNode  *ODPNamedNodeMap::getNamedItem(const char *name){
  return NULL;
}

ODPNode  *ODPNamedNodeMap::setNamedItem(ODPNode *arg){
  NMAE("in NamedNodeMap.setNamedItem");
}

ODPNode  *ODPNamedNodeMap::removeNamedItem(const char *name){
  NMAE("in NamedNodeMap.removeNamedItem");
}

ODPNode  *ODPNamedNodeMap::item(unsigned long index){
  return NULL;
}

unsigned long ODPNamedNodeMap::getLength(){
  return 0;
}

ODPAttr::ODPAttr():ODPNode(){
}

ODPAttr::ODPAttr(ODPNode *node):ODPNode(node){
}

ODPAttr::ODPAttr(ODPNode &node):ODPNode(node){
}

char *ODPAttr::getName(){
  return NULL;
}

int   ODPAttr::getSpecified(){
  return 1;
}

char *ODPAttr::getValue(){
  return NULL;
}

void  ODPAttr::setValue(const char *s){
  NMAE("in Attr.setValue");
}

ODPChildList::ODPChildList(ODPNode *node){
  len=-1;
  this->node.pos=node->pos;
  this->node.doc=node->doc;
#ifndef NO_POS_CACHE  
  pos_cache=-1;
  index_cache=0;
#endif  
}

ODPChildList::ODPChildList(ODPNode &node){
  len=-1;
  this->node.pos=node.pos;
  this->node.doc=node.doc;
#ifndef NO_POS_CACHE  
  pos_cache=-1;
  index_cache=0;
#endif  
}

ODPNode *ODPChildList::item(unsigned long index){
  ODPNode *n = new ODPNode(node);
  unsigned long i=0;
#ifndef NO_POS_CACHE
//    printf("pos_start=%ld index=%ld pos_cache=%ld index_cache=%ld\n",
//    n->pos,index,pos_cache,index_cache);
    if ((pos_cache>=0) && (index>=index_cache)){
      n->pos=pos_cache;
      i=index_cache;
//      printf("pos cache hit\n");
    }
    else{
      if (!n->down()){
        delete n;
        return NULL;
      }
    }
#else
  if (!n->down()){
    delete n;
    return NULL;
  }
#endif  

  for (;;){
    if (i==index){
#ifndef NO_POS_CACHE    
//      printf("pos cache set\n");
      pos_cache=n->pos;
      index_cache=i;
#endif    
      return n;
    }
    if (n->next()){
      i++;
    }
    else{
      delete n;
      return NULL;        
    }
  }
}

unsigned long ODPChildList::getLength(){
  if (len>=0){
    return len;
  }
  else{
    ODPNode n(node);
    if (n.down()){
      len=1;
      while (n.next()){
        len++;
      }
      return len;
    }
    else{
      len=0;
      return 0;
    }
  }
}

ODPAttributeMap::ODPAttributeMap(){
  len=-1;
  this->node.pos=ODP_INVALID_NODE;
  this->node.doc=NULL;
}

ODPAttributeMap::ODPAttributeMap(ODPNode *node){
  len=-1;
  this->node.pos=node->pos;
  this->node.doc=node->doc;
}

ODPAttributeMap::ODPAttributeMap(ODPNode &node){
  len=-1;
  this->node.pos=node.pos;
  this->node.doc=node.doc;
}

void ODPAttributeMap::setNode(ODPNode *node){
  len=-1;
  this->node.pos=node->pos;
  this->node.doc=node->doc;
}

void ODPAttributeMap::setNode(ODPNode &node){
  len=-1;
  this->node.pos=node.pos;
  this->node.doc=node.doc;
}
  
ODPNode  *ODPAttributeMap::getNamedItem(const char *name){
  ODPAttr *n = new ODPAttr(node);
  if (n->down()){    
    for (;;){
      if (n->poschar()!=ODP_MARK_ATTRIBUTE){
	delete n;
	return NULL;                
      }
      if (ODP_strcmp(name,n->getNodeName())==0){
        return n;
      }
      if (!n->next()){
	delete n;
	return NULL;        
      }
    }
  }
  else{
    delete n;
    return NULL;
  }  
}

char *ODPAttributeMap::getAttribute(const char *name){
  ODPNode n(node);
  long l = n.doc->len;
  if (n.down()){    
    for (;;){
      if (n.poschar()!=ODP_MARK_ATTRIBUTE){
	return NULL;                
      }
      if (ODP_strcmp(name,n.getNodeName())==0){
        return n.getNodeValue();
      }
      if (!n.next()){
	return NULL;        
      }
    }
  }
  else{
    return NULL;
  }  
}

ODPNode  *ODPAttributeMap::item(unsigned long index){
  ODPAttr *n = new ODPAttr(node);
  if (n->down()){    
    for (long i=0;;){
      if (n->poschar()!=ODP_MARK_ATTRIBUTE){
	delete n;
	return NULL;                
      }
      if (i==long(index)){
        return n;
      }
      if (n->next()){
        i++;
      }
      else{
	delete n;
	return NULL;        
      }
    }
  }
  else{
    delete n;
    return NULL;
  }  
}

unsigned long ODPAttributeMap::getLength(){
  if (len>=0){
    return len;
  }
  else{
    ODPNode n(node);
    if (n.down()){
      if (n.poschar() != ODP_MARK_ATTRIBUTE){
        len=0;
	return 0;
      }
      len=1;
      while (n.next()){
        if (n.poschar() != ODP_MARK_ATTRIBUTE){
	  break;
	}
        len++;
      }
      return len;
    }
    else{
      len=0;
      return 0;
    }
  }
}

ODPElementsByTagNameList::ODPElementsByTagNameList(ODPNode *node, const char *tag){
//  printf("new ODPElementsByTagNameList(%s)\n",tag);
  this->tag = ODP_strclone(tag);
  len=-1;
  this->node.pos=node->pos;
  this->node.doc=node->doc;
#ifndef NO_POS_CACHE  
  pos_cache=-1;
  index_cache=0;
  level_cache=0;
#endif  
}

ODPElementsByTagNameList::ODPElementsByTagNameList(ODPNode &node, const char *tag){
//  printf("new ODPElementsByTagNameList(%s)\n",tag);
  this->tag = ODP_strclone(tag);
  len=-1;
  this->node.pos=node.pos;
  this->node.doc=node.doc;
#ifndef NO_POS_CACHE  
  pos_cache=-1;
  index_cache=0;
  level_cache=0;
#endif  
}



ODPElementsByTagNameList::~ODPElementsByTagNameList(){
 delete tag;
}

ODPNode *ODPElementsByTagNameList::item(unsigned long index){
//  printf("ODPElementsByTagNameList::item(%ld)\n",index);
  long level=0;
  ODPElement *n = new ODPElement(node);
  long l=n->doc->len;
  long i=0;
  if (n->pos==ODP_DOCUMENT_NODE){
    long pos_start=0;
#ifndef NO_POS_CACHE
//    printf("pos_start=%ld index=%ld pos_cache=%ld index_cache=%ld level_cache=%ld\n",
//    pos_start,index,pos_cache,index_cache,level_cache);
    if ((pos_cache>=0) && (index>=index_cache)){
      pos_start=pos_cache;
      i=index_cache;
      level=level_cache;
//      printf("pos cache hit\n");
    }    
#endif    
    for(n->pos=pos_start; n->pos<l; n->pos++){
      if (n->poschar()==ODP_MARK_NODE_BEGIN){
	if (ODP_strcmp(tag,n->getNodeName())==0){
	  if (i==long(index)){
#ifndef NO_POS_CACHE    
//            printf("pos cache set\n");
	    pos_cache=n->pos;
	    index_cache=i;
	    level_cache=level;
#endif    
	    n->refreshAttr();
//	    printf("Return a %p\n",n);
	    return n;
	  }
	  i++;
	}
      }
    }
  }
  else{
    long pos_start=n->pos+1;
#ifndef NO_POS_CACHE    
//    printf("pos_start=%ld index=%ld pos_cache=%ld index_cache=%ld level_cache=%ld\n",
//    pos_start,index,pos_cache,index_cache,level_cache);
    if ((pos_cache>=0) && (index>=index_cache)){
      pos_start=pos_cache;
      i=index_cache;
      level=level_cache;
//      printf("pos cache hit\n");
    }
#endif    
    for(n->pos=pos_start; n->pos<l; n->pos++){
//      printf("%3ld <%c> %3d level:%3ld %s\n",n->pos,
//      n->doc->text[n->pos],n->doc->text[n->pos],level,&n->doc->text[n->pos]);
      switch (n->poschar()){
	case ODP_MARK_NODE_BEGIN:
//	  printf("ODP_MARK_NODE_BEGIN\n");
	  if (level>=0){
	    if (ODP_strcmp(tag,n->getNodeName())==0){
	      if (i==long(index)){
#ifndef NO_POS_CACHE    
//                printf("pos cache set\n");
                pos_cache=n->pos;
		index_cache=i;
		level_cache=level;
#endif    
		n->refreshAttr();
//    	        printf("Return b %p\n",n);
		return n;
	      }
	      i++;
	    }
	    level++;
	  }
	  else{
	    delete n;
//	    printf("Return c NULL\n");
	    return NULL;
	  }
	  break;
	case ODP_MARK_NODE_ENDTERM:
	case ODP_MARK_NODE_TERM:
	  if (level<=0){
	    delete n;
//	    printf("Return d NULL %d\n",level);
	    return NULL;
	  }
	  level--;
	  break;
      }
    }
  }
  delete n;
//  printf("Return e NULL\n");
  return NULL;
}

unsigned long ODPElementsByTagNameList::getLength(){
//  printf("ODPElementsByTagNameList::getLength()\n");
  if (len>=0){
//    printf("len known:%ld\n",len);
    return len;
  }
  else{
    if (node.pos==ODP_DOCUMENT_NODE){
      ODPNode n(node);
      long l=n.doc->len;
      len=0;
      for(n.pos=0; n.pos<l; n.pos++){
        if (n.poschar()==ODP_MARK_NODE_BEGIN){
	  if (ODP_strcmp(tag,n.getNodeName())==0){
	    len++;
	  }
	}
      }
      return len; 
    }
    else{
      len=0;
      long level=0;
      ODPNode n(node);
      long l=n.doc->len;
      for(n.pos++; n.pos<l; n.pos++){
//	printf("%3ld len:%3ld level:%3ld %s\n",n.pos,len,level,&n.doc->text[n.pos]);
	switch (n.poschar()){
	  case ODP_MARK_NODE_BEGIN:
	    if (level>=0){
	      if (ODP_strcmp(tag,n.getNodeName())==0){
		len++;
	      }
	      level++;
	    }
	    else{
	      return len;
	    }
	    break;
	  case ODP_MARK_NODE_ENDTERM:
	  case ODP_MARK_NODE_TERM:
	    if (level<=0){
	      return len;
	    }
	    level--;
	    break;
	}
      }
      return len;
    }
  }      
}





ODPChildrenByTagNameList::ODPChildrenByTagNameList(ODPNode *node, const char *tag){
//  printf("new ODPChildrenByTagNameList(%s)\n",tag);
  this->tag = ODP_strclone(tag);
  len=-1;
  this->node.pos=node->pos;
  this->node.doc=node->doc;
#ifndef NO_POS_CACHE  
  pos_cache=-1;
  index_cache=0;
#endif  
}

ODPChildrenByTagNameList::ODPChildrenByTagNameList(ODPNode &node, const char *tag){
//  printf("new ODPChildrenByTagNameList(%s)\n",tag);
  this->tag = ODP_strclone(tag);
  len=-1;
  this->node.pos=node.pos;
  this->node.doc=node.doc;
#ifndef NO_POS_CACHE  
  pos_cache=-1;
  index_cache=0;
#endif  
}



ODPChildrenByTagNameList::~ODPChildrenByTagNameList(){
 delete tag;
}

ODPNode *ODPChildrenByTagNameList::item(unsigned long index){
  ODPNode *n = new ODPNode(node);
  unsigned long i=0;
#ifndef NO_POS_CACHE
//    printf("pos_start=%ld index=%ld pos_cache=%ld index_cache=%ld\n",
//    n->pos,index,pos_cache,index_cache);
    if ((pos_cache>=0) && (index>=index_cache)){
      n->pos=pos_cache;
      i=index_cache;
//      printf("pos cache hit\n");
    }
    else{
      if (!n->down()){
        delete n;
        return NULL;
      }
      while(ODP_strcmp(tag,n->getNodeName())!=0){
	if (!n->next()){
	  delete n;
	  return NULL;        
	}
      }
    }
#else
  if (!n->down()){
    delete n;
    return NULL;
  }
  while(ODP_strcmp(tag,n->getNodeName())!=0){
    if (!n->next()){
      delete n;
      return NULL;        
    }
  }
#endif  

  for (;;){
    if (i==index){
#ifndef NO_POS_CACHE    
//      printf("pos cache set\n");
      pos_cache=n->pos;
      index_cache=i;
#endif    
      return n;
    }
    if (n->next()){
      if (ODP_strcmp(tag,n->getNodeName())==0){
	i++;
      }
    }
    else{
      delete n;
      return NULL;        
    }
  }
}

unsigned long ODPChildrenByTagNameList::getLength(){
  if (len>=0){
    return len;
  }
  else{
    ODPNode n(node);
    len=0;
    if (n.down()){
      if (ODP_strcmp(tag,n.getNodeName())==0){
	len++;
      }
      while (n.next()){
	if (ODP_strcmp(tag,n.getNodeName())==0){
	  len++;
	}
      }
      return len;
    }
    else{
      len=0;
      return 0;
    }
  }
}
