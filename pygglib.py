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
from Contacts import *
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
	def __init__(self, uin, password, initial_status = GGStatuses.Avail, initial_description = '', contacts_list = None):
		assert type(uin) == types.IntType
		assert type(password) == types.StringType
		assert initial_status in GGStatuses
		assert type(initial_description) == types.StringType and len(initial_description) <= 70
		assert type(contacts_list) == ContactsList or contacts_list == None		
		EventsList.__init__(self, ['on_login_ok', 'on_login_failed', 'on_need_email', 'on_msg_recv', \
				'on_unknown_packet', 'on_send_msg_ack', 'on_notify_reply', 'on_pubdir_recv', 'on_userlist_reply'])
		self.__uin = uin
		self.__password = password
		self.__status = initial_status
		self.__description = initial_description
		self.__contacts_list = contacts_list
		self.__importing = False # informuje, czy aktualnie importujemy liste kontaktow z serwera Gadu-Gadu
		self.__contact_buffer = "" # bufor na importowane z serwera kontakty
		
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
	
	def __get_contacts_list(self):
		return self.__contacts_list
	def __set_contacts_list(self, contacts_list):
		assert type(contacts_list) == ContactsList
		self.__contacts_list = contacts_list
	
	## Metoda powoduje uruchomienie listenera
	#
	def __events_loop(self):
		while self.__logged:
			header = GGHeader()
			try: #TODO: yyyyy ugly ;)  (przy wylogowaniu wyjatek leci)
				header.read(self.__connection)
			except:
				return
			if header.type == GGIncomingPackets.GGRecvMsg:
				in_packet = GGRecvMsg()
				in_packet.read(self.__connection, header.length)
				self.on_msg_recv(self, (in_packet.sender, in_packet.seq, in_packet.time, in_packet.msg_class, in_packet.message))
			elif header.type == GGIncomingPackets.GGSendMsgAck:
				in_packet = GGSendMsgAck()
				in_packet.read(self.__connection, header.length)
				self.on_send_msg_ack(self, (in_packet.status, in_packet.recipient, in_packet.seq))
			elif header.type == GGIncomingPackets.GGNotifyReplyOld:
				in_packet = GGNotifyReplyOld(self.__contacts_list)
				in_packet.read(self.__connection, header.length)
				self.on_notify_reply(self, self.__contacts_list)
			elif header.type == GGIncomingPackets.GGNotifyReply60 or header.type == GGIncomingPackets.GGNotifyReply77:
				in_packet = GGNotifyReply(self.__contacts_list, header.type)
				in_packet.read(self.__connection, header.length)
				self.__contacts_list = in_packet.contacts
				self.on_notify_reply(self, self.__contacts_list)
			elif header.type == GGIncomingPackets.GGPubDir50Reply:
				in_packet = GGPubDir50Reply()
				in_packet.read(self.__connection, header.length)
				self.on_pubdir_recv(self, (in_packet.reqtype, in_packet.seq, in_packet.reply))
			elif header.type == GGIncomingPackets.GGDisconnecting:
				in_packet = GGDisconnecting()
				in_packet.read(self.__connection, header.length)
				self.login() # po rozlaczeniu przez serwer laczymy sie ponownie
			elif header.type == GGIncomingPackets.GGUserListReply:
				in_packet = GGUserListReply()
				in_packet.read(self.__connection, header.length)
				self.on_userlist_reply(self, (in_packet.reqtype, in_packet.request))
				
				if in_packet.reqtype == GGUserListReplyTypes.GetMoreReply:
					self.__contact_buffer += in_packet.request
				if in_packet.reqtype == GGUserListReplyTypes.GetReply:
					self.__importing = False # zaimportowano cala liste
					self.__contact_buffer += in_packet.request #... bo lista moze przyjsc w kilku pakietach
					self.__make_contacts_list(self.__contact_buffer)
					self.__contact_buffer = "" # oprozniamy bufor
					
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
			self.__connection = Connection(server, 443)
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
				self.on_login_ok(self, None)
				self.__events_thread.start() #uruchamiamy watek listenera
				time.sleep(0.5) #TODO: potrzebne to?
				self.__send_contacts_list()
				#self.change_status(self.__status, self.__description) #ustawienie statusu przy pakiecie GGLogin cos nie dziala :/
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
	def send_msg(self, rcpt, msg, seq = 0, msg_class = GGMsgTypes.Msg, richtext = False):
		assert type(rcpt) == types.IntType
		assert type(msg) == types.StringType and len(msg) < 2000 #TODO: w dalszych iteracjach: obsluga richtextmsg
		assert type(seq) == types.IntType
		assert msg_class in GGMsgTypes
		
		if not self.__logged:
			raise GGNotLogged
		
		if richtext:
			message = Helpers.pygglib_rtf_to_gg_rtf(msg)
		else:
			message = msg
		
		with self.__lock:
			out_packet = GGSendMsg(rcpt, message, seq, msg_class)
			out_packet.send(self.__connection)
	
	def pubdir_request(self, request, reqtype = GGPubDirTypes.Search):
		assert type(request) == types.StringType or type(request) == types.DictType
		assert reqtype in GGPubDirTypes
		
		if not self.__logged:
			raise GGNotLogged
			
		with self.__lock:
			out_packet = GGPubDir50Request(request, reqtype)
			out_packet.send(self.__connection)
	
	def export_contacts_list(self, method, filename = None):
		"""
		Eksportuje liste kontaktow do serwera lub do pliku. Metoda przekazywana jest jako parametr method:
			0 - do serwera
			1 - do pliku
		Nazwa pliku przekazywana jest w opcjonalnym parametrze filename.
		"""
		assert type(method) == types.IntType
		while self.__importing == True:
			time.sleep(0.1)
		if self.__contacts_list != None:
			if method == 0:
				if not self.__logged:
					raise GGNotLogged
				
				sub_lists = Helpers.split_list(self.__contacts_list.export_request_string(), 2038)
				with self.__lock:
					out_packet = GGUserListRequest(GGUserListTypes.Put, sub_lists[0])
					out_packet.send(self.__connection)
					if len(sub_lists) > 1:
						for l in sub_lists[1:len(sub_lists)]:
							out_packet = GGUserListRequest(GGUserListTypes.PutMore, l)
							out_packet.send(self.__connection)
			elif method == 1:
				assert type(filename) == types.StringType
				request = self.__contacts_list.export_request_string()
				file = open(filename, "w")
				file.write(request)
				file.close()
			
	def delete_contacts_from_server(self):
		"""
		Usuwa liste kontaktow z serwera Gadu-Gadu
		"""
		if not self.__logged:
			raise GGNotLogged
		
		out_packet = GGUserListRequest(GGUserListTypes.Put, "")
		out_packet.send(self.__connection)
		
	def import_contacts_list(self, method, filename = None):
		"""
		Wysyla zadanie importu listy z serwera (method = 0) lub pliku o nazwie filename (method = 1). Zaimportowana lista zapisywana jest w self.__contacts_list
		"""
		
		if method == 0:
			if not self.__logged:
				raise GGNotLogged
			out_packet = GGUserListRequest(GGUserListTypes.Get, "")
			out_packet.send(self.__connection)
			self.__importing = True
		else:
			assert type(filename) == types.StringType
			file = open(filename, "r")
			request = file.read()
			file.close()
			self.__make_contacts_list(request)
	
	def add_contact(self, contact, user_type = 0x3, notify = True):
		"""
		Dodajemy kontakt 'contact' do listy kontaktow. Jesli jestesmy polaczeni z serwerem i notify == True to dodatkowo
		powiadamiamy o tym fakcie serwer. Od tego momentu serwer bedzie nas informowal o statusie tego kontaktu.
		"""
		assert type(contact) == Contact
		self.__contacts_list.add_contact(contact)
		if self.__logged and notify:
			out_packet = GGAddNotify(contact.uin, user_type)
			out_packet.send(self.__connection)

	def remove_contact(self, uin, notify = True):
		"""
		Usuwamy z listy kontaktow kontakt o numerze 'uin'. Jesli jestesmy polaczeni z serwerem i notify == True to dodatkowo
		powiadamiamy o tym fakcie serwer. Od tego momentu serwer nie bedzie nas juz informowal o statusie tego kontaktu.
		"""
		self.__contacts_list.remove_contact(uin)
		if self.__logged and notify:
			out_packet = GGRemoveNotify(uin)
			out_packet.send(self.__connection)
	
	def change_user_type(self, uin, user_type):
		"""
		Zmieniamy typ uzytkownika. user_type jest mapa wartosci z GGUserTypes.
		Np., zeby zablokowac uzytkownka piszemy:
			change_user_type(12454354, GGUserTypes.Blocked)
		"""
		if not self.__logged:
			raise GGNotLogged

		out_packet = GGRemoveNotify(uin, user_type)
		out_packet.send(self.__connection)

	def __send_contacts_list(self):
		"""
		Wysyla do serwera nasza liste kontaktow w celu otrzymania statusow.
		Powinno byc uzyte zaraz po zalogowaniu sie do serwera.
		UWAGA: To nie jest eksport listy kontaktow do serwera!
		"""
		assert self.__contacts_list  == None or type(self.__contacts_list) == ContactsList
		
		if not self.__logged:
			raise GGNotLogged
		
		if self.__contacts_list == None or len(self.__contacts_list) == 0:
			with self.__lock:
				out_packet = GGListEmpty()
				out_packet.send(self.__connection)
			return
		
		uin_type_list = [] # [(uin, type), (uin, type), ...]
		for contact in self.__contacts_list.data: #TODO: brrrrrrr, nie .data!!!!
			print contact.uin, contact.type
			uin_type_list.append((contact.uin, contact.type))
		sub_lists = Helpers.split_list(uin_type_list, 400)
		
		with self.__lock:
			for l in sub_lists[:-1]: #zostawiamy ostatnia podliste
				out_packet = GGNotifyFirst(l)
				out_packet.send(self.__connection)
			# zostala juz ostatnia lista do wyslania
			out_packet = GGNotifyLast(sub_lists[-1])
			out_packet.send(self.__connection)
	
	def __make_contacts_list(self, request):
		contacts = request.split("\n")
		for contact in contacts:
			if contact != '':
				newcontact = Contact({'request_string':contact})
				if self.__contacts_list == None:
					self.__contacts_list = ContactsList()
				if self.__contacts_list[newcontact.uin] == None:
					self.__contacts_list.add_contact(Contact({'request_string':contact}))
				else:
					self.__contacts_list[newcontact.uin] = newcontact
				
	#
	# Properties
	#
	contacts_list = property(__get_contacts_list, __set_contacts_list)
