#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import urllib
import urllib2
import types

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

	get_server = classmethod(get_server)
	get_token_data = classmethod(get_token_data)
