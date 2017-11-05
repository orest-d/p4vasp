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
#include <ctype.h>
#include <stdlib.h>
#include <ODP/mark.h>
#include <ODP/Exceptions.h>

inline int ODP_isterm(int c){
#if ODP_MARK_END=='\0'
  return ((c == ODP_MARK_END         ) ||
	  (c == ODP_MARK_NODE_END    ) ||
	  (c == ODP_MARK_NODE_ENDTERM) ||
	  (c == ODP_MARK_ATTRIBUTE   ) ||
	  (c == ODP_MARK_NODE_BEGIN  ) ||
	  (c == ODP_MARK_VALUE       ) ||
	  (c == ODP_MARK_PROCESSING  ) ||
	  (c == ODP_MARK_UNSUPPORTED ) ||
	  (c == ODP_MARK_NODE_TERM   ) ||
	  (c == ODP_MARK_CDATA       ) ||
	  (c == ODP_MARK_COMMENT     ));  
#else
  return ((c == '\0'                 ) ||
          (c == ODP_MARK_END         ) ||
	  (c == ODP_MARK_NODE_END    ) ||
	  (c == ODP_MARK_NODE_ENDTERM) ||
	  (c == ODP_MARK_ATTRIBUTE   ) ||
	  (c == ODP_MARK_NODE_BEGIN  ) ||
	  (c == ODP_MARK_VALUE       ) ||
	  (c == ODP_MARK_PROCESSING  ) ||
	  (c == ODP_MARK_UNSUPPORTED ) ||
	  (c == ODP_MARK_NODE_TERM   ) ||
	  (c == ODP_MARK_CDATA       ) ||
	  (c == ODP_MARK_COMMENT     ));  
#endif	  
}

long ODP_strlen(const char *s){
  long l=0;
  for (; !ODP_isterm(s[l]); l++)
    {;}
  return l;
}

long ODP_wordlen(const char *s){
  long l=0;
  for (; !(ODP_isterm(s[l]) || isspace(s[l])); l++)
    {;}
  return l;
}

char *ODP_clone(const char *s){
  long l=strlen(s);
  char *d = new char[l+1];
#if CHECK>0
  if (s==NULL){
    THROW_ODPEXC("Can't clone(NULL) string.");
  }
#endif

#if VERBOSE>3
  printf("string clone('%s');\n",s);
#endif
  memcpy(d,s,l+1);
  return d;
}

char *ODP_strdup(const char *s){
#if CHECK>0
  if (s==NULL){
    THROW_ODPEXC("Can't strdup(NULL) string.");
  }
#endif
  long l=ODP_strlen(s);
  char *ns= (char *)malloc(l+1);
  if (ns!=NULL){
    memcpy(ns,s,l);
    ns[l]='\0';
  }
  return ns;
}

char *ODP_strclone(const char *s){
  if (s==NULL){
    return NULL;
  }
/*
#if CHECK>0
  if (s==NULL){
    THROW_ODPEXC("Can't strclone(NULL) string.");
  }
#endif
*/
  long l=ODP_strlen(s);
  char *ns=new char[l+1];
  if (ns!=NULL){
    memcpy(ns,s,l);
    ns[l]='\0';
  }
  return ns;
}

char *ODP_worddup(const char *s){
#if CHECK>0
  if (s==NULL){
    THROW_ODPEXC("Can't worddup(NULL) string.");
  }
#endif
  long l=ODP_wordlen(s);
  char *ns= (char *)malloc(l+1);
  if (ns!=NULL){
    memcpy(ns,s,l);
    ns[l]='\0';
  }
  return ns;
}

char *ODP_wordclone(const char *s){
#if CHECK>0
  if (s==NULL){
    THROW_ODPEXC("Can't wordclone(NULL) string.");
  }
#endif
  long l=ODP_wordlen(s);
  char *ns=new char[l+1];
  if (ns!=NULL){
    memcpy(ns,s,l);
    ns[l]='\0';
  }
  return ns;
}

char *ODP_strcpy(char *dest,const char *src){
  char *d=dest;
  char *s=(char *)src;
  while (!ODP_isterm(*s)){
    *d=*s;
    d++;
    s++;    
  }
  *d='\0';
  return dest;
}

char *ODP_strncpy(char *dest,const char *src,long n){
  char *d=dest;
  char *s=(char *)src;
  for (long i=0; (i<n) && (!ODP_isterm(*s)); i++){
    *d=*s;
    d++;
    s++;    
  }
  *d='\0';
  return dest;
}

int ODP_strcmp(const char *s1,const char *s2){
  char *a = (char *)s1;
  char *b = (char *)s2;
  while ( (!ODP_isterm(*a)) && (!ODP_isterm(*b)) ){
    if (*a!=*b){
      if (*a<*b){
        return -1;
      }
      else{
        return 1;
      }	
    }
    a++;
    b++;
  }
  if (ODP_isterm(*a)){
    if (ODP_isterm(*b)){
      return 0;
    }
    else{
      return -1;
    }
  }
  else{
    return 1;
  }
}

int ODP_strncmp(const char *s1,const char *s2,long n){
  char *a = (char *)s1;
  char *b = (char *)s2;
  
  for (long i=0; i<n; i++){
    if (ODP_isterm(*a)){
      if (ODP_isterm(*b)){
	return 0;
      }
      else{
	return -1;
      }
    }
    else if (ODP_isterm(*b)){
      return 1;
    }
    if (*a!=*b){
      if (*a<*b){
        return -1;
      }
      else{
        return 1;
      }	
    }
    a++;
    b++;
  }
  return 0;
}

int ODP_strcasecmp(const char *s1,const char *s2){
  char *a = (char *)s1;
  char *b = (char *)s2;
  while ( (!ODP_isterm(*a)) && (!ODP_isterm(*b)) ){
    char A=toupper(*a);
    char B=toupper(*b);
    if (A!=B){
      if (A<B){
        return -1;
      }
      else{
        return 1;
      }	
    }
    a++;
    b++;
  }
  if (ODP_isterm(*a)){
    if (ODP_isterm(*b)){
      return 0;
    }
    else{
      return -1;
    }
  }
  else{
    return 1;
  }
}

int ODP_strncasecmp(const char *s1,const char *s2,long n){
  char *a = (char *)s1;
  char *b = (char *)s2;
  
  for (long i=0; i<n; i++){
    if (ODP_isterm(*a)){
      if (ODP_isterm(*b)){
	return 0;
      }
      else{
	return -1;
      }
    }
    else if (ODP_isterm(*b)){
      return 1;
    }
    char A=toupper(*a);
    char B=toupper(*b);
    if (A!=B){
      if (A<B){
        return -1;
      }
      else{
        return 1;
      }	
    }
    a++;
    b++;
  }
  return 0;
}
