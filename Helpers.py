#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import types
import socket

class Helpers(object):
	hash_type = 0x01 # -- hash obliczany za pomoca "zwyklej", "starej" funkcji do obliczania gg_hashu
	#hash_type = 0x02 # -- hash obliczany za pomoca sha-1
	def gg_login_hash(password, seed):
		assert type(password) == types.StringType
		assert type(seed) == types.IntType
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

	def host_to_int32(host):
		assert type(host) == types.StringType
		return socket.inet_aton(socket.gethostbyname(host))
		
	
	def ip_to_int32(ip):
		assert type(ip) == types.StringType
		return socket.inet_aton(ip)
	
	gg_login_hash = staticmethod(gg_login_hash)
	host_to_int32 = staticmethod(host_to_int32)
	ip_to_int32 = staticmethod(ip_to_int32)
