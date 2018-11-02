import sys
sys.path.append("C:/Users/David/Desktop/programacion/python/Anime Battle Online/client")
import pygame.font
import pygame.image
from pygame import K_BACKSPACE, K_SPACE #usado en el textbox
import settings
from functions.ShortFunctions import load_image



class Skill():
	def __init__(self, n, nCharacter, cd):
		self.n = n
		self.imageOriginal = load_image("graphics/GUI/skills/" + str(nCharacter) + "_" + str(n) + ".png", False)#.convert_alpha()
		self.image = self.imageOriginal.copy()
		
		self.greySurfaceCd = pygame.Surface(self.imageOriginal.get_size(), pygame.SRCALPHA)
		self.greySurfaceCd.fill((0,0,0,150))
		self.font = pygame.font.Font("fonts/Pixeled.ttf", 12)
		#self.cd = cd
		self.actualCd = 0
		
	def tWaitCd(self, tEventExit, cdsList):
		for cd in cdsList:
			self.actualCd = cd #pone el cd actual en cd maximo
			while self.actualCd > 0 and tEventExit.is_set() == False: #y lo va bajando poco a poco hasta que llega 0
				pygame.time.wait(100)
				self.actualCd -= 0.1
				
	def draw(self, pantalla): #asumiendo que pantalla es la barraInferior
		self.image = self.imageOriginal.copy() #restablece la imagen a la original para pintar sobre ella el cd
		if self.actualCd > 0:
			txt = str(round(self.actualCd,2))
			txtRender = self.font.render(txt, 0, (255,255,255))
			self.image.blit(self.greySurfaceCd, (0,0))
			self.image.blit(txtRender, (self.image.get_width()/2 - txtRender.get_width()/2, self.image.get_height()/2 - txtRender.get_height()/2))
		pantalla.blit(self.image, (222,81))
		
		
class Ranking():
	def __init__(self):
		self.rankingList = [] #la rankinglist se recibe del servidor, y se dibuja en drawEverything
	def draw(self, pantalla, font):
		i = 0
		g = locals()
		for listItem in self.rankingList: #el ranking
			g["rankingItem" + str(i)] = font.render(listItem[1] + " - " + listItem[0], 0, (0,0,0)) #rankingList esta formado por listas, el primer elemento de cada una de ella es el nombre del jugador
			#y el segundo elemento es su puntuación
			pantalla.blit(eval("rankingItem" + str(i)), (settings.CLIENT_SCREEN_SIZE[0] * 0.80, settings.CLIENT_SCREEN_SIZE[1] * 0.03 * i))
			i += 1


class mTextBox():
	def __init__(self, pos, size, initialText = ""):
		self.pos = pos
		self.size = size
		self.text = initialText
		self.font = pygame.font.Font("fonts/Pixeled.ttf", 10)
		
	def draw(self, pantalla):
		#dibujo un rect negro y otro blanco mas chico para simular el borde del textbox
		pygame.draw.rect(pantalla, (0,0,0), (self.pos[0], self.pos[1], self.size[0], self.size[1]))
		pygame.draw.rect(pantalla, (255,255,255), (self.pos[0]+2, self.pos[1]+2, self.size[0]-4, self.size[1]-4))
		self.textRender = self.font.render(self.text, 0, (0,0,0))
		pantalla.blit(self.textRender, (self.pos[0]+3, self.pos[1]-6))
		
	def checkKeys(self, eventkey):
		key = pygame.key.name(eventkey)
		if key.isalnum() and len(key) == 1:
			if len(self.text) < 14:
				self.text += key.upper()
		elif eventkey == K_BACKSPACE:
			self.text = self.text[0:-1]
		elif eventkey == K_SPACE:
			self.text += " "

class mRadioButton():
	def __init__(self, pos, elements, font, initialElementChosen):
		self.pos = pos
		self.elementChosen = initialElementChosen
		self.elements = elements
		self.font = font
		self.circles = []
		
	def draw(self, pantalla):
		i = 0
		n = 30
		for element in self.elements:
			circle =pygame.draw.circle(pantalla, (0,0,0), (self.pos[0], self.pos[1]+i), 5, 2)
			if self.circles.count(circle) == 0:
				self.circles.append(circle)
			text = self.font.render(element, 0, (0,0,0))
			pantalla.blit(text, (self.pos[0]+18, self.pos[1]+i-24))
			i += n
		pygame.draw.circle(pantalla, (0,0,0), (self.pos[0], self.pos[1]+(n*self.elementChosen)), 2)

	def collide(self, mousePos):
		for circle in self.circles:
			if circle.collidepoint(mousePos):
				self.elementChosen = self.circles.index(circle)
		
class Menu():
	def __init__(self, fnt):
		self.image = pygame.Surface((settings.CLIENT_SCREEN_SIZE[0]*0.70, settings.CLIENT_SCREEN_SIZE[1]*0.70))
		self.image.fill((120,120,120))
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = settings.CLIENT_SCREEN_SIZE[0]*0.15, settings.CLIENT_SCREEN_SIZE[1]*0.15
		self.size = (self.rect.width, self.rect.height)#self.image.get_size()
		#textos---------
		txtInstructions=["Move: w a s d.", "Normal shoot: left click.", "Charged attack: hold right click.", "Game by", "KleSoft, Kyntasia and CerviGamer"]
		i=0
		g = locals()
		for txt in txtInstructions[0:-1]: 
			g["txtInstructions" + str(i)] = fnt.render(txt, 0, (0,0,0))
			#eval("txtInstructions" + str(i)).set_alpha(200)
			self.image.blit(eval("txtInstructions" + str(i)), (self.size[0] * 0.20, self.size[1]*(0.20 + (0.10*i))))
			i+=1
		g["txtInstructions" + str(i)] = fnt.render(txtInstructions[-1], 0, (255,0,0)) #el ultimo lo hace aparte, ya que va con un color diferente
		self.image.blit(eval("txtInstructions" + str(i)), (self.size[0] * 0.20, self.size[1]*(0.20 + (0.10*i))))
		#fintextos------
		#buttons--------
		self.buttonSalir = load_image("graphics/GUI/exitButton.png", True)
		
		
		self.buttonSalirRect = self.buttonSalir.get_rect()
		self.buttonSalirRect.x, self.buttonSalirRect.y = self.size[0]*0.85, self.size[1]*0.85 #esta colision seria dentro del surface del menu
		self.buttonSalirRealRect = self.buttonSalir.get_rect()
		self.buttonSalirRealRect.x, self.buttonSalirRealRect.y = self.buttonSalirRect.x + self.rect.x, self.buttonSalirRect.y + self.rect.y #y esta colision seria en la pantalla entera
		self.image.blit(self.buttonSalir, self.buttonSalirRect )
		self.image.set_alpha(200)
		
	def draw(self, pantalla):
		pantalla.blit(self.image, self.rect)
		#pygame.draw.rect(self.image, (255,0,0), self.buttonSalirRect, 3)
		#el ultimo texto corresponde al de los nombres, que se pone en la misma linea que la penultima, pero un poco mas a la derecha
