import sys
sys.path.append("C:/Users/David/Desktop/programacion/python/Anime Battle Online/server")
import pygame
import threading
from random import randint

import settings
import Globals
from functions.ShortFunctions import *


class PowerUp():
	def __init__(self, variableDelJugadorACambiar, changeBy, n, timeToAppearMin, timeToAppearMax, timeToRestoreAttr):
		self.n = n
		self.image = pygame.image.load("graphics/powerups/" + str(self.n) + ".png")
		self.timeToAppearMax = timeToAppearMax
		self.timeToAppearMin = timeToAppearMin
		self.timeToAppear = 0
		self.timeToRestoreAttr = timeToRestoreAttr
		self.rect = self.image.get_rect()
		self.visible = False
		self.charging = False
		self.playerVar = variableDelJugadorACambiar
		self.changeBy = changeBy
		thread = threading.Thread(target=self.tWaitToAppear, name="self.tWaitToAppear", daemon=True)
		thread.start()
		
	def tWaitToAppear(self):
		self.charging = True
		self.timeToAppear = randint(self.timeToAppearMin, self.timeToAppearMax)
		pygame.time.wait(self.timeToAppear)
		self.rect.centerx = randint(round(self.rect.width/2), round(settings.CLIENT_SCREEN_SIZE[0]-self.rect.width/2))
		self.rect.centery = randint(0+ self.rect.height/2, settings.CLIENT_SCREEN_SIZE[1]-self.rect.height/2)
		self.visible = True
		self.charging = False
		sendDataToAllPlayers(packPacket(["powerUpAppear", self.n, self.rect.centerx, self.rect.centery]))
	
	def collide(self, MurosRects):
		if self.visible:
			if self.rect.collidelist(MurosRects) != -1:
				while self.rect.collidelist(MurosRects) != -1:
					self.rect.centerx = randint(round(self.rect.width/2), round(settings.CLIENT_SCREEN_SIZE[0]-self.rect.width/2))
					self.rect.centery = randint(0+ self.rect.height/2, settings.CLIENT_SCREEN_SIZE[1]-self.rect.height/2)
					print(self.n, "had to change")
				sendDataToAllPlayers(packPacket(["powerUpAppear", self.n, self.rect.centerx, self.rect.centery]))
			
				
			colisionIndex = self.rect.collidelist(Globals.JugadoresEncontradosRects)
			if colisionIndex != -1:
				player = getPlayerByRect(Globals.JugadoresEncontradosRects[colisionIndex]) #obtengo el jugador al que voy a mejorar
				setattr(player.character, self.playerVar, getattr(player.character, self.playerVar) + self.changeBy) #cambio el atributo del objeto player que hay en la variable playerVar 
				self.visible = False
				sendDataToAllPlayers(packPacket(["powerUpDisappear", self.n]))
				
				thread = threading.Thread(target=self.tWaitToRestoreAttr, args=(player, self.playerVar, self.changeBy, self.timeToRestoreAttr), name="self.tWaitToRestoreAttr", daemon=True)
				thread.start()
				thread2 = threading.Thread(target=self.tWaitToAppear, name="tWaitToAppear", daemon=True)
				thread2.start()
	
	def tWaitToRestoreAttr(self, player, playerVar, changeBy, waitTime):
		player.character.playerVarsBeenChanging.append([playerVar, changeBy]) #meto la variable que he cambiado y por cuanto en una variable del jugador
		pygame.time.wait(waitTime)
		setattr(player.character, playerVar, getattr(player.character, playerVar) - changeBy)
		player.character.playerVarsBeenChanging.remove([playerVar, changeBy]) #cuando he vuelto el atributo a su normalidad, lo quito de la variable del jugador
		#esto es por si el jugador se desconecta mientras esta funcion se esta ejecutando. en este caso, el metodo reset del player devuelve todos los valores
		#a la normalidad, y despues los que estaban cambiandose los mejora, de manera que sea esta funcion la que los devuelva a la normalidad
