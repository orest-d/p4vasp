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
#include <errno.h>
#include <string.h>
#include <ODP/Exceptions.h>
#include <ODP/string.h>
#include <ODP/markText.h>
#include <ODP/Document.h>

ODPDocument *ODP_parseStringDestructively(char *s){
  long l = strlen(s);
  ODP_markText(s,l);
  return new ODPDocument(s,l);
}

ODPDocumentParent *ODP_parseString(const char *src){
  char *s = ODP_clone(src);
  long l  = strlen(s);
  ODP_markText(s,l);
  return new ODPDocumentParent(s,l);
}

ODPDocumentParent *ODP_parseFile(FILE *f){
  char buff[256];
  long startpos=ftell(f);
#if CHECK>0
  if (startpos==-1){
    snprintf(buff,250,"ftell() failed in parseFile() (a)\n%s",strerror(errno));
    buff[251]='\0';
    THROW_ODPEXC(buff);
  }
#endif
  if ((fseek(f,0L,SEEK_END))==-1){
#if CHECK>0  
    snprintf(buff,250,"fseek() failed in parseFile() (a)\n%s",strerror(errno));
    buff[251]='\0';
    THROW_ODPEXC(buff);  
#endif    
  }
  long endpos=ftell(f);
#if CHECK>0
  if (endpos==-1){
    snprintf(buff,250,"ftell() failed in parseFile() (b)\n%s",strerror(errno));
    buff[251]='\0';
    THROW_ODPEXC(buff);
  }
#endif
  long l=endpos-startpos;
  if ((fseek(f,startpos,SEEK_SET))==-1){
#if CHECK>0  
    snprintf(buff,250,"fseek(%ld) failed in parseFile() (b)\n%s",startpos,strerror(errno));
    buff[251]='\0';
    THROW_ODPEXC(buff);  
#endif    
  }
  char *txt = new char[l+1];
#if CHECK>0
  if (txt==NULL){
    THROW_ODPEXC("Buffer allocation failed in parseFile()");
  }
#endif
  long rl = fread(txt,1,l,f);
#if CHECK>0
  if (rl!=l){
    snprintf(buff,250,"fread() failed in parseFile()\n%s",strerror(errno));
    buff[251]='\0';
    THROW_ODPEXC(buff);
  }
#endif
  txt[l]='\0';
  ODP_markText(txt,l);
  return new ODPDocumentParent(txt,l);  
}

ODPDocumentParent *ODP_parseFile(FILE *f,long len){
  char buff[256];
  long startpos=ftell(f);
#if CHECK>0
  if (startpos==-1){
    snprintf(buff,250,"ftell() failed in parseFile() (a)\n%s",strerror(errno));
    buff[251]='\0';
    THROW_ODPEXC(buff);
  }
#endif
  if ((fseek(f,0L,SEEK_END))==-1){
#if CHECK>0  
    snprintf(buff,250,"fseek() failed in parseFile() (a)\n%s",strerror(errno));
    buff[251]='\0';
    THROW_ODPEXC(buff);  
#endif    
  }
  long endpos=ftell(f);
#if CHECK>0
  if (endpos==-1){
    snprintf(buff,250,"ftell() failed in parseFile() (b)\n%s",strerror(errno));
    buff[251]='\0';
    THROW_ODPEXC(buff);
  }
#endif
  long l=endpos-startpos;
  if (len<l){
    l=len;
  }
  if ((fseek(f,startpos,SEEK_SET))==-1){
#if CHECK>0  
    snprintf(buff,250,"fseek(%ld) failed in parseFile() (b)\n%s",startpos,strerror(errno));
    buff[251]='\0';
    THROW_ODPEXC(buff);  
#endif    
  }
  char *txt = new char[l+1];
#if CHECK>0
  if (txt==NULL){
    THROW_ODPEXC("Buffer allocation failed in parseFile()");
  }
#endif
  long rl = fread(txt,1,l,f);
#if CHECK>0
  if (rl!=l){
    snprintf(buff,250,"fread() failed in parseFile()\n%s",strerror(errno));
    buff[251]='\0';
    THROW_ODPEXC(buff);
  }
#endif
  txt[l]='\0';
  ODP_markText(txt,l);
  return new ODPDocumentParent(txt,l);  
}


ODPDocumentParent *ODP_parseFile(const char *path){
  char buff[256];
  FILE *f = fopen(path,"r");
#if CHECK>0
  if (f==NULL){
    snprintf(buff,250,"fopen() failed in parseFile(%s)\n%s",path,strerror(errno));
    buff[251]='\0';
    THROW_ODPEXC(buff);
  }
#endif

  if ((fseek(f,0L,SEEK_END))==-1){
#if CHECK>0  
    snprintf(buff,250,"fseek() failed in parseFile(%s)\n%s",path,strerror(errno));
    buff[251]='\0';
    THROW_ODPEXC(buff);  
#endif    
  }
  long l=ftell(f);
#if CHECK>0
  if (l==-1){
    snprintf(buff,250,"ftell() failed in parseFile(%s)\n%s",path,strerror(errno));
    buff[251]='\0';
    THROW_ODPEXC(buff);
  }
#endif
  rewind(f);
  char *txt = new char[l+1];
#if CHECK>0
  if (txt==NULL){
    snprintf(buff,250,"Buffer allocation failed in parseFile(%s);"
                      " requested size was %ld",path,l+1);
    buff[251]='\0';		      
    THROW_ODPEXC(buff);
  }
#endif
  long rl = fread(txt,1,l,f);
#if CHECK>0
  if (rl!=l){
    snprintf(buff,250,"fread() failed in parseFile(%s)\n%s",path,strerror(errno));
    buff[251]='\0';
    THROW_ODPEXC(buff);
  }
#endif
  int rclose=fclose(f);
#if CHECK>0
  if (rclose){
    snprintf(buff,250,"fclose() failed in parseFile(%s)\n%s",path,strerror(errno));
    buff[251]='\0';
    THROW_ODPEXC(buff);
  }
#endif
  txt[l]='\0';
  ODP_markText(txt,l);
  return new ODPDocumentParent(txt,l);  
}

