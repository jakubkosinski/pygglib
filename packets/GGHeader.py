#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import types

class GGHeader(object):
	"""
	Kazdy pakiet wysylany/pobierany do/od serwera zawiera na poczatku
	naglowek - tym naglowkiem jest wlasnie struktura GGHeader.
	"""
	def __init__(self, type_, length, connection = None):
		assert type(type_) == types.IntType
		assert type(length) == types.IntType
		assert connection == None || type(connection) == type(Connection)
		
		self.type = type_
		self.length = length
	
	def read(self):
		self.type = connection.read_int32()
		self.length = connection.read_int32()
