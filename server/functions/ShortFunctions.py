import sys

sys.path.append("C:/Users/David/Desktop/programacion/python/Anime Battle Online/server")
import settings
import Globals


def packPacket(args):
	packet = ""
	for arg in args:
		packet = packet + str(arg) + "|"
	return packet

def unpackPacket(string):
	args = string.split('|')
	return args

def sendDataToPlayer(packet, player):
	Globals.s.sendto(packet.encode(), player.addr)
	
def sendDataToAllPlayers(packet):
	for jugador in Globals.JugadoresEncontrados:
		Globals.s.sendto(packet.encode(), jugador.addr)
		
def sendPlayersPosToPlayer(player):
	for jugador in Globals.JugadoresEncontrados:
		sendDataToPlayer(packPacket(["pos", jugador.n, jugador.character.rect.centerx, jugador.character.rect.centery, int(jugador.character.moving)]), player)
		
def sendPlayersDataToPlayer(player):
	for jugador in Globals.JugadoresEncontrados:
		sendDataToPlayer(packPacket(["newUser", jugador.n, jugador.name, jugador.character.n]), player)
		

def sendDataToAddress(packet, address):
	Globals.s.sendto(packet.encode(), address)

def getPlayerByAddress(address):
	for jugador in Globals.JugadoresEncontrados:
		if jugador.addr == address:
			return jugador
	return 0
			
def getPlayerByNumber(numero):
	for player in Globals.Jugadores:
		if player.n == numero:
			return player
	else:
		return None
	
def getPlayerByRect(rect):
	for jugador in Globals.JugadoresEncontrados:
		if jugador.character.rect == rect:
			return jugador
	return 0
	
def getBulletByNumber(numeroBala, character):
	#print(bala1)
	#~ for bala in character.balas: #FORMA EXTRAÑA, SE USA EL FOR PARA "CARGAR" LAS VARIABLES DENTRO DE CHARACTER.BALAS (LO DESCUBRI POR ACCIDENTE)
		#~ try:
			#~ print("1")
			#~ return eval("bala" + str(numeroBala)) #Y DEVUELVE LA VARIABLE balaN. NO FUNCIONA BIEN
		#~ except:
			#~ print("2")
			#~ return 0
			
	for bala in character.balas:  #FORMA ORIGINAL: RECORRE LA LISTA DE BALAS HASTA QUE LA ENCUENTRA
		if bala.n == numeroBala:
			return bala
	return 0


#una manera de obtener los puntos de un cuadrado desde un punto central con un lado x*2+1,
#siendo x la distancia del centro al lado
#ejemplo cuadrado de lado 3: 
#lado arriba: (-1, -1) (0, -1) (1, -1)
#lado abajo: (-1, 1) (0, 1) (1, 1)
#lado derecha: (1, -1) (1, 0) (1, -1)
#lado izquierda: (-1, -1) (-1, 0) (-1, 1)
#faltaria quitarle las esquinas repetidas
#para entenderlo mejor es bueno dibujarlo con una cuadricula
def getPuntosPerimetroCuadrado(distanciaLado):
	lado = 2 * distanciaLado + 1
	puntos = []
	#lado de arriba
	for i in range(0, lado): 
		puntos.append((distanciaLado-i, -distanciaLado))
	#lado de abajo
	for i in range(0, lado):
		puntos.append((distanciaLado-i, distanciaLado))
	#lado de derecha menos esquina superior derecha y esquina inferior izquierda
	for i in range(1, lado-1):
		puntos.append((distanciaLado, distanciaLado-i))
	#lado de izquierda menos esquina superior izquierda y esquina inferior izquierda
	for i in range(1, lado-1):
		puntos.append((-distanciaLado, distanciaLado-i))
	return puntos

