#29/11/2017

#VERSION EN PROCESO DE AÑADIR ATAQUES

#TAREA: 	
#		X	QUE EL SERVER ENVIE A LOS CLIENTES PARA QUE SE CIERREN CUANDO SE CIERRE
#		X	REESTRUCTURAR drawEverything PARA QUE SOLO LLAME AL METODO DRAW DE CADA OBJETO
#		X	LAS POCIONES NO FUNCIONAN AL RELOGEAR
#		X	LA MUSICA DEBE PONERSE DE NUEVO CUANDO SE ACABE
#		X	ELIMINAR lastUpdate (comentado): sustituir por 16ms
#		X	AÑADIR OPCIONES RESOLUCION
#		X	HACER UN IS ALIVE PACKETING (ES NECESARIO?) --> SUSTIYENDOSE POR TIMEOUT
#		X	ARREGLAR BUG CUANDO SE DISPARA APUNTANDO A LA COORDENADA (0,0) DEL PERSONAJE
#		X	MIRAR A VER POR QUE DISMINUYEN FPS CUANDO SE PONE EL MENU DENTRO DEL JUEGO --> ES POR EL ALPHA, ARREGLADO PARA QUE DISMINUYAN ALGO MENOS
#			ERROR INVALID INT BASE 10: 'POS'
#		X	AÑADIR MEMORIA DE RESOLUCION
#		X	AÑADIR COOLDOWNS
#		X	MEJORAR VARIABLES DE COOLDOWNS
#		X	MEJORAR MANERA DE player.points, METER DENTRO DE decreaseHp Y die SI NECESARIO
#		X	MEJORAR MANERA DE tSpecialAttack, HACER FUNCION SKILL() A LA QUE SE LE PASE LOS PARAMETROS
#		X	PROBAR SI eval("jugador" + n) = getplayerbyn
#		X	IMPLEMENTAR ANIMACION RASENGAN NARUTO EN CLIENTE
#		X	IMPLEMENTANDO ANIMACIONES EN GENERAL EN EL CLIENTE
#		X	IMPLEMENTAR ANIMACION DEKU
#		X	REVISAR TODOS LOS SPECIALATTACKS Y LOS THREADS
#		X	HACER QUE LAS BALAS SALGAN DE LA MANO
#		x	HACER QUE NARUTO NO PUEDA DISPARAR MIENTRAS CARGA
#		X	HACER BOTON PARA VOLVER AL MENU
#		X	MIRAR A VER POR QUE LAS BALAS SE DESVIAN UN POCO DE LA TRAYECTORIA
#		X	IDEA: QUE EL SERVIDOR CREE UNA ESPECIE DE MAPA ALEATORIO CON COLISIONES. PUEDE ENVIARLE LOS RECTS AL CLIENTE Y QUE LOS DIBUJE, O CREAR UNA IMAGEN, ENVIARSELA Y QUE LA DIBUJE
#		X	ANALIZAR LA OPCION DE PONER DEAD COMO UN STATE EN VEZ DE COMO UN PACKET APARTE
#		X	VER SI ES MEJOR PONER LAS COLISIONES DE BALAS CON WALLS EN collide() EN VEZ DE EN calcPos()
#		X	ES HORA DE ORGANIZAR DIRECTORIOS.
#		X	BUSCAR DONDE USO globals Y locals
#		X	QUE EL JUGADOR Y LAS POWERUPS NO PUEDAN APARECER DENTRO DE UN MURO
#		X	QUE EN CALCPOS NO ESTE LO DE POWERUP
#			ANALIZAR DAEMON THREADS
#		X	POR QUE FUNCIONA EL eval DEL powerUpAppear DEL RECVDATA DEL CLIENT? --> LAS POWERUPS SE CREAN EN EL MISMO METODO
#		X	TIMEOUT PARA CUANDO EL SERVER SE CIERRE REPENTINAMENTE
#			TIMEOUT PARA CUANDO EL CLIENT SE CIERRE REPENTINAMENTE-->el cliente deberia enviar un packet al server cada x tiempo y asi el server comprueba si sigue vivo o no
#				esto se puede hacer que lo este haciendo todo el rato, o solo en el instante en el que recibe un ConnectionResetError para ver qué jugador se ha desconectado abruptamente y eliminarlo
#				--> EL SERVER DA ERROR CUANDO UN CLIENT SE CIERRA SIN CERRAR EL SOCKET, Y DA EL ERROR CONTINUAMENTE. ELIMINAR EL JUGADOR NO SIRVE DE NADA PORQUE DA ERROR AL RECIBIR DATOS.
#		X	IMPLEMENTAR ULTIMATE SORA
#		X	EL CLIENTE NO SE CIERRA HASTA QUE TERMINA CD
#			VER SI MERECE LA PENA CAMBIAR EL MENU INICIAL DEL CLIENTE A OTRO ARCHIVO. PODRIA CURRARMELO MAS Y QUE SE VEA EN EL MENU SI EL SERVER ESTA ON O NO 
#			REVISAR DONDE SE USA LOCALS, GLOBALS Y G
#		X	REVISAR FUNCION DE CLIENTE checkIfAnyPlayerCollidesWithRect(rectangulo, pos=0):
#			HACER MENU_ACTIVADO UN ATRIBUTO DE MENUINGAME
#			REVISAR EVENTOS EN EL CLIENTE CON pygame.event.get Y CON keys. MIRAR A VER SI ES MEJOR HACERLO DE SOLO UNA FORMA 
#		X	IMPLEMENTANDO SKILL1
#		X	CAMBIANDO LA MANERA EN LA QUE UN NUEVO JUGADOR RECIBE LOS DATOS DE TODOS LOS JUGADORES
#			EL CLIENTE CREA LOS OBJETOS JUGADORES MIENTRAS SE VAN CONECTANDO, MIENTRAS QUE EL SERVER LOS CREA TODOS AL INICIARSE. MIRAR SI ESTO ES LO MEJOR O SI SERIA MEJOR QUE AMBOS LO HICIERAN IGUAL

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import socket
import threading
import pygame
import sys
from random import randint

