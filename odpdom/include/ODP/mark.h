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
 
#ifndef ODPmark_h
#define ODPmark_h

#define ODP_DOCUMENT_NODE        -10
#define ODP_INVALID_NODE         -1

#define ODP_MARK_END              '\000'
#define ODP_MARK_NODE_BEGIN       '\001'
#define ODP_MARK_NODE_END         '\002'
#define ODP_MARK_NODE_ENDTERM     '\003'
#define ODP_MARK_NODE_TERM        '\004'
#define ODP_MARK_ATTRIBUTE        '\005'
#define ODP_MARK_VALUE            '\006'
#define ODP_MARK_COMMENT          '\020'
#define ODP_MARK_CDATA            '\021' 
#define ODP_MARK_PROCESSING       '\022' 
#define ODP_MARK_UNSUPPORTED      '\023'

#endif
