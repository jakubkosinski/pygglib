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

class GGSession(EventsList):
	def __init__(self, uin, password):
		EventsList.__init__(self, ["on_msg_recv", "on_status_changed"])
		self.__uin = uin
		self.__password = password
	
	def login(self):
		
		login_packet = GGLogin(self.__uin, self.__password, 0x0002, )