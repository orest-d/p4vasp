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
 
#ifndef ODP_string_h
#define ODP_string_h
#include "mark.h"

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


long ODP_strlen(const char *s);
char *ODP_strdup(const char *s);
char *ODP_clone(const char *s);
char *ODP_strclone(const char *s);
long ODP_wordlen(const char *s);
char *ODP_worddup(const char *s);
char *ODP_wordclone(const char *s);
char *ODP_strcpy(char *dest,const char *src);
char *ODP_strncpy(char *dest,const char *src, long n);
int ODP_strcmp(const char *s1,const char *s2);
int ODP_strncmp(const char *s1,const char *s2,long n);
int ODP_strcasecmp(const char *s1,const char *s2);
int ODP_strncasecmp(const char *s1,const char *s2,long n);

#endif
