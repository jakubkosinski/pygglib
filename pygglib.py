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

from __future__ import with_statement

from IncomingPackets import *
from OutgoingPackets import *
from HeaderPacket import GGHeader
from Helpers import *
from GGConstans import *
from Networking import Connection
from Exceptions import *
from HTTPServices import *
import types
import threading
import thread
from threading import Timer
import time


## Glowna klasa do obslugi protokolu gg. 
# Umozliwia podstawowe operacje. Tworzy sesje obslugi protokolu.
#
class GGSession(EventsList):	
		## Konstruktor dla sesji gg.
		#
		#\param uin	                          nr gadu-gadu, dla ktorego bedzie tworzona sesja
		#\param password	                 haslo dla nr gadu-gadu
		#\param initial_status           poczatkowy status dostepnosci
		#\param initial_description     poczatkowy opis 
		#
	def __init__(self, uin, password, initial_status = GGStatuses.Avail, initial_description = ''):
		assert type(uin) == types.IntType
		assert type(password) == types.StringType
		assert initial_status in GGStatuses
		assert type(initial_description) == types.StringType and len(initial_description) <= 70
		
		EventsList.__init__(self, ['on_login_ok', 'on_login_failed', 'on_need_email', 'on_msg_recv', \
								   'on_unknown_packet', 'on_send_msg_ack', 'on_notify_reply'])
		self.__uin = uin
		self.__password = password
		self.__status = initial_status
		self.__description = initial_description
		
		self.__local_ip = "127.0.0.1" 
		self.__local_port = 1550
		self.__external_ip = "127.0.0.1"
		self.__external_port = 0
		self.__image_size = 255
		
		self.__connected = False # czy jestesmy polaczeni z serwerem
		self.__logged = False # czy uzytkownik jest zalogowany do serwera
		
		self.__connection = None
		
		self.__pinger = Timer(120.0, self.__ping) # co 2 minuty pingujemy serwer
		self.__events_thread = threading.Thread(target = self.__events_loop)
	
		self.__lock = threading.RLock() #blokada dla watku
		
	## Metoda powoduje uruchomienie listenera
	#
	def __events_loop(self):
		while self.__logged:
			header = GGHeader()
			header.read(self.__connection)
			if header.type == GGIncomingPackets.GGRecvMsg:
				in_packet = GGRecvMsg()
				in_packet.read(self.__connection, header.length)
				self.on_msg_recv(self, (in_packet.sender, in_packet.seq, in_packet.time, in_packet.msg_class, in_packet.message))
			elif header.type == GGIncomingPackets.GGSendMsgAck:
				in_packet = GGSendMsgAck()
				in_packet.read(self.__connection, header.length)
				self.on_send_msg_ack(self, (in_packet.status, in_packet.recipient, in_packet.seq))
			elif header.type == GGIncomingPackets.GGNotifyReplyOld:
				in_packet = GGNotifyReplyOld(self.contacts_list)
				in_packet.read(self.__connection, header.length)
				self.on_notify_reply(self, self.contacts_list)
			elif header.type == GGIncomingPackets.GGNotifyReply60 or header.type == GGIncomingPackets.GGNotifyReply77:
				in_packet = GGNotifyReply(self.contacts_list, header.type)
				in_packet.read(self.__connection, header.length)
				self.on_notify_reply(self, self.contacts_list)
			else:
				self.__connection.read(header.length) #odbieramy smieci.. ;)
				self.on_unknown_packet(self, (header.type, header.length))
			time.sleep(0.1)
	
	
	## Metoda wysyla pakiet GGPing do serwera
	#
	def __ping(self):
		if not self.__logged:
			raise GGNotLogged
		with self.__lock:
			out_packet = GGPing()
			out_packet.send(self.__connection)
	
	## Logowanie do sieci gg
	#
	def login(self):
		with self.__lock:
			server, port = HTTPServices.get_server(self.__uin)
			self.__connection = Connection(server, port)
			self.__connected = True #TODO: sprawdzanie tego i timeouty
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
				self.__events_thread.start() #uruchamiamy watek listenera
			elif header.type == GGIncomingPackets.GGLoginFailed:
				self.on_login_failed(self, None)
			elif header.type == GGIncomingPackets.GGNeedEMail:
				self.on_need_email(self, None)
			else:
				raise GGUnexceptedPacket((header.type, header.length))

	## Wylogowanie z sieci GG i ustawienie statusu na niedostepny
	# \param description Taki opis zostanie pozostawiony
	#
	def logout(self, description = ''):
		assert type(description) == types.StringType and len(description) <= 70
		
		if not self.__logged:
			raise GGNotLogged
		
		self.change_status(description == '' and GGStatuses.NotAvail or GGStatuses.NotAvailDescr, description)
		with self.__lock:
			self.__logged = False # przed join(), zeby zakonczyc watek
			self.__events_thread.join()
			self.__pinger.cancel()
			self.__connection.disconnect()
			self.__connected = False
		
	## Zmiana statusu i opisu
	# \param status Taki staus dosteonosci zostanie ustawiony
	#\param description Taki opis zostanie ustawiony
	def change_status(self, status, description):
		assert type(status) == types.IntType and status in GGStatuses
		assert type(description) == types.StringType and len(description) <= 70
		
		if not self.__logged:
			raise GGNotLogged
		
		with self.__lock:
			out_packet  = GGNewStatus(status, description)
			out_packet.send(self.__connection)
			self.__status = status
			self.__description = description
	
	def change_description(self, description):
		assert type(description) == types.StringType and len(description) <= 70
		
		if self.__status != GGStatuses.AvailDescr and self.__status != GGStatuses.BusyDescr and self.__status != GGStatuses.InvisibleDescr:
			raise GGException("Can't change description - current status has'n description") 
		if not self.__logged:
			raise GGNotLogged
		
		self.change_status(self.__status, description)
	
	## Wyslanie wiadomosci gg
	# \param rcpt nr gadu-gadu odbiorcy
	#\param msg wiadomosc do dostarczenia, dlugosc musi byc mniejsza od 2000 znakow
	def send_msg(self, rcpt, msg, seq = 0, msg_class = GGMsgTypes.Msg):
		assert type(rcpt) == types.IntType
		assert type(msg) == types.StringType and len(msg) < 2000 #TODO: w dalszych iteracjach: obsluga richtextmsg
		assert type(seq) == types.IntType
		assert type(msg_class) in GGMsgTypes
		
		if not self.__logged:
			raise GGNotLogged
		
		with self.__lock:
			out_packet = GGSendMsg(rcpt, msg, seq, msg_class)
			out_packet.send(self.__connection)
	
	
	def send_contacts_list(self):
		"""
		Wysyla do serwera nasza liste kontaktow w celu otrzymania statusow.
		Powinno byc uzyte zaraz po zalogowaniu sie do serwera.
		UWAGA: To nie jest eksport listy kontaktow do serwera!
		"""
		if not self.__logged:
			raise GGNotLogged
		
		uin_type_list = [] # [(uin, type), (uin, type), ...]
		for contact in self.contacts_list:
			list.append((contact.uin, contact.type))
		sub_lists = Helpers.split_list(uin_type_list, 400)
		
		with self.__lock:
			for l in sub_lists[:-1]: #zostawiamy ostatnia podliste
				out_packet = GGNotifyFirst(l)
				out_packet.send(self.__connection)
			# zostala juz ostatnia lista do wyslania
			out_packet = GGNotifyLast(sub_lists[-1])
			out_packet.send(self.__connection)