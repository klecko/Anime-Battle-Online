import sys
sys.path.append("C:/Users/David/Desktop/programacion/python/Anime Battle Online/client")
import pygame.transform

from functions.ShortFunctions import load_image


class Animation(list):
	def __init__(self, name, frames, delayBetweenFrames, nImagenStr, animationMirror = None, mirrorX = 0, mirrorY = 0):
		self.name = name
		self.frames = frames
		self.delayBetweenFrames = round(delayBetweenFrames)
		if animationMirror: #si la animacion es una copia de otra, la copia
			for frame in animationMirror:
				self.append(pygame.transform.flip(frame, mirrorX, mirrorY))
		else: #si no, la carga
			g = locals()
			for i in range(1, self.frames+1):
				g["image" + name + str(i)] = load_image("graphics/pjs/" + nImagenStr + "/" + name + str(i) + ".png", True)
				self.append(eval("image" + name + str(i)))
			
