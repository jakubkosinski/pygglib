#
# Testy listy kontaktow, pakietow GGNotify* i statusow
#
import os
import sys
if os.sys.platform == 'win32':
	sys.path.append("..\\..\\src") # - dla windowsa
else:
	sys.path.append("../") # - dla linuksa
from pygglib import GGSession
from GGConstans import *
from Contacts import *
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
	
def print_unknown_packet(sender, args):
	print 'Unknow packet received: type: %d, length: %d' % (args[0], args[1])
	print

def notify_reply(sender, args):
	print 'dupa'
	
	
if __name__ == "__main__":
	try:
		contacts = ContactsList([Contact(3993939), Contact(3217426), Contact(4102378)])
		session = GGSession(uin = 11327271, password = 'eto2007', contacts_list = contacts)
		session.register('on_login_ok', login_ok)
		session.register('on_msg_recv', print_msg)
		session.register('on_unknown_packet', print_unknown_packet)
		session.register('on_notify_reply', notify_reply)
		session.login()
		time.sleep(2)
		print "uin: %d, status: %d description: %s" % (session.contacts_list[3217426].uin, session.contacts_list[3217426].status, session.contacts_list[3217426].description)
		print "uin: %d, status: %d description: %s" % (session.contacts_list[4102378].uin, session.contacts_list[4102378].status, session.contacts_list[4102378].description)
		print "uin: %d, status: %d description: %s" % (session.contacts_list[3993939].uin, session.contacts_list[3993939].status, session.contacts_list[3993939].description)
		time.sleep(4)
		session.logout()
	#except GGException, e:
	#	print '[!]GGException caught: %s ' % (repr(e),)
	#	
	#except Exception, e:
	#	print '[!]Generic exception caught: %s ' % (repr(e), )
	finally:
		try:
			session.logout()
		except: #znaczy, ze nie jestesmy zalogowani
			pass 
		
