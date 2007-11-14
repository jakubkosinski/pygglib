#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import types
import socket
import struct

def gg_login_hash(password, seed):
	assert type(password) == types.StringType
	#assert type(seed) == types.IntType
	x = 0L
	y = long(seed)
	z = 0L
	for c in password:
		x = (x & 0xffffff00L) | ord(c)
		y ^= x
		y &= 0xffffff00L
		y += x
		y &= 0xffffff00L
		x <<= 8
		x &= 0xffffff00L
		y ^= x
		y &= 0xffffff00L
		x <<= 8
		x &= 0xffffff00L
		y -= x
		y &= 0xffffff00L
		x <<= 8
		x &= 0xffffff00L
		y ^= x
		y &= 0xffffff00L
		z = y & 0x1f
		y = (y << z) | (y >> (32 - z))
		y &= 0xffffff00L
	return y


def ip_to_int32(ip):
	assert type(ip) == types.StringType
	return struct.unpack("<I", socket.inet_aton(ip))[0]

