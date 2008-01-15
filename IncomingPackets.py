#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import struct
from Contacts import *
from Helpers import Enum

GGIncomingPackets = Enum({
	"GGWelcome":0x0001, #Poczatek komunikacji z serwerem - przychodzi seed potrzebny do zalogowania sie
	"GGStatus": 0x0002, #Zmiana stanu przed GG 6.0
	"GGLoginOK":0x0003, #Logowanie sie powiodlo
	"GGSendMsgAck":0x0005, #Potwierdzenie wiadomosci
	"GGPong":0x0007, #Pong
	"GGLoginFailed":0x0009, #Logowanie sie nie powiodlo
	"GGRecvMsg":0x000a, # Przyszla nowa wiadomosc
	"GGDisconnecting":0x000b, #Zerwanie polaczenia
	"GGNotifyReplyOld":0x000c, #Stan listy kontaktow przed GG 6.0
	"GGPubDir50Reply":0x000e, #Odpowiedz katalogu publicznego
	"GGUserListReply":0x0010, #Odpowiedz listy kontaktow na serwerze
	"GGNotifyReply60":0x0011, #Stan listy kontaktow
	"GGNeedEMail":0x0014, #Logowanie powiodlo sie, ale powinnismy uzupelnic adres e-mail w katalogu publicznym
	"GGNotifyReply77":0x0018, # Stan listy kontaktow (GG 7.0)
	"GGStatus":0x0002, # Zmiana statusu uzytkownika z listy kontaktow
	"GGStatus60":0x000f # jw. (wersja > 6)
	})

class GGIncomingPacket(object):
	"""
	"Abstrakcyjna" klasa pakietow przychodzacych od serwera
	"""
	def read(self, connection, size):
		pass


class GGWelcome(GGIncomingPacket):
	"""
	Pakiet wysylany przez serwer zaraz po nawiazaniu polaczenia.
	Znajduje sie w nim 'seed' konieczny do zalogowania sie do serwera.
	"""
	def __init__(self):
		self.seed = None
	
	def read(self, connection, size):
		self.seed = struct.unpack("<I", connection.read(size))[0]

class GGLoginOK(GGIncomingPacket):
	"""
	Pakiety wysylany przez serwer w przypadku pomyslnego zalogowania sie.
	Czasem ma dane dlugosci 1 (0x1f), a czasem nic nie ma...
	"""
	def __init__(self):
		pass
	
	def read(self, connection, size):
		connection.read(size)
		
class GGRecvMsg(GGIncomingPacket):
	"""
	Pakiet przychodzacej wiadomosci. Jego struktura jest nastepujaca:
		int sender -- numer nadawcy
		int seq -- numer sekwencyjny
		int time -- czas nadania
		int class -- klasa wiadomosci
		string -- tresc wiadomosci
	"""
	def __init__(self):
		pass
	
	def read(self, connection, size):
		structure = struct.unpack("<IIII%ds" % (size - 16), connection.read(size))
		self.sender = structure[0]
		self.seq = structure[1]
		self.time = structure[2]
		self.msg_class = structure[3]
		self.message = structure[4]

class GGSendMsgAck(GGIncomingPacket):
	"""
	Pakiet ten serwer do nas przesyla zaraz po wyslaniu wiadomosci. Jego struktura jest nastepujaca:
		int status -- stan wiadomosci
		int recipient -- numer odbiorcy
		int seq	-- numer sekwencyjny
	"""
	def __init__(self):
		pass
	
	def read(self, connection, size):
		structure = struct.unpack("<III", connection.read(size))
		self.status = structure[0]
		self.recipient = structure[1]
		self.seq = structure[2]


class GGNotifyReplyOld(GGIncomingPacket):
	"""
	___Pakiet dla starych wersji klientow___
	Odpowiedz serwera na pakiety GGNotifyFirst i GGNotifyLast.
	Zawiera liste struktur postaci:
		int uin -- numer
		char status -- status danej osoby
		int remote_ip -- adres ip delikwenta
		short remote_port -- port, na ktorym slucha klient
		int version -- wersja klienta
		string description -- opis, nie musi wystapic
		int time -- czas, nie musi wystapic
	"""
	def __init__(self, contacts):
		assert type(contacts) == ContactsList
		self.__contacts = contacts
	
	def read(self, connection, size):
		raise NotImplemented

	def __get_contacts(self):
		return self.__contacts
	
	contacts = property(__get_contacts)


