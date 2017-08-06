#Version 1.4
#Introduciendo menu, graficos con diferentes personajes y arreglando bugs.



#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
from pygame import *
import socket
import threading
import sys

SERVER_HOST = "192.168.191.120"
SERVER_PORT = 25565

#respuesta = input("Introduzca host. Si se quiere conectar a " + SERVER_HOST + ", pulse enter: ")
#if respuesta:
#	SERVER_HOST = respuesta

CLIENT_VERSION = 1.4
SERVER_ADDR = (SERVER_HOST, SERVER_PORT)
SERVER_ADDR_STR = SERVER_ADDR[0] + ":" + str(SERVER_ADDR[1])
CLIENT_SCREEN_SIZE = (1600, 900)
CLIENT_SCREEN_TITLE = "Anime Battle v" + str(CLIENT_VERSION)
MENU_SCREEN_SIZE = (400,300)
MENU_ACTIVADO = False
NUMERO_JUGADORES_ESCOGIBLES = 5
g=globals()

#FUNCIONES---------------------------------------------------------
#players-------------------------------
def getPlayerByNumber(numero):
	player = "Jugador" + str(numero)
	return eval(player)
	
def getBulletByNumber(numeroBala, player):
	for bala in player.balas:
		if bala.n == numeroBala:
			return bala
	else:
		return 0
	
#network-------------------------------
def packPacket(args):
	packet = ""
	for arg in args:
		packet = packet + str(arg) + "|"
	return packet

def unpackPacket(string):
	args = string.split('|')
	return args

def sendDataToServer(packet):
	s.sendto(packet.encode(), SERVER_ADDR)

def recvSinglePacketFromServer():
	recv = s.recvfrom(1024)
	dataSplitted = unpackPacket(recv[0].decode())
	return dataSplitted

def recvData():
	while True:
		recv = s.recvfrom(1024)
		dataSplitted = unpackPacket(recv[0].decode())
		print(dataSplitted)
		#print(dataSplitted)
		if dataSplitted[0] == "newUser":
			g["Jugador" + dataSplitted[1]] = Player(int(dataSplitted[1]))
			eval("Jugador" + dataSplitted[1]).pj = int(dataSplitted[3])
			eval("Jugador" + dataSplitted[1]).cargarImagen()
			eval("Jugador" + dataSplitted[1]).setName(str(dataSplitted[2]))
			
			JugadoresEncontrados.append(eval("Jugador" + dataSplitted[1]))
			print(dataSplitted)
		elif dataSplitted[0] == "pos":
			jugador = getPlayerByNumber(int(dataSplitted[1]))
			jugador.rect.centerx = int(float(dataSplitted[2]))
			jugador.rect.centery = int(float(dataSplitted[3]))
			jugador.moving = bool(int(dataSplitted[4]))
			if jugador.lastPos[0] - jugador.rect.centerx < 0:
				jugador.direction = 1
			elif jugador.lastPos[0] - jugador.rect.centerx > 0:
				jugador.direction = -1
				#--------------------------------
			jugador.lastPos[0] = jugador.rect.centerx
			jugador.lastPos[1] = jugador.rect.centery
		elif dataSplitted[0] == "bye":
			JugadoresEncontrados.remove(getPlayerByNumber(int(dataSplitted[1])))	
			print("Jugador numero " + str(dataSplitted[1]) + " eliminado.")
		elif dataSplitted[0] == "newBullet":
			getPlayerByNumber(dataSplitted[1]).newBullet(float(dataSplitted[2]), float(dataSplitted[3]))
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
		elif dataSplitted[0] == "dead":
			jugador = getPlayerByNumber(int(dataSplitted[1]))
			jugador.currentHp = 0
			jugador.alive = False
			jugador.image = jugador.imageDead
		elif dataSplitted[0] == "alive":
			jugador = getPlayerByNumber(int(dataSplitted[1]))
			jugador.currentHp = jugador.maxHp
			jugador.alive = True
			jugador.image = jugador.imageAlive1
			print("jugador numero " + str(jugador.n) + " revivido")
			
	
#graphics--------------------------------
def load_image(filename, transparent=False):
	image = pygame.image.load(filename)
	image = image.convert()
	if transparent:
		color = image.get_at((0,0))
		image.set_colorkey(color, RLEACCEL)
	return image
        