import settings
import Globals
#import classes
from classes.Bullet import Bullet
from classes.Players import Player, character, charNaruto, charHinata, charDeku, charSaitama, charSora
from classes.PowerUp import PowerUp
from classes.OtherClasses import Wall, Ranking
#import functions
from functions.CalcAndSend import calcPosOfEverything, sendPosOfEverything, tCalcAndSend, tTimeOut
from functions.RecvData import tRecvData
from functions.ShortFunctions import *




		
#-------------------------------------
def main():
	print("W3LC0M3")
	pygame.init()
	
	print("Librería inicializada")
	#El server crea todos los personajes al principio, mientras el cliente los va creando mientras se van metiendo
	g = globals() #manera para crear variables cuyo nombre usa el contenido de otra
	for x in range(settings.SERVER_MAX_PLAYERS): 
		newPlayer = "Jugador" + str(x+1) #el nombre de la variable del jugador es Jugador + numero
		g[newPlayer]=Player(x+1) #g[nameVar] crea una variable cuyo nombre es el contenido de nameVar
		#ejemplo: g["Jugador1"] = Player(1) es lo mismo que Jugador1 = Player(1)
		Globals.Jugadores.append(eval(newPlayer)) #meto la variable que tiene de nombre el contenido de newPlayer (Jugador1, Jugador2, etc) en Jugadores.
	
	PowerUpShootSpeed = PowerUp("shootSpeed", -125, 1, 5000, 15000, 5000)
	PowerUpMoveSpeed = PowerUp("speed", 0.15, 2, 5000, 15000, 5000)
	PowerUps = [PowerUpShootSpeed, PowerUpMoveSpeed]
	PointsRanking = Ranking()
	Muros = []
	MurosRects = []
	for i in range(5):
		g["Muro" + str(i+1)] = Wall(i+1, pygame.Rect(randint(0, settings.CLIENT_SCREEN_SIZE[0]), randint(0, settings.CLIENT_SCREEN_SIZE[1]), randint(0,500), randint(0,500)), (randint(0,255), randint(0,255), randint(0,255)), 0)#randint(1,10))
		Muros.append(eval("Muro" + str(i+1)))
		MurosRects.append(eval("Muro" + str(i+1) + ".rect"))
	#Muro = Wall(1, pygame.Rect(400,500,200,500), (255,0,0), 1)
	
	print("Todos los objetos creados")
	
	Globals.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
	Globals.s.bind(settings.SERVER_ADDR) #solo se hace en el servidor
	print("Servidor establecido en " + settings.SERVER_ADDR_STR)
	
	threadRecvData = threading.Thread(target=tRecvData, args=(PowerUps, Muros), name="tRecvData", daemon=True)
	threadRecvData.start()
	
	threadCalcAndSend = threading.Thread(target=tCalcAndSend, args=(PowerUps, MurosRects, PointsRanking), name="tCalcAndSend", daemon=True)
	threadCalcAndSend.start()
	
	threadTimeOut = threading.Thread(target=tTimeOut, name="tTimeOut", daemon=True)
	threadTimeOut.start()
	
	#threadIsAlive = threading.Thread(target=tIsAlivePacketing)
	
	input("")
	sendDataToAllPlayers("exit")
	Globals.s.close()
	sys.exit()
	
	
if __name__ == "__main__":
    main()



