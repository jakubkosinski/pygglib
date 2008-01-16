# $Id$
# Test dla zmiany statusu  GGSession.change_description(string new_descr).

## Opis testu
# Mamy dwa numery gg.
# Logujemy sie numerem 2
#Czekamy
#Logujemy sie nr 1
#nr 1 powiadamia serwer, ze ma nr drugi gg w kontaktach
# Czekamy (w tym czasie serwer wysle nam pakiet gg_notify_reply z informacja o opisie nr 2)
#nr 2 zmienia status
#Czekamy ( w tym czasie serwer wysle nam pakiet gg_status z informacja o nowym statusie)

import time
import sys
import unittest
if sys.platform == 'win32':
	sys.path.append(".\\..") # - dla windowsa
else:
	sys.path.append("../") # - dla linuksa
from pygglib import GGSession
from GGConstans import *
from Contacts import *


UIN1 = 11327271
UIN2 = 7743510
PASS1 = 'eto2007'
PASS2 = 'eto2007'

DESC1 = 'a'
DESC2 = 'b'

global PASSED
global INITIAL
global CHANGED
PASSED = True
INITIAL = False
CHANGED = False

def on_notify_reply(sender, args):
	global INITIAL
	global PASSED
	INITIAL = True
	PASSED = True
	print 'status poczatkowy uzytkownika', args.contacts_list[UIN2].description
	if args.contacts_list[UIN2].description != DESC1:
		PASSED = False
	
def on_status_changed(sender, args):
	global CHANGED
	global PASSED
	CHANGED = True
	PASSED = True
	print 'Zmiana statusu'
	print args.contact.uin, "'"+args.contact.description+"'"
	if (args.contact.uin != UIN2 or args.contact.description != DESC2):
		PASSED = False

def on_disconnecting(sender, args):
	print "Rozlaczono przez serwer"

class ChangeStatusTest(unittest.TestCase):
	def setUp(self):
		self.session1 = GGSession(uin = UIN1, password = PASS1, contacts_list = ContactsList([Contact({'uin':UIN2})]))
		self.session2 = GGSession(uin = UIN2, password = PASS2, initial_status = GGStatuses.AvailDescr, initial_description=DESC1)
		
		self.session1.register('on_notify_reply', on_notify_reply)
		self.session1.register('on_status_changed', on_status_changed)
		self.session1.register('on_disconnecting', on_disconnecting)
		self.session2.register('on_disconnecting', on_disconnecting)

	def testChangeStatus(self):
		self.session2.login()
		while self.session2.logged != True:
			time.sleep(0.1)
		print "Session2 logged in"
		time.sleep(1)
		self.session1.login()
		while self.session1.logged != True:
			time.sleep(0.1)
		print "Session1 logged in"
		
		time.sleep(5)
		self.session2.change_description(DESC2)		
		time.sleep(5)
		
		self.session1.logout()
		self.session2.logout()
		self.assertTrue(PASSED)
		self.assertTrue(CHANGED)
		self.assertTrue(INITIAL)
		
if __name__ == "__main__":
    suite1 = unittest.makeSuite(ChangeStatusTest)
    unittest.TextTestRunner().run(suite1)
