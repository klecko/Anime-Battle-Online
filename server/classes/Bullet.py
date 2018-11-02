import sys
sys.path.append("C:/Users/David/Desktop/programacion/python/Anime Battle Online/server")
import pygame.image

import settings
import Globals
from functions.ShortFunctions import *


class Bullet():
	def __init__(self, numero, numeroPlayer, initialPos, vector, dmg, sizeMultiplier, nImagen):
		self.n = numero
		self.numeroPlayer = numeroPlayer
		self.vector = vector
		self.dmg = dmg
		image = pygame.image.load("graphics/shots/" + str(nImagen) + ".png")
		self.imageSize = [image.get_size()[0]*sizeMultiplier,image.get_size()[1]*sizeMultiplier]
		self.pos = [initialPos[0],initialPos[1]]
		self.rect = pygame.Rect(initialPos[0], initialPos[1], self.imageSize[0], self.imageSize[1])
		self.eliminada = False
	def calcPos(self):
		self.pos[0] += self.vector[0] * 16 #LASTUPDATE
		self.pos[1] += self.vector[1] * 16 #una variable POS es necesaria para tener en cuenta los decimales, ya que si se pone directamente al rect, la exactitud disminuye mucho
		self.rect.centerx = self.pos[0]##self.pos[0]
		self.rect.centery = self.pos[1]##self.pos[1]
		
			
	def collide(self, MurosRects):
		colisionIndexList = self.rect.collidelistall(Globals.JugadoresEncontradosRects) #lista de indices de rectangulos con los que colisiona de la lista Globals.JugadoresEncontradosRects
		#uso collidelistall porque si uso collidelist, el resultado va a ser siempre el jugador que dispara
		#ya que es el primer jugador al que "toca"
		if(colisionIndexList): #si colisiona con algun player
			for colisionIndex in colisionIndexList: #por cada colision
				if not Globals.JugadoresEncontradosRects[colisionIndex] == getPlayerByNumber(self.numeroPlayer).character.rect: #si el rectangulo con el que colisiona no es el del jugador que ha disparado:

					jugadorColisionado = getPlayerByRect(Globals.JugadoresEncontradosRects[colisionIndex])
					jugadorColisionado.character.decreaseHp(self.dmg, getPlayerByNumber(self.numeroPlayer).character)
					self.eliminar()
					break #y se sale para no colisionar con mas de uno
					
		elif (self.rect.centerx > (settings.CLIENT_SCREEN_SIZE[0]+self.rect.width) or  #si se sale de la pantalla
		self.rect.centery > (settings.CLIENT_SCREEN_SIZE[1]+self.rect.height) or 
		self.rect.x <= -self.rect.width or 
		self.rect.y <= -self.rect.height): 
			self.eliminar()
			
		else:
			if self.rect.collidelist(MurosRects) != -1:
				self.eliminar()
		
		
	def eliminar(self):
		if self.eliminada == False: #a veces al colisionar con un player y un wall se eliminaba dos veces
			sendDataToAllPlayers(packPacket(["delBullet", self.numeroPlayer, self.n]))
			getPlayerByNumber(self.numeroPlayer).character.balas.remove(self)
			self.eliminada = True
			del(self)
