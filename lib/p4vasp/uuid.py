"""handling RFC 4122 compatible UUIDs"""

"""Copyright (c) 2006 Juergen Urner

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to
do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

__version__ = "0.3.2"

import calendar as _calendar
import md5 as _md5
import random as _random
import re as _re
import sha as _sha
import sys as _sys
import time as _time
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

VARIANT_UNKNOWN =  0    # unknown variant
VARIANT_NCS          =    1     # reserved for NCS backward compatibility
VARIANT_RFC4122  =    2 # RFC4122 compatible (produced by this module)
VARIANT_MS            =    3    # Reserved for Microsoft backward compatibility
VARIANT_FUTURE    =    4        # Reserved for future definition


VERSION_UNKNOWN  = 0    # unknown version
VERSION_TIME            = 1     # time based UUID
VERSION_DCE             = 2     # DCE Security version
VERSION_MD5            = 3      # name based UUID with MD5 hashing
VERSION_RANDOM     = 4  # randomly generated UUID
VERSION_SHA1           = 5      # name based UUID with SHA1 hashing


NAMESPACE_DNS = '{6ba7b810-9dad-11d1-80b4-00c04fd430c8}'        # DNS namespace UUID
NAMESPACE_URL = '{6ba7b811-9dad-11d1-80b4-00c04fd430c8}'                # URL namespace UUID
NAMESPACE_OID = '{6ba7b812-9dad-11d1-80b4-00c04fd430c8}'                # OID namespace UUID
NAMESPACE_X500 = '{6ba7b814-9dad-11d1-80b4-00c04fd430c8}'       # X500 namespace UUID

UUID_NIL = '{00000000-0000-0000-0000-000000000000}'                             # UUID NULL


# TODO: the thrown in getrandbits() replacement may not work as expected
# check if getrandbits is available (requires python 2.4)
try:
    _getrandbits = _random.getrandbits
except:
    def _getrandbits(num_bits):     # took this from: http://www.zopelabs.com/cookbook/1067449107
        rnd = _random.Random()
        bytes = 0L
        for i in range(0, num_bits):
            bytes += long(rnd.randint(0,1)) << i
        return bytes


# throw replacement in for socket.htonl and friends (enshures? we always get a ulong in return)
def _DWORD(num): return num & 0xFFFFFFFFL
def _WORD(num): return num & 0xFFFF

if _sys.byteorder == 'big':
    def _htonl(dw): return _DWORD(dw)
    def _htons(w): return _WORD(w)
else:
    def _htons(w):
        w = _WORD(w)
        return ((w & 0xff00) >> 8) | ((w & 0x00ff) << 8)
    def _htonl(dw):
        dw = _DWORD(dw)
        return ((dw & 0xff000000L) >> 24) | \
                                ((dw & 0x00ff0000L) >> 8)  |    \
                                ((dw & 0x0000ff00L) << 8)  |    \
                                ((dw & 0x000000ffL) << 24)
_ntohs = _htons
_ntohl = _htonl


class UuidError(Exception):
    """default error"""


class _GeneratorState(object):

    CLOCK_SEQ_MAX = 0x3FFF

    # TODO: how to calculate time resolution ?
    # holds the number of 100ns ticks of the actual resolution of the system's clock
    # the current implementation just limits the number or UUIDs generated/tick to 10.000,
    # no matter what tick is
    UUIDS_PER_TICK = 10000

    # time delta in 100ns steps from system epoch to uuid epoch (00:00:00.00, 15 October 1582)
    # calculate delta of the actual epoch relative to UNIX_EPOCH
    GM_UNIX_EPOCH = (1970, 1, 1, 0, 0, 0, 3, 1, 0)
    UNIX_EPOCH = _calendar.timegm(GM_UNIX_EPOCH) * 10000000
    UNIX_OFFSET = 0x01b21dd213814000                # offset in nanoseconds to uuid epoch
    TDELTA = UNIX_OFFSET - UNIX_EPOCH

    def __init__(self):
        self.is_inited = False
        self.time_last = 0
        self.clock_seq = 0
        self.uuids_per_tick = 0

    def load(self):
        """supposed to read state from storage"""
        #try:
        #       read state from storage
        #       self.is_inited = True
        #except:
        #       self.clock_seq = _getrandbits(14)
        #       self.is_inited = False
        self.clock_seq = _getrandbits(14)

    def dump(self):
        """supposed to dump state to storage"""


####################
#                                               #
# uuid generator                     #
#                                               #
####################

class UuidGen(object):


    def __init__(self):

        self._state = _GeneratorState()


        # public methods -----------------------------------------------------------

    def uuid_time(self):
        time_now = self._get_time_now()
        clock_seq = self._state.clock_seq

        time_low = time_now & 0xFFFFFFFFL
        time_mid = (time_now >> 32) & 0xFFFF
        time_hi_and_version = (time_now>> 48)   & 0x0FFFF
        node = _getrandbits(47)                                         # throw in random bits instead of MAC address
        node |= (1 << 47)                                                               # set unicast/multicast bit

        # put in variant and version bits
        time_hi_and_version |= (1 << 12)
        clock_seq_low = clock_seq &     0xFF
        clock_seq_hi_and_reserved = (clock_seq & 0x3F00) >> 8
        clock_seq_hi_and_reserved |= 0x80

        return self._format(time_low, time_mid, time_hi_and_version,
                                                                        clock_seq_hi_and_reserved, clock_seq_low, node)


    def uuid_random(self):
        rnd = _getrandbits(128)
        time_low = rnd & 0xFFFFFFFFL
        time_mid = (rnd >> 32) & 0x0FFFF
        time_hi_and_version = (rnd >> 48) & 0x0FFFF
        clock_seq_hi_and_reserved = (rnd >> 64) & 0x0FF
        clock_seq_low= (rnd >> 72) & 0x0FF
        node = (rnd >> 80)

        # put in variant and version bits
        time_hi_and_version &= 0x0FFF;
        time_hi_and_version |= (4 << 12)
        clock_seq_hi_and_reserved &= 0x3F
        clock_seq_hi_and_reserved |= 0x80

        return self._format(time_low, time_mid, time_hi_and_version,
                                                                        clock_seq_hi_and_reserved, clock_seq_low, node)


    def uuid_md5(self, nsuuid, name):
        return self._format_uuid_v3or5(nsuuid, name, _md5, 3)


    def uuid_sha1(self, nsuuid, name):
        return self._format_uuid_v3or5(nsuuid, name, _sha, 5)


    # helper methods --------------------------------------------------------

    def _format(self, *args):
        return '{%08x-%04x-%04x-%02x%02x-%012x}' % args


    def _int_to_bytes(self, num):
        out = ''
        while num:
            num, tail = divmod(num, 256)
            out += chr(tail)
        return out[-1::-1]


    def _bytes_to_int(self, bytes):
        num = 0
        for char in bytes:
            num = (num << 8) + ord(char)
        return num


    # helper for md5 and sha1 UUIDS
    def _format_uuid_v3or5(self, nsuuid, name, hasher, ver):
        try:
            nsuuid = clean(nsuuid)
        except:
            raise UuidError('invalid namespace uuid: %r' % nsuuid)
        # convert UUID bytes to network byte order
        time_low = _htonl(long(nsuuid[:8], 16))
        time_mid = _htons(long(nsuuid[9:13], 16))
        time_hi_and_version = _htons(long(nsuuid[14:18], 16))

        # hash the stuff
        h = hasher.new()
        h.update(self._int_to_bytes(time_low))
        h.update(self._int_to_bytes(time_mid))
        h.update(self._int_to_bytes(time_hi_and_version))
        h.update(name)
        hash_ = h.digest()[:16]

        # convert hash to back to host byte order
        time_low = _ntohl(self._bytes_to_int(hash_[:4]))
        time_mid = _ntohs(self._bytes_to_int(hash_[4:6]))
        time_hi_and_version = _ntohs(self._bytes_to_int(hash_[6:8]))
        clock_seq_hi_and_reserved = _ntohs(self._bytes_to_int(hash_[8:9]))
        clock_seq_low= self._bytes_to_int(hash_[9:10])
        node = self._bytes_to_int(hash_[10:])

        # throw in variant and version bits
        time_hi_and_version &= 0x0FFF;
        time_hi_and_version |= (ver << 12)
        clock_seq_hi_and_reserved &= 0x3F
        clock_seq_hi_and_reserved |= 0x80

        return self._format(time_low, time_mid, time_hi_and_version,
                                                                        clock_seq_hi_and_reserved, clock_seq_low, node)



    # returns a new timestamp for time based UUIDs
    def _get_time_now(self):

        self._state.load()

        while True:

            time_now = _time.time() * 10000000

            if time_now < self._state.time_last - self._state.uuids_per_tick:       # adjust clock_seq if time turned backwards
                if self._state.is_inited:
                    self._state.clock_seq += 1
                    if self._state.clock_seq > self._state.CLOCK_SEQ_MAX:
                        self._state.clock_seq = 0
                self._state.uuids_per_tick = 0
                break

            elif time_now <= self._state.time_last: # patch/slow down if more then 1 uuid is requested/tick
                self._state.uuids_per_tick += 1
                if self._state.uuids_per_tick < self._state.UUIDS_PER_TICK:
                    time_now += self._state.uuids_per_tick
                    break

            else:
                self._state.uuids_per_tick = 0
                break

        ##
        self._state.time_last = time_now
        self._state.dump()
        return long(time_now) + self._state.TDELTA



####################
#                                               #
#   functions                             #
#                                               #
####################

def uuid_time():
    return UuidGen().uuid_time()


def uuid_random():
    return UuidGen().uuid_random()


def uuid_md5(nsuuid, name):
    return UuidGen().uuid_md5(nsuuid, name)


def uuid_sha1(nsuuid, name):
    return UuidGen().uuid_sha1(nsuuid, name)


def clean(uuid):
    match = UUID_PAT.match(uuid)
    if not match:
        raise ValueError('invalid UUID: %r' % uuid)
    return match.group(1)

UUID_PAT = _re.compile(r'''
        .*?
        ([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12})
        .*?
        ''', _re.I|_re.X)


def get_variant(uuid):
    uuid = clean(uuid)
    variant = long(uuid[19:21], 16)
    if not variant & 0x80:
        return VARIANT_NCS
    elif not variant & 0x40 and variant & 0x80:
        return VARIANT_RFC4122
    elif not variant & 0x20 and variant & 0x40 and variant & 0x80:
        return VARIANT_MS
    elif variant & 0x20 and variant & 0x40 and variant & 0x80:
        return VARIANT_FUTURE
    else:
        return VARIANT_UNKNOWN


def get_version(uuid):
    uuid = clean(uuid)
    time_hi_and_version = long(uuid[14:18], 16)
    version =  time_hi_and_version >> 12
    if 1 < version > 5:
        version = VERSION_UNKNOWN
    return version


def get_time(uuid):
    uuid = clean(uuid)
    time_low = long(uuid[:8], 16)
    time_mid = long(uuid[9:13], 16)
    time_hi_and_version = long(uuid[14:18], 16)
    variant = long(uuid[19:21], 16)
    version =  time_hi_and_version >> 12
    if version == 1 and(variant & 0x80) and not (variant & 0x40):
        time_hi_and_version &= ~(version << 12)
        time_now = time_low | (time_mid << 32) | (time_hi_and_version << 48)
        return  (float(time_now) - _GeneratorState.TDELTA) /10000000
    return 0


def get_mac_address(uuid):
    uuid = clean(uuid)
    node = long(uuid[24:], 16)
    time_hi_and_version = long(uuid[14:18], 16)
    variant = long(uuid[19:21], 16)
    version =  time_hi_and_version >> 12
    if version == 1 and(variant & 0x80) and not (variant & 0x40):
        return node
    return 0


def format_mac_address(mac_addr):
    return '%02x-%02x-%02x-%02x-%02x-%02x' % (
                            (mac_addr & 0xFF0000000000) >> 40,
                            (mac_addr & 0xFF00000000)>> 32,
                            (mac_addr & 0xFF000000) >> 24,
                            (mac_addr & 0xFF0000) >> 16,
                            (mac_addr& 0xFF00) >> 8,
                            mac_addr & 0xFF
                            )

####################
#                                             #
#   commandline interface   #
#                                             #
####################

if __name__ == '__main__':
    import sys
    import getopt


    USAGE = """'generates a UUID of the specified type and prints it to stdout

