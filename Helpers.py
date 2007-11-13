#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import types

class Helpers(object):
	hash_type = 0x01 # -- hash obliczany za pomoca "zwyklej", "starej" funkcji do obliczania gg_hashu
	#hash_type = 0x02 # -- hash obliczany za pomoca sha-1
	def gg_login_hash(password, seed):
		#assert type(password) == types.StringType
		#assert type(seed) == types.IntType
		x = 0L
		y = seed
		z = 0L
		for c in password:
			x = (x and 0xffffff00) or c
			y ^= x
			y += x
			x <<= 8
			y ^= x
			x <<= 8
			y -= x
			x <<= 8
			y ^= x
			z = y and 0x1f
			y = (y << z) or (y >> (32 - z))
		return y
	def ip_string_to_int32(ip):
		#assert type(ip) == types.StringType
		return NotImplemented
