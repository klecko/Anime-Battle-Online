import sys
sys.path.append("C:/Users/David/Desktop/programacion/python/Anime Battle Online/server")
import threading

import settings
import Globals
from functions.ShortFunctions import *
from classes.Players import *


def tRecvData(PowerUps, Muros):
	#reloj = pygame.time.Clock()
	while True:
		try:
			recv = Globals.s.recvfrom(1024)
		except ConnectionResetError:
			print("FATAL ERROR: CONNECTION RESET")
			try:
				sendDataToAllPlayers(packPacket(["areyoualive"]))
			except ConnectionResetError:
				print("ERROR AL ENVIAR AREYOUALIVE PACKET")
			continue
		#print(recv)
		dataRecv = recv[0].decode()
		dataRecvSplitted = unpackPacket(dataRecv)
		#print(dataRecvSplitted) #TRAFICO DE DATOS RECIBIDOS
		addressRecv = recv[1]
		jugadorRecv = getPlayerByAddress(addressRecv)
		if dataRecvSplitted[0] == "newUser": #procedimiento para aceptar nuevo usuario
			if len(Globals.JugadoresEncontrados) < settings.SERVER_MAX_PLAYERS and dataRecvSplitted[1]:  #si hay hueco y el nombre no esta vacio (solo puede estar vacio si se hackeara)
				if Globals.JugadoresSalidos: #si se ha salido algun jugador y sigue desconectado:
					newPlayer = Globals.JugadoresSalidos[0] #el nuevo jugador es el ultimo jugador que se salio
					Globals.JugadoresSalidos.remove(newPlayer)
				else:
					newPlayer = getPlayerByNumber(len(Globals.JugadoresEncontrados)+1) #si no hay ninguno desconectado, se coge uno nuevo
				
				newPlayer.addr = addressRecv
				newPlayer.name = dataRecvSplitted[1]
				
				if settings.HACKED:
					if newPlayer.addr[0] == "192.168.191.120": #mi ip EJEJJEJE
						newPlayer.character.bulletDmg = 20
						print("settings.HACKED")
				
				if dataRecvSplitted[2] == "1":	
					newPlayer.character = charNaruto(newPlayer.n)
				elif dataRecvSplitted[2] == "2":	
					newPlayer.character = charHinata(newPlayer.n)
				elif dataRecvSplitted[2] == "3":	
					newPlayer.character = charSaitama(newPlayer.n)
				elif dataRecvSplitted[2] == "4":	
					newPlayer.character = charDeku(newPlayer.n)
				elif dataRecvSplitted[2] == "5":	
					newPlayer.character = charSora(newPlayer.n)
				sendDataToPlayer(packPacket(["1"]), newPlayer) #acepto la conexion
				print("Nuevo jugador: " + newPlayer.name + ". Numero: " + str(newPlayer.n) + "; address: " + str(newPlayer.addr))
				sendDataToAllPlayers(packPacket(["newUser", newPlayer.n, newPlayer.name, newPlayer.character.n])) #le envio a todos los jugadores menos al nuevo los datos del nuevo jugador
				Globals.JugadoresEncontrados.append(newPlayer)
				Globals.JugadoresEncontradosRects.append(newPlayer.character.rect)
				
				sendPlayersDataToPlayer(newPlayer)#le envio al nuevo jugador la informacion de todos los jugadores conectados incluyendole(numero, nombre y personaje escogido)
				sendPlayersPosToPlayer(newPlayer) #le envio tambien las posiciones de estos jugadores
				for powerup in PowerUps:
					sendDataToPlayer(packPacket(["newPowerUp", powerup.n, int(powerup.visible), powerup.rect.centerx, powerup.rect.centery]), newPlayer) #tambien las powerups existentes
				
				for muro in Muros:
					sendDataToPlayer(packPacket(["newWall", muro.n, muro.rect.x, muro.rect.y, muro.rect.width, muro.rect.height, muro.color[0], muro.color[1], muro.color[2], muro.width]), newPlayer)
				newPlayer.ready = True
				
			else:
				print("Nuevo jugador, pero no hay espacio.")
				sendDataToAddress(packPacket(["0"]), addressRecv)
				
		elif dataRecvSplitted[0] == "input":
			jugadorRecv.character.Input[0] = int(dataRecvSplitted[1])
			jugadorRecv.character.Input[1] = int(dataRecvSplitted[2])
			
		elif dataRecvSplitted[0] == "bye":
			Globals.JugadoresEncontrados.remove(jugadorRecv)
			if jugadorRecv.character.alive == True:
				Globals.JugadoresEncontradosRects.remove(jugadorRecv.character.rect)
			Globals.JugadoresSalidos.append(jugadorRecv)
			jugadorRecv.reset()
			sendDataToAllPlayers(packPacket(["bye", jugadorRecv.n]))
			print("Jugador numero " + str(jugadorRecv.n) + " se ha salido.")
			
		elif dataRecvSplitted[0] == "shoot":
			jugadorRecv.character.shoot([int(dataRecvSplitted[1]), int(dataRecvSplitted[2])], jugadorRecv.character.bulletDmg)
		
		elif dataRecvSplitted[0] == "skill":
			skill = eval("jugadorRecv.character.tSkill" + dataRecvSplitted[1])
			threadSpecialAttack = threading.Thread(target=skill, args=([int(dataRecvSplitted[2]), int(dataRecvSplitted[3])],), name="jugadorRecv.character.tSkill" + dataRecvSplitted[1], daemon=True)
			threadSpecialAttack.start()
		#CHARGING
		#~ elif dataRecvSplitted[0] == "startChargingAttack":
			#~ threadChargeAttack = threading.Thread(target=jugadorRecv.tStartChargingAttack)
			#~ threadChargeAttack.setDaemon = True
			#~ threadChargeAttack.start()
		#~ elif dataRecvSplitted[0] == "stopChargingAttack":
			#~ jugadorRecv.stopChargingAttack([int(dataRecvSplitted[1]), int(dataRecvSplitted[2])])
			
		#reloj.tick(60)
