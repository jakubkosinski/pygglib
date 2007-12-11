#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#

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


import unittest


## trzeba napisac zbiernie opisow od serwera
def on_notify_reply(sender, args):
	print 'status poczatkowy uzytkownika'
	opis_poczatkowy_odczytany = 'aa'
	
def on_notify_reply60(sender, args):
	print 'status poczatkowy uzytkownika'
	opis_poczatkowy_odczytany = 'aa'
	
def on_status_change(sender, args):
	print 'status zmieniony'
	opis_zmieniony_odczytany = 'bb'
	
def on_status_change60(sender, args):
	print 'status zmieniony'
	opis_zmieniony_odczytany = 'bb'
	

class ChangeStatusTest(unittest.TestCase):
	def setUp(self):
		session1 = GGSession(uin = 11327271, password = 'eto2007')
		session2 = GGSession(uin = 3839480, password = 'eto2007', initial_description='aa')
		
		session1.register('on_login_ok', login_ok_event_handler)
		session1.register('on_unknown_packet', on_unknown_packet_event_handler)
		
		# nienapisna jest obsluga tych pakietow
		session1.register('on_notify_reply', on_notify_reply)
		session1.register('on_notify_reply60', on_notify_reply60)
		session1.register('on_status_change', on_status_change)
		session1.register('on_status_change60', on_status_change60)

		
		session2.register('on_login_ok', login_ok_event_handler)
		session2.register('on_unknown_packet', on_unknown_packet_event_handler)

		
	def tearDown(self):
		session1.logout()
		session2.logout()

	def testChangeStatus(self):
		session2.login()
		
		time.sleep(2)
		session1.login()
		
		# powiadamiamy serwer
		#session1.notify(3839480, type)
		
		time.sleep(2)
		
		assert opis_poczatkowy_odczytany == 'aa', "odczytany opis poczatkowy z serwera jest niepoprawny"
		
		session2.change_description('bb')
		
		time.sleep(2)
		
		assert opis_zmieniony == 'bb', "opis po zmianie nie jest poprawny"
		

		
