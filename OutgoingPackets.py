#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import types
import sys
import struct
from HeaderPacket import GGHeader
from Networking import Connection
import Helpers



class GGOutgoingPacket(object):
	"""
	"Abstrakcyjna" klasa pakietow wysylanych do serwera
	"""
	def send(self):
		pass


class GGLogin(GGOutgoingPacket):
	"""
	Pakiet ten wysylamy do serwera, zeby sie zalogowac
	"""
	def __init__(self, uin, password, status, seed, description = "", local_ip = "127.0.0.1", local_port = 1550, external_ip = "127.0.0.1", external_port = 0, image_size = 255, time = 0):
		"""
		uin - numer gadu-gadu (int)
		password - haslo (string)
		status - status poczatkowy (GGStatus)
		seed - seed z pakietu GGWelcome (int)
		"""
		assert type(uin) == types.IntType
		assert type(password) == types.StringType
		#assert type(status) in GGStatus
		#assert type(seed) == types.IntType or type(seed) == types.LongType
		assert type(description) == types.StringType and len(description) <= 255
		assert type(local_ip) == types.StringType
		assert type(local_port) == types.IntType
		assert type(external_ip) == types.StringType
		assert type(external_port) == types.IntType
		assert type(time) == types.IntType
		assert type(image_size) == types.IntType
		
		self.uin = uin
		self.password = password
		self.status = status
		self.seed = seed
		self.local_ip = local_ip
		self.local_port = local_port
		self.description = description
		self.external_ip = external_ip
		self.external_port = external_port
		self.image_size = image_size
		self.time = time
		self.version = 0x27 # GG 7.0

	def send(self, connection):
		assert type(connection) == Connection
		
		"""
		#data = struct.pack("<IBIIIBIHIHBB%dsI" % (len(self.description) + 1),
		data = struct.pack("<IB64sIIBIHIHBB%dsI" % (len(self.description) + 1),
			self.uin, 
			0x01, 
			Helpers.gg_login_hash(self.password, self.seed), 
			self.status, 
			self.version, 
			0x00, 
			Helpers.ip_to_int32(self.local_ip), 
			self.local_port, 
			Helpers.ip_to_int32(self.external_ip), 
			self.external_port, 
			self.image_size, 
			0xbe,
			self.description,
			self.time)

		#connection.send(repr(GGHeader(0x019, len(data))) + data)
		"""
		data = struct.pack("<IIIIBIhIhBB%dsI" % (len(self.description) + 1),
			self.uin, Helpers.gg_login_hash(self.password, self.seed), self.status, self.version, 0x00,
			Helpers.ip_to_int32(self.local_ip), self.local_port, Helpers.ip_to_int32(self.external_ip), self.external_port,
			self.image_size, 0xbe, self.description, self.time)

		connection.send(struct.pack("<ii", 0x0015, len(data)) + data)

		

