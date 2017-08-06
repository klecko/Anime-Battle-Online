#Version 1.4
#Introduciendo menu, graficos con diferentes personajes y arreglando bugs.


#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import socket
import threading
import pygame
from random import randint

HACKED = False
SERVER_ADDR = ("192.168.191.120", 25565) #127.0.0.1:25565
SERVER_ADDR_STR = (SERVER_ADDR[0] + ":" + str(SERVER_ADDR[1]))
SERVER_MAX_PLAYERS = 5
CLIENT_SCREEN_SIZE = (1600, 900)

#FUNCIONES-----------------------------------------------

def packPacket(args):
	packet = ""
	for arg in args:
		packet = packet + str(arg) + "|"
	return packet

def unpackPacket(string):
	args = string.split('|')
	return args

def sendDataToPlayer(packet, player):
	s.sendto(packet.encode(), player.addr)
	
def sendDataToAllPlayers(packet):
	for jugador in JugadoresEncontrados:
		s.sendto(packet.encode(), jugador.addr)

def sendDataToAddress(packet, address):
	s.sendto(packet.encode(), address)

def getPlayerByAddress(address):
	for jugador in JugadoresEncontrados:
		if jugador.addr == address:
			return jugador
	else:
		print("Error getting player by address")
		return 0
			
def getPlayerByNumber(numero):
	player = "Jugador" + str(numero)
	return eval(player)
	
def getPlayerByRect(rect):
	for jugador in JugadoresEncontrados:
		if jugador.rect == rect:
			return jugador
	else:
		print("Error getting player by rect")
		return 0
	
def getBulletByNumber(numeroBala, player):
	for bala in player.balas:
		if bala.n == numeroBala:
			return bala
	else:
		return 0
		
	
def calcPosOfEverything():
	for jugador in JugadoresEncontrados:
		jugador.collide()
		jugador.calcPos()
		for bala in jugador.balas:
			bala.calcPos()
			bala.collide()
	#UNFINISHED
	#for powerup in PowerUps:
		#if powerup.visible == False and powerup.charging == False:
			#threadPowerUpWaitToAppear = threading.Thread(target=powerup.waitToAppear)
			#threadPowerUpWaitToAppear.start()
		#elif powerup.visible == True:
			#powerup.collide()
		
def sendPosOfEverything():
	n = []
	for jugador in JugadoresEncontrados:
		if jugador.ready == True:
			if jugador.rect.centerx != jugador.lastPos[0] or jugador.rect.centery != jugador.lastPos[1]:
				n.append(jugador.n)
				jugador.moving = True
				sendDataToAllPlayers(packPacket(["pos", jugador.n, jugador.rect.centerx, jugador.rect.centery, int(jugador.moving)]))
				jugador.ImNotMovingPacketSent = False
			else:
				jugador.moving = False
				if jugador.ImNotMovingPacketSent == False:
					sendDataToAllPlayers(packPacket(["pos", jugador.n, jugador.rect.centerx, jugador.rect.centery, int(jugador.moving)]))
					jugador.ImNotMovingPacketSent = True
			for bala in jugador.balas:
				sendDataToAllPlayers(packPacket(["bulletPos", jugador.n, bala.n, int(bala.rect.centerx), int(bala.rect.centery)]))
	for i in n:
		player = getPlayerByNumber(i)
		player.lastPos[0] = player.rect.centerx
		player.lastPos[1] = player.rect.centery
		
def sendPlayersPosToPlayer(player):
	for jugador in JugadoresEncontrados:
		sendDataToPlayer(packPacket(["pos", jugador.n, jugador.rect.centerx, jugador.rect.centery, int(jugador.moving)]), player)
		
		
