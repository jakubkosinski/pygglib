#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import types
import struct
from Networking import Connection

class GGHeader(object):
	"""
	Kazdy pakiet wysylany/pobierany do/od serwera zawiera na poczatku
	naglowek - tym naglowkiem jest wlasnie struktura GGHeader.
	"""

	def __init__(self):
		"""
		Konstruktor ten wywolujemy gdy naglowek bedziemy odbierac
		"""
		pass
	
	def __init__(self, type_, length):
		"""
		Konstruktor ten wywolujemy wtedy kiedy pakiet jest przeznaczony do wyslania
		"""
		assert type(type_) == types.IntType
		assert type(length) == types.IntType
		
		self.type = type_
		self.length = length
		self.connection = None
	
	def read(self, connection):
		assert type(connection) == Connection
		data = connection.read(8)
		self.type, self.length = struct.unpack("<II", data)
	
	def __repr__(self):
		return struct.pack("<II", self.type, self.length)