def drawEverything(pantalla):
	reloj = pygame.time.Clock()
	fnt = pygame.font.Font("fonts/Pixeled.ttf", 10)
	txtIntructions1 = fnt.render("Move: w a s d.", 0, (0,0,0))
	txtIntructions2 = fnt.render("Normal shoot: left click.", 0, (0,0,0))
	txtIntructions3 = fnt.render("Charged attack: hold right click.", 0, (0,0,0))
	txtIntructions4 = fnt.render("Game by", 0, (0,0,0))
	txtIntructions5 = fnt.render("KleSoft, Kyntasia and CerviGamer", 0, (255,0,0))
	time = pygame.time.get_ticks()
	while True:
		pantalla.fill((255,255,255))
		#global MENU_ACTIVADO
		for jugador in JugadoresEncontrados:  #primero dibuja los jugadores y sus balas
			if jugador.alive == True:
				if jugador.direction == 1:
					if jugador.fotograma != 1 and jugador.fotograma != 3:
						jugador.setFotograma(1)
					if pygame.time.get_ticks() - jugador.time >= 200:
						if jugador.fotograma == 1:
							jugador.setFotograma(3)
						elif jugador.fotograma == 3:
							jugador.setFotograma(1)
						jugador.time = pygame.time.get_ticks()
				elif jugador.direction == -1:
					if jugador.fotograma != 2 and jugador.fotograma != 4:
						jugador.setFotograma(2)
					if pygame.time.get_ticks() - jugador.time >= 200:
						if jugador.fotograma == 2:
							jugador.setFotograma(4)
						elif jugador.fotograma == 4:
							jugador.setFotograma(2)
						jugador.time = pygame.time.get_ticks()
			pantalla.blit(jugador.image, jugador.rect)
			#pygame.draw.rect(pantalla, (255,0,0), jugador.rect, 2)
			for bala in jugador.balas:
				pantalla.blit(bala.image, bala.rect)
				#pygame.draw.rect(pantalla, (255,0,0), bala.rect, 2)
		for jugador in JugadoresEncontrados: #y luego las barras de vida
			jugador.drawHPBar(pantalla)
			pantalla.blit(jugador.nameRender, (jugador.rect.centerx-(jugador.nameRender.get_width()/2), jugador.rect.centery-108))
		if MENU_ACTIVADO == True:
			menu = pygame.Surface((CLIENT_SCREEN_SIZE[0]*0.70,CLIENT_SCREEN_SIZE[1]*0.70), pygame.SRCALPHA)
			menu.fill((0,0,0,128))
			pantalla.blit(txtIntructions1, (CLIENT_SCREEN_SIZE[0] * 0.20, CLIENT_SCREEN_SIZE[1]*0.20))
			pantalla.blit(txtIntructions2, (CLIENT_SCREEN_SIZE[0] * 0.20, CLIENT_SCREEN_SIZE[1]*0.30))
			pantalla.blit(txtIntructions3, (CLIENT_SCREEN_SIZE[0] * 0.20, CLIENT_SCREEN_SIZE[1]*0.40))
			pantalla.blit(txtIntructions4, (CLIENT_SCREEN_SIZE[0] * 0.20, CLIENT_SCREEN_SIZE[1]*0.50))
			pantalla.blit(txtIntructions5, (CLIENT_SCREEN_SIZE[0] * 0.33, CLIENT_SCREEN_SIZE[1]*0.50))
			pantalla.blit(menu, (CLIENT_SCREEN_SIZE[0]*0.15, CLIENT_SCREEN_SIZE[1]*0.15))
			
		pygame.display.flip()
		
		reloj.tick(60)

def mCambiarPjElegido(n, Input):
	if Input == -1:
		if n == 1:
			n = NUMERO_JUGADORES_ESCOGIBLES
		else:
			n -= 1
	elif Input == 1:
		if n == NUMERO_JUGADORES_ESCOGIBLES:
			n = 1
		else:
			n += 1
	return n