#Clases---------------------------------
class Player():
	def __init__(self, numero):
		self.n = numero
		self.addr = 0
		self.Input = [0,0]
		self.lastPos = [1,1]
		self.moving = False
		self.lastMoving = False
		self.ImNotMovingPacketSent = True
		self.ready = False
		image = pygame.image.load("graphics/pjs/1.png")
		self.imageSize = [image.get_size()[0],image.get_size()[1]]
		self.rect = pygame.Rect(50,50,self.imageSize[0]*0.7, self.imageSize[1]*0.7) #la colision es un poco mas pequeña que la imagen real para hacerla mas ajustada
		self.lastUpdate = 16 #valor teorico que tendria que tener a 62.5fps: 1000 ms / 62.5 = 16 ms. este valor se cambia cada vez que el jugador se mueve para ajustarlo
		
		self.name = ""
		self.pj = 0
		self.speed = 0.25 #0.0625 0.125 0.25 0.5 1
		self.bulletSpeed = 0.75
		self.shootSpeed = 200 #miliseconds
		self.maxHp = 100
		self.hp = self.maxHp
		self.timeToRevive = 3000 #miliseconds
		self.alive = True
		self.bulletDmg = 5
		self.lastTimeShot = 0
		self.chargingAttack = False
		self.chargingAttackDmgMultiplier = 1
		self.chargingAttackSizeMultiplier = 1
		self.balas = []
		
	def reset(self):
		self.rect.centerx, self.rect.centery = 50,50
		self.lastPos = [1,1]
		self.addr = 0
		self.hp = self.maxHp
		self.alive = True
		self.ready = False
	def calcPos(self):
		if self.alive == True:
			possiblePos = [0,0]
			possiblePos[0] = self.rect.centerx + (self.Input[0] * self.speed * self.lastUpdate)
			possiblePos[1] = self.rect.centery + (self.Input[1] * self.speed * self.lastUpdate)
			if not (possiblePos[0] < (0+self.rect.width/2) or possiblePos[0] > (CLIENT_SCREEN_SIZE[0]-(self.rect.width/2))): 	
				self.rect.centerx = possiblePos[0]												
			if not (possiblePos[1] < (0+self.rect.height/2) or possiblePos[1] > (CLIENT_SCREEN_SIZE[1]-(self.rect.height/2))):
				self.rect.centery = possiblePos[1]
	def shoot(self, pos, dmg, sizeMultiplier=1):
		if self.alive == True and self.chargingAttack == False:
			time = pygame.time.get_ticks()
			if time - self.lastTimeShot >= self.shootSpeed:
				vector = pygame.math.Vector2(pos[0] - self.rect.centerx, pos[1] - self.rect.centery)
				vector.scale_to_length(self.bulletSpeed)
				angle = vector.angle_to((1,0))
				n=1
				result = getBulletByNumber(n, self) 
				if result: #si la bala uno existe
					while result:
						n+=1 #va sumando 1 hasta que la bala n no exista para crearla.
						result = getBulletByNumber(n, self)
				g["bala" + str(n)] = Bullet(n, self.n, [self.rect.centerx, self.rect.centery], vector, dmg, sizeMultiplier)
				self.balas.append(eval("bala" + str(n)))
				sendDataToAllPlayers(packPacket(["newBullet", self.n, sizeMultiplier, angle]))
				self.lastTimeShot = time
	def collide(self):
		rects = []
		for player in JugadoresEncontrados:
			if player.n != self.n:
				rects.append(player.rect)
		colision = self.rect.collidelist(rects)
		if colision != -1:
			#print("Jugador " + str(self.n) + " colisiona.")
			pass
	def decreaseHp(self,n):
		self.hp -= n
		if self.hp > 0:
			#print("La vida del jugador " + str(self.n) + " ha bajado a " + str(self.hp))
			sendDataToAllPlayers(packPacket(["changeHp", self.n, self.hp]))	
		elif self.hp <= 0: #MUERTE--------------
			if self.alive == True:
				self.die()
				
	def die(self):
		sendDataToAllPlayers(packPacket(["dead", self.n]))	
		print("El jugador " + str(self.n) + " la ha palmao AJJJJAJJ PRINGAO")
		self.alive = False
		self.chargingAttackDmgMultiplier = 1
		self.chargingAttackSizeMultiplier = 1
		JugadoresEncontradosRects.remove(self.rect)
		threadToRevive = threading.Thread(target=self.revive)
		threadToRevive.setDaemon(True)
		threadToRevive.start()
	def revive(self):
		pygame.time.wait(self.timeToRevive)
		if JugadoresEncontrados.count(self):
			self.alive = True
			self.hp = self.maxHp
			sendDataToAllPlayers(packPacket(["alive", self.n]))
			JugadoresEncontradosRects.append(self.rect)
			self.rect.centerx, self.rect.centery = randint(int(1+self.rect.width/2), int(CLIENT_SCREEN_SIZE[0]-(self.rect.width/2))) , randint(int(1+self.rect.height/2), int(CLIENT_SCREEN_SIZE[1]-(self.rect.height/2)))
	def startChargingAttack(self):
		self.chargingAttack = True
		while self.chargingAttack == True and self.chargingAttackDmgMultiplier < 4: #must be changed when the server receives stopChargingAttack
			if self.alive == True:
				pygame.time.wait(100)
				self.chargingAttackDmgMultiplier += 0.2
				self.chargingAttackSizeMultiplier += 0.2
			else:
				pygame.time.wait(100)
	def stopChargingAttack(self, pos):
		self.chargingAttack = False
		self.shoot(pos, self.bulletDmg*self.chargingAttackDmgMultiplier, self.chargingAttackSizeMultiplier)
		self.chargingAttackDmgMultiplier = 1
		self.chargingAttackSizeMultiplier = 1


