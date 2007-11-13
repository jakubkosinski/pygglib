#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import types
from socket import *

class Connection(object):
	def __init__(self, ip, port):
		self.__ip = ip
		self.__port = port
		self.__socket = socket(AF_INET, SOCK_STREAM)
		self.__socket.connect((ip, port))
	
	def send(self, data):
		self.__socket.send(data)
	
	def recv(self, limit = 1024):
		return self.__socket.recv(limit)
	
	def disconnect(self):
		self.__socket.close()
