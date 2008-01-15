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

	def read(self, size = 1024, timeout = 0): #TODO: Petla do odbierania pakietow > 1024 bajty
		times = 0 #ile razy probowalismy odebrac cos, a nie udawalo sie
		got = 0
		packet = []
		while got < size:
			data = self.__socket.recv(size)
			if not data and timeout > 0:
				times += 1
			if times > timeout: #oczywiscie nie zajdzie wtedy gdy timeout = 0 (brak timeoutu)
				break
			got += len(data)
			packet.append(data)
			time.sleep(0.01) #poczekaj chwile, moze zaraz cos przyjdzie :-)
			
		return ''.join(packet)
	
	def connect(self):
		self.__socket.connect((self.__ip, self.__port))
	
	def disconnect(self):
		self.__socket.close()
