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

if __name__ == "__main__":
	session = GGSession(uin = 11327271, password = 'eto2007')
	session.register('on_login_ok', login_ok_event_handler)
	session.login()
	time.sleep(5)
	session.logout('Nie ma Henia')
	x = raw_input()

