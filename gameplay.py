import os, sys
import math
import random
from random import randint

import pygame
from pygame import font
from pygame import key

from pygame import Rect
from pygame import draw

from gameObjects import Paddle
from gameObjects import Ball
from gameObjects import Brick
from gameObjects import collides

from gameObjects import Pickup
from gameObjects import rectCollides

import particles
import randomTools

import menu

# screen & color data
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 900
BG_COLOR = 0, 0, 0
FONT_COLOR = 12, 222, 12

# initalize the libraries
pygame.init()
font.init()

class BREAKOUT():
	def __init__(self, goBack, highscore, keys):
		self.goBack = goBack
		self.highscore = highscore
		self.keys = keys

		self.livesPosition = (30, 815)
		self.scorePosition = (800, 815)

		self.outputFont = font.Font("textures/MATRIX.ttf", 44)
		self.gameOverFont = font.Font("textures/MATRIX.ttf", 120)

		# set up the display
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

		# use dictionaries becasue python doesn't have switch statements
		# assigns points for bricks in each row and color assignments in each row
		self.pointAssigns = {
			0: 5,
			1: 5,
			2: 3,
			3: 3,
			4: 2,
			5: 2,
			6: 1,
			7: 1
		}

		self.colorAssigns = {
			0: (14, 255, 31),
			1: (14, 255, 31),
			2: (21, 70, 255),
			3: (21, 70, 255),
			4: (255, 135, 5),
			5: (255, 135, 5),
			6: (241, 255, 8),
			7: (241, 255, 8)
		}

		self.paddleLoc = Paddle(self.screen, (375, 865), (180, 20), 650, self.keys)
		self.shrunk = False
		self.balls = []

		self.pickups = []

		self.countdown = 3.0

		self.speedUps = 0

		self.gameOver = False
		self.running = True
		self.lives = 3
		self.score = 0
		self.newBallPoints = 0

		self.bricksDestroyed = 0

		self.bricks = []
		self.rowsCleared = []

		self.particles = particles.ParticleSystem(self.screen, "textures/greensparksmall.png", 50, 10, 1, .5)

	def run_game(self, keys):
		clock = pygame.time.Clock()

		self.particles.clear()

		self.keys = keys

		self.paddleLoc = Paddle(self.screen, (375, 865), (180, 20), 650, self.keys)
		self.shrunk = False
		self.balls = []
		self.balls.append(Ball(self.screen, (self.paddleLoc.pos.x + self.paddleLoc.w / 2, self.paddleLoc.pos.y - 15), math.pi * 7 / 4, 15, 500))

		self.pickups = []
		self.slowTime = 0
		self.fastTime = 0
		self.shrinkTime = 0
		self.growTime = 0

		self.pickupShrunk = False
		self.pickupGrow = False

		self.countdown = 3.0

		self.speedUps = 0

		self.gameOver = False
		self.running = True
		self.lives = 3
		self.score = 0
		self.newBallPoints = 0

		self.bricksDestroyed = 0

		self.bricks = []
		self.rowsCleared = []

		for row in range(0, 8):
			self.bricks.append([])
			self.rowsCleared.append(False)

			pts = self.pointAssigns[row]
			color = self.colorAssigns[row]

			for brick in range(0, 14):
				self.bricks[row].append(Brick(self.screen, (1000 / 14 * brick + 3, 75 + 40 * row), (71, 40), pts, color))

		# The main game loop
		while self.running:
			# Limit frame speed to a glorious 60 FPS
			time_passed = clock.tick(60)

			# Event loop to catch if the user has quit
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if key.get_pressed()[self.keys['quit']]:
						self.running = False
						if self.gameOver:
							self.highscore.run()
						else:
							self.goBack()
	        
			# Redraw the background
			self.screen.fill(BG_COLOR)

			# update the particles
			if self.slowTime > 0:
				self.particles.update(float(time_passed) / 2)
			elif self.fastTime > 0:
				self.particles.update(float(time_passed) * 2)
			else:
				self.particles.update(float(time_passed))

			if not self.gameOver:
				self.update(time_passed)

			self.render()

			pygame.display.flip()

	def update(self, timePassed):
		# Update the paddle (because we need to move it while the countdown is running)
		self.paddleLoc.update(float(timePassed))

		toDelete = []
		# iterate through pickups
		for idx, pickup in enumerate(self.pickups):
			pickup.update(timePassed)

			if pickup.pos.y > self.screen.get_rect().height:
				toDelete.append(idx)
			elif rectCollides(pickup.getHitBox(), self.paddleLoc.getHitBox()):
				self.resetAllPickupEffects()

				if pickup.kind == 'slow':
					self.slowTime = 3.0
				elif pickup.kind == 'fast':
					self.fastTime = 3.0
				elif pickup.kind == 'shrink':
					self.shrinkTime = 3.0
				elif pickup.kind == 'grow':
					self.growTime = 3.0

				toDelete.append(idx)

		for x in reversed(toDelete):
			del self.pickups[x]

		if self.countdown > 0.0:
			self.countdown = self.countdown - float(timePassed) / 1000
			self.balls[0].setPos((self.paddleLoc.pos.x + self.paddleLoc.w / 2, self.paddleLoc.pos.y - 15))
			return

		# first determine if the paddle should be shrunk
		if not self.shrunk:
			for brick in self.bricks[0]:
				if not brick.intact:
					self.shrunk = True
					self.paddleLoc.shrink()
					break

		if self.slowTime > 0:
			self.slowTime -= float(timePassed) / 1000
			timePassed = timePassed / 2
		elif self.fastTime > 0:
			self.fastTime -= float(timePassed) / 1000
			timePassed = timePassed * 2
		elif self.shrinkTime > 0:
			self.shrinkTime -= float(timePassed) / 1000
			if not self.pickupShrunk:
				self.pickupShrunk = True
				self.paddleLoc.shrink()
		elif self.shrinkTime <= 0 and self.pickupShrunk:
			self.pickupShrunk = False
			self.paddleLoc.grow()
		elif self.growTime > 0:
			self.growTime -= float(timePassed) / 1000
			if not self.pickupGrow:
				self.pickupGrow = True
				self.paddleLoc.grow()
		elif self.growTime <= 0 and self.pickupGrow:
			self.pickupGrow = False
			self.paddleLoc.shrink()

		# update everything else
		toDelete = []

		for idx, ball in enumerate(self.balls):
			if(self.balls[idx].speedUps < self.speedUps):
				self.balls[idx].increaseSpeed(60)

			preview = self.balls[idx].getMovePreview(float(timePassed))

			# if the ball collides with the paddle react accordingly
			if collides(self.paddleLoc.getHitBox(), preview):
				if self.balls[idx].pos.x + self.balls[idx].r > self.paddleLoc.pos.x and self.balls[idx].pos.x - self.balls[idx].r < self.paddleLoc.pos.x + self.paddleLoc.w:
					step = preview.pos.x - preview.r - self.paddleLoc.pos.x
					totalLeft = math.pi * 3 / 4
					self.balls[idx].setDirection(math.pi + totalLeft - (step / self.paddleLoc.w * totalLeft))
					self.balls[idx].reflectVelX()
				else:
					self.balls[idx].reflectVelX()

				preview = self.balls[idx].getMovePreview(float(timePassed))

			for row in self.bricks:
				for brick in row:
					if brick.intact and collides(brick, preview):
						brick.destroy()
						self.score = self.score + brick.points
						self.newBallPoints = self.newBallPoints + brick.points
						self.bricksDestroyed = self.bricksDestroyed + 1

						# if the ball is going fast or the paddle is small give you a slight point bonus
						if self.fastTime > 0:
							self.score += 3
							if self.speedUps > 2:
								self.score += 5
						elif self.shrinkTime > 0:
							self.score += 3
							if self.shrunk:
								self.score += 5

						# spawn pickup
						choice = randint(1, 20)
						if choice > 16:
							self.pickups.append(Pickup(self.screen, (brick.x + brick.w / 2 - 20, brick.y + brick.h / 2 - 10), (40, 20), 200, random.choice(['slow', 'fast', 'shrink', 'grow'])))

						# spawn particles
						for x in xrange(20):
							self.particles.spawnParticle((brick.x + brick.w / 2, brick.y + brick.h / 2), randomTools.nextCircleVector())

						hitSides = self.balls[idx].pos.y > brick.y and self.balls[idx].pos.y < brick.y + brick.h
						hitTopBot = self.balls[idx].pos.x + self.balls[idx].r * 2 / 3 > brick.x and self.balls[idx].pos.x - self.balls[idx].r * 2 / 3 < brick.x + brick.w

						if hitSides == hitTopBot:
							self.balls[idx].reflectVelX()
							self.balls[idx].reflectVelY()
						elif hitSides:
							self.balls[idx].reflectVelX()
						elif hitTopBot:
							self.balls[idx].reflectVelY()

						preview = self.balls[idx].getMovePreview(float(timePassed))

			if self.balls[idx].update(float(timePassed)):
				if self.balls[idx].pos.y < 100:
					self.balls[idx].reflectVelY()
				else:
					toDelete.append(idx)

		for i in reversed(toDelete):
			for x in xrange(20):
				self.particles.spawnParticle((self.balls[i].pos.x, self.screen.get_rect().height - self.balls[i].r), randomTools.nextTopQuarterVector())

			del self.balls[i]

		# check if rows have been cleared
		for idx, row in enumerate(self.bricks):
			if not self.rowsCleared[idx]:
				cleared = True

				for brick in self.bricks[idx]:
					if brick.intact:
						cleared = False
						break

				if cleared:
					self.rowsCleared[idx] = True;
					self.score += 25
					self.newBallPoints += 25

		if self.speedUps < 1 and self.bricksDestroyed >= 4: 
			self.speedUps = 1;
		if self.speedUps < 2 and self.bricksDestroyed >= 12: 
			self.speedUps = 2;
		if self.speedUps < 3 and self.bricksDestroyed >= 36: 
			self.speedUps = 3;
		if self.speedUps < 4 and self.bricksDestroyed >= 62: 
			self.speedUps = 4;

		# determine if you should have a new ball
		if self.newBallPoints >= 100:
			self.newBallPoints = self.newBallPoints - 100
			self.balls.append(Ball(self.screen, (self.paddleLoc.pos.x + self.paddleLoc.w / 2, self.paddleLoc.pos.y - 15), math.pi * 7 / 4, 15, 500))

		# determine if you need to lose a life or game over
		if len(self.balls) == 0 and self.lives > 0:
			self.lives -= 1

			# reset all effects from pickups
			self.resetAllPickupEffects()

			# spawn particles in all pickup locations and then delete all pickups
			for pickup in self.pickups:
				for x in xrange(20):
					self.particles.spawnParticle((pickup.pos.x + pickup.w / 2, pickup.pos.y + pickup.h / 2), randomTools.nextCircleVector())
			self.pickups = []

			# then finally either spawn a new ball and initiate countdown or declare game over
			if self.lives > 0:
				self.countdown = 3.0
				self.balls.append(Ball(self.screen, (self.paddleLoc.pos.x + self.paddleLoc.w / 2, self.paddleLoc.pos.y - 15), math.pi * 7 / 4, 15, 500))
			else:
				self.gameOver = True
				self.highscore.addScore(self.score)

				for row in self.bricks:
					for brick in row:
						if brick.intact:
							for x in xrange(20):
								self.particles.spawnParticle((brick.x + brick.w / 2, brick.y + brick.h / 2), randomTools.nextCircleVector())

				for x in xrange(50):
					self.particles.spawnParticle((self.paddleLoc.pos.x + randint(0, self.paddleLoc.w), self.paddleLoc.pos.y + self.paddleLoc.h / 2), randomTools.nextTopQuarterVector())


	def render(self):
		self.particles.render()

		if self.gameOver:
			fontOut = self.gameOverFont.render("GAME OVER", True, FONT_COLOR)
			self.screen.blit(fontOut, (SCREEN_WIDTH / 2 - fontOut.get_rect().width / 2, SCREEN_HEIGHT / 2 - fontOut.get_rect().height))
		else:
			# render everything
			for ball in self.balls:
				ball.render()

			for row in self.bricks:
				for brick in row:
					brick.render()

			for pickup in self.pickups:
				pickup.render()

			self.paddleLoc.draw()

			# draw effect time on paddle if effect is active
			if self.slowTime > 0.0:
				modifier = int(self.paddleLoc.w / 2 * self.slowTime / 3.0)
				draw.rect(self.screen, (0, 198, 255), Rect(self.paddleLoc.pos.x + self.paddleLoc.w / 2 - modifier, self.paddleLoc.pos.y, modifier * 2, self.paddleLoc.h))
			elif self.fastTime > 0.0:
				modifier = int(self.paddleLoc.w / 2 * self.fastTime / 3.0)
				draw.rect(self.screen, (255, 0, 0), Rect(self.paddleLoc.pos.x + self.paddleLoc.w / 2 - modifier, self.paddleLoc.pos.y, modifier * 2, self.paddleLoc.h))
			elif self.growTime > 0.0:
				modifier = int(self.paddleLoc.w / 2 * self.growTime / 3.0)
				draw.rect(self.screen, (61, 248, 52), Rect(self.paddleLoc.pos.x + self.paddleLoc.w / 2 - modifier, self.paddleLoc.pos.y, modifier * 2, self.paddleLoc.h))
			elif self.shrinkTime > 0.0:
				modifier = int(self.paddleLoc.w / 2 * self.shrinkTime / 3.0)
				draw.rect(self.screen, (174, 0, 255), Rect(self.paddleLoc.pos.x + self.paddleLoc.w / 2 - modifier, self.paddleLoc.pos.y, modifier * 2, self.paddleLoc.h))


			if self.countdown > 0.0:
				fontOut = self.gameOverFont.render(str(int(self.countdown) + 1), True, FONT_COLOR)
				self.screen.blit(fontOut, (SCREEN_WIDTH / 2 - fontOut.get_rect().width / 2, SCREEN_HEIGHT / 2 - fontOut.get_rect().height))

		# draw lives and score to screen
		fontOut = self.outputFont.render("Lives: " + str(self.lives), True, FONT_COLOR)
		self.screen.blit(fontOut, self.livesPosition)
		fontOut = self.outputFont.render("Score: " + str(self.score), True, FONT_COLOR)
		self.screen.blit(fontOut, self.scorePosition)

	def resetAllPickupEffects(self):
		self.fastTime = 0
		self.slowTime = 0
		self.shrinkTime = 0
		self.growTime = 0

		if self.pickupShrunk:
			self.pickupShrunk = False
			self.paddleLoc.grow()
		if self.pickupGrow:
			self.pickupGrow = False
			self.paddleLoc.shrink()