usage:
uuid.py [-h] [-t <type> [-s <namespace uuid> -n <name>]]

-h        prints out this help message
-t         type of uuid (time, random, md5, sha1)
-s        namespace uuid (required for md5 or sha1)
-n        name (required for md5 or sha1)
"""
    try:
        o, args = getopt.getopt(sys.argv[1:], 'ht:s:n:')
        o = dict(o)
        if '-h' in o:
            print USAGE
        else:
            type_uuid = o.get('-t', None)
            if type_uuid == 'time':
                print uuid_time()
            elif type_uuid == 'random':
                print uuid_random()
            elif type_uuid == 'md5':
                print uuid_md5(o['-s'], o['-n'])
            elif type_uuid == 'sha1':
                print uuid_sha1(o['-s'], o['-n'])
            else:
                raise UuidError('')
    except:
        print USAGE
    sys.exit()

####################
#                                             #
#   test                                   #
#                                             #
####################

def test():
    g = globals().items()
    variants = dict([(value, name) for name, value in g \
                                                            if name.startswith('VARIANT_')])
    versions = dict([(value, name) for name, value in g \
                                                            if name.startswith('VERSION_')])

    UUIDS = (
            uuid_time(),
            uuid_random(),
            uuid_md5(NAMESPACE_DNS, 'foo'),
            uuid_sha1(NAMESPACE_DNS, 'bar'),
            )

    print
    for UUID in (UUIDS):
        print 'UUID:      %r' % UUID
        print 'variant:    ', variants.get(get_variant(UUID), 'unknown')
        print 'verson:    ', versions.get(get_version(UUID), 'unknown')
        print 'time:        ', _time.ctime(get_time(UUID)), '(%ss since epoch)' \
                                                                        % get_time(UUID)
        print 'MAC:         %s' % format_mac_address(get_mac_address(UUID))
        print

#test()
