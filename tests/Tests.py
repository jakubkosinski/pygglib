#Tests

import unittest

def msg_recv_event_handler(sender, args):
	msg_recv = args[4]

class Tests(unittest.TestCase):
	def setUp(self):
		session1 = GGSession(uin = 11327271, password = 'eto2007')
		session2 = GGSession(uin = 3839480, password = 'eto2007', initial_description='aa')
		session1.register('on_msg_recv', msg_recv_event_handler)
		session1.login()
		session2.login()
		
	def testTests(self):
		msg = 'ala ma psa'
		session1.send_msg(10659006, msg)
		assert msg == msg_recv, 'blad'
	
	def tearDown(self):
		session1.logout()
		session2.logout()