#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

from GGConstans import *
from Exceptions import *
import types

class Contact(object):
	"""
	Klasa reprezentujaca jedna osobe na liscie kontaktow
	TODO: konstruktor niech przyjmuje wszystkie parametry (domyslnie None, oprocz uinu)
	"""
	#
	# Pola, o ktorych informacje dostajemy z serwera GG
	#
	status = GGStatuses.NotAvail #aktualny status uzytkownika
	ip = 0 #ip DCC
	port = 0 #port DCC
	version = None #wersja klienta
	image_size = 0 #maksymalna wielkosc obrazka
	description = ""
	type = GGUserTypes.Normal
	
	#
	# Pola, o ktorych informacje dostarcza uzytkownik biblioteki
	#
	name = "" #imie
	surname = "" #nazwisko
	nick = "" #pseudonim
	shown_name = "" #nazwa wyswietlana
	
	def __init__(self, uin):
		self.uin = uin
		self.shown_name = repr(uin)
	

class ContactsList(list):
	"""
	Klasa reprezentujaca liste kontaktow GG
	TODO: eksport listy kontaktow, import (tutaj?)
	"""
	def __init__(self, contacts = []):
		assert type(contacts) == types.ListType
		for c in contacts:
			assert type(c) == Contact
		self.data = contacts
	
	def add_contact(self, contact):
		assert type(contact) == Contact
		self.data.append(contact)
	
	def __index_by_uin(self, uin):
		i = 0
		for c in self.data:
			if c.uin == uin:
				return i
			i += 1
		return -1
	
	def __getitem__(self, uin):
		index = self.__index_by_uin(uin)
		if index == -1:
			raise GGNotInContactsList(repr(uin))
		else:
			return self.data[index]
	
	def __len__(self):
		return len(self.data)
	
	
		