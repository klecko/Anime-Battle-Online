import sys
sys.path.append("C:/Users/David/Desktop/programacion/python/Anime Battle Online/client")
import pygame.image
import threading
from random import randint

import settings
import Globals


#FUNCIONES---------------------------------------------------------
#players-------------------------------
def getPlayerByNumber(numero):
	for jugador in Globals.JugadoresEncontrados:
		if jugador.n == int(numero):
			return jugador
	else:
		return None
	
def getBulletByNumber(numeroBala, player):
	for bala in player.balas:
		if bala.n == numeroBala:
			return bala
	else:
		return None
		
def getSkillByNumber(numero, Skills):
	for skill in Skills:
		if skill.n == int(numero):
			return skill
	else:
		return None
	
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
	Globals.s.sendto(packet.encode(), settings.SERVER_ADDR)

def recvSinglePacketFromServer():
	recv = Globals.s.recvfrom(1024)
	dataSplitted = unpackPacket(recv[0].decode())
	return dataSplitted
	
#graphics--------------------------------
def load_image(filename, transparent=False):
	image = pygame.image.load(filename)
	image = image.convert()
	if transparent:
		color = image.get_at((0,0))
		image.set_colorkey(color)
	return image
	
	
def checkIfAnyPlayerCollidesWithRect(rectangulo, pos=0):
	if pos:
		rectangulo.left, rectangulo.top = pos
	for player in Globals.JugadoresEncontrados:
		if player.rect.colliderect(rectangulo):
			return 1
	else:
		return 0
		
def checkIfMouseCollidesWithMenu(mousePos, menuRect):
	if settings.MENU_ACTIVADO == True and menuRect.collidepoint(mousePos) == True:
		return True
	else:
		return False
	#~ if settings.MENU_ACTIVADO == False or (settings.MENU_ACTIVADO == True and menuRect.collidepoint(mousePos) == False):
		#~ return False
	#~ else:
		#~ return True:

#menu---------------------------------
def mCambiarPjElegido(n, Input):
	if Input == -1:
		if n == 1:
			n = settings.NUMERO_JUGADORES_ESCOGIBLES
		else:
			n -= 1
	elif Input == 1:
		if n == settings.NUMERO_JUGADORES_ESCOGIBLES:
			n = 1
		else:
			n += 1
	return n
	
#sounds--------------------
def tCheckAndSetMusic(tEventExit):
	while tEventExit.is_set() == False:
		if pygame.mixer.music.get_busy() == False:
			cancion = randint(1, settings.NUMERO_CANCIONES_DISPONIBLES)
			pygame.mixer.music.load("sounds/music/" + str(cancion) + ".mp3")
			pygame.mixer.music.set_volume(0.15)
			pygame.mixer.music.play()
		pygame.time.wait(1000)
	
#others--------------------------------
def goodbye():
	sendDataToServer(packPacket(["bye"]))
	Globals.s.close()
	
def waitUntilAllSecondaryThreadsClosed():
	for thread in threading.enumerate(): 
		if thread.is_alive() and thread != threading.main_thread() and thread!= threading.current_thread():
			thread.join()