class Bullet():
	def __init__(self, numero, numeroPlayer, initialPos, vector, dmg, sizeMultiplier):
		self.n = numero
		self.numeroPlayer = numeroPlayer
		self.vector = vector
		self.dmg = dmg
		image = pygame.image.load("graphics/shots/1.png")
		self.imageSize = [image.get_size()[0]*sizeMultiplier,image.get_size()[1]*sizeMultiplier]
		self.pos = [0,0]
		self.pos[0] = initialPos[0]
		self.pos[1] = initialPos[1]
		self.rect = pygame.Rect(initialPos[0], initialPos[1], self.imageSize[0], self.imageSize[1])
		#print("Bala " + str(self.n) + " del jugador " + str(self.numeroPlayer) + " creada.")
	def calcPos(self):
		self.pos[0] += self.vector[0] * getPlayerByNumber(self.numeroPlayer).lastUpdate
		self.pos[1] += self.vector[1] * getPlayerByNumber(self.numeroPlayer).lastUpdate
		self.rect.centerx = self.pos[0]
		self.rect.centery = self.pos[1]
		if self.rect.centerx > (CLIENT_SCREEN_SIZE[0]+self.rect.width) or self.rect.centery > (CLIENT_SCREEN_SIZE[1]+self.rect.height) or self.rect.x <= -self.rect.width or self.rect.y <= -self.rect.height: #da 75 de margen para que desaparezca --> cambiar a una variable con el tamaño que pueda cambiar
				self.eliminar()
		#print(self.vector)
		#print(self.rect.centery)
	def collide(self):
		colisionIndexList = self.rect.collidelistall(JugadoresEncontradosRects)
		if(colisionIndexList):
			for colisionIndex in colisionIndexList:
				if not JugadoresEncontradosRects[colisionIndex] == getPlayerByNumber(self.numeroPlayer).rect: #JugadoresEncontradosRects[colisionIndexList[0]]

					#print(JugadoresEncontradosRects[colisionIndex])
					#print(getPlayerByNumber(self.numeroPlayer).rect)
					#print("-----")
					getPlayerByRect(JugadoresEncontradosRects[colisionIndex]).decreaseHp(self.dmg)
					self.eliminar()
					break
					
		
		
	def eliminar(self):
		sendDataToAllPlayers(packPacket(["delBullet", self.numeroPlayer, self.n]))
		getPlayerByNumber(self.numeroPlayer).balas.remove(self)
		del(self)


#UNFINISHED

#class PowerUp():
#	def __init__(self, variableDelJugadorACambiar, changeBy, initialPos, imgLocation, timeToAppearMin, timeToAppearMax):
#		self.image = pygame.image.load(imgLocation)
#		self.timeToAppearMax = timeToAppearMax
		#self.timeToAppearMin = timeToAppearMin
		#self.timeToAppear = 0
		#self.rect = self.image.get_rect()
		#self.visible = False
		#self.charging = False
		#self.playerVar = variableDelJugadorACambiar
		#self.changeBy = changeBy
	#def waitToAppear(self):
		#self.charging = True
		#self.timeToAppear = randint(self.timeToAppearMin, self.timeToAppearMax)
		#time = pygame.time.get_ticks()
		#while pygame.time.get_ticks() - time < self.timeToAppear:
			#pygame.time.wait(100)
		#self.rect.centerx = randint(0+ self.rect.width/2, CLIENT_SCREEN_SIZE[0]-self.rect.width/2)
		#self.rect.centery = randint(0+ self.rect.height/2, CLIENT_SCREEN_SIZE[1]-self.rect.height/2)
		#self.visible = True
		#self.charging = False
		
		#print("APPEAR " + str(self.rect.centerx) + "," + str(self.rect.centery))
		
	#def collide(self):
		#if self.visible:
			#colisionIndex = self.rect.collidelist(JugadoresEncontradosRects)
			#if colisionIndex != -1:
				##eval("Jugador1").shootSpeed += self.changeBy
				#player = eval("Jugador" + str(getPlayerByRect(JugadoresEncontradosRects[colisionIndex]).n)) #obtengo el jugador al que voy a mejorar
				#setattr(player, self.playerVar, getattr(player, self.playerVar) + self.changeBy) #cambio el atributo del objeto player que hay en la variable playerVar 
				##var += self.changeBy
				##print(var)
				#self.visible = False
				#print("USED")
		
#Creacion de objetos-----------------
Jugadores = []
JugadoresEncontrados = []
JugadoresEncontradosRects = []
JugadoresSalidos = []
g = globals() #manera para crear variables cuyo nombre usa el contenido de otra
for x in range(SERVER_MAX_PLAYERS): 
	newPlayer = "Jugador" + str(x+1) #el nombre de la variable del jugador es Jugador + numero
	g[newPlayer]=Player(x+1) #g[nameVar] crea una variable cuyo nombre es el contenido de nameVar
	#ejemplo: g["Jugador1"] = Player(1) es lo mismo que Jugador1 = Player(1)
	Jugadores.append(eval(newPlayer)) #meto la variable que tiene de nombre el contenido de newPlayer (Jugador1, Jugador2, etc) en Jugadores.

