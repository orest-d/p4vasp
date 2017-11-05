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
#include <ODP/Document.h>
#include <ODP/NodeSequences.h>
#include <ODP/Exceptions.h>
#include <ODP/string.h>

#include <ODP/mark.h>

#define NMAE(x) THROW_DOMEXC(NO_MODIFICATION_ALLOWED_ERR,x)

ODPNode::ODPNode(ODPNode *node){
  doc=node->doc;
  pos=node->pos;
}

ODPNode::ODPNode(ODPNode &node){
  doc=node.doc;
  pos=node.pos;
}

ODPNode::ODPNode(ODPDocument *document, long position){
  doc=document;
  pos=position;
}

ODPNode::ODPNode(){
  doc = NULL;
  pos = ODP_INVALID_NODE;
}

int ODPNode::poschar(){
#if CHECK>1
  if (doc==NULL){
    THROW_ODPEXC("Node.doc is NULL in Node.poschar()");
  }
  if (doc->text==NULL){
    THROW_ODPEXC("Node.doc.text is NULL in Node.poschar()");
  }
  if (pos<0){
    THROW_ODPEXC("pos<0 in Node.poschar()");
  }
  if (pos>=doc->len){
    THROW_ODPEXC("pos>=len in Node.poschar()");
  }
#endif
  return doc->text[pos];
}

char *ODPNode::getNodeName(){
//  printf("getNodeName(%c), pos=%ld\n",poschar(),pos);
  if (pos==ODP_DOCUMENT_NODE){
    return "#document";
  }
  switch (poschar()){
    case ODP_MARK_NODE_BEGIN:
      return &doc->text[pos+1];
    case ODP_MARK_ATTRIBUTE:
      return &doc->text[pos+1];
    case ODP_MARK_COMMENT:
      return "#comment";
    case ODP_MARK_CDATA:
      return "#cdata-section";
    case ODP_MARK_PROCESSING:
      return &doc->text[pos+1];
#if CHECK>1
    case ODP_MARK_END:
      THROW_ODPEXC("Invalid mark (MARK_END) in Node.getNodeName");
    case ODP_MARK_NODE_END:
      THROW_ODPEXC("Invalid mark (MARK_NODE_END) in Node.getNodeName");
    case ODP_MARK_NODE_ENDTERM:
      THROW_ODPEXC("Invalid mark (MARK_NODE_ENDTERM) in Node.getNodeName");
    case ODP_MARK_NODE_TERM:
      THROW_ODPEXC("Invalid mark (MARK_NODE_TERM) in Node.getNodeName");
    case ODP_MARK_VALUE:
      THROW_ODPEXC("Invalid mark (MARK_VALUE) in Node.getNodeName");
    case ODP_MARK_UNSUPPORTED:
      THROW_ODPEXC("Invalid mark (MARK_UNSUPPORTED) in Node.getNodeName");
#endif      
    default:
      return "#text";            
  }
}

char *ODPNode::getNodeValue(){
//  printf("getNodeValue(%c), pos=%ld\n",poschar(),pos);
  if (pos==ODP_DOCUMENT_NODE){
    return NULL;
  }
  char *val;
  switch (poschar()){
    case ODP_MARK_NODE_BEGIN:
      return NULL;
    case ODP_MARK_ATTRIBUTE:
      val=doc->_simpleSearchAfter(pos,ODP_MARK_VALUE);
      if (val==NULL){
        THROW_ODPEXC("EOF while searching for attr. value "
	             "in Node.getNodeValue");
      }
      return val;
    case ODP_MARK_COMMENT:
      return &doc->text[pos+1];
    case ODP_MARK_CDATA:
      return &doc->text[pos+1];
    case ODP_MARK_PROCESSING:
      THROW_ODPEXC("Processing instructions not fully supported "
                   "in Node.getNodeValue");
#if CHECK>1		   
    case ODP_MARK_END:
      THROW_ODPEXC("Invalid mark (MARK_END) in Node.getNodeValue");
    case ODP_MARK_NODE_END:
      THROW_ODPEXC("Invalid mark (MARK_NODE_END) in Node.getNodeValue");
    case ODP_MARK_NODE_ENDTERM:
      THROW_ODPEXC("Invalid mark (MARK_NODE_ENDTERM) in Node.getNodeValue");
    case ODP_MARK_NODE_TERM:
      THROW_ODPEXC("Invalid mark (MARK_NODE_TERM) in Node.getNodeValue");
    case ODP_MARK_VALUE:
      THROW_ODPEXC("Invalid mark (MARK_VALUE) in Node.getNodeValue");
    case ODP_MARK_UNSUPPORTED:
      THROW_ODPEXC("Invalid mark (MARK_UNSUPPORTED) in Node.getNodeValue");
#endif      
    default:
      return &doc->text[pos];
  }
}