#CLASES-----------------------------
class Player():
	def __init__(self, numero):
		self.n = numero
		self.balas = []
		self.maxHp = 100
		self.name = ""
		self.pj = 0
		self.currentHp = self.maxHp
		self.direction = 0
		self.lastPos = [0,0]
		self.alive = True
		self.moving = False
		self.time = 0
		print("Jugador numero " + str(self.n) + " creado")
	def cargarImagen(self):
		self.nImage = int(self.pj)
		self.imageAlive1 = load_image("graphics/pjs/" + str(self.nImage) + ".png", True)
		self.imageAlive3 = load_image("graphics/pjs/" + str(self.nImage) + "_3.png", True)
		if self.nImage == 2 or self.nImage == 5: #en el caso de estos hay que cargar la suya mirando hacia el otro lado
			self.imageAlive2 = load_image("graphics/pjs/" + str(self.nImage) + "_2.png", True)
			self.imageAlive4 = load_image("graphics/pjs/" + str(self.nImage) + "_4.png", True)
		else: #para los demas, basta con voltearla
			self.imageAlive2 = pygame.transform.flip(self.imageAlive1, 1, 0)
			self.imageAlive4 = pygame.transform.flip(self.imageAlive3, 1, 0)
		#right quieto: 1
		#left quieto: 2
		#animacion right quieto: 3
		#animacion left quieto:4
		self.imageDead = load_image("graphics/pjs/dead.png", True)
		self.setFotograma(1)
		self.rect = self.image.get_rect()
	def setFotograma(self, n):
		self.image = eval("self.imageAlive" + str(n))
		self.fotograma = n
	def newBullet(self, sizeModifier, angle):
		n=1
		result = getBulletByNumber(n, self)
		if result:
			while result:
				n+=1
				result = getBulletByNumber(n, self)
		g["bala" + str(n)] = Bullet(n, self.n, self.nImage, sizeModifier, angle)
		#g["bala" + str(len(self.balas)+1)] = Bullet(len(self.balas)+1, self.n)
		self.balas.append(eval("bala" + str(n)))
	def drawHPBar(self, pantalla):
		#elijo color
		if self.currentHp / self.maxHp >= 0.7:
			color = (0,255,0)
		elif self.currentHp / self.maxHp < 0.7 and self.currentHp / self.maxHp > 0.3:
			color = (255,200,0)
		elif self.currentHp / self.maxHp <= 0.3:
			color = (255,75,0)
		#regla de 3: si maxHp es ~46 de largo, currentHp es x
		hpDrawn = round(self.currentHp*46/self.maxHp)
		if self.currentHp>0:
			rectVida = pygame.draw.rect(pantalla, color, (self.rect.centerx-23, self.rect.y-20, hpDrawn, 15))
		
		if self.currentHp < self.maxHp:
			if self.currentHp == 0:
				leftRectVidaBlanco = self.rect.centerx-23
			else:
				leftRectVidaBlanco = rectVida.right
			rectVidaBlanco = pygame.draw.rect(pantalla, (255,255,255), (leftRectVidaBlanco, self.rect.y-20, 46-hpDrawn, 15))
		rectRecuadroVida = pygame.draw.rect(pantalla, (0,0,0), (self.rect.centerx-25, self.rect.y-20, 50, 15), 3)
		#pygame.draw.rect(pantalla, (0,255,0), (self.rect.centerx-23, self.rect.y-18, 46, 11), 0)
	def setName(self, name):
		self.name = name
		self.nameRender = pygame.font.Font("fonts/Pixeled.ttf", 13).render(name, 0, (0,0,0))
		
class Bullet():
	def __init__(self, numero, numeroPlayer, numeroImagenPlayer, sizeModifier, angle):
		self.n = numero
		self.nPlayer = numeroPlayer
		self.image = load_image("graphics/shots/" + str(numeroImagenPlayer) + ".png", True)
		if angle >= -90 and angle <= 90:
			self.image = pygame.transform.rotate(self.image, angle) #si el angulo es de la mitad derecha, lo rota los angulos necesarios
		elif angle > 90 or angle < -90:
			self.image = pygame.transform.rotate(self.image, 180-angle)#si es de la mitad izquierda, lo rota los angulos como si fuera de la mitad derechaa (180-angle)
			self.image = pygame.transform.flip(self.image, 1, 0)#y despues los voltea horizontalmente
			#esto es para que por ejemplo el puño no aparezca hacia abajo
		if sizeModifier != 1:
			self.image = pygame.transform.scale(self.image, (int(self.image.get_size()[0]*sizeModifier), int(self.image.get_size()[1]*sizeModifier)))
		self.rect = self.image.get_rect()
		self.rect.centerx, self.rect.centery = -200, -200
		self.timeStarted = pygame.time.get_ticks()
		#self.pos = [0,0]
		#print("Bala " + str(self.n) + " del jugador " + str(self.nPlayer) + " creada.")
	def eliminar(self):
		getPlayerByNumber(self.nPlayer).balas.remove(self)
		#print("Bala " + str(self.n) + " del jugador " + str(self.nPlayer) + " eliminada con un time alive de " + str((pygame.time.get_ticks() - self.timeStarted)/1000))
		del(self)

		
		
class mButton():
	def __init__(self, pos, imageLocation, transparency):
		self.image = load_image(imageLocation, transparency)
		self.rect = self.image.get_rect()
		self.rect.centerx = pos[0]
		self.rect.centery = pos[1]
	def draw(self, pantalla):
		pantalla.blit(self.image, self.rect)
		
