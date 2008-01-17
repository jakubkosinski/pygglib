import os
import sys
if os.sys.platform == 'win32':
	sys.path.append(".\\..") # - dla windowsa
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
	print 'Zalogowano :>'
	print

def status_notify_event_handler(sender, args):
	print args.args()
	print 'Numerek %d zmienil status' % args.uin
	print

def unknown_packet_event_handler(sender, args):
	print 'Unknow packet received: type: 0x%04x, length: 0x%04x' % (args.type, args.length)
	print
	

if __name__ == "__main__":
	session = GGSession(uin = 11327271, password = 'eto2007', initial_status = GGStatuses.Invisible)
	session.register('on_login_ok', login_ok_event_handler)
	session.register('on_status_changed', status_notify_event_handler)
	session.register('on_unknown_packet', unknown_packet_event_handler)
	session.login()
	time.sleep(0.5)
	session.logout('Nie ma Henia')