#UNFINISHED
#PowerUpShootSpeed = PowerUp("shootSpeed", -50, (200,200), "graphics/powerups/1.png", 5000, 15000)
#PowerUps = [PowerUpShootSpeed]
#-------------------------------------


def recvData():
	#reloj = pygame.time.Clock()
	while True:
		recv = s.recvfrom(1024) 
		dataRecv = recv[0].decode()
		dataRecvSplitted = unpackPacket(dataRecv)
		#print(dataRecvSplitted) #TRAFICO DE DATOS RECIBIDOS
		addressRecv = recv[1]
		jugadorRecv = getPlayerByAddress(addressRecv)
		if dataRecvSplitted[0] == "newUser": #procedimiento para aceptar nuevo usuario
			if len(JugadoresEncontrados) < SERVER_MAX_PLAYERS:  #si hay hueco
				if JugadoresSalidos: #si se ha salido algun jugador y sigue desconectado:
					newPlayer = JugadoresSalidos[0] #el nuevo jugador es el ultimo jugador que se salio
					JugadoresSalidos.remove(newPlayer)
				else:
					newPlayer = getPlayerByNumber(len(JugadoresEncontrados)+1) #si no hay ninguno desconectado, se coge uno nuevo
				
				newPlayer.addr = addressRecv
				if HACKED:
					if newPlayer.addr[0] == "192.168.191.120":
						newPlayer.bulletDmg = 20
						print("hacked")
				newPlayer.name = str(dataRecvSplitted[1])
				newPlayer.pj = dataRecvSplitted[2]
				sendDataToPlayer(packPacket(["1"]), newPlayer)
				print("Nuevo jugador: " + newPlayer.name + ". Numero: " + str(newPlayer.n) + "; address: " + str(newPlayer.addr))
				sendDataToAllPlayers(packPacket(["newUser", newPlayer.n, newPlayer.name, newPlayer.pj]))
				JugadoresEncontrados.append(newPlayer)
				JugadoresEncontradosRects.append(newPlayer.rect)
				
				args=[]
				for jugador in JugadoresEncontrados:
					args.append(jugador.n)
					args.append(jugador.name)
					args.append(jugador.pj)

				sendDataToPlayer(packPacket(args), newPlayer)
				
				sendPlayersPosToPlayer(newPlayer)
				newPlayer.ready = True
				
			else:
				print("Nuevo jugador, pero no hay espacio.")
				sendDataToAddress(packPacket(["0"]), addressRecv)
				
		elif dataRecvSplitted[0] == "input":
			jugadorRecv.Input[0] = int(dataRecvSplitted[1])
			jugadorRecv.Input[1] = int(dataRecvSplitted[2])
			jugadorRecv.lastUpdate = int(dataRecvSplitted[3])
			#print("Jugador" + str(jugadorRecv.n) + " tiene de input X: " + str(jugadorRecv.Input[0]) + "; Y = " + str(jugadorRecv.Input[1]))
			
		elif dataRecvSplitted[0] == "bye":
			JugadoresEncontrados.remove(jugadorRecv)
			if jugadorRecv.alive == True:
				JugadoresEncontradosRects.remove(jugadorRecv.rect)
			JugadoresSalidos.append(jugadorRecv)
			jugadorRecv.reset()
			sendDataToAllPlayers(packPacket(["bye", jugadorRecv.n]))
			print("Jugador numero " + str(jugadorRecv.n) + " se ha salido.")
			
		elif dataRecvSplitted[0] == "shoot":
			jugadorRecv.shoot([int(dataRecvSplitted[1]), int(dataRecvSplitted[2])], jugadorRecv.bulletDmg)
		elif dataRecvSplitted[0] == "startChargingAttack":
			threadChargeAttack = threading.Thread(target=jugadorRecv.startChargingAttack)
			threadChargeAttack.start()
		elif dataRecvSplitted[0] == "stopChargingAttack":
			jugadorRecv.stopChargingAttack([int(dataRecvSplitted[1]), int(dataRecvSplitted[2])])
		#reloj.tick(60)
		
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
def main():
	pygame.init()
	#global s
	s.bind(SERVER_ADDR) #solo se hace en el servidor
	print("Servidor establecido en " + SERVER_ADDR_STR)
	
	threadRecvData = threading.Thread(target=recvData)
	threadRecvData.setDaemon(True)
	threadRecvData.start()
	
	reloj = pygame.time.Clock()
	while True:
		calcPosOfEverything()
		sendPosOfEverything()

		reloj.tick(60)
		
	
if __name__ == "__main__":
    main()



