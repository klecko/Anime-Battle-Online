import sys
sys.path.append("C:/Users/David/Desktop/programacion/python/Anime Battle Online/server")
import pygame.time

import settings
import Globals
from functions.ShortFunctions import *

def tCalcAndSend(PowerUps, MurosRects, Ranking):
	reloj = pygame.time.Clock()
	while True:
		calcPosOfEverything(PowerUps, MurosRects, Ranking)
		sendPosOfEverything()
		reloj.tick(60)

def tTimeOut():
	while True:
		sendDataToAllPlayers(packPacket(["1"]))
		pygame.time.wait(2000)

def calcPosOfEverything(PowerUps, MurosRects, Ranking):
	
	for jugador in Globals.JugadoresEncontrados:
		#jugador.character.collide()
		jugador.character.calcPos(MurosRects)
		for bala in jugador.character.balas:
			bala.calcPos()
			bala.collide(MurosRects)
	for powerup in PowerUps:
		powerup.collide(MurosRects)
			
	Ranking.actualizar()
	
		
		
def sendPosOfEverything():
	n = []
	
	for jugador in Globals.JugadoresEncontrados:
		if jugador.ready == True:
			if jugador.character.rect.centerx != jugador.character.lastPos[0] or jugador.character.rect.centery != jugador.character.lastPos[1]:
				n.append(jugador.n)
				jugador.character.moving = True
				sendDataToAllPlayers(packPacket(["pos", jugador.n, jugador.character.rect.centerx, jugador.character.rect.centery, int(jugador.character.moving)]))
				jugador.character.ImNotMovingPacketSent = False
				jugador.character.lastPos = [jugador.character.rect.centerx, jugador.character.rect.centery]
			else:
				jugador.character.moving = False
				if jugador.character.ImNotMovingPacketSent == False:
					sendDataToAllPlayers(packPacket(["pos", jugador.n, jugador.character.rect.centerx, jugador.character.rect.centery, int(jugador.character.moving)]))
					jugador.character.ImNotMovingPacketSent = True
			for bala in jugador.character.balas:
				sendDataToAllPlayers(packPacket(["bulletPos", jugador.n, bala.n, round(bala.rect.centerx), round(bala.rect.centery)]))
	#~ for i in n:
		#~ player = getPlayerByNumber(i)
		#~ player.character.lastPos[0] = player.character.rect.centerx
		#~ player.character.lastPos[1] = player.character.rect.centery
