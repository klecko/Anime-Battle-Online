import sys
sys.path.append("C:/Users/David/Desktop/programacion/python/Anime Battle Online/server")

import settings
import Globals
from functions.ShortFunctions import *


class Wall():
	def __init__(self, n, rect, color, width=0):
		self.n = n
		self.rect = rect
		self.color = color
		self.width = width
	def checkIfCollidingWithRect(self, rect):
		return self.rect.colliderect(rect)
		


		
class Ranking():
	def __init__(self):
		self.rankingList = []
		self.lastRankingList = ["H3YBR0"]
		
	def actualizar(self):
		self.rankingList = []
		for jugador in Globals.JugadoresEncontrados:
			rankingItem = []
			rankingItem.append(jugador.name)
			rankingItem.append(str(jugador.character.points))
			self.rankingList.append(rankingItem)
		if self.rankingList != self.lastRankingList:
			self.lastRankingList = self.rankingList
			args = ["ranking"]
			for lista in self.rankingList:
				for elemento in lista:
					args.append(elemento)
			sendDataToAllPlayers(packPacket(args))