void ODPNode::setNodeValue(const char *v){
  NMAE("setting of Node.nodeValue not supported.");
}


unsigned short ODPNode:: getNodeType(){
//  printf("getNodeType(%c), pos=%ld\n",poschar(),pos);
  if (pos==ODP_DOCUMENT_NODE){
    return DOCUMENT_NODE;
  }
  switch (poschar()){
    case ODP_MARK_NODE_BEGIN:
      return ELEMENT_NODE;
    case ODP_MARK_ATTRIBUTE:
      return ATTRIBUTE_NODE;
    case ODP_MARK_COMMENT:
      return COMMENT_NODE;
    case ODP_MARK_CDATA:
      return CDATA_SECTION_NODE;
    case ODP_MARK_PROCESSING:
      return PROCESSING_INSTRUCTION_NODE;
#if CHECK>1      
    case ODP_MARK_END:
      THROW_ODPEXC("Invalid mark (MARK_END) in Node.getNodeType");
    case ODP_MARK_NODE_END:
      THROW_ODPEXC("Invalid mark (MARK_NODE_END) in Node.getNodeType");
    case ODP_MARK_NODE_ENDTERM:
      THROW_ODPEXC("Invalid mark (MARK_NODE_ENDTERM) in Node.getNodeType");
    case ODP_MARK_NODE_TERM:
      THROW_ODPEXC("Invalid mark (MARK_NODE_TERM) in Node.getNodeType");
    case ODP_MARK_VALUE:
      THROW_ODPEXC("Invalid mark (MARK_VALUE) in Node.getNodeType");
    case ODP_MARK_UNSUPPORTED:
      THROW_ODPEXC("Invalid mark (MARK_UNSUPPORTED) in Node.getNodeType");
#endif      
    default:
      return TEXT_NODE;
  }  
}

ODPNode *ODPNode::getParentNode(){
  ODPNode *node = new ODPNode(this);
  if (node->up()){
    return node;
  }
  else{
    delete node;
    return NULL;
  }
}

ODPNodeList *ODPNode::getChildNodes(){
  if (poschar()==ODP_MARK_NODE_BEGIN){
    return new ODPChildList(this);    
  }
  else{
    return new ODPNodeList();
  }  
}

ODPNode *ODPNode::getFirstChild(){
  ODPNode *node = new ODPNode(this);
  if (node->down()){
    return node;
  }
  else{
    delete node;
    return NULL;
  }  
}

ODPNode *ODPNode::getLastChild(){
  long last;
  ODPNode *node = new ODPNode(this);
  if (node->down()){
    last=node->pos;
    while (node->next()){
      last=node->pos;
    }
    node->pos=last;
    return node;
  }
  else{
    delete node;
    return NULL;
  }  
}

ODPNode *ODPNode::getPreviousSibling(){
  ODPNode *node = new ODPNode(this);
  if (node->previous()){
    return node;
  }
  else{
    delete node;
    return NULL;
  }  
}

ODPNode *ODPNode::getNextSibling(){
  ODPNode *node = new ODPNode(this);
  if (node->next()){
    return node;
  }
  else{
    delete node;
    return NULL;
  }  
}

ODPNamedNodeMap *ODPNode::getAttributes(){
  if (poschar()==ODP_MARK_NODE_BEGIN){
    return new ODPAttributeMap(this);    
  }
  else{
    return NULL;
  }
}

ODPDocument *ODPNode::getOwnerDocument(){
  return doc;
}

ODPNode *ODPNode::insertBefore(ODPNode *newChild, ODPNode *refChild){
  NMAE("in Node.insertBefore");
}

ODPNode *ODPNode::replaceChild(ODPNode *newChild, ODPNode *oldChild){
  NMAE("in Node.replaceChild");
}

ODPNode *ODPNode::removeChild(ODPNode *oldChild){
  NMAE("in Node.removeChild");
}

