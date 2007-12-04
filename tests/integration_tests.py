import sys
# sys.path.append("../") # - dla linuksa
sys.path.append("..\\..\\src") # - dla windowsa
from pygglib import GGSession
from GGConstans import *

#
# 11327271, haslo eto2007 
#

def login_ok_event_handler(sender, args):
	print 'Zalogowano :>'

if __name__ == "__main__":
	session = GGSession(uin = 11327271, password = 'eto2007')
	session.on_login_ok = login_ok_event_handler 
	session.login()