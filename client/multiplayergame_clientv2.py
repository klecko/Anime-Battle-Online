#29/11/2017

#VERSION EN PROCESO DE AÑADIR ATAQUES

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
from pygame import *
import socket
import threading
import sys

import settings
import Globals

from classes.Players import Player
from classes.GUI import Skill, Ranking, mTextBox, mRadioButton, Menu

from functions.DrawEverything import tDrawEverything
from functions.RecvData import tRecvData
from functions.ShortFunctions import packPacket, sendDataToServer, recvSinglePacketFromServer, load_image, mCambiarPjElegido, tCheckAndSetMusic, goodbye, waitUntilAllSecondaryThreadsClosed, checkIfMouseCollidesWithMenu
			
#---------------------------------------



def main():
	print("Bienvenido al mejor juego de la historia")
	
	resFile = open("resolution", "r")
	res = resFile.read()
	resFile.close()
	g = locals()
	pygame.init()
	
	#MENU-----------------------------------------------------------------------------
	empezar = False
	pantalla = pygame.display.set_mode(settings.MENU_SCREEN_SIZE)
	pygame.display.set_caption(settings.CLIENT_SCREEN_TITLE)
	reloj = pygame.time.Clock()
	
	mFont = pygame.font.Font("fonts/Pixeled.ttf", 15)
	mNameTextBox = mTextBox([125,190], [150, 20])
	mButtonConectarRect = pygame.Rect(170,231,61,29)
	mButtonCambiarPJRightRect = pygame.Rect(286, 135, 46, 28)
	mButtonCambiarPJLeftRect = pygame.Rect(71,137, 46,28)
	mOptionsSurface = pygame.Surface((settings.MENU_SCREEN_SIZE[0]*0.80, settings.MENU_SCREEN_SIZE[1]*0.80), pygame.SRCALPHA)
	mOptionsAbiertas = False
	mOptions = mRadioButton((int(settings.MENU_SCREEN_SIZE[0]*0.20), int(settings.MENU_SCREEN_SIZE[1]*0.20)), ["2000x1125","1600x900","1350x760", "1200x675", "800x450"], mFont, int(res))
	
	for i in range(settings.NUMERO_JUGADORES_ESCOGIBLES): #cargo las imagenes de todos los personajes
		#g["mP" + str(i+1)] = [load_image("graphics/pjs/" + str(i+1) + ".png", True), load_image("graphics/pjs/" + str(i+1) + "_3.png", True)]
		g["mP" + str(i+1)] = [load_image("graphics/pjs/" + str(i+1) + "/StillRight1.png", True), load_image("graphics/pjs/" + str(i+1) + "/StillRight2.png", True)]
	
	fotograma = 0
	time = pygame.time.get_ticks()
	mMenuImage = load_image("graphics/GUI/menu.png", False)
	settings.mPEscogido = 1
	#definir imagenes
	
	while empezar == False:
		reloj.tick(60)
		mouse = pygame.mouse.get_pressed()
		mousePos = pygame.mouse.get_pos()
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			if event.type == pygame.KEYDOWN:
				
				mNameTextBox.checkKeys(event.key)
				
				
				if event.key == pygame.K_LEFT:
					settings.mPEscogido = mCambiarPjElegido(settings.mPEscogido, -1)
				elif event.key == pygame.K_RIGHT:
					settings.mPEscogido = mCambiarPjElegido(settings.mPEscogido, 1)
				elif event.key == pygame.K_RETURN:
					if mNameTextBox.text:
						empezar = True
				elif event.key == pygame.K_ESCAPE:
					if mOptionsAbiertas == False:
						mOptionsAbiertas = True
					else:
						mOptionsAbiertas = False
				if mOptionsAbiertas == True:
					if event.key == pygame.K_DOWN:
						if mOptions.elementChosen != len(mOptions.elements)-1:
							mOptions.elementChosen += 1
						else:
							mOptions.elementChosen = 0
					elif event.key == pygame.K_UP:
						if mOptions.elementChosen != 0:
							mOptions.elementChosen -= 1
						else:
							mOptions.elementChosen = len(mOptions.elements)-1
				
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				if mButtonConectarRect.collidepoint(mousePos):
					if mNameTextBox.text:
						empezar = True
				elif mButtonCambiarPJRightRect.collidepoint(mousePos):
					settings.mPEscogido = mCambiarPjElegido(settings.mPEscogido, 1)
				elif mButtonCambiarPJLeftRect.collidepoint(mousePos):
					settings.mPEscogido = mCambiarPjElegido(settings.mPEscogido, -1)
				if mOptionsAbiertas == True:
					mOptions.collide(mousePos)
					
				
		
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
		if settings.mPEscogido == 3:
			pantalla.blit(eval("mP" + str(settings.mPEscogido))[fotograma], (147,80)) #a saitama se le pone un poco a la izquierda por el tamaño de imagen
		else:
			pantalla.blit(eval("mP" + str(settings.mPEscogido))[fotograma], (163,80))
		#pygame.draw.rect(pantalla, (0,0,0), (100,20,200,20))	
		mNameTextBox.draw(pantalla)
		
		if mOptionsAbiertas: 
			mOptionsSurface.fill((255,255,255,200))
			pantalla.blit(mOptionsSurface, (settings.MENU_SCREEN_SIZE[0]*0.10, settings.MENU_SCREEN_SIZE[1]*0.10))
			mOptions.draw(pantalla)
		pygame.display.flip()
	
	
	#FINMENU-------------------------------------------------------------------------
	if mOptions.elementChosen == 0: RESOLUCION = (2000, 1125)
	elif mOptions.elementChosen == 1: RESOLUCION = (1600, 900)
	elif mOptions.elementChosen == 2: RESOLUCION = (1350, 760)
	elif mOptions.elementChosen == 3: RESOLUCION = (1200, 675)
	elif mOptions.elementChosen == 4: RESOLUCION = (800, 450)
	
	resFile = open("resolution", "w")
	resFile.write(str(mOptions.elementChosen))
	resFile.close()
	
	#Creacion de objetos-----------------------------
	Globals.JugadoresEncontrados=[]
	PowerUps = []
	Skills = []
	Muros = []
	PointsRanking = Ranking()
	Globals.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	Globals.s.settimeout(5)
	MenuIngame = Menu(pygame.font.Font("fonts/Pixeled.ttf", 20))
	
	Skill2 = Skill(2, settings.mPEscogido, 25)
	Skills.append(Skill2)
	#------------------------------------------------
	
	#Proceso de conexión-----------------------------
	print("Intentando conectar...")
	sendDataToServer(packPacket(["newUser", mNameTextBox.text, settings.mPEscogido]))
	try:
		answer=recvSinglePacketFromServer() #compruebo si el servidor me acepta
	except ConnectionResetError:
		print("FATAL ERROR: CONNECTION RESET")
		sys.exit()
	if not int(answer[0]):
		print("Conexión rechazada")
		sys.exit()
		
	print("Let's go")
	
	pantalla = pygame.Surface((settings.CLIENT_SCREEN_SIZE)) #pantalla es la surface donde se dibuja todo, y que tiene el tamaño original de settings.CLIENT_SCREEN_SIZE
	truePantalla = pygame.display.set_mode(RESOLUCION) #truePantalla es la pantalla verdadera, que tiene el tamaño de la resolucion escogida. la superficie anterior
	#se escala al tamaño de la resolucion despues de que se haya dibujado todo en ella, y se dibuja en truePantalla. todo esto ocurre en tDrawEverything
	pygame.display.set_caption(settings.CLIENT_SCREEN_TITLE)
	#NOTA: Ahora los datos de todos los jugadores, walls, powerups, etc los recibe el cliente dentro de tRecvData
	
	tEventExit = threading.Event()
	threadRecvData = threading.Thread(target=tRecvData, args=(tEventExit, PowerUps, Skills, Muros, PointsRanking), name="tRecvData", daemon=True)
	threadRecvData.start()
	threadDrawEverything = threading.Thread(target=tDrawEverything, args=(tEventExit, PowerUps, Skills, Muros, PointsRanking, MenuIngame, pantalla, truePantalla), name="tDrawEverything", daemon=True)
	threadDrawEverything.start()
	threadMusica = threading.Thread(target=tCheckAndSetMusic, args=(tEventExit,), name="tCheckAndSetMusic", daemon=True)
	threadMusica.start()
	
	
	
	UPfirst, DOWNfirst, LEFTfirst, RIGHTfirst = False, False, False, False
	inputx, inputy, lastinputx, lastinputy = 0, 0, 0, 0
	
	while tEventExit.is_set() == False:
		time = reloj.tick(60)
		#print(reloj.get_fps())
		keys = pygame.key.get_pressed()
		mouse = pygame.mouse.get_pressed()
		screenMousePos = pygame.mouse.get_pos() #obtiene la posicion del raton en la pantalla del cliente, sin embargo esta posicion puede ser diferente a la real del servidor
		mousePos = [0,0] #dependiendo de la resolucion. por ello, se multiplica por la relacion entre la resolucion real y la del cliente
		mousePos[0] = int(screenMousePos[0] * settings.CLIENT_SCREEN_SIZE[0]/RESOLUCION[0]) #ej: si la resolucion del cliente es 1200x675 y la del servidor es de 1600x900,
		mousePos[1] = int(screenMousePos[1] * settings.CLIENT_SCREEN_SIZE[1]/RESOLUCION[1]) #si clickas en la coordenada x 1200, la resolucion real seria 1600.
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT: #al intentar salir:
				tEventExit.set() #activa una flag para todos los threads terminen
				waitUntilAllSecondaryThreadsClosed() #espera a que terminen todos menos el main thread antes de cerrar el socket y enviar "bye" al server
				#esto es necesario ya que si no podriamos cerrar el socket mientras tRecvData lo usa o algo parecido.
				goodbye() #se cierra el socket, se envia bye y se sale
				break
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1: #LEFT CLICK
					if settings.MENU_ACTIVADO == True and MenuIngame.buttonSalirRealRect.collidepoint(mousePos):
						tEventExit.set() #todo es lo mismo que if event.type == pygame.QUIT:
						 #la unica diferencia es que aqui no se cierra el socket, y despues vuelve a empezar el programa
						waitUntilAllSecondaryThreadsClosed()
						sendDataToServer(packPacket(["bye"]))
						settings.MENU_ACTIVADO = False
						main()
				if event.button == 3: #RIGHT CLICK
					if not checkIfMouseCollidesWithMenu(mousePos, MenuIngame.rect):
						sendDataToServer(packPacket(["skill", 1, mousePos[0], mousePos[1]]))
					
			
			
			#CHARGING
			#~ if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: #left click pulsar
				#~ sendDataToServer(packPacket(["startChargingAttack"]))
			#~ if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
				#~ sendDataToServer(packPacket(["stopChargingAttack", mousePos[0], mousePos[1]]))
			
			if event.type == pygame.KEYDOWN:
				if event.key == K_ESCAPE:
					if settings.MENU_ACTIVADO == False:
						settings.MENU_ACTIVADO = True
					elif settings.MENU_ACTIVADO == True:
						settings.MENU_ACTIVADO = False
				if event.key == K_SPACE:
					if Skill2.actualCd <= 0: #esta comprobacion se hace en el servidor, pero tambien en el cliente. eso se debe a que hay 0.5 secs de diferencia entre
						#el cd del server y el del cliente, y si se enviara esta peticion en esos 0.5 secs, el cd del cliente se bugearia
						#a efectos practicos no tiene consecuencias ya que el que cuenta es el cd del server, pero queda feo
						sendDataToServer(packPacket(["skill", 2, mousePos[0], mousePos[1]]))
			
					
		if mouse[0]: #left click continuado:
			if not checkIfMouseCollidesWithMenu(mousePos, MenuIngame.rect):
				sendDataToServer(packPacket(["shoot", mousePos[0], mousePos[1]]))
			#print(mousePos)
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
			sendDataToServer(packPacket(["input", inputx, inputy]))
		lastinputx = inputx
		lastinputy = inputy


		
	


if __name__ == "__main__":
    main()
