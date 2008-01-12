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
	description = ""
	type = GGUserTypes.Normal
	
	def __init__(self, params):
		assert type(params) == types.DictType
		if params.has_key('request_string'):
			if params['request_string'] == '':
				pass
			self.name, self.surname, self.nick, self.shown_name, self.mobilephone, self.group, self.uin, self.email, self.available, self.available_source, self.message, self.message_source, self.hidden, self.telephone = params['request_string'].split(";")
			if self.available == "":
				self.available = 0
			else:
				self.available = int(self.available)
			if self.message == "":
				self.message = 0
			else:
				self.message = int(self.message)
			if self.hidden == "":
				self.hidden = 0
			else:
				self.hidden = int(self.hidden)
		else:
			self.uin = params['uin']
			if params.has_key('name'):
				self.name = params['name']
			if params.has_key('surname'):
				self.surname = params['surname']
			if params.has_key('nick'):
				self.nick = params['nick']
			if params.has_key('shown_name'):
				self.shown_name = str(repr(params['uin']))
			else:
				self.shown_name = params['shown_name']
			if params.has_key('mobilephone'):
				self.mobilephone = str(params['mobilephone'])
			if params.has_key('group'):
				self.group = params['group']
			if params.has_key('email'):
				self.email = params['email']
			if params.has_key('available'):
				self.available = int(params['available'])
			if params.has_key('available_source'):
				self.available_source = params['available_source']
			if params.has_key('message'):
				self.message = int(params['message'])
			if params.has_key('message_source'):
				self.message_source = params['message_source']
			if params.has_key('hidden'):
				self.hidden = int(params['hidden'])
			if params.has_key('telephone'):
				self.telephone = str(params['telephone'])
		
	def request_string(self):
		return ";".join([self.name, self.surname, self.nick, self.shown_name, self.mobilephone, self.group, str(self.uin), self.email, str(self.available), self.available_source, str(self.message), self.message_source, str(self.hidden), self.telephone])
	

class ContactsList(list):
	"""
	Klasa reprezentujaca liste kontaktow GG
	"""
	def __init__(self, contacts = []):
		assert type(contacts) == types.ListType or types.StringType
		if type(contacts) == types.ListType:
			for c in contacts:
				assert type(c) == Contact
			self.data = contacts
		else:
			list = contacts.split("\n")
			tmp = []
			for c in list:
				if c != "" and c != "GG70ExportString,;":
					tmp.append({'request_string':c})
			clist = []
			for c in tmp:
				clist.append(Contact(c))
			self.data = clist
	
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
	
	def export_request_string(self):
		return "\n".join(map(Contact.request_string, self.data))
		
	
		