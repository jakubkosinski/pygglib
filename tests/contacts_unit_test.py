# $Id$

import sys
import unittest
if sys.platform == 'win32':
	sys.path.append(".\\..") # - dla windowsa
else:
	sys.path.append("../") # - dla linuksa
from GGConstans import *
from Contacts import *

class ContactUnitTest(unittest.TestCase):        
    def testCreateDictWithShownName(self):
        uin = 1234
        nick = 'Nick'
        shown_name = 'Test'
        dict = {'uin':uin, 'nick':nick, 'shown_name':shown_name}
        contact = Contact(dict)
        
        self.assertEqual(contact.shown_name, shown_name)
        self.assertEqual(contact.uin, uin)
        self.assertEqual(contact.nick, nick)
        self.assertEqual(contact.name, "")
        self.assertEqual(contact.surname, "")
        self.assertEqual(contact.mobilephone, "")
        self.assertEqual(contact.group, "")
        self.assertEqual(contact.email, "")
        self.assertEqual(contact.available, 0)
        self.assertEqual(contact.available_source, "")
        self.assertEqual(contact.message, 0)
        self.assertEqual(contact.message_source, "")
        self.assertEqual(contact.hidden, 0)
        self.assertEqual(contact.telephone, "")
        
    def testCreateDictWithoutShownName(self):
        uin = 1234
        nick = 'Nick'
        name = 'Name'
        surname = 'Surname'
        mobilephone = '123456789'
        group = 'Group'
        email = 'email@email'
        available = 2
        available_source = 'source'
        message = 1
        message_source = 'source'
        hidden = 0
        telephone = '123456789'
        dict = {'uin':uin,'nick':nick,'name':name,'surname':surname,'mobilephone':mobilephone,'group':group,'email':email,'available':available, \
                           'available_source':available_source,'message':message,'message_source':message_source,'hidden':hidden,'telephone':telephone}
        contact = Contact(dict)
        
        self.assertEqual(contact.shown_name, str(uin))
        self.assertEqual(contact.uin, uin)
        self.assertEqual(contact.nick, nick)
        self.assertEqual(contact.name, name)
        self.assertEqual(contact.surname, surname)
        self.assertEqual(contact.mobilephone, mobilephone)
        self.assertEqual(contact.group, group)
        self.assertEqual(contact.email, email)
        self.assertEqual(contact.available, available)
        self.assertEqual(contact.available_source, available_source)
        self.assertEqual(contact.message, message)
        self.assertEqual(contact.message_source, message_source)
        self.assertEqual(contact.hidden, hidden)
        self.assertEqual(contact.telephone, telephone)
        
    def testCreateString(self):
        uin = 1234
        nick = 'Nick'
        shown_name = 'ShownName'
        name = 'Name'
        surname = 'Surname'
        mobilephone = '123456789'
        group = 'Group'
        email = 'email@email'
        available = 2
        available_source = 'source'
        message = 1
        message_source = 'source'
        hidden = 0
        telephone = '123456789'
        request_string = ";".join([name, surname, nick, shown_name, mobilephone, group, str(uin), email, str(available), available_source, str(message), message_source, str(hidden), telephone])
        dict = {'request_string':request_string}
        
        contact = Contact(dict)
        
        self.assertEqual(contact.shown_name, shown_name)
        self.assertEqual(contact.uin, uin)
        self.assertEqual(contact.nick, nick)
        self.assertEqual(contact.name, name)
        self.assertEqual(contact.surname, surname)
        self.assertEqual(contact.mobilephone, mobilephone)
        self.assertEqual(contact.group, group)
        self.assertEqual(contact.email, email)
        self.assertEqual(contact.available, available)
        self.assertEqual(contact.available_source, available_source)
        self.assertEqual(contact.message, message)
        self.assertEqual(contact.message_source, message_source)
        self.assertEqual(contact.hidden, hidden)
        self.assertEqual(contact.telephone, telephone)
    
    def testRequestString(self):
        uin = 1234
        nick = 'Nick'
        shown_name = 'ShownName'
        name = 'Name'
        surname = 'Surname'
        mobilephone = '123456789'
        group = 'Group'
        email = 'email@email'
        available = 2
        available_source = 'source'
        message = 1
        message_source = 'source'
        hidden = 0
        telephone = '123456789'
        request_string = ";".join([name, surname, nick, shown_name, mobilephone, group, str(uin), email, str(available), available_source, str(message), message_source, str(hidden), telephone])
        dict = {'request_string':request_string}
        
        contact = Contact(dict)
        
        self.assertEqual(contact.request_string(), request_string)
    
class ContactsListUnitTest(unittest.TestCase):
    def setUp(self):
        file = open('kontakty.txt')
        self.request_string = file.read()
        self.lines = self.request_string.split("\n")
        file.close()
        self.contacts = []
        for line in self.lines:
            if line != '':
                self.contacts.append(Contact({'request_string':line}))
        
    def testAddContact(self):
        clist = ContactsList()
        clist.add_contact(self.contacts[0])
        
        self.assertEqual(len(clist), 1)
        self.assertEqual(clist[self.contacts[0].uin], self.contacts[0])
        
        for contact in self.contacts:
            clist.add_contact(contact)
            
        self.assertEqual(len(clist), len(self.contacts))
        for contact in self.contacts:
            self.assertEqual(clist[contact.uin], contact)
            
    def testRemoveContact(self):
        clist = ContactsList(self.request_string)
        clist.remove_contact(self.contacts[0].uin)
        
        self.assertEqual(clist[self.contacts[0].uin], None)
        self.assertEqual(len(clist), len(self.contacts) - 1)
    
    def testRequestString(self):
        clist = ContactsList(self.request_string)
        self.assertEqual(clist.export_request_string(), self.request_string)
    
    def testContainsContact(self):
        clist = ContactsList()
	c = Contact({"uin":1234, "shown_name":"Trol"})
        self.assertFalse(1234 in clist)
        self.assertFalse(c in clist)
	clist.add_contact(c)
        self.assertTrue(1234 in clist)
        self.assertTrue(c in clist)

        
if __name__ == "__main__":
    suite1 = unittest.makeSuite(ContactUnitTest)
    unittest.TextTestRunner().run(suite1)
    suite2 = unittest.makeSuite(ContactsListUnitTest)
    unittest.TextTestRunner().run(suite2)
