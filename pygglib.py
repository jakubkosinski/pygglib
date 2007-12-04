"""
Biblioteka sluzaca do osblugi protokolu Gadu-Gadu (http://www.gadu-gadu.pl).
Biblioteka powstala dzieki opisie protokolu ze strony: 
http://ekg.chmurka.net/docs/protocol.html

Autorzy:
	Marek Chrusciel
	Jakub Kosinski
	Marcin Krupowicz
	Mateusz Strycharski
"""

#$Id$

from IncomingPackets import *
from OutgoingPackets import *
from HeaderPacket import GGHeader
from Helpers import *
from GGConstans import *
from Networking import Connection
from Exceptions import *
from HTTPServices import *
import types


class GGSession(EventsList):
	def __init__(self, uin, password, initial_status = GGStatuses.Avail, initial_description = ''):
		assert type(uin) == types.IntType
		assert type(password) == types.StringType
		assert initial_status in GGStatuses
		assert type(initial_description) == types.StringType and len(initial_description) <= 70
		
		EventsList.__init__(self, ['on_login_ok', 'on_login_failed', 'on_need_email'])
		self.__uin = uin
		self.__password = password
		self.__status = initial_status
		self.__description = initial_description
		
		self.__local_ip = "127.0.0.1" 
		self.__local_port = 1550
		self.__external_ip = "127.0.0.1"
		self.__external_port = 0
		self.__image_size = 255
		
		self.__logged = False # czy uzytkownik jest zalogowany do serwera
		
		self.__connection = None
		
	
	def login(self):
		server, port = HTTPServices.get_server(self.__uin)
		self.__connection = Connection(server, port)
		header = GGHeader()
		header.read(self.__connection)
		if header.type != GGIncomingPackets.GGWelcome:
			raise GGUnexceptedPacket((header.type, header.length))
		in_packet = GGWelcome()
		in_packet.read(self.__connection, header.length)
		seed = in_packet.seed
		out_packet = GGLogin(self.__uin, self.__password, self.__status, seed, self.__description, self.__local_ip, \
								self.__local_port, self.__external_ip, self.__external_port, self.__image_size)
		out_packet.send(self.__connection)
		header.read(self.__connection)
		if header.type == GGIncomingPackets.GGLoginOK:
			self.__logged = True
			in_packet = GGLoginOK()
			in_packet.read(self.__connection, header.length)
			self.change_status(self.__status, self.__description) #ustawienie statusu przy pakiecie GGLogin cos nie dziala :/
			self.on_login_ok(self, None)
		elif header.type == GGIncomingPackets.GGLoginFailed:
			self.on_login_failed(self, None)
		elif header.type == GGIncomingPackets.GGNeedEMail:
			self.on_need_email(self, None)
		else:
			raise GGUnexceptedPacket((header.type, header.length))
	
		
		
	def change_status(self, status, description):
		"""
		Zmiana statusu
		"""
		assert type(status) == types.IntType and status in GGStatuses
		assert type(description) == types.StringType and len(description) <= 70
		
		if not self.__logged:
			raise GGNotLogged
		
		out_packet  = GGNewStatus(status, description)
		out_packet.send(self.__connection)
		self.__status = status
		self.__description = description
		