import sys
sys.path.append("C:/Users/David/Desktop/programacion/python/Anime Battle Online/server")
import threading
import pygame.image
from random import randint

import settings
import Globals
from functions.ShortFunctions import *
from classes.Bullet import Bullet

class Player():
	def __init__(self, numero):
		self.n = numero
		self.addr = 0
		self.ready = False
		

		self.name = ""
		self.character = 0
	#CHARGING
	#~ def tStartChargingAttack(self):
		#~ self.chargingAttack = True
		#~ while self.chargingAttack == True and self.chargingAttackDmgMultiplier < 5: #must be changed when the server receives stopChargingAttack
			#~ if self.alive == True:
				#~ self.chargingAttackDmgMultiplier += 0.2
				#~ self.chargingAttackSizeMultiplier += 0.2
				#~ self.chargingAttackSpeedMultiplier += 0.05
			#~ pygame.time.wait(100)
	#~ def stopChargingAttack(self, pos):
		#~ self.chargingAttack = False
		#~ self.shoot(pos, self.bulletDmg*self.chargingAttackDmgMultiplier, self.chargingAttackSizeMultiplier, self.chargingAttackSpeedMultiplier)
		#~ self.chargingAttackDmgMultiplier = 1
		#~ self.chargingAttackSizeMultiplier = 1
		#~ self.chargingAttackSpeedMultiplier = 1
	def reset(self): #resetea todos los valores a los valores iniciales
		self.character.reset()
		self.addr = 0
		self.ready = False
		self.name = ""


