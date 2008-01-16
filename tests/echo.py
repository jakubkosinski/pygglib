# $Id$
# echo.py - demonstracja pygglib - Gadu-Gadu echo
# (c) Marek Chrusciel
#     Jakub Kosinski
#     Marcin Krupowicz
#     Mateusz Strycharski
#

import time
import sys
if sys.platform == 'win32':
	sys.path.append("..\\..\\src") # - dla windowsa
else:
	sys.path.append("../") # - dla linuksa
from pygglib import GGSession
from GGConstans import *
from Contacts import *

def on_login_ok_event_handler(sender, args):
	print '---'
	print 'Succesfully logged in.'

def on_login_failed_event_handler(sender, args):
	print '---'
	print 'Login failed!'

def on_need_email_event_handler(sender, args):
	print '---'
	print 'Server needs e-mail!'

def on_msg_recv_event_handler(sender, args):
	print '---'
	contact = sender.contacts_list[args.sender]
	if contact != None:
		print 'Message from', contact.shown_name
	else:
		print 'Message from', args.sender
	print 'Message sequence number:', args.seq
	print 'Message Classes:', GGMsgTypes.reverse_lookup(args.msg_class)
	print '"' + args.message + '"'

def on_msg_recv_echo(sender, args):
	assert type(sender) == GGSession
	sender.send_msg(args.sender, args.message, msg_class = GGMsgTypes.Chat)
	
def on_unknown_packet_event_handler(sender, args):
	print '---'
	print 'Unknown packet received: type: 0x%04x, length: 0x%04x' % (args.type, args.length)
	print
	
def on_msg_ack_event_handler(sender, args):
	print '---'
	print 'Message ack received: status: %s, recipient: %d, seq: %d' % (GGMsgStatus.reverse_lookup_without_mask(args.status), args.recipient, args.seq)
	print

def on_notify_reply_event_handler(sender, args):
	print '---'
	print 'Notify from server:', len(args.contacts_list)
	for contact in args.contacts_list.data:
		print contact.shown_name + ' is ' + GGStatuses.reverse_lookup_without_mask(contact.status)
		if contact.description != "":
			print 'Description:', contact.description

def on_userlist_reply_event_handler(sender, args):
	print '---'
	print 'Contacts list received from server'
	for contact in sender.contacts_list.data:
		print contact.shown_name + ': ' + str(contact.uin)

def on_status_changed_event_handler(sender, args):
	print '---'
	print args.contact.shown_name + ' has changed status.'
	print 'New status: ', GGStatuses.reverse_lookup_without_mask(args.contact.status)
	if args.contact.description != '':
		print '"' + args.contact.description + '"'

def on_disconnecting_event_handler(sender, args):
	print '---'
	print 'Server has closed the connection'
	
if __name__ == "__main__":
	contacts_list = ContactsList([Contact({'uin':3993939,'shown_name':'Cinu'}), Contact({'uin':4668758,'shown_name':'Anna'})])
	# Inicjowanie sesji
	session = GGSession(uin = 11327271, password = 'eto2007', initial_status = GGStatuses.AvailDescr, initial_description = 'pygglib echo demo', contacts_list = contacts_list)
	# Rejestrowanie obslugi zdarzen
	session.register('on_login_ok', on_login_ok_event_handler)
	session.register('on_msg_recv', on_msg_recv_event_handler)
	session.register('on_msg_recv', on_msg_recv_echo)
	session.register('on_unknown_packet', on_unknown_packet_event_handler)
	session.register('on_send_msg_ack', on_msg_ack_event_handler)
	session.register('on_notify_reply', on_notify_reply_event_handler)
	session.register('on_userlist_reply', on_userlist_reply_event_handler)
	session.register('on_status_changed', on_status_changed_event_handler)
	session.register('on_disconnecting', on_disconnecting_event_handler)

	session.login()
	session.import_contacts_list()
	x = ''
	while x != 'quit':
		x = raw_input()
	session.logout()
	
