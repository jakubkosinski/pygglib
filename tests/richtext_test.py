import os
import sys
import time
if os.sys.platform == 'win32':
	sys.path.append("..\\..\\src") # - dla windowsa
else:
	sys.path.append("../") # - dla linuksa
from pygglib import GGSession
from GGConstans import *

def login_ok(sender, args):
	print 'Zalogowano :>'

def print_msg(sender, args):
	print '<%d>: %s' % (args[0], args[4])

	
def print_unknown_packet(sender, args):
	print 'Unknow packet received: type: %d, length: %d' % (args[0], args[1])
	print

if __name__ == "__main__":
	session = GGSession(uin = 11327271, password = 'eto2007')
	session.register('on_login_ok', login_ok)
	session.register('on_msg_recv', print_msg)
	session.register('on_unknown_packet', print_unknown_packet)
	session.login()
	session.change_status(GGStatuses.InvisibleDescr, "richtext_test.py")
	session.send_msg(3993939, 'Zwykla wiadomosc')
	session.send_msg(3993939, 'Richtext: <b>Ala <i><u>ma</u></i></b><color red=123 green=143 blue=123> KOTA</color>', richtext = True)
	time.sleep(10)
	session.logout()