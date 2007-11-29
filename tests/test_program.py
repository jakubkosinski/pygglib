import sys
# sys.path.append("../") # - dla linuksa
sys.path.append("..\\..\\src") # - dla windowsa
from OutgoingPackets import *
from HeaderPacket import GGHeader
from IncomingPackets import *
from Networking import Connection

#
# 11327271, haslo eto2007 
#

if __name__ == "__main__":
	conn = Connection("217.17.45.153", 8074)
	header = GGHeader()
	header.read(conn)
	if header.type != 0x0001:
		raise "Unexpected packet got!"
	packet = GGWelcome()
	packet.read(conn)
	seed = packet.seed
	# mamy juz seeda
	packet = GGLogin(11327271, "eto2007", 0x0004, seed, "opis :)")
	packet.send(conn)
	header.read(conn)
	print "Got Packet:\n \ttype: %d\n\tlength: %d" % (header.type, header.length)
	if header.type == 0x0003:
		print 'Logged in'
	if header.length > 0:
		conn.read(header.length) # jeszcze jakies COS przychodzi po zalogowaniu sie
	packet  = GGNewStatus(0x0004, "pygglib w akcji")
	packet.send(conn)
	print 'Status changed'
	# w takim razie jeszcze poczekajmy na jakis pakiecik...
	header.read(conn)
	print "Got Packet:\n \ttype: %d\n\tlength: %d" % (header.type, header.length)
	if header.type == 0x000a:
		packet = GGRecvMsg()
		packet.read(conn, header.length)
		print "New message received:\n\tsender: %d\n\tmessage: %s" % (packet.sender, packet.message)
	print conn.read(1) #delay