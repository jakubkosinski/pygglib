#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#

from Helpers import Enum

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
	"FriendsMask":0x8000, #Tylko dla przyjaciol
	})

GGUserTypes = Enum({
	"Buddy":0x01, #Kazdy uzytkownik dodany do listy kontaktow
	"Friend":0x02, #Uzytkownik, dla ktorego jestesmy widoczni w trybie "tylko dla przyjaciol"
	"Blocked":0x04, #Uzytkownik, ktorego wiadomosci nie chcemy otrzymywac
	})
	
GGRemotePort = Enum({
	"NotStraightConnection":0, #Klient nie obsluguje bezposredniego polaczenia
	"BehindNAT":1, #Klient laczy sie zza NAT lub innej formy maskarady
	"NotInBuddyList":2, #Klient nie ma nas w swojej liscie kontaktow
	})
	
