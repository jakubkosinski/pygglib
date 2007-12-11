#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

from Helpers import Enum

## Mozliwe wartosci statusow dostepnosci
#
GGStatuses = Enum({
	"NotAvail":0x0001, #Niedostepny
	"NotAvailDescr":0x0015, #Niedostepny (z opisem)
	"Avail":0x0002, #Dostepny
	"AvailDescr":0x0004, #Dostepny (z opisem)
	"Busy":0x0003, #Zajety
	"BusyDescr":0x0005, #Zajety (z opisem)
	"Invisible":0x0014, #Niewidoczny
	"InvisibleDescr":0x0016, #Niewidoczny (z opisem)
	"Blocked":0x0006, #Zablokowany
	"FriendsMask":0x8000 #Tylko dla przyjaciol
	})

## Typ uzytkownika gg, ktory jest w naszych kontaktach. 
# Okresla jak traktujemy dany nr gg
#
GGUserTypes = Enum({
	"Buddy":0x01, #Kazdy uzytkownik dodany do listy kontaktow
	"Friend":0x02, #Uzytkownik, dla ktorego jestesmy widoczni w trybie "tylko dla przyjaciol"
	"Blocked":0x04 #Uzytkownik, ktorego wiadomosci nie chcemy otrzymywac
	})
	
## Informacje o uzytkowniku, ktorego gg mamy w kontaktach (pytujemy serwer o te informacje)
#
GGRemotePort = Enum({
	"NotStraightConnection":0, #Klient nie obsluguje bezposredniego polaczenia
	"BehindNAT":1, #Klient laczy sie zza NAT lub innej formy maskarady
	"NotInBuddyList":2 #Klient nie ma nas w swojej liscie kontaktow
	})
	
## Mapa bitowa dla wiadomosci, okresla parametry wiadomosci
#
GGMsgTypes = Enum({
	"Queued":0x0001, #Bit ustawiany wylacznie przy odbiorze wiadomosci, gdy wiadomosc zostala wczesniej zakolejkowana z powodu nieobecnosci
	"Msg":0x0004, #Wiadomosc ma sie pojawic w osobnym okienku
	"Chat":0x0008, #Wiadomosc jest czescia toczacej sie rozmowy i zostanie wyswietlona w istniejacym okienku
	"Ctcp":0x0010, #Wiadomosc jest przeznaczona dla klienta Gadu-Gadu i nie powinna byc wyswietlona uzytkownikowi
	"Ack":0x0020 #Klient nie zyczy sobie potwierdzenia wiadomosci
	})

## Okreslaja stan wyslanej wiadomosci
#
GGMsgStatus = Enum({
	"Blocked":0x0001, #Wiadomosci nie przeslano (zdarza sie przy wiadomosciach zawierajacych adresy internetowe blokowanych przez serwer GG gdy odbiorca nie ma nas na liscie)
	"Delivered":0x0002, #Wiadomosc dostarczona
	"Queued":0x0003, #Wiadomosc zakolejkowana
	"MBoxFull":0x0004, #Wiadomosc nie dostarczona. Skrzynka odbiorcza na serwerze jest pelna (20 wiadomosci max.). Wystepuje tylko w trybie off-line
	"NotDelivered":0x0006 #Wiadomosc nie dostarczona. Odpowiedz ta wystepuje tylko w przypadku wiadomosci klasy Ctcp
	})
	
## Typy pakietow wysylanych do serwera z lista kontaktow w "pakietach" po 400 wpisow
#
GGNotifyTypes = Enum({
	"NotifyFirst":0x000f, # nieostatnie 400 wpisow w liscie kontaktow
	"NotifyLast":0x0010   # ostatnie 400 wpisow
	})

	
