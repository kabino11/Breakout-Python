import math

import pygame
from pygame.sprite import Sprite

from vec2d import vec2d

import randomTools

class Particle(Sprite):
	def __init__(self, screen, image, loc, dir_vector, spd, spd_dev, mean_life, dev_life):
		Sprite.__init__(self)

		self.screen = screen
		self.image = image

		self.pos = vec2d(loc)
		self.dir = dir_vector
		self.speed = max(1, randomTools.nextGaussian(spd, spd_dev))
		self.size = max(1, randomTools.nextGaussian(12, 4))
		self.rotation = 0
		self.lifetime = max(.01, randomTools.nextGaussian(mean_life, dev_life))

		self.alive = 0.0

	def update(self, timepassed):
		self.alive = self.alive + timepassed / 1000

		dx = self.speed * self.dir.x * timepassed / 1000
		dy = self.speed * self.dir.y * timepassed / 1000

		self.rotation = self.rotation + self.speed * timepassed / 500 * 3

		self.pos = self.pos + vec2d(dx, dy)

	def render(self):
		originalsize = self.image.get_rect()

		outimage = pygame.transform.rotate(self.image, self.rotation)
		outimage = pygame.transform.scale(outimage, (int(self.size), int(self.size)))
		draw_pos = outimage.get_rect().move(self.pos.x, self.pos.y)
		self.screen.blit(outimage, draw_pos)


class ParticleSystem():
	def __init__(self, screen, img_filename, spd, spd_dev, lifetime, life_dev):
		self.screen = screen

		self.base_image = pygame.image.load(img_filename).convert_alpha()
		self.image = self.base_image

		self.spd = spd
		self.spd_dev = spd_dev

		self.lifetime = lifetime
		self.life_dev = life_dev

		self.particles = []

	def clear(self):
		self.particles = []

	def spawnParticle(self, location, direction):
		self.particles.append(Particle(self.screen, self.image, location, direction, self.spd, self.spd_dev, self.lifetime, self.life_dev))

	def update(self, timepassed):
		toDelete = []

		for idx, particle in enumerate(self.particles):
			self.particles[idx].update(timepassed)

			if self.particles[idx].alive >= self.particles[idx].lifetime:
				toDelete.append(idx)

		for i in reversed(toDelete):
			del self.particles[i]

	def render(self):
		for particle in self.particles:
			particle.render()
