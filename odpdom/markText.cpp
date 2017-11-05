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
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include <ODP/mark.h>

inline int ODP_markChar(char **ptr, long &pos, long len,char to,char mark=ODP_MARK_END){
  while (pos<len){
    if ((**ptr)==to){
      **ptr=mark;
      (*ptr)++;
      pos++;
      return 0;
    }  
    (*ptr)++;
    pos++;
  }
  return -1;
}   

inline int ODP_markQuote(char **ptr, long &pos, long len,char mark=ODP_MARK_END){
  while (pos<len){
    if ( ((**ptr)=='\"') || ((**ptr)=='\'') ){
      **ptr=mark;
      (*ptr)++;
      pos++;
      return 0;
    }  
    (*ptr)++;
    pos++;
  }
  return -1;
}   

inline int ODP_markChars2(char **ptr, long &pos, long len,char *to,char mark=ODP_MARK_END){
  long l=len-1;
  while (pos<l){
    if (((*ptr)[0]==to[0]) && ((*ptr)[1]==to[1])){
      (*ptr)[0]=mark;
      (*ptr)[1]=mark;
      (*ptr)+=2;
      pos+=2;
      return 0;
    }  
    (*ptr)++;
    pos++;
  }
  return -1;
}   

inline int ODP_markChars3(char **ptr, long &pos, long len,char *to,char mark=ODP_MARK_END){
  long l=len-2;
  while (pos<l){
    if (((*ptr)[0]==to[0]) && ((*ptr)[1]==to[1]) && ((*ptr)[2]==to[2])){
      (*ptr)[0]=mark;
      (*ptr)[1]=mark;
      (*ptr)[2]=mark;
      (*ptr)+=3;
      pos+=3;
      return 0;
    }  
    (*ptr)++;
    pos++;
  }
  return -1;
}   


int ODP_markNameEnd(char **ptr, long &pos, long len){
  while (pos<len){
    char c=**ptr;
    if (isalnum(c) || (c=='.') || (c=='-') || (c=='_') || (c==':')){
      pos++;
      (*ptr)++;
    }
    else{
      (**ptr)=ODP_MARK_END;
      return c;
    }  
  }
  return -1;
}

int ODP_markText(char *text,long len){
  long pos=0;
  char *ptr = text;
  int c;
  long l=len-1;
  while (pos<l){
    if (*ptr == '<'){
      *ptr=ODP_MARK_END;
      ptr++;
      pos++;
      c=*ptr;
      switch (c){
        case '?':
	  *ptr=ODP_MARK_PROCESSING;
	  if (pos>=l) return -1;
	  ptr++;
	  pos++;	  
	  if (ODP_markChars2(&ptr,pos,len,"?>")){
	    return -1;
	  }
	  break;
	case '/':
	  *ptr=ODP_MARK_NODE_TERM;
	  if (pos>=l) return -1;
	  ptr++;
	  pos++;	  
	  switch (ODP_markNameEnd(&ptr,pos,len)){
	    case '>':
	      break;
	    case -1:
	      return -1;
	    default:    
	      while (1){
	        if (pos<len){
	          if ( (*ptr) == '>' ){
	            *ptr=ODP_MARK_END;
                    ptr++;
                    pos++;
		    break;
		  }	      
	          *ptr=ODP_MARK_END;
                  ptr++;
                  pos++;
		}
		else{
		  return -1;
		}	  
	      }
          }
	  break;
	case '!':{
	  char *unsupptr=ptr;	  
	  *ptr=ODP_MARK_END;
	  if (pos>=l) return -1;
    	  ptr++;
	  pos++;
	  if ( (pos+1) < l){
	    if ( (ptr[0]=='-') && (ptr[1]=='-') ){
	      ptr[0]=ODP_MARK_END;
	      ptr[1]=ODP_MARK_COMMENT;
	      ptr+=2;
	      pos+=2;
	      if (ODP_markChars3(&ptr,pos,len,"-->")){
	        return -1;
	      }
	      unsupptr=NULL;
	    }
	    else if ((pos+6)<l){
	      if ( (ptr[0]=='[') && 
	           (ptr[1]=='C') &&
	           (ptr[2]=='D') &&
	           (ptr[3]=='A') &&
	           (ptr[4]=='T') &&
	           (ptr[5]=='A') &&
	           (ptr[6]=='[')
		 ){
		ptr[0]=ODP_MARK_END;
		ptr[1]=ODP_MARK_END;
		ptr[2]=ODP_MARK_END;
		ptr[3]=ODP_MARK_END;
		ptr[4]=ODP_MARK_END;
		ptr[5]=ODP_MARK_END;
		ptr[6]=ODP_MARK_CDATA;
		ptr+=7;
		pos+=7;
		if (ODP_markChars3(&ptr,pos,len,"]]>")){
	          return -1;
		}
                unsupptr=NULL;
	      }
	    }
	  }
	  if (unsupptr!=NULL){
	    *unsupptr=ODP_MARK_UNSUPPORTED;
	    if (ODP_markChar(&ptr,pos,len,'>')){
	      return -1;
	    }	    
	  }
	  break;
	}
	default:
	  ptr[-1]=ODP_MARK_NODE_BEGIN;
//	  printf("Node begin <%s\n",ptr);
	  c=ODP_markNameEnd(&ptr,pos,len);
//	  printf("Tag term '%c' pos:%2ld %s\n",c,pos,ptr);
	  if (c==-1) return -1;
	  if (c=='>'){
	    *ptr=ODP_MARK_NODE_END;
	  }
	  else if (c=='/'){
	    ptr++;
	    pos++;
	    if (pos>=len) return -1;
	    if (*ptr =='>'){
	      *ptr=ODP_MARK_NODE_ENDTERM;
	      ptr++;
	      pos++;
	    }
	    else{
	      return -1;
	    }
	  }
	  else{
	    pos++;
	    ptr++;
	    while (pos<l){
	      if (*ptr == '>'){
		*ptr=ODP_MARK_NODE_END;
		ptr++;
		pos++;
		break;
	      }
	      else if (*ptr == '/'){
		*ptr=ODP_MARK_END;
		ptr++;
		pos++;
		if (pos>=len) return -1;
		if (*ptr =='>'){
	          *ptr=ODP_MARK_NODE_ENDTERM;
		  ptr++;
		  pos++;
		  break;
		}
	      }
	      if (isalpha(ptr[0])){
		ptr[-1]=ODP_MARK_ATTRIBUTE;
        	if (ODP_markNameEnd(&ptr,pos,len)==-1)      return -1;
		if (ODP_markQuote(&ptr,pos,len,ODP_MARK_VALUE)) return -1;
		if (ODP_markQuote(&ptr,pos,len,ODP_MARK_END))   return -1;
	      }
	      else{
		*ptr=ODP_MARK_END;
		ptr++;
		pos++;
	      }
	    }
	  }
      }
    }
    else{
      ptr++;
      pos++;	  
    }
  }
  return 0;
}
