import urllib
import urllib2
import types

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

	get_server = classmethod(get_server)
