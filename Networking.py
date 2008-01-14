#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import types
from socket import *
import time
import struct

class Connection(object): #TODO: obsluga timeoutow
	def __init__(self, ip, port):
		self.__ip = ip
		self.__port = port
		self.__socket = socket(AF_INET, SOCK_STREAM)
		self.__socket.connect((ip, port))
		
	def send(self, data):
		self.__socket.send(data)

	def read(self, size = 1024): #TODO: Petla do odbierania pakietow > 1024 bajty
		got = 0
		packet = []
		while got < size:
			data = self.__socket.recv(size)
			got += len(data)
			packet.append(data)
			
		return ''.join(packet)
	
	def connect(self):
		self.__socket.connect((self.__ip, self.__port))
	
	def disconnect(self):
		self.__socket.close()
