#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import types
import socket
import struct
import hashlib

def gg_login_hash(password, seed):
	assert type(password) == types.StringType
	#assert type(seed) == types.IntType
	x = 0L
	y = long(seed)
	z = 0L
	for c in password:
		x = (x & 0xffffffffL) | ord(c)
		y ^= x
		y &= 0xffffffffL
		y += x
		y &= 0xffffffffL
		x <<= 8
		x &= 0xffffffffL
		y ^= x
		y &= 0xffffffffL
		x <<= 8
		x &= 0xffffffffL
		y -= x
		y &= 0xffffffffL
		x <<= 8
		x &= 0xffffffffL
		y ^= x
		y &= 0xffffffffL
		z = y & 0x1f
		y = (y << z) | (y >> (32 - z))
		y &= 0xffffffffL
	return y
	#return struct.pack("<I60s", y, str(0x00))[0]
	#return hashlib.sha1(password).digest()



def ip_to_int32(ip):
	assert type(ip) == types.StringType
	return struct.unpack("<I", socket.inet_aton(ip))[0]

