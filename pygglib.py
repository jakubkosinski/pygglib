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


class GGSession(EventsList):	
	"""
	Glowna klasa do obslugi protokolu gg. Jest to pojedyncza sesja obslugujaca protokol.
	Pola publiczne:
		* contacts_list - zawiera liste kontaktow zalogowanego uzytkownika.
	Aby utworzyc obiekt tej klasy nalezy przekazac do konstruktora nastepujace parametry:
		* uin - numer gadu-gadu, dla ktorego bedzie tworzona sesja
		* password - haslo dla numeru gadu-gadu uin
		* initial_status - poczatkowy status dostepnosci (wartosc domyslna - GGStatuses.Avail)
		* initial_description - poczatkowy opis (wartosc domyslna - '')
		* contacts_list - lista kontaktow (wartosc domyslna - None)
	 
	Przyklad uzycia:
	 1. GGSession(1111111, 'kaczka', , 'moj nowy opis', );
	 Tworzy nowy obiekt sesji dla uzytkownika o numerze 1111111 z haslem kaczka i z poczatkowym statusem 'moj nowy opis'
	"""
	
	def __init__(self, uin, password, initial_status = GGStatuses.Avail, initial_description = '', contacts_list = ContactsList()):
		assert type(uin) == types.IntType
		assert type(password) == types.StringType
		assert initial_status in GGStatuses
		assert type(initial_description) == types.StringType and len(initial_description) <= 70
		assert type(contacts_list) == ContactsList or contacts_list == None		
		EventsList.__init__(self, ['on_login_ok', 'on_login_failed', 'on_need_email', 'on_msg_recv', \
				'on_unknown_packet', 'on_send_msg_ack', 'on_notify_reply', 'on_pubdir_recv', 'on_userlist_reply', \
				'on_status_changed', 'on_disconnecting', 'on_server_not_operating'])
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
	

	def __events_loop(self):
		"""
		Metoda powoduje uruchomienie listenera
		"""
		while self.__logged:
			header = GGHeader()
			try:
				header.read(self.__connection)
			except: #paskudnie, ale coz... ;) Na koniec sesji to jest potrzebne
				break
			if header.type == GGIncomingPackets.GGRecvMsg:
				in_packet = GGRecvMsg()
				with self.__lock:
					in_packet.read(self.__connection, header.length)
				self.on_msg_recv(self, EventArgs({\
					"sender" : in_packet.sender,\
					"seq" : in_packet.seq,\
					"time" : in_packet.time,\
					"msg_class" : in_packet.msg_class,\
					"message" : in_packet.message}))

			elif header.type == GGIncomingPackets.GGSendMsgAck:
				in_packet = GGSendMsgAck()
				with self.__lock:
					in_packet.read(self.__connection, header.length)
				self.on_send_msg_ack(self, EventArgs({\
					"status" : in_packet.status,\
					"recipient" : in_packet.recipient,\
					"seq" : in_packet.seq}))

			elif header.type == GGIncomingPackets.GGNotifyReplyOld:
				in_packet = GGNotifyReplyOld(self.__contacts_list)
				with self.__lock:
					in_packet.read(self.__connection, header.length)
				self.__contacts_list = in_packet.contacts
				self.on_notify_reply(self, EventArgs({"contacts_list" : self.__contacts_list}))

			elif header.type == GGIncomingPackets.GGNotifyReply60 or header.type == GGIncomingPackets.GGNotifyReply77:
				in_packet = GGNotifyReply(self.__contacts_list, header.type)
				with self.__lock:
					in_packet.read(self.__connection, header.length)
				self.__contacts_list = in_packet.contacts
				self.on_notify_reply(self, EventArgs({"contacts_list" : self.__contacts_list}))

			elif header.type == GGIncomingPackets.GGPubDir50Reply:
				in_packet = GGPubDir50Reply()
				with self.__lock:
					in_packet.read(self.__connection, header.length)
				self.on_pubdir_recv(self, EventArgs({\
					"req_type" : in_packet.reqtype,\
					"seq" : in_packet.seq,\
					"reply" : in_packet.reply}))

			elif header.type == GGIncomingPackets.GGDisconnecting:
				in_packet = GGDisconnecting()
				with self.__lock:
					in_packet.read(self.__connection, header.length)
				self.on_disconnecting(self, EventArgs({}))

			elif header.type == GGIncomingPackets.GGUserListReply:
				in_packet = GGUserListReply()
				with self.__lock:
					in_packet.read(self.__connection, header.length)
				if in_packet.reqtype == GGUserListReplyTypes.GetMoreReply:
					self.__contact_buffer += in_packet.request
				if in_packet.reqtype == GGUserListReplyTypes.GetReply:
					self.__importing = False # zaimportowano cala liste
					self.__contact_buffer += in_packet.request #... bo lista moze przyjsc w kilku pakietach
					self.__make_contacts_list(self.__contact_buffer)
					self.__contact_buffer = "" # oprozniamy bufor
					self.on_userlist_reply(self, EventArgs({"contacts_list" : self.__contacts_list}))
				else:
					self.on_userlist_reply(self, EventArgs({"reqtype":in_packet.reqtype, "request":in_packet.request}))

			elif header.type == GGIncomingPackets.GGStatus:
				in_packet = GGStatus()
				with self.__lock:
					in_packet.read(self.__connection, header.length)
				uin = in_packet.uin
				self.__contacts_list[uin].status = in_packet.status
				self.__contacts_list[uin].description = in_packet.description
				self.__contacts_list[uin].return_time = in_packet.return_time
				self.on_status_changed(self, EventArgs({"contact" : self.__contacts_list[uin]}))

			elif header.type == GGIncomingPackets.GGStatus60:
				in_packet = GGStatus60()
				with self.__lock:
					in_packet.read(self.__connection, header.length)
				uin = in_packet.uin
				if self.__contacts_list[uin] == None:
					self.__contacts_list.add_contact(Contact({"uin":in_packet.uin}))
				self.__contacts_list[uin].status = in_packet.status
				self.__contacts_list[uin].description = in_packet.description
				self.__contacts_list[uin].return_time = in_packet.return_time
				self.__contacts_list[uin].ip = in_packet.ip
				self.__contacts_list[uin].port = in_packet.port
				self.__contacts_list[uin].version = in_packet.version
				self.__contacts_list[uin].image_size = in_packet.image_size
				self.on_status_changed(self, EventArgs({"contact" : self.__contacts_list[uin]}))

			else:
				with self.__lock:
					self.__connection.read(header.length) #odbieramy smieci.. ;)
				self.on_unknown_packet(self, EventArgs({"type" : header.type, "length" : header.length}))

			time.sleep(0.1)
	
	def __ping(self):
		"""
		Metoda wysyla pakiet GGPing do serwera
		"""
		if not self.__logged:
			raise GGNotLogged
		with self.__lock:
			out_packet = GGPing()
			out_packet.send(self.__connection)
	

	def login(self):
		"""
		Metoda loguje uzytkownika do sieci gadu-gadu. Parametry podawane sa w konstruktorze.
		"""
		limit = 7 #tyle pobierze nowych serwerow zanim zaprzestanie prob
		times = 0 #ile razy juz pobieral nowy serwer
		with self.__lock:
			while not self.__connected:
				server, port = HTTPServices.get_server(self.__uin)
				try:
					self.__connection = Connection(server, port)
					self.__connected = True
				except GGServerNotOperating:
					times += 1
					if times >= limit:
						self.on_server_not_operating(self, EventArgs({}))
						return
					#else niech pobierze inny serwer i probuje dalej :-)
			
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
				self.on_login_ok(self, EventArgs({}))
				self.__events_thread.start() #uruchamiamy watek listenera
				time.sleep(0.5) #TODO: potrzebne to?
				self.__send_contacts_list()
				#self.change_status(self.__status, self.__description) #ustawienie statusu przy pakiecie GGLogin cos nie dziala :/
			elif header.type == GGIncomingPackets.GGLoginFailed:
				self.on_login_failed(self, EventArgs({}))
			elif header.type == GGIncomingPackets.GGNeedEMail:
				self.on_need_email(self, EventArgs({}))
			elif header.type == GGIncomingPackets.GGDisconnecting:
				self.on_disconnecting(self, EventArgs({}))
			else:
				raise GGUnexceptedPacket((header.type, header.length))

	def logout(self, description = ''):
		"""
		Metoda wylogowuje uzytkownika z sieci gadu-gadu. Ustawiany jest opis zawarty w parametrze description.
		Domyslnie opis pusty.
		"""
		assert type(description) == types.StringType and len(description) <= 70
		
		if not self.__logged:
			raise GGNotLogged
		
		self.change_status(description == '' and GGStatuses.NotAvail or GGStatuses.NotAvailDescr, description)
		#with self.__lock:
		self.__connection.disconnect()
		self.__logged = False # przed join(), zeby zakonczyc watek
		self.__events_thread.join()
		self.__pinger.cancel()
		#self.__connection.disconnect()
		self.__connected = False
	
	def change_status(self, status, description = ""):
		"""
		Metoda powoduje zmiane statusu i opisu. Jako parametry przyjmuje nowy status i nowy opis (domyslnie - opis pusty).
		"""
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
		"""
		Metoda powoduje zmiane opisu. Jako parametr przyjmuje nowy opis.
		"""
		assert type(description) == types.StringType and len(description) <= 70
		
		if self.__status != GGStatuses.AvailDescr and self.__status != GGStatuses.BusyDescr and self.__status != GGStatuses.InvisibleDescr:
			raise GGException("Can't change description - current status has'n description") 
		if not self.__logged:
			raise GGNotLogged
		
		self.change_status(self.__status, description)

	def send_msg(self, rcpt, msg, seq = 0, msg_class = GGMsgTypes.Msg, richtext = False):
		"""
		Metoda sluzy do wysylania wiadomosci w siecie gadu-gadu. Parametry:
		 * rcpt - numer gadu-gadu odbiorcy wiadomosci
		 * msg - wiadomosc do dostarczenia
		 * seq - numer sekwencyjny wiadomosci, sluzy do potwierdzen dostarczenia wiadomosci. Domyslnie wartosc 0
		 * msg_class - klasa wiadomosci (typ GGMsgTypes). Domyslnie wiadomosc pojawia sie w nowym oknie
		 * richtext - okresla czy wiadomosc bedzie interpretowana jako zwykly tekst czy jako tekst formatowany.
		   Domyslnie nieformatowany
		"""
		assert type(rcpt) == types.IntType
		assert type(msg) == types.StringType and ((not richtext and len(msg) < 2000) or (richtext))  #TODO: w dalszych iteracjach: obsluga richtextmsg
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
		"""
		Metoda obslugujaca katalog publiczny. Wysyla zapytanie do serwera. Parametry:
		 * request - zapytanie dla serwera
		 * reqtype - typ zapytania
		"""
		assert type(request) == types.StringType or type(request) == types.DictType
		assert reqtype in GGPubDirTypes
		
		if not self.__logged:
			raise GGNotLogged
			
		with self.__lock:
			out_packet = GGPubDir50Request(request, reqtype)
			out_packet.send(self.__connection)
	
	def export_contacts_list(self, filename = None):
		"""
		Eksportuje liste kontaktow do serwera lub do pliku, w przypadku podania nazwy jako parametr filename
		"""
		while self.__importing == True:
			time.sleep(0.1)
		if self.__contacts_list != None:
			if filename == None:
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
			else:
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
		
		with self.__lock:
			out_packet = GGUserListRequest(GGUserListTypes.Put, "")
			out_packet.send(self.__connection)
		
	def import_contacts_list(self, filename = None):
		"""
		Wysyla zadanie importu listy z serwera lub pliku, gdy podamy jego nazwe w parametrze filename.
		Zaimportowana lista zapisywana jest w self.__contacts_list
		"""
		
		if filename == None:
			if not self.__logged:
				raise GGNotLogged
			with self.__lock:
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
			with self.__lock:
				out_packet = GGAddNotify(contact.uin, user_type)
				out_packet.send(self.__connection)

	def remove_contact(self, uin, notify = True):
		"""
		Usuwamy z listy kontaktow kontakt o numerze 'uin'. Jesli jestesmy polaczeni z serwerem i notify == True to dodatkowo
		powiadamiamy o tym fakcie serwer. Od tego momentu serwer nie bedzie nas juz informowal o statusie tego kontaktu.
		"""
		self.__contacts_list.remove_contact(uin)
		if self.__logged and notify:
			with self.__lock:
				out_packet = GGRemoveNotify(uin)
				out_packet.send(self.__connection)
	
	def change_user_type(self, uin, user_type):
		"""
		Zmieniamy typ uzytkownika. user_type jest mapa wartosci z GGUserTypes.
		Np. zeby zablokowac uzytkownka piszemy:
			change_user_type(12454354, GGUserTypes.Blocked)
		"""
		if not self.__logged:
			raise GGNotLogged

		with self.__lock:
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
			uin_type_list.append((contact.uin, contact.user_type))
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
		if self.__contacts_list == None:
			self.__contacts_list = ContactsList()
		for contact in contacts:
			if contact != '' and contact != "\n":
				newcontact = Contact({'request_string':contact})
				self.add_contact(newcontact)
				
	def __get_logged(self):
		return self.__logged
	
	#
	# Properties
	#
	contacts_list = property(__get_contacts_list, __set_contacts_list)
	logged = property(__get_logged)
