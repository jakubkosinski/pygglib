#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import struct

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
	
	def read(self, connection):
		self.seed = struct.unpack("<I", connection.read(4))[0]

class GGRecvMsg(GGIncomingPacket):
	"""
	Pakiet przychodzacej wiadomosci. Jego struktura jest nastepujaca:
		int sender;		/* numer nadawcy */
		int seq;		/* numer sekwencyjny */
		int time;		/* czas nadania */
		int class;		/* klasa wiadomosci */
		char message[];	/* tresc wiadomosci */
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