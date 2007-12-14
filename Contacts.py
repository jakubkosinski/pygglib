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
	"""
	#
	# Pola, o ktorych informacje dostajemy z serwera GG
	#
	status = GGStatuses.NotAvail #aktualny status uzytkownika
	ip = 0 #ip DCC
	port = 0 #port DCC
	version = None #wersja klienta
	image_size = 0 #maksymalna wielkosc obrazka
	descriptiption = ""
	
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
	

class ContactsList(object):
	"""
	Klasa reprezentujaca liste kontaktow GG
	TODO: eksport listy kontaktow, import (tutaj?)
	"""
	def __init__(self):
		self.__contacts = {}
	
	def add_contact(self, contact):
		assert type(contact) == Contact
		self.__contacts[contact.uin] = contact
	
	def __getitem__(self, uin):
		if not self.__contacts.has_key(uin):
			raise GGNotInContactsList(repr(uin))
		
		return self.__contacts[uin]
		