import sys
sys.path.append("C:/Users/David/Desktop/programacion/python/Anime Battle Online/client")
import pygame.font


from classes.Animation import Animation
from classes.Bullet import Bullet
from functions.ShortFunctions import load_image, getBulletByNumber



class Player():
	def __init__(self, numero, pj, name):
		self.n = numero
		self.balas = []
		self.maxHp = 100
		self.name = name
		self.nameRender = pygame.font.Font("fonts/Pixeled.ttf", 13).render(name, 0, (0,0,0))
		self.pj = pj
		self.currentHp = self.maxHp
		self.direction = [0, 0]
		self.lastDirection = [0, 0]
		self.lastPos = [0,0]
		self.moving = False
		self.state = "normal"
		self.time = 0
		
		#image stuff----------------------------------------------
		#cargar imagenes y animaciones comunes a todos
		nImageStr = str(self.pj)
		self.fotogramaEnAnimacion = 0
		self.currentAnimation = None
		self.nextAnimations = []
		self.animationStillRight = Animation("StillRight", 2, 200, nImageStr)
		self.animationStillLeft = Animation("StillLeft", 2, 200, nImageStr, self.animationStillRight, 1, 0)  #la left es igual que la right
		self.imageDead = load_image("graphics/pjs/dead.png", True)
		
		
		#cargar imagenes y animaciones especificas de cada uno
		if self.pj == 1:
			self.animationChargeAttackRight = Animation("ChargeAttackRight", 8, 62.5, nImageStr)
			self.animationChargeAttackLeft = Animation("ChargeAttackLeft", 8, 62.5, nImageStr, self.animationChargeAttackRight, 1, 0)
		
		if self.pj == 3:
			self.animationChargeAttackRight = Animation("ChargeAttackRight", 5, 100, nImageStr)
			self.animationChargeAttackLeft = Animation("ChargeAttackLeft", 5, 100, nImageStr, self.animationChargeAttackRight, 1, 0)
			
		if self.pj == 4 or self.pj == 2:
			self.animationUltiRight = Animation("UltiRight", 2, 200, nImageStr)
			self.animationUltiLeft = Animation("UltiLeft", 2, 200, nImageStr, self.animationUltiRight, 1, 0)
		
		
		#right quieto: 1
		#left quieto: 2
		#animacion right quieto: 3
		#animacion left quieto:4
		
		self.setAnimation(self.animationStillRight)
		self.image = self.animationStillRight[0]
		self.rect = self.image.get_rect()
				
	def setAnimation(self, animation):
		#self.image = eval("self.imageAlive" + str(n))
		#self.fotograma = n
		self.currentAnimation = animation
		self.image = animation[0]
		self.fotogramaEnAnimacion = -1
		
	def setImageNoAnimation(self, image):
		self.currentAnimation = 0
		self.image = image
	
	def newBullet(self, sizeModifier, angle, initialPos, nImagen):
		#~ if not nImagen: #si no se ha dado una nImagen
			#~ nImagen = self.pj #se pone la de por defecto, que es el numero del pj
		n=1
		result = getBulletByNumber(n, self)
		if result:
			while result:
				n+=1
				result = getBulletByNumber(n, self)
		locals()["bala" + str(n)] = Bullet(n, self.n, nImagen, sizeModifier, angle, initialPos)
		#g["bala" + str(len(self.balas)+1)] = Bullet(len(self.balas)+1, self.n)
		self.balas.append(eval("bala" + str(n)))
		
	def draw(self, pantalla):
		#print(self.moving)
		if self.state == "normal":  
			if self.direction[0] == 1 and self.currentAnimation != self.animationStillRight:
				self.setAnimation(self.animationStillRight)
			elif self.direction[0] == -1 and self.currentAnimation != self.animationStillLeft:
				self.setAnimation(self.animationStillLeft)
		elif self.state == "buffed":
			if self.direction[0] == 1 and self.currentAnimation != self.animationUltiRight:
				self.setAnimation(self.animationUltiRight)
			elif self.direction[0] == -1 and self.currentAnimation != self.animationUltiLeft:
				self.setAnimation(self.animationUltiLeft)
		elif self.state == "chargingAttack":
			if self.direction[0] == 1 and self.currentAnimation != self.animationChargeAttackRight:
				self.setAnimation(self.animationChargeAttackRight)
				self.nextAnimations.append(self.animationStillRight)
			elif self.direction[0] == -1 and self.currentAnimation != self.animationChargeAttackLeft:
				self.setAnimation(self.animationChargeAttackLeft)
				self.nextAnimations.append(self.animationStillLeft)
		elif self.state == "dead":
			if self.image != self.imageDead:
				self.setImageNoAnimation(self.imageDead)
		#print(self.state)
		
		if self.currentAnimation: #si hay alguna animacion ejecutandose
			if pygame.time.get_ticks() - self.time >= self.currentAnimation.delayBetweenFrames:
				if self.fotogramaEnAnimacion == len(self.currentAnimation)-1: #si la animacion ha terminado
					if not self.nextAnimations: #si no hay proximas animaciones
						self.fotogramaEnAnimacion = 0 #la animacion vuelve a empezar
					else: #si hay proximas animaciones
						self.setAnimation(self.nextAnimations[0]) #se pone la siguiente
						self.nextAnimations.pop(0) #y se elimina de la lista
				else:
					self.fotogramaEnAnimacion += 1 #si la animacion no ha temrinado, continua
				self.image = self.currentAnimation[self.fotogramaEnAnimacion]
				self.time = pygame.time.get_ticks()
		
		pos = [self.rect.x, self.rect.y] #por defecto la posicion es la del rect, pero si el tamaño de la imagen es superior al del rect: 
		if self.image.get_width() > self.rect.width: #la coordenada x es la misma pero restando el espacio que se le suma por cada lado
			pos[0] = self.rect.x - (self.image.get_width()-self.rect.width)/2
		if self.image.get_height() > self.rect.height: #y la misma con la coordenada y
			pos[1] = self.rect.y - (self.image.get_height()-self.rect.height)/2
				
		pantalla.blit(self.image, pos)
		#print(self.rect.centerx, self.rect.centery)
		#pygame.draw.rect(pantalla, (255,0,0), self.rect, 2)
		#rect = self.image.get_rect()
		#rect.centerx, rect.centery = self.rect.centerx, self.rect.centery
		#pygame.draw.rect(pantalla, (0,0,255), rect, 1)
	def drawHPBar(self, pantalla):
		#elijo color
		#~ if self.currentHp / self.maxHp >= 0.7:
			#~ color = (0,255,0)
		#~ elif self.currentHp / self.maxHp < 0.7 and self.currentHp / self.maxHp > 0.3:
			#~ color = (255,200,0)
		#~ elif self.currentHp / self.maxHp <= 0.3:
			#~ color = (255,75,0)
			
				#1			  0.5 			0
		#from (0,255,0) to (255,200,0) to (255, 0, 0)
		if self.currentHp/self.maxHp >= 0.5:
			color = (510*(1-(self.currentHp/self.maxHp)), 145 + (110*(self.currentHp/self.maxHp)), 0)
		else:
			color = (255, 400*(self.currentHp/self.maxHp), 0)
		
		
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
		pantalla.blit(self.nameRender, (self.rect.centerx-(self.nameRender.get_width()/2), self.rect.centery-108))
		#pygame.draw.rect(pantalla, (0,255,0), (self.rect.centerx-23, self.rect.y-18, 46, 11), 0)