class character(): #clase character que es el personaje por defecto.
	def __init__(self, nPlayer, n=1):
		self.n = n
		self.nPlayer = nPlayer
		self.lastPos = [1,1]
		self.Input = [0, 0]
		self.direction = [0, 0]
		self.points = 0
		self.moving = False
		image = pygame.image.load("graphics/pjs/" + str(self.n) + "/StillRight1.png")
		self.imageSize = image.get_size()
		self.rect = pygame.Rect(50,50,self.imageSize[0]*0.7, self.imageSize[1]*0.7) #la colision es un poco mas pequeña que la imagen real para hacerla mas ajustada
		#self.lastUpdate = 16 #valor teorico que tendria que tener a 62.5fps: 1000 ms / 62.5 = 16 ms. este valor se cambia cada vez que el jugador se mueve para ajustarlo
		self.initialBulletPos = ((self.rect.centerx + ((self.rect.width-20)*self.direction[0])), (self.rect.centery+20))
		
		self.couldBeInsideWall = True
		self.movementAvailable = True
		self.speed = 0.25 #0.0625 0.125 0.25 0.5 1 estaba en 0.25
		self.bulletSpeed = 0.75 #ESTABA EN 0.75
		self.shootSpeed = 200 #miliseconds estaba en 200
		self.bulletSizeMultiplier = 1
		self.maxHp = 100
		self.hp = self.maxHp
		self.timeToRevive = 5000 #miliseconds
		self.alive = True
		self.bulletDmg = 5
		self.lastTimeShot = 0
		self.chargingAttack = False
		self.chargingAttackDmgMultiplier = 1
		self.chargingAttackSizeMultiplier = 1
		self.chargingAttackSpeedMultiplier = 1
		self.balas = []
		self.playerVarsBeenChanging = [] #la estructura sera [[VAR, CHANGEBY], [VAR, CHANGEBY], ...]
		self.cd2 = 26 #la ulti tiene 26 segundos de cd
		self.actualCd2 = 0 #al principio la ulti no esta en cd
		
	def shoot(self, posToShoot, dmg, sizeMultiplier=1, speedMultiplier=1, nImagen=0):
		if sizeMultiplier == 1: #por defecto esta variable es 1, si se le pasa un valor se establece ese valor
			sizeMultiplier = self.bulletSizeMultiplier #y si no se establece ninguno, adquiere el valor de self.bulletSizeMultiplier
		if not nImagen:
			nImagen = self.n
		if self.alive == True and self.chargingAttack == False:
			time = pygame.time.get_ticks()
			if time - self.lastTimeShot >= self.shootSpeed: #ENTONCES DISPARA
				vector = pygame.math.Vector2(posToShoot[0] - self.initialBulletPos[0], posToShoot[1] - self.initialBulletPos[1])
				if vector.length() != 0:
					vector.scale_to_length(self.bulletSpeed*speedMultiplier)
				else:
					return
				
				angle = vector.angle_to((1,0))
				#print("Vector:", vector, ". Angle:", angle)
				
				n=1
				result = getBulletByNumber(n, self) 
				if result: #si la bala uno existe
					while result:
						n+=1 #va sumando 1 hasta que la bala n no exista para crearla.
						result = getBulletByNumber(n, self)
				sendDataToAllPlayers(packPacket(["newBullet", self.nPlayer, sizeMultiplier, angle, nImagen, self.initialBulletPos[0], self.initialBulletPos[1]]))
				locals()["bala" + str(n)] = Bullet(n, self.nPlayer, self.initialBulletPos, vector, dmg, sizeMultiplier, nImagen)
				self.balas.append(eval("bala" + str(n)))
				
				self.lastTimeShot = time
				
	def calcPos(self, MurosRects):
		#print(self.rect.centerx, self.rect.centery)
		if self.couldBeInsideWall:
			while self.rect.collidelist(MurosRects) != -1: 
				self.rect.centerx, self.rect.centery = randint(int(self.rect.width/2), int(settings.CLIENT_SCREEN_SIZE[0]-(self.rect.width/2))) , randint(int(1+self.rect.height/2), int(settings.CLIENT_SCREEN_SIZE[1]-(self.rect.height/2)))
			self.couldBeInsideWall = False
					
		if self.alive == True and self.movementAvailable == True:
			possiblePos = [0,0]
			possiblePos[0] = self.rect.centerx + (self.Input[0] * self.speed * 16) #LASTUPDATE
			possiblePos[1] = self.rect.centery + (self.Input[1] * self.speed * 16) #16 es el numero de milisegundos entre cada fps cuando va a ~60fps 
			possibleRectx, possibleRecty = self.rect.copy(), self.rect.copy()
			possibleRectx.centerx = possiblePos[0]
			possibleRecty.centery = possiblePos[1]
			if possiblePos[0] > (self.rect.width/2) and possiblePos[0] < (settings.CLIENT_SCREEN_SIZE[0]-(self.rect.width/2)): 	#analiza si se sale de la pantalla
				if possibleRectx.collidelist(MurosRects) == -1: #si no colisiona con algun muro se cambia la posicion
					self.rect.centerx = possiblePos[0]												
			if possiblePos[1] > (self.rect.height/2) and possiblePos[1] < (settings.CLIENT_SCREEN_SIZE[1]-(self.rect.height/2)):
				if possibleRecty.collidelist(MurosRects) == -1:
					self.rect.centery = possiblePos[1]
				
			if self.rect.centerx - self.lastPos[0] != 0: #si se ha movido, calcula la direccion (1 o -1)
				self.direction[0] = (self.rect.centerx - self.lastPos[0])/abs(self.rect.centerx - self.lastPos[0])
			if self.rect.centery - self.lastPos[1] != 0:
				self.direction[1] = (self.rect.centery - self.lastPos[1])/abs(self.rect.centery - self.lastPos[1])
				
			self.initialBulletPos = ((self.rect.centerx + ((self.rect.width-20)*self.direction[0])), (self.rect.centery+20)) #calcula la posicion inicial de donde saldrian las balas
		#print(self.playerVarsBeenChanging)
	def checkIfCollidingWithPlayers(self):
		colisionIndexList = self.rect.collidelistall(Globals.JugadoresEncontradosRects)
		return colisionIndexList
		#if colision != -
			#print("Jugador " + str(self.n) + " colisiona.")
			#pass
	
	def decreaseHp(self,n, characterQueHaceDaño):
		self.hp -= n
		if self.hp > 0:
			sendDataToAllPlayers(packPacket(["changeHp", self.nPlayer, self.hp]))	
		elif self.hp <= 0: #MUERTE--------------
			if self.alive == True:
				self.die()
				characterQueHaceDaño.points += 1
				
	def die(self):
		sendDataToAllPlayers(packPacket(["state", self.nPlayer, "dead"]))
		sendDataToAllPlayers(packPacket(["changeHp", self.nPlayer, 0]))	
		self.alive = False
		self.movementAvailable = False
		#~ self.chargingAttackDmgMultiplier = 1 #CHARGING
		#~ self.chargingAttackSizeMultiplier = 1
		Globals.JugadoresEncontradosRects.remove(self.rect)
		threadToRevive = threading.Thread(target=self.tRevive, name="self.tRevive", daemon=True)
		threadToRevive.start()
		
	def tRevive(self):
		pygame.time.wait(self.timeToRevive)
		if Globals.JugadoresEncontrados.count(getPlayerByNumber(self.nPlayer)):
			self.alive = True
			self.movementAvailable = True
			self.hp = self.maxHp
			sendDataToAllPlayers(packPacket(["state", self.nPlayer, "normal"]))
			sendDataToAllPlayers(packPacket(["changeHp", self.nPlayer, self.maxHp]))
			Globals.JugadoresEncontradosRects.append(self.rect)
			self.rect.centerx, self.rect.centery = randint(int(self.rect.width/2), int(settings.CLIENT_SCREEN_SIZE[0]-(self.rect.width/2))) , randint(int(1+self.rect.height/2), int(settings.CLIENT_SCREEN_SIZE[1]-(self.rect.height/2)))
			self.couldBeInsideWall = True
			
	def reset(self): #resetea todos los valores a los valores iniciales
		self.rect.centerx, self.rect.centery = 50,50
		self.lastPos = [1,1]
		self.hp = self.maxHp
		self.alive = True
		self.speed = 0.25 #0.0625 0.125 0.25 0.5 1 estaba en 0.25
		self.bulletSpeed = 0.75 #ESTABA EN 0.75
		self.shootSpeed = 200 #miliseconds estaba en 200
		self.maxHp = 100
		self.hp = self.maxHp
		self.timeToRevive = 3000 #miliseconds
		self.bulletDmg = 5
		self.actualCdUlti = 0
		self.movementAvailable = True
		if self.playerVarsBeenChanging: #si el jugador cogio una mejora y se desconectó, el thread que volverá el valor a la normalidad seguirá activo esperando
			#este thread mete la variable que esta cambiando y el valor que le está sumando dentro de self.playerVarsBeenChanging, y la remueve despues de resetear la variable del jugador
			#cada uno de los elementos de playerVarsBeenChanging es [VAR, CHANGEBY]
			#sin embargo, el valor ya está reseteado ya que se ha desconectado, por lo que tengo que volver a subir el valor para que el thread lo baje y quede reseteado.
			
			for elemento in self.playerVarsBeenChanging:
				setattr(self, elemento[0], getattr(self, elemento[0]) + elemento[1]) #cambio el atributo del objeto player que hay en la variable playerVar 
	
	def tCdSkill(self, nSkill, cdToWait, cdsToSendToClient):
		argsPacket = ["cd", nSkill]
		for cdToSendToClient in cdsToSendToClient:
			argsPacket.append(cdToSendToClient)
		sendDataToPlayer(packPacket(argsPacket), getPlayerByNumber(self.nPlayer))
		locals()["self.actualCd" + str(nSkill)] = cdToWait #esto es complejo. eval se usa para obtener el valor dentro de la variable del nombre que le pases
		#y globals() se usa para llamar a la variable de ese nombre
		actualCdSkill =  eval("self.actualCd" + str(nSkill))
		while actualCdSkill > 0:
			pygame.time.wait(100)
			g["self.actualCd" + str(nSkill)] -= 0.1
			
	def tDefaultBuffSkill(self, varsAndChangebysList, timeMiliseconds): #[[value, changeby][value, changeby]]
		for varAndChangeby in varsAndChangebysList:
			setattr(self, varAndChangeby[0], getattr(self, varAndChangeby[0]) + varAndChangeby[1])
			self.playerVarsBeenChanging.append([varAndChangeby[0], varAndChangeby[1]])
		
		sendDataToAllPlayers(packPacket(["state", self.nPlayer, "buffed"]))
		pygame.time.wait(round(timeMiliseconds))
		sendDataToAllPlayers(packPacket(["state", self.nPlayer, "normal"]))
		
		for varAndChangeby in varsAndChangebysList:
			setattr(self, varAndChangeby[0], getattr(self, varAndChangeby[0]) - varAndChangeby[1])
			self.playerVarsBeenChanging.remove([varAndChangeby[0], varAndChangeby[1]])
			
	def tChangeVarForTime(self, var, newValue, timeMiliseconds):
		oldValue = getattr(self, var)
		setattr(self, var, newValue)
		self.playerVarsBeenChanging.append([var, newValue-oldValue])
		pygame.time.wait(round(timeMiliseconds))
		setattr(self, var, oldValue)
		self.playerVarsBeenChanging.remove([var, newValue-oldValue])
			
				