ODPNode *ODPNode::appendChild(ODPNode *newChild){
  NMAE("in Node.appendChild");
}

int ODPNode::hasChildNodes(){
  ODPNode node(this);
  return node.down();
}

ODPNode *ODPNode::cloneNode(int deep){
  THROW_DOMEXC(NOT_SUPPORTED_ERR,"Node.cloneNode is not supported.");
}

int ODPNode::nextBlock(){
  long len = doc->len;
  for (pos++; pos<len; pos++){
    switch (poschar()){
      case ODP_MARK_NODE_END:
      case ODP_MARK_NODE_ENDTERM:
      case ODP_MARK_END:
        break;
      
      case ODP_MARK_NODE_TERM:
        pos = ODP_INVALID_NODE;
        return 0;
      
      case ODP_MARK_NODE_BEGIN:
      case ODP_MARK_ATTRIBUTE:
      case ODP_MARK_CDATA:
      case ODP_MARK_COMMENT:      
      case ODP_MARK_PROCESSING:
        return 1;
      case ODP_MARK_VALUE:
      case ODP_MARK_UNSUPPORTED:
        for (pos++; poschar()!=ODP_MARK_END; pos++){
	  if (pos>=len){
	    pos = ODP_INVALID_NODE;
	    return 0;
	  }
	}
      default:
        return 1;
    }
  }
  pos = ODP_INVALID_NODE;
  return 0;
}

int ODPNode::up(){
  long level=0;
  
  for (pos--;pos>=0;pos--){
    switch (poschar()){
      case ODP_MARK_NODE_BEGIN:
        if (level==0){
	  return 1;
	}
	level++;
	break;
      case ODP_MARK_NODE_TERM:
      case ODP_MARK_NODE_ENDTERM:
        level--;
	break;
    }
  }
  pos=ODP_DOCUMENT_NODE;
  return 1;
}

int ODPNode::down(){
  long len = doc->len;
  switch(poschar()){
    case ODP_MARK_NODE_BEGIN:
      for (pos++; pos<len; pos++){
	switch (poschar()){
	  case ODP_MARK_NODE_END:
	    return nextBlock();
	  case ODP_MARK_NODE_ENDTERM:
	    pos = ODP_INVALID_NODE;
	    return 0;
	  case ODP_MARK_ATTRIBUTE:
	    return 1;
#if CHECK>1
	  case ODP_MARK_NODE_BEGIN:
	    THROW_ODPEXC("Invalid mark (MARK_NODE_BEGIN) in Node.down() (b)");
	  case ODP_MARK_NODE_TERM:
	    THROW_ODPEXC("Invalid mark (MARK_NODE_TERM) in Node.down() (b)");
	  case ODP_MARK_UNSUPPORTED:
	    THROW_ODPEXC("Invalid mark (MARK_UNSUPPORTED) in Node.down() (b)");
	  case ODP_MARK_COMMENT:
	    THROW_ODPEXC("Invalid mark (MARK_COMMENT) in Node.down() (b)");
	  case ODP_MARK_CDATA:
	    THROW_ODPEXC("Invalid mark (MARK_CDATA) in Node.down() (b)");
	  case ODP_MARK_PROCESSING:
	    THROW_ODPEXC("Invalid mark (MARK_PROCESSING) in Node.down() (b)");
#endif      
	  case ODP_MARK_END:
	  case ODP_MARK_VALUE:
	  default:
	    break;
	}        
      }
      pos = ODP_INVALID_NODE;
      return 0;
#if CHECK>1
    case ODP_MARK_END:
      THROW_ODPEXC("Invalid mark (MARK_END) in Node.down() (a)");
    case ODP_MARK_NODE_END:
      THROW_ODPEXC("Invalid mark (MARK_NODE_END) in Node.down() (a)");
    case ODP_MARK_NODE_ENDTERM:
      THROW_ODPEXC("Invalid mark (MARK_NODE_ENDTERM) in Node.down() (a)");
    case ODP_MARK_NODE_TERM:
      THROW_ODPEXC("Invalid mark (MARK_NODE_TERM) in Node.down() (a)");
    case ODP_MARK_VALUE:
      THROW_ODPEXC("Invalid mark (MARK_VALUE) in Node.down() (a)");
    case ODP_MARK_UNSUPPORTED:
      THROW_ODPEXC("Invalid mark (MARK_UNSUPPORTED) in Node.down() (a)");
#endif
    default:
      pos = ODP_INVALID_NODE;
      return 0;
  }
}

