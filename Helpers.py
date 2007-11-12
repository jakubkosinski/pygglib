"""
(C) Marek Chrusciel, 
    Jakub Kosinski, 
    Marcin Krupowicz,
    Mateusz Strycharski
"""

""" $Id: Helpers.py 1 2007-11-11 23:08:39Z cinu $ """

import types

class Helpers(object):
	hash_type = 0x01 # -- hash obliczany za pomoca "zwyklej", "starej" funkcji do obliczania gg_hashu
	#hash_type = 0x02 # -- hash obliczany za pomoca sha-1
	def gg_login_hash(password, seed):
		#assert type(password) == types.StringType
		#assert type(seed) == types.IntType
		return NotImplemented
	def ip_string_to_int32(ip):
		#assert type(ip) == types.StringType
		return NotImplemented
