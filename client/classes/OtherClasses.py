import sys
sys.path.append("C:/Users/David/Desktop/programacion/python/Anime Battle Online/client")
from pygame import draw

from functions.ShortFunctions import load_image

class PowerUp():
	def __init__(self, n, currentState, currentPos):
		self.image = load_image("graphics/powerups/" + str(n) + ".png", True)
		self.rect = self.image.get_rect()
		self.rect.centerx, self.rect.centery = currentPos[0], currentPos[1]
		self.visible = currentState
	def draw(self, pantalla):
		if self.visible == True:
			pantalla.blit(self.image, self.rect)



		
class Wall():
	def __init__(self, n, rect, color, width=0):
		self.n = n
		self.rect = rect
		self.color = color
		self.width = width
	def draw(self, pantalla):
		draw.rect(pantalla, self.color, self.rect, self.width)
		#print(self.rect)
