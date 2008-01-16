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
	Klasa reprezentujaca pojedynczy kontakt. Zawiera nastepujace pola (wszystkie publiczne):
		* uin - numer uzytkownika
		* name - imie uzytkownika
		* surname - nazwisko uzytkownika
		* shown_name - nazwa wyswietlana
		* nick - pseudonim uzytkownika
		* mobilephone - numer telefonu komorkowego
		* group - nazwa grupy
		* email - adres email uzytkownika
		* available - okresla dzwieki zwiazane z pojawieniem sie danej osoby i przyjmuje wartosci 0 (uzyte zostana ustawienia globalne), 
			1 (dzwiek powiadomienia wylaczony) lub 2 (zostanie odtworzony plik okreslony w polu available_source)
		* available_source - sciezka do pliku opisanego wyzej
		* message - dziala podobnie do available, z tym, ze okresla dzwiek przychodzacej wiadomosci
		* message_source - sciezka do dzwieku odgrywanego przy otrzymaniu wiadomosci (opis powyzej)
		* hidden - okresla, czy bedziemy dostepni (0) czy niedostepni (1) dla danej osoby w trybie 'tylko dla znajomych'
		* telephone - numer telefonu
	Powyzsze pola mozemy przekazac w konstruktorze klase w formie slownika na dwa sposoby. Pierwszy z nich podaje slownik z kluczami 
	o nazwach wlasciwosci (jedynym wymaganym kluczem jest 'uin') badz w formacie z slownika z kluczem 'request_string' o wartosci postaci:
	name;surname;nick;shown_name;mobilephone;group;uin;email;available;available_source;message;message_source;hidden;telephone
	Oprocz powyzszych pol, klasa posiada jeszcze pola modyfikowane przez klasy GGNotifyReply oraz GGStatus:
		* status - status uzytkownika
		* ip - adres IP uzytkownika do bezposrednich polaczen
		* port - port do bezposrednich polaczen
		* version - wersja klienta
		* image_size - maksymalny rozmiar przyjmowanej grafiki
		* description - opis (moze byc pusty)
		* return_time - data powrotu uzytkownika (jesli nie ma, to = 0)
		* user_type - typ uzytkownika (z klasy GGUserTypes)

	Przyklady uzycia:
		1. Contact({'uin':12345, 'name':'Tola', 'shown_name':'Tola', 'hidden':1, 'message':2, 'message_source':'/home/user/message.wav'})
		Utworzy kontakt o numerze 12345, nazwie 'Tola', wyswietlanej nazwie 'Tola', ukryty w trybie 'tylko dla znajomych' oraz ze zdefiniowanym
		dzwiekiem odgrywanym podczas przychodzacej wiadomosci

		2. Contact({'request_string':'Tola;;;Tola;;;12345;;0;1;/home/user/message.wav;1;'})
		Utworzy kontakt jak wyzej.
	"""
	status = GGStatuses.NotAvail
	ip = 0
	port = 0
	version = None
	image_size = 0
	description = ""
	return_time = 0
	user_type = GGUserTypes.Normal
	
	def __init__(self, params):
		assert type(params) == types.DictType
		if params.has_key('request_string'):
			self.name, self.surname, self.nick, self.shown_name, self.mobilephone, self.group, self.uin, self.email, self.available, self.available_source, self.message, self.message_source, self.hidden, self.telephone = params['request_string'].split(";")
			self.uin = int(self.uin)
			if self.shown_name == "":
				self.shown_name = str(self.uin)
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
			self.uin = int(params['uin'])
			if params.has_key('name'):
				self.name = params['name']
			else:
				self.name = ""
			if params.has_key('surname'):
				self.surname = params['surname']
			else:
				self.surname = ""
			if params.has_key('nick'):
				self.nick = params['nick']
			else:
				self.nick = ""
			if params.has_key('shown_name'):
				self.shown_name = params['shown_name']
			else:
				self.shown_name = str(repr(params['uin']))
			if params.has_key('mobilephone'):
				self.mobilephone = str(params['mobilephone'])
			else:
				self.mobilephone = ""
			if params.has_key('group'):
				self.group = params['group']
			else:
				self.group = ""
			if params.has_key('email'):
				self.email = params['email']
			else:
				self.email = ""
			if params.has_key('available'):
				self.available = int(params['available'])
			else:
				self.available = 0
			if params.has_key('available_source'):
				self.available_source = params['available_source']
			else:
				self.available_source = ""
			if params.has_key('message'):
				self.message = int(params['message'])
			else:
				self.message = 0
			if params.has_key('message_source'):
				self.message_source = params['message_source']
			else:
				self.message_source = ""
			if params.has_key('hidden'):
				self.hidden = int(params['hidden'])
			else:
				self.hidden = 0
			if params.has_key('telephone'):
				self.telephone = str(params['telephone'])
			else:
				self.telephone = ""
		
	def request_string(self):
		return ";".join([self.name, self.surname, self.nick, self.shown_name, self.mobilephone, self.group, str(self.uin), self.email, str(self.available), self.available_source, str(self.message), self.message_source, str(self.hidden), self.telephone])
	

class ContactsList(list):
	"""
	Klasa reprezentujaca liste kontaktow GG. Wpisy sa obiektami klast Contact. Konstruktor przyjmuje dwa rodzaje parametrow.
	Pierwszy z nich to lista obiektow typu Contact, drugi to zawartosc pliku z kontaktami (wartosci oddzielone srednikami, opis w klasie Contact)
	Dostep do kontaktow realizowany jest za pomoca uin, np. list['12345'] zwroci obiekt Contact o uin=12345 lub None w przypadku, gdy kontaktu
	nie ma na liscie.
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
		"""
		Metoda dodajaca kontakt. Jako parametr przyjmuje obiekt klasy Contact lub napis w formacie pliku kontaktow Gadu-Gadu.
		"""
		if type(contact) == types.StringType:
			c = Contact(contact)
		elif type(contact) == Contact:
			c = contact
		else:
			raise AssertionError
		
		if self[c.uin] != None:
			x = self[c.uin]
			self.data.remove(x)
			self.add_contact(c)
		else:
			self.data.append(c)
	
	def remove_contact(self, uin):
		"""
		Metoda usuwajaca kontakt o numerze uin z listy. W przypadku, gdy na liscie nie ma kontaktu o podanym uin wyrzucany jest wyjatek KeyError.
		"""
		contact = self[uin]
		if contact == None:
			raise KeyValue(uin)
		else:
			self.data.remove(contact)

	def __index_by_uin(self, uin):
		i = 0
		for c in self.data:
			if int(c.uin) == int(uin):
				return i
			i += 1
		return -1
	
	def __getitem__(self, uin):
		index = self.__index_by_uin(uin)
		if index == -1:
			return None
		else:
			return self.data[index]
	
	def __len__(self):
		return len(self.data)

	def __contains__(self, contact):
		"""
		Sprawdza czy dany kontakt jest na liscie kontaktow
		parametr:
			* contact (typu Contact lub integer)
		uzycie:
			* if 3932154 in contacts_list:
				pass
			* c = Contact({"uin":423543, "shown_name":"Juzefina})
			  if c in contacts_list:
			  	pass
		"""
		if type(contact) == types.IntType:
			return self[contact] != None
		elif type(contact) == Contact:
			return self.data.__contains__(contact)
		else:
			raise AssertionError
	
	def export_request_string(self):
		"""
		Metoda zwracajaca cala liste kontaktow w formacie pliku kontaktow Gadu-Gadu. Kazda linia reprezentuje jeden kontakt.
		"""
		return "\n".join(map(Contact.request_string, self.data))
		
	
		
