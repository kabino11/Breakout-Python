import os, sys
import math
from random import randint

import pygame
from pygame import font
from pygame import key

from gameObjects import Paddle
from gameObjects import Ball
from gameObjects import Brick
from gameObjects import collides

import particles
import randomTools

import menu

# screen & color data
BG_COLOR = 0, 0, 0
FONT_COLOR = 12, 222, 12

# initalize the libraries
pygame.init()
font.init()

class TwoPlayer():
	def __init__(self, goBack, keys):
		self.goBack = goBack
		self.keys = keys

		self.p2keys = {
			'right': keys['p2right'],
			'left': keys['p2left']
		}

		self.livesPosition = (30, 915)
		self.scorePosition = (800, 915)

		self.p2livesPosition = (30, 85)
		self.p2scorePosition = (800, 85)

		self.outputFont = font.Font("textures/MATRIX.ttf", 44)
		self.gameOverFont = font.Font("textures/MATRIX.ttf", 120)

		# set up the display
		self.screen = pygame.display.set_mode((1000, 1000), 0, 32)

		# use dictionaries becasue python doesn't have switch statements
		# assigns points for bricks in each row and color assignments in each row
		self.pointAssigns = {
			0: 3,
			1: 3,
			2: 5,
			3: 5,
			4: 5,
			5: 5,
			6: 3,
			7: 3
		}

		self.colorAssigns = {
			0: (21, 70, 255),
			1: (21, 70, 255),
			2: (14, 255, 31),
			3: (14, 255, 31),
			4: (14, 255, 31),
			5: (14, 255, 31),
			6: (21, 70, 255),
			7: (21, 70, 255)
		}

		self.paddleLoc = Paddle(self.screen, (375, 865), (180, 20), 650, self.keys)
		self.p2paddleLoc = Paddle(self.screen, (375, 20), (180, 20), 650, self.keys)
		self.balls = []

		self.countdown = 3.0

		self.speedUps = 0

		self.gameOver = False
		self.running = True
		self.lives = 3
		self.score = 0
		self.newBallPoints = 0

		self.p2lives = True
		self.p2score = True

		self.bricksDestroyed = 0

		self.bricks = []
		self.rowsCleared = []

		self.particles = particles.ParticleSystem(self.screen, "textures/greensparksmall.png", 50, 10, 1, .5)

	def run_game(self, keys):
		self.screen = pygame.display.set_mode((1000, 1000), 0, 32)

		clock = pygame.time.Clock()

		self.particles.clear()

		self.keys = keys
		self.p2keys = {
			'right': keys['p2right'],
			'left': keys['p2left']
		}

		self.paddleLoc = Paddle(self.screen, (375, 965), (180, 20), 650, self.keys)
		self.p2paddleLoc = Paddle(self.screen, (375, 20), (180, 20), 650, self.p2keys)
		self.shrunk = False
		self.balls = []
		self.balls.append(Ball(self.screen, (self.paddleLoc.pos.x + self.paddleLoc.w / 2, self.paddleLoc.pos.y - 15), math.pi * 7 / 4, 15, 500))
		self.balls[-1].setLastHit('P1')
		self.balls.append(Ball(self.screen, (self.p2paddleLoc.pos.x + self.p2paddleLoc.w / 2, self.p2paddleLoc.pos.y + self.p2paddleLoc.h + 15), math.pi / 4, 15, 500))
		self.balls[-1].setLastHit('P2')

		self.countdown = 3.0

		self.speedUps = 0

		self.gameOver = False
		self.running = True
		self.lives = 5
		self.score = 0
		self.newBallPoints = 0

		self.p2lives = 5
		self.p2score = 0

		self.bricksDestroyed = 0

		self.bricks = []
		self.rowsCleared = []

		for row in range(0, 8):
			self.bricks.append([])
			self.rowsCleared.append(False)

			pts = self.pointAssigns[row]
			color = self.colorAssigns[row]

			for brick in range(0, 14):
				self.bricks[row].append(Brick(self.screen, (1000 / 14 * brick + 3, self.screen.get_rect().height / 2 - 160 + 40 * row), (71, 40), pts, color))

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
						self.goBack()
	        
			# Redraw the background
			self.screen.fill(BG_COLOR)

			self.particles.update(float(time_passed))

			if not self.gameOver:
				self.update(time_passed)

			self.render()

			pygame.display.flip()

	def update(self, timePassed):
		# Update the paddle (because we need to move it while the countdown is running)
		if self.lives > 0:
			self.paddleLoc.update(float(timePassed))

		if self.p2lives > 0:
			self.p2paddleLoc.update(float(timePassed))

		if self.countdown > 0.0:
			self.countdown = self.countdown - float(timePassed) / 1000
			if self.lives > 0:
				self.balls[0].setPos((self.paddleLoc.pos.x + self.paddleLoc.w / 2, self.paddleLoc.pos.y - 15))
			if self.p2lives > 0:
				self.balls[-1].setPos((self.p2paddleLoc.pos.x + self.p2paddleLoc.w / 2, self.p2paddleLoc.pos.y + self.p2paddleLoc.h + 15))
			return

		# update everything else
		toDelete = []

		for idx, ball in enumerate(self.balls):
			if(self.balls[idx].speedUps < self.speedUps):
				self.balls[idx].increaseSpeed(60)

			preview = self.balls[idx].getMovePreview(float(timePassed))

			# if the ball collides with the paddle react accordingly
			if self.lives > 0 and collides(self.paddleLoc.getHitBox(), preview):
				if self.balls[idx].pos.x + self.balls[idx].r > self.paddleLoc.pos.x and self.balls[idx].pos.x - self.balls[idx].r < self.paddleLoc.pos.x + self.paddleLoc.w:
					step = preview.pos.x - preview.r - self.paddleLoc.pos.x
					totalLeft = math.pi * 3 / 4
					self.balls[idx].setDirection(math.pi + totalLeft - (step / self.paddleLoc.w * totalLeft))
					self.balls[idx].reflectVelX()
				else:
					self.balls[idx].reflectVelX()

				self.balls[idx].setLastHit('P1')

				preview = self.balls[idx].getMovePreview(float(timePassed))

			if self.p2lives > 0 and collides(self.p2paddleLoc.getHitBox(), preview):
				if self.balls[idx].pos.x + self.balls[idx].r > self.p2paddleLoc.pos.x and self.balls[idx].pos.x - self.balls[idx].r < self.p2paddleLoc.pos.x + self.p2paddleLoc.w:
					step = preview.pos.x - preview.r - self.p2paddleLoc.pos.x
					totalLeft = math.pi * 3 / 4
					self.balls[idx].setDirection(totalLeft - (step / self.paddleLoc.w * totalLeft))
				else:
					self.balls[idx].reflectVelX()

				self.balls[idx].setLastHit('P2')

				preview = self.balls[idx].getMovePreview(float(timePassed))

			for row in self.bricks:
				for brick in row:
					if brick.intact and collides(brick, preview):
						brick.destroy()
						brick.setDestroyedBy(ball.lastHit)
						if self.balls[idx].lastHit == 'P1':
							self.score = self.score + brick.points
						else:
							self.p2score = self.p2score + brick.points

						self.newBallPoints = self.newBallPoints + brick.points
						self.bricksDestroyed = self.bricksDestroyed + 1

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
				toDelete.append(idx)
				if self.balls[idx].pos.y < 100:
					self.p2lives -= 1
				else:
					self.lives -= 1

		for i in reversed(toDelete):
			for x in xrange(20):
				self.particles.spawnParticle((self.balls[i].pos.x, self.balls[i].pos.y), randomTools.nextCircleVector())

			del self.balls[i]

		# check if rows have been cleared
		for idx, row in enumerate(self.bricks):
			if not self.rowsCleared[idx]:
				cleared = True

				p1cleared = 0
				p2cleared = 0

				for brick in self.bricks[idx]:
					if brick.intact:
						cleared = False
						break
					elif brick.destroyedBy == 'P1':
						p1cleared += 1
					elif brick.destroyedBy == 'P2':
						p2cleared += 1

				if cleared:
					self.rowsCleared[idx] = True;
					self.newBallPoints += 25
					if p1cleared > p2cleared:
						self.score += 25
					elif p2cleared > p1cleared:
						self.p2score += 25
					else:
						self.score += 10
						self.p2score += 10

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
			if self.lives > 0:
				self.balls.append(Ball(self.screen, (self.paddleLoc.pos.x + self.paddleLoc.w / 2, self.paddleLoc.pos.y - 15), math.pi * 7 / 4, 15, 500))
				self.balls[-1].setLastHit('P1')
			if self.p2lives > 0:
				self.balls.append(Ball(self.screen, (self.p2paddleLoc.pos.x + self.p2paddleLoc.w / 2, self.p2paddleLoc.pos.y + self.p2paddleLoc.h + 15), math.pi / 4, 15, 500))
				self.balls[-1].setLastHit('P2')


		# determine if you need to lose a life or game over
		if len(self.balls) == 0:
			if self.lives > 0 or self.p2lives > 0:
				self.countdown = 3.0

				if self.lives > 0:
					self.balls.append(Ball(self.screen, (self.paddleLoc.pos.x + self.paddleLoc.w / 2, self.paddleLoc.pos.y - 15), math.pi * 7 / 4, 15, 500))
					self.balls[0].setLastHit('P1')
				if self.p2lives > 0:
					self.balls.append(Ball(self.screen, (self.p2paddleLoc.pos.x + self.p2paddleLoc.w / 2, self.p2paddleLoc.pos.y + self.p2paddleLoc.h + 15), math.pi / 4, 15, 500))
					self.balls[-1].setLastHit('P2')
			
			if self.lives <= 0 or self.p2lives <= 0:
				self.initalizeGameOver()

		if self.lives <= 0 or self.p2lives <= 0:
			self.initalizeGameOver()

	def render(self):
		self.particles.render()

		if self.gameOver:
			fontOut = self.gameOverFont.render("GAME OVER", True, FONT_COLOR)
			self.screen.blit(fontOut, (self.screen.get_rect().width / 2 - fontOut.get_rect().width / 2, self.screen.get_rect().height / 2 - fontOut.get_rect().height))
			if self.score > self.p2score:
				fontOut = self.gameOverFont.render("PLAYER 1 WINS", True, FONT_COLOR)
			elif self.score < self.p2score:
				fontOut = self.gameOverFont.render("PLAYER 2 WINS", True, FONT_COLOR)
			else:
				fontOut = self.gameOverFont.render("IT\'S A TIE!!!")
			self.screen.blit(fontOut, (self.screen.get_rect().width / 2 - fontOut.get_rect().width / 2, self.screen.get_rect().height / 2))
		else:
			# render everything
			for ball in self.balls:
				ball.render()

			for row in self.bricks:
				for brick in row:
					brick.render()

			if self.lives > 0:
				self.paddleLoc.draw()
			if self.p2lives > 0:
				self.p2paddleLoc.draw()

			if self.countdown > 0.0:
				fontOut = self.gameOverFont.render(str(int(self.countdown) + 1), True, (174, 0, 255))
				self.screen.blit(fontOut, (self.screen.get_rect().width / 2 - fontOut.get_rect().width / 2, self.screen.get_rect().height / 2 - fontOut.get_rect().height))

		# draw lives and score to screen
		fontOut = self.outputFont.render("Lives: " + str(self.lives), True, FONT_COLOR)
		self.screen.blit(fontOut, self.livesPosition)
		fontOut = self.outputFont.render("Score: " + str(self.score), True, FONT_COLOR)
		self.screen.blit(fontOut, self.scorePosition)

		fontOut = self.outputFont.render("Lives: " + str(self.p2lives), True, FONT_COLOR)
		self.screen.blit(fontOut, self.p2livesPosition)
		fontOut = self.outputFont.render("Score: " + str(self.p2score), True, FONT_COLOR)
		self.screen.blit(fontOut, self.p2scorePosition)

	def initalizeGameOver(self):
		self.gameOver = True

		for row in self.bricks:
			for brick in row:
				if brick.intact:
					for x in xrange(20):
						self.particles.spawnParticle((brick.x + brick.w / 2, brick.y + brick.h / 2), randomTools.nextCircleVector())

		for x in xrange(50):
			self.particles.spawnParticle((self.paddleLoc.pos.x + randint(0, self.paddleLoc.w), self.paddleLoc.pos.y + self.paddleLoc.h / 2), randomTools.nextTopQuarterVector())
		for x in xrange(50):
			self.particles.spawnParticle((self.p2paddleLoc.pos.x + randint(0, self.p2paddleLoc.w), self.p2paddleLoc.pos.y + self.p2paddleLoc.h / 2), randomTools.nextCircleVector())