class mTextBox():
	def __init__(self, pos, size, initialText = ""):
		self.pos = pos
		self.size = size
		self.text = initialText
		self.font = pygame.font.Font("fonts/Pixeled.ttf", 10)
		
	def draw(self, pantalla):
		pygame.draw.rect(pantalla, (0,0,0), (self.pos[0], self.pos[1], self.size[0], self.size[1]))
		pygame.draw.rect(pantalla, (255,255,255), (self.pos[0]+2, self.pos[1]+2, self.size[0]-4, self.size[1]-4))
		self.textRender = self.font.render(self.text, 0, (0,0,0))
		pantalla.blit(self.textRender, (self.pos[0]+3, self.pos[1]-6))
#---------------------------------------
JugadoresEncontrados=[]
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
def main():
	print("Bienvenido al mejor juego de la historia")
	
	pygame.init()
	#MENU-----------------------------------------------------------------------------
	empezar = False
	pantalla = pygame.display.set_mode(MENU_SCREEN_SIZE)
	pygame.display.set_caption(CLIENT_SCREEN_TITLE)
	reloj = pygame.time.Clock()
	mNameTextBox = mTextBox([125,190], [150, 20])
	mButtonConectarRect = pygame.Rect(170,231,61,29)
	mButtonCambiarPJRightRect = pygame.Rect(286, 135, 46, 28)
	mButtonCambiarPJLeftRect = pygame.Rect(71,137, 46,28)
	pygame.mixer.music.load("sounds/1.mp3")
	pygame.mixer.music.set_volume(0.08)
	pygame.mixer.music.play()
	for i in range(NUMERO_JUGADORES_ESCOGIBLES):
		#g["mP" + str(i+1)] = [load_image("graphics/pjs/" + str(i+1) + ".png", True), load_image("graphics/pjs/" + str(i+1) + "_3.png", True)]
		g["mP" + str(i+1)] = [load_image("graphics/pjs/" + str(i+1) + ".png", True), load_image("graphics/pjs/" + str(i+1) + "_3.png", True)]
	fotograma = 0
	time = pygame.time.get_ticks()
	mMenuImage = load_image("graphics/GUI/menu.png", False)
	mPEscogido = 1
	#definir imagenes
	while empezar == False:
		reloj.tick(60)
		mouse = pygame.mouse.get_pressed()
		mousePos = pygame.mouse.get_pos()
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				s.close()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				key = pygame.key.name(event.key)
				if key.isalnum() and len(key) == 1:
					if len(mNameTextBox.text) < 14:
						mNameTextBox.text += key.upper()
				elif event.key == K_BACKSPACE:
					mNameTextBox.text = mNameTextBox.text[0:-1]
				if event.key == pygame.K_LEFT:
					mPEscogido = mCambiarPjElegido(mPEscogido, -1)
				elif event.key == pygame.K_RIGHT:
					mPEscogido = mCambiarPjElegido(mPEscogido, 1)
				elif event.key == pygame.K_RETURN:
					empezar = True
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				if mButtonConectarRect.collidepoint(mousePos):
					empezar = True
				elif mButtonCambiarPJRightRect.collidepoint(mousePos):
					mPEscogido = mCambiarPjElegido(mPEscogido, 1)
				elif mButtonCambiarPJLeftRect.collidepoint(mousePos):
					mPEscogido = mCambiarPjElegido(mPEscogido, -1)
		
		pantalla.blit(mMenuImage, (0,0))

		#for button in mButtons:
		#	if button.rect.collidepoint(mousePos):
		#		if mouse[0]:
		#			empezar = True
			#button.draw(pantalla)
		if pygame.time.get_ticks() - time >= 200:
			if fotograma == 0:
				fotograma = 1
			elif fotograma == 1:
				fotograma = 0
			time = pygame.time.get_ticks()
		if mPEscogido == 3:
			pantalla.blit(eval("mP" + str(mPEscogido))[fotograma], (147,80)) #a saitama se le pone un poco a la izquierda por el tamaño de imagen
		else:
			pantalla.blit(eval("mP" + str(mPEscogido))[fotograma], (163,80))
		#pygame.draw.rect(pantalla, (0,0,0), (100,20,200,20))	
		mNameTextBox.draw(pantalla)
		pygame.display.flip()
	print("Personaje escogido: " + str(mPEscogido))
	
	#FINMENU-------------------------------------------------------------------------
	print("Intentando conectar...")
	sendDataToServer(packPacket(["newUser", mNameTextBox.text, mPEscogido]))
	answer=recvSinglePacketFromServer() #compruebo si el servidor me acepta
	if not int(answer[0]):
		print("El servidor esta lleno")
		sys.exit()
	print("Let's go")
	pantalla = pygame.display.set_mode(CLIENT_SCREEN_SIZE)#((round(CLIENT_SCREEN_SIZE[0]/2), round(CLIENT_SCREEN_SIZE[1]/2)))
	pygame.display.set_caption(CLIENT_SCREEN_TITLE)
	answer=recvSinglePacketFromServer() #compruebo cuantos jugadores hay al inicio para crearlos
	print(answer)
	i=0
	while answer[i]: #los datos de cada jugador son 3:
		newPlayer = "Jugador" + str(answer[i]) #el numero
		g[newPlayer] = Player(int(answer[i]))
		JugadoresEncontrados.append(eval(newPlayer))
		eval(newPlayer).setName(answer[i+1]) #el nombre
		eval(newPlayer).pj = answer[i+2] #y el personaje escogido
		i = i + 3
	for jugador in JugadoresEncontrados:
		jugador.cargarImagen()
		
	threadRecvData = threading.Thread(target=recvData)
	threadRecvData.setDaemon(True)
	threadRecvData.start()
	threadDrawEverything = threading.Thread(target=drawEverything, args=(pantalla,))
	threadDrawEverything.setDaemon(True)
	threadDrawEverything.start()

	
	
	
	UPfirst, DOWNfirst, LEFTfirst, RIGHTfirst = False, False, False, False
	inputx, inputy, lastinputx, lastinputy = 0, 0, 0, 0
	global MENU_ACTIVADO
	
	while True:
		time = reloj.tick(60)
		#print(reloj.get_fps())
		keys = pygame.key.get_pressed()
		mouse = pygame.mouse.get_pressed()
		mousePos = pygame.mouse.get_pos()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sendDataToServer(packPacket(["bye"]))
				s.close()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: #left click pulsar
				sendDataToServer(packPacket(["startChargingAttack"]))
			if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
				sendDataToServer(packPacket(["stopChargingAttack", mousePos[0], mousePos[1]]))
			if event.type == pygame.KEYDOWN:
				if event.key == K_ESCAPE:
					if MENU_ACTIVADO == False:
						MENU_ACTIVADO = True
					elif MENU_ACTIVADO == True:
						MENU_ACTIVADO = False
						#sendDataToServer(packPacket(["bye"]), s)
						#s.close()
						#exit()
		if mouse[0]: #left click continuado:
			sendDataToServer(packPacket(["shoot", mousePos[0], mousePos[1]]))
		if keys[K_w]: 
			if not keys[K_s]:
				inputy = -1
				UPfirst = True
				DOWNfirst = False
		if keys[K_s]:
			if not keys[K_w]:
				inputy = 1
				DOWNfirst = True
				UPfirst = False
		if keys[K_s] and keys[K_w]:
			if DOWNfirst == True:
					inputy = -1
			elif UPfirst == True:
				inputy = 1
		if not keys[K_w] and not keys[K_s]:
			inputy = 0
			
		#EXPLICACION: si solo la tecla de arriba esta pulsada, va hacia arriba, y se establece que se pulsó primero la de arriba y no la de abajo.
		#Si solo la tecla de abajo esta pulsada, va hacia abajo, y se establece que se pulsó primero la de abajo y no la de arriba.
		#Si estan las dos pulsadas, y se pulsó primero la de abajo, va hacia arriba. Si se pulsó primero la de arriba, va hacia abajo.
		#Si no hay ninguna pulsada, no se mueve. Todo esto es aplicable también para el eje x.
		
		#Todo esto recoge la direccion a la que debe ir el jugador, y es enviado al servidor, quien se encarga de hacer los calculos y dar la posicion resultante.
		if keys[K_d]: 
			if not keys[K_a]:
				inputx = 1
				RIGHTfirst = True
				LEFTfirst = False
		if keys[K_a]:
			if not keys[K_d]:
				inputx = -1
				LEFTfirst = True
				RIGHTfirst = False
		if keys[K_d] and keys[K_a]:
			if RIGHTfirst == True:
					inputx = -1
			elif LEFTfirst == True:
				inputx = 1
		if not keys[K_d] and not keys[K_a]:
			inputx = 0
		
		
		
		if inputx != lastinputx or inputy!= lastinputy:
			sendDataToServer(packPacket(["input", inputx, inputy, time]))
		#creo que si hay bajon de fps se lia parda
		lastinputx = inputx
		lastinputy = inputy
		
	


if __name__ == "__main__":
    main()
