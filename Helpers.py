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
import re

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
		attributes = []
		for x in self.__reverse_lookup.keys():
			if int(x) & int(value):
				attributes.append(self.__reverse_lookup[x])
		return ",".join(attributes)
	
	def reverse_lookup_without_mask(self,value):
		if not self.__reverse_lookup.has_key(value):
			raise AttributeError(value)
		return self.__reverse_lookup[value]
	
	def __contains__(self, value):
		"""
		Sprawdza, czy wartosc znajduje sie w Enumie, np.:
		if 0x002 in GGStatuses:
			[...]
		"""
		return self.__reverse_lookup.has_key(value)
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
		del self.__events[event][self._events[event].index(event_handler)] # i usuwamy handlera z listy funkcji zdarzeia
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

def gg_http_hash(email,pwd):
	"""
	Zwraca hash z emaila oraz hasla, potrzebny przy rejestracji i usuwaniu konta
	"""
	a = 0
	b = -1
	
	for c in email:
		a = (ord(c) ^ b) + ((ord(c) << 8) & 0xffffffff);
		b = (a >> 24) | ((a << 8) & 0xffffffff);
	
	for c in pwd:
		a = (ord(c) ^ b) + ((ord(c) << 8) & 0xffffffff);
		b = (a >> 24) | ((a << 8) & 0xffffffff);

	return int(abs(b))


def ip_to_int32(ip):
	assert type(ip) == types.StringType
	return struct.unpack("<I", socket.inet_aton(ip))[0]

def split_list(xs, size):
	"""
	Dzieli liste 'xs' na podlisty. Kazda z nich, oprocz ostatniej, ma dlugosc 'size'.
	Ostatnia podlista ma dlugosc <= 'size'.
	Returns: liste podlist
	"""
	import math
	ret = []
	ret_size = int(math.ceil(len(xs)/float(size)))
	for i in range(ret_size):
		ret.append(xs[(i*size):((i+1)*size)])
	return ret

def dict_to_request(hash):
	"""
	Zamienia slownik parametrow zapytania do katalogu publicznego na format rozpoznawany przez serwer Gadu-Gadu
	"""
	assert type(hash) == types.DictType
	
	request = ""
	for x in hash:
		request += str(x) + "\0" + str(hash[x]) + "\0"
		
	return request
	
def request_to_dict(request):
	"""
	Zamienia parametry zapytania do katalogu publicznego rozpoznawane przez serwer Gadu-Gadu na slownik postaci nazwa_parametru:wartosc
	"""
	assert type(request) == types.StringType
	
	list = request.split("\0")
	tuples = []
	i = 0
	while i < len(list) - 1:
		tuples.append((list[i],list[i+1]))
		i += 2
	return dict(tuples)

def pygglib_rtf_to_gg_rtf(rtf_msg):
	"""
	Konwertuje tekst z formatu pygglib richtext do formatu Gadu-Gadu richtext.
		pygglib richtext: <b>Ala <i><u>ma</u></i></b><color red=123 green=143 blue=123> KOTA</color>
		Gadu-Gadu richtext: /patrz opis protokolu Gadu-Gadu (http://ekg.chmurka.net/docs/protocol.html#ch1.6)
	"""
	plain_text = "" #czysty tekst, bez formatowania (GG richtext zaczyna sie od czystego tekstu)
	format_string = "" #ciag formatujacy plain_text (patrz. opis protokolu)
	
	regexp = re.compile(r'<(/?(color|i|b|u)[^>]*)>')
	colors_regexp = re.compile(r'color\s+red=(?P<red>[0-9]{1,3})\s+green=(?P<green>[0-9]{1,3})\s+blue=(?P<blue>[0-9]{1,3})')
	
	markups_length = 0 #laczna dlugosc wszystkich znacznikow (potrzebne do oznaczania pozycji formatowanego tekstu)
	flags = 0x0
	for format in regexp.finditer(rtf_msg):
		markup = format.groups(0)[0]
		markups_length += len(markup) + 2

		colors_match = colors_regexp.match(markup)
		if markup == 'b':
			format_string += struct.pack('<HB', format.end(0) - markups_length, flags | 0x01)
		elif markup == 'i':
			format_string += struct.pack('<HB', format.end(0) - markups_length, flags | 0x02)
		elif markup == 'u':
			format_string += struct.pack('<HB', format.end(0) - markups_length, flags | 0x04)
		elif colors_match is not None:
			red = int(colors_match.group('red'))
			green = int(colors_match.group('green'))
			blue = int(colors_match.group('blue'))
			format_string += struct.pack('<HBBBB', format.end(0) - markups_length, flags | 0x08, red, green, blue)
			
		elif markup == '/b':
			format_string += struct.pack('<HB', format.end(0) - markups_length, flags ^ 0x01)
		elif markup == '/i':
			format_string += struct.pack('<HB', format.end(0) - markups_length, flags ^ 0x02)
		elif markup == '/u':
			format_string += struct.pack('<HB', format.end(0) - markups_length, flags ^ 0x04)
		elif markup == '/color':
			format_string += struct.pack('<HB', format.end(0) - markups_length, flags ^ 0x08)
		else:
			pass
	
	plain_text = re.sub(r'</?(color|i|b|u)[^>]*>', '', rtf_msg) #usuwamy znaczniki formatowania
	return struct.pack('<%dsBH%ds' % (len(plain_text) + 1, len(format_string)), plain_text, 0x02, len(format_string), format_string) #TODO: +1?????

def gg_rtf_to_pygglib_rtf(rtf_msg):
	"""
	Konwertuje tekst z formatu Gadu-Gadu richtext do formatu pygglib richtext.
		pygglib richtext: <b>Ala <i><u>ma</u></i></b><color red=123 green=143 blue=123> KOTA</color>
		Gadu-Gadu richtext: /patrz opis protokolu Gadu-Gadu (http://ekg.chmurka.net/docs/protocol.html#ch1.6)
	"""
	try:
		index = rtf_msg.index('\x02')
	except ValueError:
		return rtf_msg
	plain_text, format_string = rtf_msg[:index], rtf_msg[index:]
	#TODO: skonczyc....

#if __name__ == "__main__":
#	pygglib_rtf_to_gg_rtf("<b>Ala <i>ma</i></b><color red=123 green=143 blue=123> KOTA</color>")
	
