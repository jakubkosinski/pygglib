#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import struct
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
	"GGNotifyReply":0x000c, #Stan listy kontaktow przed GG 6.0
	"GGPubDir50Reply":0x000e, #Odpowiedz katalogu publicznego
	"GGStatus60":0x000f, #Zmiana stanu
	"GGUserListReply":0x0010, #Odpowiedz listy kontaktow na serwerze
	"GGNotifyReply60":0x0011, #Stan listy kontaktow
	"GGNeedEMail":0x0014 #Logowanie powiodlo sie, ale powinnismy uzupelnic adres e-mail w katalogu publicznym
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
		structure = struct.unpack("<III", connection.read(12))
		self.status = structure[0]
		self.recipient = structure[1]
		self.seq = structure[2]

		
class GGNotifyReply(GGIncomingPacket):
	"""
	Odpowiedz serwera na pakiety GGNotifyFirst i GGNotifyLast.
	Zawiera liste struktur postaci:
		
	"""
	pass #TODO