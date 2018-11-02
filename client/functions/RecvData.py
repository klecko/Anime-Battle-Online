import sys
sys.path.append("C:/Users/David/Desktop/programacion/python/Anime Battle Online/client")
import threading
from pygame import Rect
from socket import timeout

import settings
import Globals
from functions.ShortFunctions import unpackPacket, getPlayerByNumber, getBulletByNumber, getSkillByNumber, goodbye, waitUntilAllSecondaryThreadsClosed
from classes.OtherClasses import PowerUp, Wall
from classes.Players import Player

def tRecvData(tEventExit, PowerUps, Skills, Muros, PointsRanking):
	g = locals()
	while tEventExit.is_set() == False:
		
		try:
			recv = Globals.s.recvfrom(1024)
		except ConnectionResetError:
			print("FATAL ERROR CONNECTION RESET: Se ha perdido la conexión.")
			tEventExit.set()
			waitUntilAllSecondaryThreadsClosed()
			Globals.s.close()
			break
		except timeout:
			print("FATAL ERROR TIMEOUT: Se ha perdido la conexión.")
			tEventExit.set()
			waitUntilAllSecondaryThreadsClosed()
			goodbye()
			break
		dataSplitted = unpackPacket(recv[0].decode())
		#print(dataSplitted)
		if dataSplitted[0] == "exit": #el servidor se ha cerrado: se cierran todos los threads, se cierra el socket y se sale. no es necesario enviar nada al server
			print("EL SERVIDOR SE HA CERRADO")
			tEventExit.set()
			waitUntilAllSecondaryThreadsClosed()
			Globals.s.close()
			break
		elif dataSplitted[0] == "newUser":
			g["Jugador" + dataSplitted[1]] = Player(int(dataSplitted[1]), int(dataSplitted[3]), dataSplitted[2])
			
			Globals.JugadoresEncontrados.append(eval("Jugador" + dataSplitted[1]))
		elif dataSplitted[0] == "pos":
			jugador = getPlayerByNumber(int(dataSplitted[1]))
			jugador.rect.centerx = int(float(dataSplitted[2]))
			jugador.rect.centery = int(float(dataSplitted[3]))
			jugador.moving = bool(int(dataSplitted[4]))
			#~ if jugador.lastPos[0] - jugador.rect.centerx < 0:
				#~ jugador.direction = 1
			#~ elif jugador.lastPos[0] - jugador.rect.centerx > 0:
				#~ jugador.direction = -1
			if jugador.rect.centerx - jugador.lastPos[0] != 0: #si se ha movido, calcula la direccion (1 o -1)
				jugador.direction[0] = (jugador.rect.centerx - jugador.lastPos[0])/abs(jugador.rect.centerx - jugador.lastPos[0])
			if jugador.rect.centery - jugador.lastPos[1] != 0: #si se ha movido, calcula la direccion (1 o -1)
				jugador.direction[1] = (jugador.rect.centery - jugador.lastPos[1])/abs(jugador.rect.centery - jugador.lastPos[1])
			#~ if jugador.direction[0] != jugador.lastDirection[0] and jugador.state == "normal":
				#~ if jugador.direction[0] == 1:
					#~ jugador.setAnimation(jugador.animationStillRight)
				#~ else:
					#~ jugador.setAnimation(jugador.animationStillLeft)
				#~ jugador.lastDirection[0] = jugador.direction[0]
			jugador.lastPos[0] = jugador.rect.centerx
			jugador.lastPos[1] = jugador.rect.centery
		elif dataSplitted[0] == "bye":
			Globals.JugadoresEncontrados.remove(getPlayerByNumber(int(dataSplitted[1])))	
		elif dataSplitted[0] == "newBullet":
			getPlayerByNumber(dataSplitted[1]).newBullet(float(dataSplitted[2]), float(dataSplitted[3]), (float(dataSplitted[5]), float(dataSplitted[6])), dataSplitted[4])
		elif dataSplitted[0] == "delBullet":
			bala = getBulletByNumber(int(dataSplitted[2]), getPlayerByNumber(dataSplitted[1]))
			if bala:
				bala.eliminar()
		elif dataSplitted[0] == "bulletPos":
			bala = getBulletByNumber(int(dataSplitted[2]), getPlayerByNumber(dataSplitted[1]))
			if bala:
				bala.rect.centerx = int(dataSplitted[3])
				bala.rect.centery = int(dataSplitted[4])
		elif dataSplitted[0] == "changeHp":
			getPlayerByNumber(int(dataSplitted[1])).currentHp = float(dataSplitted[2])
			
		elif dataSplitted[0] == "newPowerUp":
			g["PowerUp" + dataSplitted[1]] = PowerUp(dataSplitted[1], int(dataSplitted[2]), (int(dataSplitted[3]), int(dataSplitted[4])))
			PowerUps.append(eval("PowerUp" + dataSplitted[1]))
		elif dataSplitted[0] == "powerUpAppear":
			powerup = eval("PowerUp" + dataSplitted[1]) #el eval este funciona porque la powerup ha sido creada en este metodo
			#por ello, no es necesario buscar la powerup en las listas, como ocurre con las skills (ver elif dataSplitted[0] == "cd")
			powerup.visible = True 
			powerup.rect.centerx = int(dataSplitted[2])
			powerup.rect.centery = int(dataSplitted[3])
		elif dataSplitted[0] == "powerUpDisappear":
			eval("PowerUp" + dataSplitted[1]).visible = False
		elif dataSplitted[0] == "ranking":
			rankingList = []
			i = 1
			while dataSplitted[i]:
				rankingItem = [dataSplitted[i], dataSplitted[i+1]]
				rankingList.append(rankingItem)
				i = i + 2 #los valores recibidos van de dos en dos: nombre Y PUNTOS
			PointsRanking.rankingList = rankingList
		elif dataSplitted[0] == "cd": #cd nskill cd1 cd2 cd3...
			skill = getSkillByNumber(dataSplitted[1], Skills)
			cds = [] #creo una lista vacia
			i=2 #y un contador que empieza en 2, ya que el primer cd esta en la posicion 2
			while dataSplitted[i]: #si hay un numero en la posicion i, la añade a la lista, y mira en la siguiente posicion
				cds.append(float(dataSplitted[i]))
				i += 1
			threadWaitCd = threading.Thread(target=skill.tWaitCd, args=(tEventExit,cds,), name="skill.tWaitCd", daemon=True)
			threadWaitCd.start()
		#~ elif dataSplitted[0] == "animation":
			#~ #sendDataToAllPlayers(packPacket(["animation", self.nPlayer, "chargeRasenganLeft"]))
			#~ jugador = getPlayerByNumber(int(dataSplitted[1]))
			#~ jugador.setAnimation(eval("Jugador" + dataSplitted[1] + ".animation" + dataSplitted[2]))
			#~ #if not dataSplitted[2] == "StillRight" or dataSplitted[2] == "StillLeft":
			#~ if jugador.direction[0] == 1:
				#~ jugador.nextAnimations.append(jugador.animationStillRight)
			#~ elif jugador.direction[0] == -1:
				#~ jugador.nextAnimations.append(jugador.animationStillLeft)
		#~ elif dataSplitted[0] == "image":
			#~ jugador.setImageNoAnimation(eval("Jugador" + dataSplitted[1] + ".image" + dataSplitted[2]))
		elif dataSplitted[0] == "state":
			jugador = getPlayerByNumber(int(dataSplitted[1]))
			jugador.state = dataSplitted[2]
			
			

				
		elif dataSplitted[0] == "newWall":#(["newWall", muro.n, muro.rect.x, muro.rect.y, muro.rect.width, muro.rect.height, muro.color[0], muro.color[1], muro.color[2], muro.width()])
			#(self, n, rect, color, width=0):
			g["Muro" + dataSplitted[1]] = Wall(int(dataSplitted[1]), Rect(int(dataSplitted[2]), int(dataSplitted[3]), int(dataSplitted[4]), int(dataSplitted[5])),
			(int(dataSplitted[6]), int(dataSplitted[7]), int(dataSplitted[8])), int(dataSplitted[9]))
			Muros.append(eval("Muro" + dataSplitted[1]))
