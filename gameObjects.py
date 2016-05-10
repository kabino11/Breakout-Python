import math

import pygame
from pygame import Rect
from pygame import key
from pygame import display
from pygame import draw

from vec2d import vec2d

class Paddle():
	def __init__(self, screen, init_position, size, speed, keys):

		self.screen = screen
		self.speed = speed

		self.keys = keys

		#was used when class was a sprite
		#self.base_image = pygame.image.load(img_filename).convert_alpha()
		#self.image = self.base_image

		self.w, self.h = size

		self.pos = vec2d(init_position)

	def update(self, time_passed):
		pressed = key.get_pressed()

		dx = 0

		# Take the keypresses and move character accordingly
		if pressed[self.keys['left']]:
			dx -= self.speed * (time_passed / 1000)
		if pressed[self.keys['right']]:
			dx += self.speed * (time_passed / 1000)

		result = self.pos + vec2d(dx, 0)

		#check to see if you're hitting the walls, if so correct your movement
		gameScreen = display.get_surface();

		if result.x < 0:
			result.x = 0
		if result.x + self.w > gameScreen.get_width():
			result.x = gameScreen.get_width() - self.w

		self.pos = result

	def shrink(self):
		self.w = self.w / 2
		self.pos.x = self.pos.x + self.w / 2

	def grow(self):
		self.w = self.w * 2
		self.pos.x = self.pos.x - self.w / 4

	def getHitBox(self):
		return Rect(self.pos.x, self.pos.y, self.w, self.h)

	def draw(self):
		# draw_pos = self.image.get_rect().move(self.pos.x,  self.pos.y)
		# self.screen.blit(self.image, draw_pos)

		draw.rect(display.get_surface(), (0, 255, 0), Rect(self.pos.x, self.pos.y, self.w, self.h))
		draw.rect(display.get_surface(), (0, 0, 0), Rect(self.pos.x, self.pos.y, self.w, self.h), 3)


class Ball():
	def __init__(self, screen, init_position, init_direction, size, speed):
		self.screen = screen
		self.speed = speed

		self.r = size

		self.pos = vec2d(init_position)
		self.direction = init_direction

		self.speedUps = 0

		self.lastHit = ''

	def setLastHit(self, who):
		self.lastHit = who

	def setPos(self, pos):
		self.pos = vec2d(pos)

	def increaseSpeed(self, spd):
		if spd > 0:
			self.speed = self.speed + spd
			self.speedUps = self.speedUps + 1

	# functions for changing the ball angle (first 2 just reflect across a major axis velocity-wise)
	def reflectVelX(self):
		self.direction = math.pi - self.direction
		self.direction = self.direction % (2.0 * math.pi)

	def reflectVelY(self):
		self.direction = (2 * math.pi) - self.direction
		self.direction = self.direction % (2.0 * math.pi)

	def setDirection(self, angle):
		self.direction = angle
		self.direction = self.direction % (2 * math.pi)

	def getHitRegion(self):
		return Circle(self.pos, self.r)

	def getMovePreview(self, time_passed):
		dx = self.speed * math.cos(self.direction) * (time_passed / 1000)
		dy = self.speed * math.sin(self.direction) * (time_passed / 1000)
		r = self.r

		outPos = self.pos + vec2d(dx, dy)

		return Circle(outPos, r)

	def update(self, time_passed):
		dx = math.cos(self.direction) * self.speed * (time_passed / 1000)
		dy = math.sin(self.direction) * self.speed * (time_passed / 1000)

		outPos = self.pos + vec2d(dx, dy)

		if outPos.x - self.r < 0 or outPos.x + self.r > self.screen.get_width():
			self.reflectVelX()
			dx = self.speed * math.cos(self.direction) * (time_passed / 1000)
			outPos = self.pos + vec2d(dx, dy)

		self.pos = self.pos + vec2d(dx, dy)

		return outPos.y + self.r > self.screen.get_height() or outPos.y - self.r < 0

	def render(self):
		draw.circle(display.get_surface(), (0, 0, 255), vec2d(int(self.pos.x), int(self.pos.y)), self.r)
		draw.circle(display.get_surface(), (0, 0, 0), vec2d(int(self.pos.x), int(self.pos.y)), self.r, 3)


class Brick():
	def __init__(self, screen, init_position, size, points, color):
		self.screen = screen

		self.x, self.y = init_position
		self.w, self.h = size
		self.points = points
		self.color = color
		self.intact = True

		self.destroyedBy = ''

	def destroy(self):
		self.intact = False

	def setDestroyedBy(self, who):
		self.destroyedBy = who

	def render(self):
		if self.intact:
			display.get_surface().set_alpha(180)
			draw.rect(display.get_surface(), self.color, Rect(self.x, self.y, self.w, self.h))
			display.get_surface().set_alpha(None)
			draw.rect(display.get_surface(), (12, 222, 12), Rect(self.x, self.y, self.w, self.h), 3)


class Pickup():
	def __init__(self, screen, init_position, size, speed, kind):
		self.screen = screen
		self.pos = vec2d(init_position)
		self.w, self.h = size

		self.speed = speed

		self.kind = kind

	def update(self, time_passed):
		dy = self.speed * time_passed / 1000

		changed = vec2d(0, dy)

		self.pos = self.pos + changed

	def render(self):
		color = (0, 0, 0)

		if self.kind == 'slow':
			color = (0, 198, 255)
		elif self.kind == 'fast':
			color = (255, 0, 0)
		elif self.kind == 'shrink':
			color = (174, 0, 255)
		elif self.kind == 'grow':
			color = (61, 248, 52)

		display.get_surface().set_alpha(180)
		draw.rect(display.get_surface(), color, Rect(self.pos.x, self.pos.y, self.w, self.h))
		display.get_surface().set_alpha(None)
		draw.rect(display.get_surface(), (0, 0, 0), Rect(self.pos.x, self.pos.y, self.w, self.h), 3)

	def getHitBox(self):
		return Rect(self.pos.x, self.pos.y, self.w, self.h)


class Circle():
	def __init__(self, pos, size):
		self.r = size
		self.pos = vec2d(pos)


def collides(rect, circle):
	half = vec2d(rect.w / 2, rect.h / 2)
	center = vec2d(circle.pos.x - (rect.x + half.x), circle.pos.y - (rect.y + half.y))

	side = vec2d(abs(center.x) - half.x, abs(center.y) - half.y)

	if side.x > circle.r or side.y > circle.r:
		return False
	if side.x < 0 or side.y < 0:
		return True

	return side.x * side.x + side.y * side.y < circle.r * circle.r

def rectCollides(a, b):
	return a.x < b.x + b.w and a.x + a.w > b.x and a.y < b.y + b.h and a.h + a.y > b.y