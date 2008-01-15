import os
import sys
if os.sys.platform == 'win32':
	sys.path.append("..\\..\\src") # - dla windowsa
else:
	sys.path.append("../") # - dla linuksa
from pygglib import GGSession
from GGConstans import *
import time

#
# 11327271, haslo eto2007 
#

def login_ok(sender, args):
	print 'Zalogowano :>'

def print_msg(sender, args):
	print 'Message received:'
	print 'sender:', args[0]
	print 'seq:', args[1]
	print 'msg_class:', GGMsgTypes.reverse_lookup(args[3])
	print 'messange:', args[4]
	print

def echo(sender, args):
	assert type(sender) == GGSession
	sender.send_msg(args[0], args[4])
	
def print_unknown_packet(sender, args):
	print 'Unknow packet received: type: %d, length: %d' % (args[0], args[1])
	print
	
def print_msg_ack(sender, args):
	print 'Message ack received: status: %s, recipient: %d, seq: %d' % (GGMsgStatus.reverse_lookup(args[0]), args[1], args[2])
	print

	
if __name__ == "__main__":
	session = GGSession(uin = 11327271, password = 'eto2007')
	session.register('on_login_ok', login_ok)
	session.register('on_msg_recv', print_msg)
	session.register('on_msg_recv', echo)
	session.register('on_unknown_packet', print_unknown_packet)
	session.register('on_send_msg_ack', print_msg_ack)
	session.login()
	session.change_status(GGStatuses.AvailDescr, "pygglib")
	time.sleep(5)
	session.logout()
		
