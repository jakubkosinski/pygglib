#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import types
import socket
import struct
import hashlib

#============================
# Enum
#
class Enum(object):
	"""
	Klasa reprezentujaca typ wyliczeniowy.
	Uzycie (np.):
		IncomingPackets = Enum({"GGRecvMsg":0x000a, "GGWelcome":0x0001})
	"""
	def __init__(self, enums = {}):
		self.__lookup = enums
		self.__reverse_lookup = {}
		for k, v in self.__lookup.iteritems():
			self.__reverse_lookup[v] = k
	
	def __getattr__(self, key):
		"""
		Funkcja ta pozwala nam korzystac z klasy w taki sposob (odnosnie przykladu z opisu klasy):
			if packet_type == IncomingPackets.GGRecvMsg: (...)
		Returns: wartosc elementu 'key'
		"""
		if not self.__lookup.has_key(key):
			raise AttributeError
		return self.__lookup[key]
	
	def reverse_lookup(self, value):
		"""
		Funkcja pozwala na sprawdzenie odwrotnej wartosc, czyli np.:
			IncomingPackets.reverse_lookup(0x000a) - zwroci "GGRecvMsg"
		Returns: klucz dla ktorego wartoscia jest 'value'
		"""
		if not self.__reverse_lookup.has_key(value):
			raise AttributeError
		return self.__reverse_lookup[value]
#
# Enum
#========================

#============================
# Obsluga zdarzen
#
class UnknowEventError(AttributeError):
	pass

class UnknowEventHandlerError(AttributeError):
	pass
	
class NotCallableError(Exception):
	pass
	
class Event(object):
	""" Stanowi liste funkcji, ktora mozna wywolac za pomoca: __call__(*args), czyli np.:
		on_msg_recv = Event([f1, f2, f3])
		on_msg_recv() - uruchomi wszytkie funkcje: f1, f2, f2
	"""
	def __init__(self, funs):
		for f in funs:
			if not callable(f):
				raise NotCallableError
		self.__funs = funs
	
	def __call__(self, *args):
		for f in self.__funs:
			apply(f, args)

class EventsList(object):
	def __init__(self, events):
		self.__events = {}
		self.__event_handlers = {} # slownik odwrotny do slownika __events (potrzebne do unregister)
		for e in events:
			self.__events[e] = [] # kazde zdarzenie ma na poczatku pusta liste funkcji
		self.__slots__ = events # innych nie mozna wywolac! Tylko te, ktore na poczatku podalismy
	
	def __getattr__(self, event):
		""" Returns: liste funkcji ktore obsluguja zdarzenie 'event'
		"""
		if not self.__events.has_key(event):
			raise UnknowEventError
		return Event(self.__events[event])
	
	def register(self, event, event_handler):
		if not self.__events.has_key(event):
			raise UnknowEventError
		if not callable(event_handler):
			raise NotCallableError
		self.__events[event].append(event_handler)
		self.__event_handlers[event_handler] = event
	
	def unregister(self, event, event_handler):
		if not self.__event_handlers.has_key(event_handler):
			raise UnknowEventHandler
		del self.__event_handlers[event_handler] # usuwamy handlera ze slownika odwrotnego
		del self.__events[event][self.__events[event].index(event_handler)] # i usuwamy handlera z listy funkcji zdarzeia
#
# Oblsuga zdarzen
#========================

	
def gg_login_hash(password, seed):
	assert type(password) == types.StringType
	#assert type(seed) == types.IntType
	x = 0L
	y = long(seed)
	z = 0L
	for c in password:
		x = (x & 0xffffffffL) | ord(c)
		y ^= x
		y &= 0xffffffffL
		y += x
		y &= 0xffffffffL
		x <<= 8
		x &= 0xffffffffL
		y ^= x
		y &= 0xffffffffL
		x <<= 8
		x &= 0xffffffffL
		y -= x
		y &= 0xffffffffL
		x <<= 8
		x &= 0xffffffffL
		y ^= x
		y &= 0xffffffffL
		z = y & 0x1f
		y = (y << z) | (y >> (32 - z))
		y &= 0xffffffffL
	return y
	#return struct.pack("<I60s", y, str(0x00))[0]
	#return hashlib.sha1(password).digest()



def ip_to_int32(ip):
	assert type(ip) == types.StringType
	return struct.unpack("<I", socket.inet_aton(ip))[0]

