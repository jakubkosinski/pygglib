#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import urllib
import urllib2
import types
import time
import random
import Helpers

class Token(object):
	"""
	Klasa reprezentujaca dane tokena potrzebnego do rejestracji konta Gadu-Gadu
	"""
	def __init__(self, width, height, length, id, url):
		self.__width = width
		self.__height = height
		self.__length = length
		self.__id = id
		self.__url = url
		
	def __get_width(self):
		return self.__width
		
	def __get_height(self):
		return self.__height
		
	def __get_length(self):
		return self.__lenght
		
	def __get_id(self):
		return self.__id
		
	def __get_url(self):
		return self.__url
		
	width = property(__get_width)
	height = property(__get_height)
	length = property(__get_length)
	id = property(__get_id)
	url = property(__get_url)

class HTTPServices(object):
	
	def get_server(self,uin):
		"""
		Metoda pobiera z serwerow Gadu-Gadu adres serwera oraz port, na ktorym nasluchuje
		"""
		assert type(uin) == types.IntType
		
		url = 'http://appmsg.gadu-gadu.pl/appsvc/appmsg4.asp?fmnumber=' + str(uin) + '&version=7,7,0,3315&lastmsg=0'
		user_agent = 'Mozilla/4.7 [en] (Win98; I)'

		request = urllib2.Request(url)
		request.add_header('User-Agent', user_agent)
		
		response = urllib2.urlopen(request)
		info = response.read().split(' ')
		server = info[2].split(':')[0]
		port = info[2].split(':')[1]
		return server, int(port)
		
	def get_token_data(self):
		"""
		Metoda pobiera z serwera Gadu-Gadu dane tokena potrzebnego do rejestracji konta. Zwraca obiekt typu Token
		"""
		url = 'http://register.gadu-gadu.pl/appsvc/regtoken.asp'
		user_agent = 'Mozilla/4.0 (compatible; MSIE 5.0; Windows 98)'
		
		request = urllib2.Request(url)
		request.add_header('User-Agent', user_agent)
		
		response = urllib2.urlopen(request)
		info = response.read().replace('\r\n',' ').split(' ')
		width, height, length, id, url = info
		return Token(width, height, length, id, url + '?tokenid=' + id)

	def register_account(self, pwd, email, tokenid, tokenval):
		"""
		Metoda rejestruje nowe konto w sieci Gadu-Gadu. Przyjmuje nastepujace parametry:
			* pwd - haslo uzytkownika
			* email - email uzytkownika, sluzacy do odzyskiwania hasla
			* tokenid - ID tokena pobranego metoda get_token_data
			* tokenval - tresc z obrazka tokena
		Zwraca przydzielony numer konta. W przypadku blednych danych tokena rzucany jest wyjatek
		"""
		code = Helpers.gg_http_hash(email, pwd)
		url = 'http://register.gadu-gadu.pl/appsvc/fmregister3.asp'
		user_agent = 'Mozilla/4.0 (compatible; MSIE 5.0; Windows 98)'
		data = urllib.urlencode({'pwd' : pwd, 'email' : email, 'tokenid' : tokenid, 'tokenval' : tokenval, 'code' : code})
		
		request = urllib2.Request(url, data)
		request.add_header('User-Agent', user_agent)
		
		response = urllib2.urlopen(request)
		text = response.read()
		if text == 'bad_tokenval':
			raise Exception('HTTPServices.register_account: Bad tokenval')
		uin = text[text.find(':')+1:len(text)]
		return uin
		
	def delete_account(self, fmnumber, fmpwd, tokenid, tokenval):
		"""
		Metoda usuwa konto o numerze fmnumber z serwerow Gadu-Gadu. Przyjmuje nastepujace parametry:
			* fmnumber - numer Gadu-Gadu do usuniecia
			* fmpwd - haslo do numeru
			* tokenid - ID tokena pobranego metoda get_token_data
			* tokenval - tresc z obrazka tokena
		Zwraca True gdy numer zostanie usuniety lub False w przeciwnym wypadku
		"""
		code = Helpers.gg_http_hash('deleteaccount@gadu-gadu.pl', fmpwd)
		random.seed(int(time.time()))
		pwd = random.randint(0,0xffff)
		url = 'http://register.gadu-gadu.pl/appsvc/fmregister3.asp'
		user_agent = 'Mozilla/4.0 (compatible; MSIE 5.0; Windows 98)'
		data = urllib.urlencode({'fmnumber' : fmnumber, 'fmpwd' : fmpwd, 'delete' : 1, 'pwd' : pwd, 'email' : 'deleteaccount@gadu-gadu.pl', 'tokenid' : tokenid, 'tokenval' : tokenval, 'code' : code})
		
		request = urllib2.Request(url, data)
		request.add_header('User-Agent', user_agent)
		
		response = urllib2.urlopen(request)
		text = response.read()
		if text == 'reg_success:'+str(fmnumber):
			return True
		else:
			return False
	
	def remind_password(self, userid, email, tokenid, tokenval):
		"""
		Metoda wysyla przypomnienie hasla na adres email podany przy rejestracji. Przyjmuje parametry:
			* userid - numer Gadu-Gadu uzytkownika
			* email - email podany przy rejestracji
			* tokenid - ID tokena pobranego metoda get_token_data
			* tokenval - tresc z obrazka tokena
		Zwraca True gdy przypomnienie zostalo wyslane, False w przeciwnym wypadku
		"""
		code = Helpers.gg_http_hash(str(userid), email)
		url = 'http://retr.gadu-gadu.pl/appsvc/fmsendpwd3.asp'
		user_agent = 'Mozilla/4.0 (compatible; MSIE 5.0; Windows 98)'
		data = urllib.urlencode({'userid' : userid, 'email' : email, 'tokenid' : tokenid, 'tokenval' : tokenval, 'code' : code})
		
		request = urllib2.Request(url, data)
		request.add_header('User-Agent', user_agent)
		
		response = urllib2.urlopen(request)
		text = response.read()
		if text == 'pwdsend_success':
			return True
		else:
			return False
		
	get_server = classmethod(get_server)
	get_token_data = classmethod(get_token_data)
	register_account = classmethod(register_account)
	delete_account = classmethod(delete_account)
	remind_password = classmethod(remind_password)