class charNaruto(character):
	def __init__(self, nPlayer):
		super().__init__(nPlayer, 1)
	
	def tSkill1(self, mousePos):
		pass
		
	def tSkill2(self, mousePos):
		#self.shoot(self, pos, dmg, sizeMultiplier=0, speedMultiplier=1, nImagen=0)
		if self.actualCd2 <= 0:
			#~ if self.direction[0] == 1:
				#~ sendDataToAllPlayers(packPacket(["animation", self.nPlayer, "ChargeRasenganRight"]))
			#~ elif self.direction[0] == -1:
				#~ sendDataToAllPlayers(packPacket(["animation", self.nPlayer, "ChargeRasenganLeft"]))
			sendDataToAllPlayers(packPacket(["state", self.nPlayer, "chargingAttack"]))
			threadCdUlti = threading.Thread(target=self.tCdSkill, args=(2, self.cd2, [self.cd2]), name="self.tCdSkill", daemon=True)
			threadCdUlti.start()
			self.tChangeVarForTime("movementAvailable", False, 500) #no es necesario hacer un thread, ya que simplemente podemos esperar 
			sendDataToAllPlayers(packPacket(["state", self.nPlayer, "normal"]))
			self.lastTimeShot = pygame.time.get_ticks() - self.shootSpeed #se hace para que este listo para disparar
			self.shoot(mousePos, self.bulletDmg*15, 1, 2, "1_ulti")
			

