import sys
sys.path.append("C:/Users/David/Desktop/programacion/python/Anime Battle Online/client")
import pygame.time
import threading

import settings
import Globals
from functions.ShortFunctions import load_image, checkIfAnyPlayerCollidesWithRect

def tDrawEverything(tEventExit, PowerUps, Skills, Muros, PointsRanking, MenuIngame, pantalla, pantallaVerdadera):
	reloj = pygame.time.Clock()
	#creacion de textos y surfaces
	fnt = pygame.font.Font("fonts/Pixeled.ttf", 20)
			
	barraInferior = load_image("graphics/GUI/skillbar.png", True)
	imageCharacter = load_image("graphics/pjs/" + str(settings.mPEscogido) + "/c.png", True)
	
	barraInferior.blit(imageCharacter, (9,14))
	
	#fin creacion de textos y surfaces
	time = pygame.time.get_ticks()
	while tEventExit.is_set() == False:
		#print(Globals.JugadoresEncontrados)
		pantalla.fill((255,255,255))
		#global settings.MENU_ACTIVADO
		
		for jugador in Globals.JugadoresEncontrados:  #primero dibuja los jugadores y sus balas
			jugador.draw(pantalla)
			#pygame.draw.rect(pantalla, (255,0,0), jugador.rect, 2)
			for bala in jugador.balas:
				bala.draw(pantalla)
				#pygame.draw.rect(pantalla, (255,0,0), bala.rect, 2)

		for muro in Muros:
			muro.draw(pantalla)

		for powerup in PowerUps: #las powerups
			powerup.draw(pantalla)
			
		
		for jugador in Globals.JugadoresEncontrados: #las barras de vida y nombre, y la foto del pj
			jugador.drawHPBar(pantalla)
			
		
		if settings.MENU_ACTIVADO == True:
			MenuIngame.draw(pantalla)
			
		
		PointsRanking.draw(pantalla, fnt)
		
		
		for skill in Skills:
			skill.draw(barraInferior)
			#print(int((barraInferior.get_height()/2) - skill.image.get_height()), int(barraInferior.get_width()*0.20))
		
		
		if checkIfAnyPlayerCollidesWithRect(barraInferior.get_rect(), (0, settings.CLIENT_SCREEN_SIZE[1]-barraInferior.get_height())):
			barraInferior.set_alpha(170)
		else:
			barraInferior.set_alpha(255)
		pantalla.blit(barraInferior, (0, settings.CLIENT_SCREEN_SIZE[1]-barraInferior.get_height()))
		#pygame.draw.rect(pantalla, (255,0,0), (200,200,20,100), 1)
		
		#todas las cosas se dibujan en la variable pantalla, que tiene de tamaño settings.CLIENT_SCREEN_SIZE (el tamaño original del servidor)
		#después, esta pantalla se escala al tamaño de la resolucion elegida para dibujarse en la pantallaVerdadera
		pantallaVerdadera.blit(pygame.transform.scale(pantalla, pantallaVerdadera.get_size()), (0,0))
		pygame.display.flip()
		#print(reloj.get_fps())
		reloj.tick(60)

