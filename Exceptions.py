#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

class GGException(Exception):
	pass

class GGUnexceptedPacket(GGException):
	pass
	
class GGNotLogged(GGException):
	pass

class GGServerNotOperating(GGException):
	pass
	
class GGBadTokenVal(GGException):
	pass