int ODPNode::next(){
  long len = doc->len;
  long level;
 
  switch (poschar()){

    case ODP_MARK_NODE_BEGIN:
      for (pos++; pos<len; pos++){
        switch (poschar()){
	  case ODP_MARK_NODE_END:
	    level=0;
	    for (pos++; pos<len; pos++){
              switch (poschar()){
		case ODP_MARK_NODE_BEGIN:
		  level++;
		  break;
		case ODP_MARK_NODE_TERM:
		  for (pos++; pos<len; pos++){
		    if (poschar() == ODP_MARK_END){
        	      if (level==0){
                	return nextBlock();
		      }
		      break;		      
		    }
		  }
		  if (pos>=len){
		    pos=ODP_INVALID_NODE;
		    return 0;
		  }
        	  level--;
		  break;
		case ODP_MARK_NODE_ENDTERM:
        	  if (level==0){
		    for (pos++; pos<len; pos++){
		      if (poschar() == ODP_MARK_END){
		        return nextBlock();
		      }
		    }
		    pos = ODP_INVALID_NODE;
		    return 0;
		  }
        	  level--;
		  break;
	      }	      
	    }
	    pos = ODP_INVALID_NODE;
	    return 0;
	  case ODP_MARK_NODE_ENDTERM:
	    return nextBlock();
#if CHECK>1	
	  case ODP_MARK_NODE_TERM:
            THROW_ODPEXC("Invalid mark (MARK_NODE_TERM) in Node.next()");
          case ODP_MARK_NODE_BEGIN:
            THROW_ODPEXC("Invalid mark (MARK_NODE_BEGIN) in Node.next()");
	  case ODP_MARK_UNSUPPORTED:
            THROW_ODPEXC("Invalid mark (MARK_UNSUPPORTED) in Node.next()");
	  case ODP_MARK_CDATA:
            THROW_ODPEXC("Invalid mark (MARK_CDATA) in Node.next()");
	  case ODP_MARK_COMMENT:      
            THROW_ODPEXC("Invalid mark (MARK_COMMENT) in Node.next()");
	  case ODP_MARK_PROCESSING:
            THROW_ODPEXC("Invalid mark (MARK_PROCESSING) in Node.next()");
#endif	    
	}
      }
    case ODP_MARK_ATTRIBUTE:
      for (pos++; pos<len; pos++){
        switch (poschar()){
	  case ODP_MARK_ATTRIBUTE:
	    return 1;
	  case ODP_MARK_NODE_END:
	    return nextBlock();
	  case ODP_MARK_NODE_ENDTERM:
	    pos = ODP_INVALID_NODE;
	    return 0;	      
#if CHECK>1
	  case ODP_MARK_NODE_TERM:
            THROW_ODPEXC("Invalid mark (MARK_NODE_TERM) in Node.next()");
          case ODP_MARK_NODE_BEGIN:
            THROW_ODPEXC("Invalid mark (MARK_NODE_BEGIN) in Node.next()");
	  case ODP_MARK_UNSUPPORTED:
            THROW_ODPEXC("Invalid mark (MARK_UNSUPPORTED) in Node.next()");
	  case ODP_MARK_CDATA:
            THROW_ODPEXC("Invalid mark (MARK_CDATA) in Node.next()");
	  case ODP_MARK_COMMENT:      
            THROW_ODPEXC("Invalid mark (MARK_COMMENT) in Node.next()");
	  case ODP_MARK_PROCESSING:
            THROW_ODPEXC("Invalid mark (MARK_PROCESSING) in Node.next()");
#endif	    
	}
      }
      pos = ODP_INVALID_NODE;
      return 0;	      

#if CHECK>1    
    case ODP_MARK_VALUE:
      THROW_ODPEXC("Invalid mark (MARK_VALUE) in Node.next()");
    case ODP_MARK_NODE_END:
      THROW_ODPEXC("Invalid mark (MARK_NODE_END) in Node.next()");
    case ODP_MARK_NODE_ENDTERM:
      THROW_ODPEXC("Invalid mark (MARK_NODE_ENDTERM) in Node.next()");
    case ODP_MARK_NODE_TERM:
      THROW_ODPEXC("Invalid mark (MARK_NODE_TERM) in Node.next()");
    case ODP_MARK_END:
      THROW_ODPEXC("Invalid mark (MARK_END) in Node.next()");
#endif

    case ODP_MARK_UNSUPPORTED:
    case ODP_MARK_CDATA:
    case ODP_MARK_COMMENT:      
    case ODP_MARK_PROCESSING:
    default:
      for (pos++; pos<len; pos++){
        switch (poschar()){
	  case ODP_MARK_NODE_BEGIN:
	  case ODP_MARK_CDATA:
	  case ODP_MARK_COMMENT:
	  case ODP_MARK_PROCESSING:
	    return 1;
	  case ODP_MARK_END:  
            return nextBlock();	
	}
      }
      pos = ODP_INVALID_NODE; 
      return 0;
  }
}