class GGNotifyReply(GGIncomingPacket):
	"""
	Odpowiedz serwera na pakiety GGNotifyFirst i GGNotifyLast.
	Zawiera liste struktur postaci:
		int uin -- numer
		char status -- status danej osoby
		int ip -- adres ip osoby
		short port -- port, na ktorym slucha klient
		int version -- wersja klienta
		string description -- opis, nie musi wystapic
		int return_time -- czas, nie musi wystapic
	"""
	def __init__(self, contacts, notify_reply_version = GGIncomingPackets.GGNotifyReply60):
		"""
		Domyslnie odbieramy pakiet starszy - GGNotifyReply60
		"""
		assert type(contacts) == ContactsList
		assert notify_reply_version == GGIncomingPackets.GGNotifyReply60 or notify_reply_version == GGIncomingPackets.GGNotifyReply77
		self.notify_reply_version = notify_reply_version
		if contacts == None:
			self.__contacts = ContactsList()
		else:
			self.__contacts = contacts
	
	def read(self, connection, size):
		dummy_size = (self.notify_reply_version == GGIncomingPackets.GGNotifyReply60 and 1 or 4)
		
		count = 0 #ile juz odebralismy bajtow
		finish = False #czy juz konczymy odbieranie
		
		while not finish:
			tuple = struct.unpack("<IBIHBB%dx" % (dummy_size,), connection.read(13 + dummy_size))
			count += 13 + dummy_size
			status = tuple[1]
			uin = (tuple[0] & 0x00ffffff)#bierzemy UIN, maske odrzucamy
			if self.__contacts[uin] == None:
				self.__contacts.add_contact(Contact({'uin':uin}))
			self.__contacts[uin].uin = uin
			self.__contacts[uin].status = tuple[1]
			self.__contacts[uin].ip = tuple[2]
			self.__contacts[uin].port = tuple[3]
			self.__contacts[uin].version = tuple[4]
			self.__contacts[uin].image_size = tuple[5]
			
			#czy status jest opisowy? Jesli nie, to znaczy, ze dalej zaczyna sie info o kolejnym numerku
			if status == GGStatuses.AvailDescr or status == GGStatuses.NotAvailDescr or status == GGStatuses.BusyDescr or status == GGStatuses.InvisibleDescr:
				# zostala jeszcze na pewno dlugosc opisu i opis (moze tez czas)
				tuple = struct.unpack("<B", connection.read(1))
				count += 1
				desc_size = tuple[0]
				if desc_size <=4:
					tuple = struct.unpack("<%ds" % (desc_size,), connection.read(desc_size))
					self.__contacts[uin].description = tuple[0]
					count += desc_size
				else:
					tuple = struct.unpack("<%ds" % ((desc_size - 4),), connection.read(desc_size - 4)) 	#bo zaraz sprawdzimy czy ostatnim bajtem w tuple[0] jest 0x00.
					count += desc_size - 4
																									#jesli tak, to znaczy, ze na koncu jest czas. Jesli nie, to znaczy, ze
																									#dalsze 4 bajty, to dalsza czesc opisu
					description = tuple[0]	
					if ord(description[len(description)-1]) == 0x00: # 4 kolejne bajty, to czas
						description.replace(chr(0x00), '') #usuwamy 0x00
						tuple = struct.unpack("<I", connection.read(4))
						count += 4
						self.__contacts[uin].description = description
						self.__contacts[uin].return_time = tuple[0]
					else: #4 kolejne bajty, to koncowka opisu
						tuple = struct.unpack("4s", connection.read(4))
						count += 4
						description += tuple[0]
						self.__contacts[uin].description = description
						self.__contacts[uin].return_time = 0
			
			if count >= size:
				finish = True

	def __get_contacts(self):
		return self.__contacts
	
	contacts = property(__get_contacts)
				
