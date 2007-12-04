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
	if header.type != GGIncomingPackets.GGWelcome:
		raise "Unexpected packet got!"
	in_packet = GGWelcome()
	in_packet.read(conn, header.length)
	seed = in_packet.seed
	# ... i mamy juz seeda
	
	# Logowanie sie
	out_packet = GGLogin(11327271, "eto2007", 0x0004, seed, "opis :)")
	out_packet.send(conn)
	header.read(conn)
	print "Got Packet:\n \ttype: %d\n\tlength: %d" % (header.type, header.length)
	if header.type == GGIncomingPackets.GGLoginOK:
		print 'Logged in'
	else:
		print 'Invalid password or uin!'
		sys.exit()
	in_packet = GGLoginOK()
	in_packet.read(conn, header.length)
	
	# Zmiana statusu
	out_packet  = GGNewStatus(0x0004, "pygglib w akcji")
	out_packet.send(conn)
	print 'Status changed'
	
	# w takim razie jeszcze poczekajmy na jakis pakiecik...
	header.read(conn)
	print "Got Packet:\n \ttype: %d\n\tlength: %d" % (header.type, header.length)
	if header.type == GGIncomingPackets.GGRecvMsg:
		in_packet = GGRecvMsg()
		in_packet.read(conn, header.length)
		print "New message received:\n\tsender: %d\n\tmessage: %s" % (in_packet.sender, in_packet.message)
		
		#echo
		sender = in_packet.sender
		message = in_packet.message
		out_packet = GGSendMsg(sender, message)
		out_packet.send(conn)
		
		#potwierdzenie dostarczenia wiadomosci
		header.read(conn)
		print "Got Packet:\n \ttype: %d\n\tlength: %d" % (header.type, header.length)
		if header.type == GGIncomingPackets.GGSendMsgAck:
			in_packet = GGSendMsgAck()
			in_packet.read(conn, header.length)
			print "Status of message which was sent:\n\tstatus: %d\n\trecipient: %d\n\tseq: %d" % (in_packet.status, in_packet.recipient, in_packet.seq)
	else:
		conn.read(header.length) #.. i olewamy co bylo
	
	print conn.read(1) #delay