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
	print 'Zalogowano :>'
	print

def status_notify_event_handler(sender, args):
	print 'Status zmienil numerek', args[0]
	print

def unknown_packet_event_handler(sender, args):
	print 'Unknow packet received: type: 0x%04x, length: 0x%04x' % (args[0], args[1])
	print
	

if __name__ == "__main__":
	session = GGSession(uin = 11327271, password = 'eto2007')
	session.register('on_login_ok', login_ok_event_handler)
	session.register('on_status_changed', status_notify_event_handler)
	session.register('on_unknown_packet', unknown_packet_event_handler)
	session.login()
	time.sleep(1)
	session.logout('Nie ma Henia')
