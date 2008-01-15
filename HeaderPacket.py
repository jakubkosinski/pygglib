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

	#def __init__(self):
	#	"""
	#	Konstruktor ten wywolujemy gdy naglowek bedziemy odbierac
	#	"""
	#	pass
	
	def __init__(self, type_=0, length=0):
		assert type(type_) == types.IntType
		assert type(length) == types.IntType
		
		self.type = type_
		self.length = length
		self.connection = None
	
	def read(self, connection):
		assert type(connection) == Connection
		data = connection.read(8, timeout = 10)
		self.type, self.length = struct.unpack("<II", data)
	
	def __repr__(self):
		return struct.pack("<II", self.type, self.length)
