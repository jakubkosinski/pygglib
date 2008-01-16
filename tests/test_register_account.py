import os
import sys
if os.sys.platform == 'win32':
	sys.path.append(".\\..") # - dla windowsa
else:
	sys.path.append("../") # - dla linuksa
from pygglib import *
from HTTPServices import *

def register_account(pwd,email):
	token = HTTPServices.get_token_data()
	f = open('token-'+token.id+'.gif','wb')
	f.write(token.image)
	f.close()
	
	print "Podaj kod z obrazka: "
	tokenval = raw_input()
	
	try:
		uin = HTTPServices.register_account(pwd,email,token.id,tokenval)
	except:
		print "Rejestracja konta nieudana"
	
	print "Zarejestrowany numer ", str(uin)
	return uin

def delete_account(uin, pwd):
	token = HTTPServices.get_token_data()
	f = open('token-'+token.id+'.gif','wb')
	f.write(token.image)
	f.close()
	
	print "Podaj kod z obrazka: "
	tokenval = raw_input()
	
	if HTTPServices.delete_account(uin,pwd,token.id,tokenval) == True:
		print "Konto o numerze " + str(uin) + " usuniete."
	else:
		print "Nie udalo sie usunac konta"
	
if __name__ == "__main__":
	print "Podaj haslo rejestrowanego konta:"
	pwd = raw_input()
	print "Podaj email rejestrowanego konta:"
	email = raw_input()
	uin = register_account(pwd,email)
	print "Czy usunac konto? [t/n]"
	op = raw_input()
	if op == 't' or op == 'T':
		delete_account(uin,pwd)
