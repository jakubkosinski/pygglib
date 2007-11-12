#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import types
import GGOutgoingPacket
from Helpers import *

class GGLogin(GGOutgoingPacket):
	"""
	Pakiet ten wysylamy do serwera, zeby sie zalogowac
	"""
	def __init__(self, uin, password, status, seed, description, local_ip = "127.0.0.1", local_port = "1550"):
		"""
		uin - numer gadu-gadu (int)
		password - haslo (string)
		status - status poczatkowy (GGStatus)
		seed - seed z pakietu GGWelcome (int)
		"""
		assert type(uin) == types.IntType
		assert type(password) == types.StringType
		assert type(status) in GGStatus
		assert type(seed) == types.IntType
		assert type(description) == types.StringType && len(description) <= 255
		assert type(local_ip) == types.StringType
		assert type(local_port) = types.IntType
		
		self.uin = uin
		self.password = password
		self.status = status
		self.seed = seed
		self.local_ip = local_ip
		self.local_port = local_port
		self.description = description
	
	def send(self, connection):
		assert type(connection) == Connection

		connection.send_header(GGOutgoingPacketTypes["Login60"], ____)
		connection.send_int32(self.uin)
		connection.send_byte(Helpers.hash_type)
		hash = Helpers.gg_login_hash(self.password, self.seed)
		connection.send_data(hash, 64)
		connection.send_int32(self.status)
		connection.send_int32(0x24)
		connection.send_byte(0x00)
		ip_int32 = Helpers.ip_string_to_int32(local_ip)
		connection.send_int32(ip_int32)
		connection.send_short(local_port)
		connection.send_int32(0x0)
		connection.send_short(0x0)
		connection.send_byte(255)
		connection.send_byte(0xbe)
		connection.send_data(description, len(description))