int ODPNode::previous(){
  if (poschar() == ODP_MARK_ATTRIBUTE){
    for (pos--; pos>=0; pos--){
      switch (poschar()){
        case ODP_MARK_ATTRIBUTE:      
          return 1;
	case ODP_MARK_NODE_BEGIN:
	  pos = ODP_INVALID_NODE;
	  return 0;
      }
    }
    pos = ODP_INVALID_NODE;
    return 0;
  }
  else{
    char c;
    long level;
    do{
      pos--;
      if (pos<0){
        pos = ODP_INVALID_NODE;
	return 0;
      }
      c=poschar();
    }
    while ( (c==ODP_MARK_END) || (c==ODP_MARK_UNSUPPORTED) );
    
    switch (c){
      case ODP_MARK_CDATA:
      case ODP_MARK_COMMENT:      
      case ODP_MARK_PROCESSING:    
	return 1;

      case ODP_MARK_NODE_ENDTERM:
        for (pos--; pos>=0; pos--){
	  if (poschar()==ODP_MARK_NODE_BEGIN){
	    return 1;
	  }
	}
	pos = ODP_INVALID_NODE;
	return 0;
      case ODP_MARK_NODE_END:
	for (pos--; pos>=0; pos--){
	  switch (poschar()){
            case ODP_MARK_ATTRIBUTE:
	      return 1;
	    case ODP_MARK_NODE_BEGIN:
	      pos = ODP_INVALID_NODE;
	      return 0;		    
	  }
	}
        pos = ODP_INVALID_NODE;
	return 0;
      case ODP_MARK_NODE_TERM:
	level=0;
	for (pos--; pos>=0; pos--){
          switch (poschar()){
	    case ODP_MARK_NODE_BEGIN:
              if (level==0){
		return 1;
	      }
	      level++;
	      break;
	    case ODP_MARK_NODE_TERM:
	    case ODP_MARK_NODE_ENDTERM:
	      level--;
	      break;
	  }	      
	}
	pos = ODP_INVALID_NODE;
	return 0;
      
#if CHECK>1
      case ODP_MARK_ATTRIBUTE:
        THROW_ODPEXC("Invalid mark (MARK_ATTRIBUTE) in Node.previous()");
      case ODP_MARK_VALUE:
        THROW_ODPEXC("Invalid mark (MARK_VALUE) in Node.previous()");
      case ODP_MARK_NODE_BEGIN:
        THROW_ODPEXC("Invalid mark (MARK_NODE_BEGIN) in Node.previous()");	
#endif      
      default:
        for (pos--; pos>=0; pos--){
          switch (poschar()){
	    case ODP_MARK_CDATA:
	    case ODP_MARK_COMMENT:      
	    case ODP_MARK_PROCESSING:
	      return 1;
	    case ODP_MARK_END:
	    case ODP_MARK_NODE_END:
	    case ODP_MARK_NODE_ENDTERM:
	      return nextBlock();
	    case ODP_MARK_NODE_TERM:
	      level=0;
	      for (pos--; pos>=0; pos--){
        	switch (poschar()){
		  case ODP_MARK_NODE_BEGIN:
        	    if (level==0){
		      return 1;
		    }
		    level++;
		    break;
		  case ODP_MARK_NODE_TERM:
		  case ODP_MARK_NODE_ENDTERM:
		    level--;
		    break;
		}	      
	      }
	      pos = ODP_INVALID_NODE;
	      return 0;
	    
	  }
	}
	pos = ODP_INVALID_NODE;
	return 0;
    }
  }
}


