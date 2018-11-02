import sys
sys.path.append("C:/Users/David/Desktop/programacion/python/Anime Battle Online/client")
import pygame.transform

from functions.ShortFunctions import load_image, getPlayerByNumber

class Bullet():
	def __init__(self, numero, numeroPlayer, numeroImagen, sizeModifier, angle, initialPos):
		self.n = numero
		self.nPlayer = numeroPlayer
		self.image = load_image("graphics/shots/" + str(numeroImagen) + ".png", True)
		if angle >= -90 and angle <= 90:
			self.image = pygame.transform.rotate(self.image, angle) #si el angulo es de la mitad derecha, lo rota los angulos necesarios
		elif angle > 90 or angle < -90:
			self.image = pygame.transform.rotate(self.image, 180-angle)#si es de la mitad izquierda, lo rota los angulos como si fuera de la mitad derechaa (180-angle)
			self.image = pygame.transform.flip(self.image, 1, 0)#y despues los voltea horizontalmente
			#esto es para que por ejemplo el puño no aparezca hacia abajo
		if sizeModifier != 1:
			self.image = pygame.transform.scale(self.image, (int(self.image.get_size()[0]*sizeModifier), int(self.image.get_size()[1]*sizeModifier)))
		self.rect = self.image.get_rect(center=initialPos) #la initialPos es necesaria, ya que a veces se dibuja un fotograma en el que el servidor
		#no ha enviado la posicion de la bala. en estos casos, la bala se dibuja en la posicion (0,0), y queda feo
	def draw(self,pantalla):
		pantalla.blit(self.image, self.rect)
	def eliminar(self):
		getPlayerByNumber(self.nPlayer).balas.remove(self)
		del(self)
