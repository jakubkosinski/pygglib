import os
import sys
if os.sys.platform == 'win32':
	sys.path.append(".\\..") # - dla windowsa
else:
	sys.path.append("../") # - dla linuksa
from pygglib import GGSession
from Helpers import *
from GGConstans import *
from Contacts import *
import time

#
# 11327271, haslo eto2007 
#	

def login_ok_event_handler(sender, args):
	print 'Zalogowano.'

def msg_recv_event_handler(sender, args):
	print 'Message received:'
	if sender.contacts_list[args.sender] != None:
		print 'sender:', sender.contacts_list[args.sender].shown_name, "(", args.sender, ")"
	else:
		print 'sender:', args.sender
	print 'seq:', args.seq
	print 'msg_class:', GGMsgTypes.reverse_lookup(args.msg_class)
	print 'message:', args.message
	print
	
def on_unknown_packet_event_handler(sender, args):
	print 'Unknown packet received: type: %d, length: %d' % (args.type, args.length)
	print
	
def on_send_msg_ack_event_handler(sender, args):
	print 'msg_send_ack received: status: %s, recipient: %d, seq: %d' % (GGMsgStatus.reverse_lookup_without_mask(args.status), args.recipient, args.seq)
	
def on_pubdir_recv_event_handler(sender, args):
	print 'PubDir type', args.req_type
	print 'PubDir sequence numer', args.seq
	entries = args.request.split("\0\0")
	for item in entries:
		print request_to_dict(item)
	print
	
def on_userlist_reply(sender, args):
	print 'UserListReply'
	print

def on_status_changed(sender, args):
	print args.contact.shown_name + ' has changed status'
	print 'New status:', GGStatuses.reverse_lookup_without_mask(args.contact.status)
	print 'Desc: ', args.contact.description
	print

def on_notify_reply(sender, args):
	for contact in args.contacts_list:
		print contact.shown_name, contact.uin, GGStatuses.reverse_lookup_without_mask(contact.status), contact.description

def on_pubdir_recv_event_handler(sender, args):
	entry = request_to_dict(args.reply.split("\0\0")[0])
	contact = Contact({'uin':entry['FmNumber'], 'shown_name':entry['nickname']})
	sender.add_contact(contact)

if __name__ == "__main__":
	session = GGSession(uin = 11327271, password = 'eto2007')
	session.register('on_login_ok', login_ok_event_handler)
	session.register('on_msg_recv', msg_recv_event_handler)
	session.register('on_unknown_packet', on_unknown_packet_event_handler)
	session.register('on_userlist_reply', on_userlist_reply)
	session.register('on_pubdir_recv', on_pubdir_recv_event_handler)
	session.register('on_status_changed', on_status_changed)
        session.import_contacts_list("kontakty.txt")
	session.login()
	session.pubdir_request({'FmNumber':1308535})
	session.change_status(GGStatuses.AvailDescr, ':>')
	print "Dodaje kontakt"
	session.add_contact(Contact({'uin':3993939,'shown_name':'Ty'}))
	time.sleep(10)
	print "Zmiana typu - blokada"
	session.change_user_type(1308535, GGUserTypes.Blocked)
	session.change_user_type(3993939, GGUserTypes.Blocked)
	time.sleep(10)
	print "Zmiana typu - odblokowanie mnie"
	session.change_user_type(1308535, GGUserTypes.Normal)
	print "Usuniecie ciebie"
	session.remove_contact(3993939)
	time.sleep(10)
	print "Eksport"
	session.export_contacts_list()
	session.export_contacts_list("kontakty.txt")
	print "Wylogowanie..."
	session.logout("Ni ma Henia...")
	print "Wylogowano"