class charHinata(character):
	def __init__(self, nPlayer):
		super().__init__(nPlayer, 2)
		self.timeSkill2 = 4.5
	
	def tSkill1(self, mousePos):
		pass
	
	def tSkill2(self, mousePos):
		if self.actualCd2 <= 0:
			shootSpeedChangeValue = -150
			bulletSpeedChangeValue = 0.75
			
			varsAndChangebysList = [["shootSpeed", shootSpeedChangeValue],["bulletSpeed", bulletSpeedChangeValue]]
			threadCdUlti = threading.Thread(target=self.tCdSkill, args=(2, self.cd2, [self.timeSkill2, self.cd2 - self.timeSkill2]), name="self.tCdSkill", daemon=True)
			threadCdUlti.start()
			self.tDefaultBuffSkill(varsAndChangebysList, self.timeSkill2*1000)
			#~ threadBuffUlti = threading.Thread(target=self.tDefaultBuffSkill, args=(varsAndChangebysList, self.timeSkill2*1000))
			#~ threadBuffUlti.setDaemon = True
			#~ threadBuffUlti.start()

			
	
class charSaitama(character):
	def __init__(self, nPlayer):
		super().__init__(nPlayer, 3)
	
	def tSkill1(self, mousePos):
		pass
	
	def tSkill2(self, mousePos):
		if self.actualCd2 <= 0:
			threadCdUlti = threading.Thread(target=self.tCdSkill, args=(2, self.cd2, [self.cd2]), name="self.tCdSkill", daemon=True)
			threadCdUlti.start()
			colisionIndexList = self.checkIfCollidingWithPlayers()
			for colisionIndex in reversed(colisionIndexList): #se hace en reverse porque cuando un jugador muere se quita de esa lista,
				#de manera que el que esta en la pos 2 pasaria a estar en la pos 1
				#getPlayerByNumber(colisionIndex+1).character.decreaseHp(100) solo funciona cuando no se ha salido ningun personaje
				playerColisionado = getPlayerByRect(Globals.JugadoresEncontradosRects[colisionIndex])
				if playerColisionado.character.rect != self.rect:
					sendDataToAllPlayers(packPacket(["state", self.nPlayer, "chargingAttack"]))
					threadInmovilizar = threading.Thread(target=self.tChangeVarForTime, args=("movementAvailable", False, 500), name="self.tChangeVarForTime", daemon=True)
					threadInmovilizar.start()
					playerColisionado.character.tChangeVarForTime("movementAvailable", False, 500)#es necesario hacer un thread, porque hay que cambiar dos vars
					
					playerColisionado.character.decreaseHp(100, self)
					sendDataToAllPlayers(packPacket(["state", self.nPlayer, "normal"]))
					
			
			
	
