#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import types
from socket import *

class Connection(object): #TODO: obsluga timeoutow
	def __init__(self, ip, port):
		self.__ip = ip
		self.__port = port
		self.__socket = socket(AF_INET, SOCK_STREAM)
		self.__socket.connect((ip, port))
	
	def send(self, data):
		self.__socket.send(data)
	
	def read(self, limit = 1024): #TODO: Petla do odbierania pakietow > 1024 bajty
		return self.__socket.recv(limit)
	
	def connect(self):
		self.__socket.connect((self.__ip, self.__port))
	
	def disconnect(self):
		self.__socket.close()
