PYGGLIB

1. Opis biblioteki
Biblioteka pygglib realizuje operacje oparte o protokó³ gg. Opis protoko³u znajduje siê na stronie http://ekg.chmurka.net/docs/protocol.html.
Jest napisana w jêzyku python. S³u¿y do pisania aplikacji korzystaj¹cych z protoko³u gg. Zrealizowana miêdzy innymi jako projekt na Uniwersytecie
Wroc³awskim.


2. Przyk³ad u¿ycia GGSession:
  Klasa GGSession realizuje g³ówne zadania zwi¹zane z obs³uga protoko³u gadu-gadu. Wiêkszoœæ operacji wykonuje siê korzsytaj¹c z jej mo¿liwosæi.
  Poni¿ej krótki przyk³ad u¿ycia klasy
  
  
  Na pocz¹tek tworzymy obiekt GGSession dla numeru 1111111 z haslem 'kaczka', pocz¹tkowym statusem dostêpny.
  Szczegó³owy opis klasy dostêpny jest wraz z kodem klasy GGSession.
  
  ##  session = GGSession(1111111, 'kaczka', GGStatuses.Avail , 'moj nowy opis', )  
  
  
  Teraz logujemy siê do sieci gg. Wysylamy równie¿ do serwera dane o swoich kontaktach.
  
  ## session.login() $
  
  Celem wys³ania wiadomoœci u¿ytkonikowi o numerze 123456 wywo³ujemy metodê
  Szczegó³owy opis metody w klasie GGSession
  
  ## session.send_msg(123456 , "wiadomosc", seq, GGMsgTypes.Msg, richtext = False)
  
  
  Gdy chcemy eksportowac listê kontaktów na serwer korzystamy z metody
  
  ## session.export_contacts_list(filename)
  
  Mo¿emy oczywiœcie te¿ importowaæ listê kontaktów z serwera
  
  ## session.import_contacts_list(filename)
  
  Za pomoc¹ metody 
  
  ## pubdir_request(self, request, reqtype = GGPubDirTypes.Search)
  
  uzyskujemy dane z katalogu publicznego i modyfikujemy wlasne dane
  
  
  Celem wylogowania siê z sieci korzystamy z metody
  
  ## session.logout()
  
  
  W klasie GGSession znajduj¹ siê równie¿ inne metody, odsy³am do dokumentacji klasy.
  
  
3. Rejestracja i usuwanie konta:
 Celem rejestracji i usuniêcia konta korzystamy z klasy HTTPServices.
 Przyk³ad u¿ycia :
 
 #######################################################
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
	#########################################################


4. Opis sta³ych
4.1. Mozliwe wartosci statusow dostepnosci
GGStatuses = Enum({
	"NotAvail":0x0001, 			#Niedostepny
	"NotAvailDescr":0x0015, 	#Niedostepny (z opisem)
	"Avail":0x0002, 			#Dostepny
	"AvailDescr":0x0004, 		#Dostepny (z opisem)
	"Busy":0x0003, 				#Zajety
	"BusyDescr":0x0005, 		#Zajety (z opisem)
	"Invisible":0x0014, 		#Niewidoczny
	"InvisibleDescr":0x0016, 	#Niewidoczny (z opisem)
	"Blocked":0x0006, 			#Zablokowany
	"FriendsMask":0x8000 		#Tylko dla przyjaciol
	})

4.2. Typ uzytkownika gg, ktory jest w naszych kontaktach. Okresla jak traktujemy dany nr gg

GGUserTypes = Enum({
	"Offline":0x01, 			#Kazdy uzytkownik dodany do listy kontaktow
	"Friend":0x02, 				#Uzytkownik, dla ktorego jestesmy widoczni w trybie "tylko dla przyjaciol"
	"Normal":0x03,				#Kazdy inny uzytkownik
	"Blocked":0x04 				#Uzytkownik, ktorego wiadomosci nie chcemy otrzymywac
	})
	
4.3. Informacje o uzytkowniku, ktorego gg mamy w kontaktach (odpytujemy serwer o te informacje)

GGRemotePort = Enum({
	"NotStraightConnection":0, 	#Klient nie obsluguje bezposredniego polaczenia
	"BehindNAT":1, 				#Klient laczy sie zza NAT lub innej formy maskarady
	"NotInBuddyList":2 			#Klient nie ma nas w swojej liscie kontaktow
	})
	
4.4. Mapa bitowa dla wiadomosci, okresla parametry wiadomosci

GGMsgTypes = Enum({
	"Queued":0x0001, 			#Bit ustawiany wylacznie przy odbiorze wiadomosci, gdy wiadomosc zostala wczesniej zakolejkowana z powodu nieobecnosci
	"Msg":0x0004, 				#Wiadomosc ma sie pojawic w osobnym okienku
	"Chat":0x0008, 				#Wiadomosc jest czescia toczacej sie rozmowy i zostanie wyswietlona w istniejacym okienku
	"Ctcp":0x0010, 				#Wiadomosc jest przeznaczona dla klienta Gadu-Gadu i nie powinna byc wyswietlona uzytkownikowi
	"Ack":0x0020 				#Klient nie zyczy sobie potwierdzenia wiadomosci
	})

4.5. Okreslaja stan wyslanej wiadomosci

GGMsgStatus = Enum({
	"Blocked":0x0001, 			#Wiadomosci nie przeslano (zdarza sie przy wiadomosciach zawierajacych adresy internetowe blokowanych przez serwer GG gdy odbiorca nie ma nas na liscie)
	"Delivered":0x0002,			#Wiadomosc dostarczona
	"Queued":0x0003, 			#Wiadomosc zakolejkowana
	"MBoxFull":0x0004, 			#Wiadomosc nie dostarczona. Skrzynka odbiorcza na serwerze jest pelna (20 wiadomosci max.). Wystepuje tylko w trybie off-line
	"NotDelivered":0x0006 		#Wiadomosc nie dostarczona. Odpowiedz ta wystepuje tylko w przypadku wiadomosci klasy Ctcp
	})
	
4.6. Typy pakietow wysylanych do serwera z lista kontaktow w "pakietach" po 400 wpisow

GGNotifyTypes = Enum({
	"NotifyFirst":0x000f, 		# nieostatnie 400 wpisow w liscie kontaktow
	"NotifyLast":0x0010   		# ostatnie 400 wpisow
	})
	
4.7. Typy okreslajace operacje na katalogu publicznym
	
GGPubDirTypes = Enum({
	"Write"       : 0x01,		#Pisanie do katalogu pulicznego
	"Read"        : 0x02,		#Odczyt z katalogu
	"Search"      : 0x03,		#Szukanie w katalogu
	"SearchReply" : 0x05		#Ponowne wyszukiwanie w katalogu
	})

4.8. Typy okreslajace operacje na liscie kontaktow
	
GGUserListTypes = Enum({
	"Put"     : 0x00,			#Poczatek eksportu listy
	"PutMore" : 0x01,			#Dalsza czesc eksportu listy
	"Get"     : 0x02			#Import listy
	})

4.9. Typ pakietu do odpowiedzi serwera odnosnie listy kontaktow
	
GGUserListReplyTypes = Enum({
	"PutReply"     : 0x00,		#Poczatek eksportu listy
	"PutMoreReply" : 0x01,		#Kontynuacja
	"GetMoreReply" : 0x04,		#Poczatek importu listy
	"GetReply"     : 0x06		#Ostatnia czesc importu
	})