class charDeku(character):
	def __init__(self, nPlayer):
		super().__init__(nPlayer, 4)
		self.timeSkill2 = 4.5
	
	def tSkill1(self, mousePos):
		pass
	
	def tSkill2(self, mousePos):
		if self.actualCd2 <= 0:
			dmgChangeValue = 30
			bulletSizeMultiplierChangeValue = 0.5
			shootSpeedChangeValue = 300
			speedChangeValue = 0.25
		
			varsAndChangebysList = [["bulletDmg", dmgChangeValue],["bulletSizeMultiplier", bulletSizeMultiplierChangeValue], ["shootSpeed", shootSpeedChangeValue], ["speed", speedChangeValue]]
			threadBuffUlti = threading.Thread(target=self.tDefaultBuffSkill, args=(varsAndChangebysList, self.timeSkill2*1000), name="self.tDefaultBuffSkill", daemon=True)#[[value, changeby][value, changeby]]
			threadBuffUlti.start()
			threadCdUlti = threading.Thread(target=self.tCdSkill, args=(2, self.cd2, [self.timeSkill2, self.cd2 - self.timeSkill2]), name="self.tCdSkill", daemon=True)
			threadCdUlti.start()
			
		
		
		
	
class charSora(character):
	def __init__(self, nPlayer):
		super().__init__(nPlayer, 5)
	
	def tSkill1(self, mousePos):
		pass
	
	def tSkill2(self, mousePos):
		if self.actualCd2 <= 0:
			puntos = getPuntosPerimetroCuadrado(2) #obtiene los puntos de un cuadrado con una distancia al centro de 2
			#para mas informacion, ver la funcion
			for punto in puntos:
				self.shoot((self.initialBulletPos[0] + punto[0], self.initialBulletPos[1] + punto[1]), self.bulletDmg)
				self.lastTimeShot = pygame.time.get_ticks() - self.shootSpeed #se hace para que este listo para disparar
			threadCdUlti = threading.Thread(target=self.tCdSkill, args=(2, self.cd2, [self.cd2]), name="self.tCdSkill", daemon=True)
			threadCdUlti.start()

		#print(self.balas)
