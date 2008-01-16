# $Id$
import sys
if sys.platform == 'win32':
	sys.path.append(".\\..") # - dla windowsa
else:
	sys.path.append("../") # - dla linuksa

from pygglib import GGSession
from GGConstans import *
from Contacts import *
import time

def login_ok(sender, args):
	print 'Zalogowano :>'

def print_msg(sender, args):
	print 'Message received:'
	print 'sender:', args.sender
	print 'seq:', args.seq
	print 'msg_class:', GGMsgTypes.reverse_lookup(args.msg_class)
	print 'message:', args.message
	print
	
def print_unknown_packet(sender, args):
	print 'Unknow packet received: type: %d, length: %d' % (args.type, args.length)
	print

def notify_reply(sender, args):
	print 'reply notified'
	
	
if __name__ == "__main__":
	try:
		contacts = ContactsList([Contact({'uin':3993939}), Contact({'uin':3217426}), Contact({'uin':4102378})])
		session = GGSession(uin = 11327271, password = 'eto2007', contacts_list = contacts)
		session.register('on_login_ok', login_ok)
		session.register('on_msg_recv', print_msg)
		session.register('on_unknown_packet', print_unknown_packet)
		session.register('on_notify_reply', notify_reply)
		session.login()
		time.sleep(2)
		print "uin: %d, status: %s description: %s" % (session.contacts_list[3217426].uin, GGStatuses.reverse_lookup_without_mask(session.contacts_list[3217426].status), session.contacts_list[3217426].description)
		print "uin: %d, status: %s description: %s" % (session.contacts_list[4102378].uin, GGStatuses.reverse_lookup_without_mask(session.contacts_list[4102378].status), session.contacts_list[4102378].description)
		print "uin: %d, status: %s description: %s" % (session.contacts_list[3993939].uin, GGStatuses.reverse_lookup_without_mask(session.contacts_list[3993939].status), session.contacts_list[3993939].description)
		time.sleep(4)
		session.logout()
	finally:
		try:
			session.logout()
		except: #znaczy, ze nie jestesmy zalogowani
			pass 