class GGPubDir50Reply(GGIncomingPacket):
	"""
	Odpowiedz serwera na pakiet GGPubDir50Request o nastepujacej strukturze:
		char reqtype    -- typ odpowiedzi
		int seq      -- numer sekwencyjny
		char[] reply -- wyniki wyszukiwania w formacie "parametr\0wartosc\0", poszczegolne osoby oddzielone sa pustym polem ("\0")
	Przyklad odpowiedzi zawierajacej dwie osoby (znaki "\0" zamienione zostaly na znak "."):
		FmNumber.12345.FmStatus.1.firstname.Adam.nickname.Janek.birthyear.1979.city.Wzdow..FmNumber.32123.FmStatus.5.
		firstname.Ewa.nickname.Ewcia.birthyear.1982.city.Gdansk..nextstart.0.
	Odpowiedz katalogu nie zawiera nazwisk oraz plci znalezionych osob.
	"""
	def __init__(self):
		pass
	
	def read(self, connection, size):
		structure = struct.unpack("<BI%ds" % (size - 5), connection.read(size))
		self.reqtype = structure[0]
		self.seq = structure[1]
		self.reply = structure[2]
		
class GGDisconnecting(GGIncomingPacket):
	"""
	Pusty pakiet, ktory serwer wysyla, gdy chce nas rozlaczyc. Ma to miejsce,
	gdy probowano polaczyc sie z nieprawidlowym haslem lub gdy rownoczesnie
	polaczy sie drugi klient z tym samym numerem
	"""
	def __init__(self):
		pass
		
	def read(self, connection, size):
		connection.read(size)
		
class GGUserListReply(GGIncomingPacket):
	"""
	Odpowiedz serwera na pakiet GGUserListRequest
	TODO: poprawki, bo ta metoda nie dziala dobrze (w przypadku, gdy request jest pusty, a moze sie tak zdarzyc)
	"""
	def __init__(self):
		pass
	
	def read(self, connection, size):
		if size == 1:
			self.reqtype = struct.unpack("<B", connection.read(size))[0]
			self.request = ""
		else:
			structure = struct.unpack("<B%ds" % (size - 1), connection.read(size))
			self.reqtype = structure[0]
			self.request = structure[1]
	
class GGStatus(GGIncomingPacket):
	"""
	Pakiet informujacy o zmianie statusu uzytkownika na liscie kontaktow
	"""
	def __init__(self):
		pass

	def read(self, connection, size):
		if size == 8:
			structure = struct.unpack("<II", connection.read(size))
			self.uin = structure[0] & 0x00ffffff # TODO: to moze byc niepotrzebne
			self.status = structure[1]
			self.description = ""
			self.return_time = 0
		else:
			structure = struct.unpack("<II%ds" % (size - 8), connection.read(size))
			self.uin = structure[0] & 0x00ffffff
			self.status = structure[1]
			self.description = structure[2]
			if len(self.description) <= 4:
				self.return_time = 0
			elif ord(structure[2][-5]) == 0:
				tuple = struct.unpack("<%dsxI" % (len(self.description) - 5), self.description)
				self.description = tuple[0]
				self.return_time = tuple[1]

class GGStatus60(GGIncomingPacket):
	"""
	Pakiet informujacy o zmianie statusu uzytkownika na liscie kontaktow (dla wersji klienta > 6.0)
	"""
	def __init__(self):
		pass

	def read(self, connection, size):
		if size == 14:
			structure = struct.unpack("<IBIHBBx", connection.read(size))
			self.uin = structure[0] & 0x00ffffff
			self.status = structure[1]
			self.ip = structure[2]
			self.port = structure[3]
			self.version = structure[4]
			self.image_size = structure[5]
			self.description = ""
			self.return_time = 0
		else:
			structure = struct.unpack("<IBIHBBx%ds" % (size - 14), connection.read(size))
			self.uin = structure[0] & 0x00ffffff
			self.status = structure[1]
			self.ip = structure[2]
			self.port = structure[3]
			self.version = structure[4]
			self.image_size = structure[5]
			self.description = structure[6]
			if len(self.description) <= 4:
				self.return_time = 0
			elif ord(structure[6][-5]) == 0:
				tuple = struct.unpack("<%dsxI" % (len(self.description) - 5), self.description)
				self.description = tuple[0]
				self.return_time = tuple[1]

