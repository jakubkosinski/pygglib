import os
import sys
if os.sys.platform == 'win32':
	sys.path.append("..\\..\\src") # - dla windowsa
else:
	sys.path.append("../") # - dla linuksa
from pygglib import GGSession
from Helpers import *
from GGConstans import *
import time

#
# 11327271, haslo eto2007 
#
def login_ok_event_handler(sender, args):
	print 'Zalogowano.'

def msg_recv_event_handler(sender, args):
	print 'Message received:'
        print 'sender:', args.sender
	print 'seq:', args.seq
	print 'msg_class:', GGMsgTypes.reverse_lookup(args.msg_class)
	print 'message:', args.message
	print
	
def on_unknown_packet_event_handler(sender, args):
	print 'Unknow packet received: type: %d, length: %d' % (args.type, args.length)
	print
	
	
if __name__ == "__main__":
	session = GGSession(uin = 11327271, password = 'eto2007')
	session.register('on_login_ok', login_ok_event_handler)
	session.register('on_msg_recv', msg_recv_event_handler)
	session.register('on_unknown_packet', on_unknown_packet_event_handler)
        session.import_contacts_list("kontakty.txt")
        clist = session.contacts_list
        assert clist[12345678].shown_name == "Ania"
	session.login()
        session.export_contacts_list()
        time.sleep(5)
	session.logout()

