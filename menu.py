import pygame
import json

# Menu system lifted (and modified) from https://nebelprog.wordpress.com/2013/08/14/create-a-simple-game-menu-with-pygame-pt-1-writing-the-menu-options-to-the-screen/
class MenuItem(pygame.font.Font):
	def __init__(self, text, font=None, font_size=30,
					font_color=(255, 255, 255), (pos_x, pos_y)=(0, 0)):
		self.font = pygame.font.Font(font, font_size)
		self.text = text
		self.font_size = font_size
		self.font_color = font_color
		self.label = self.font.render(self.text, 1, self.font_color)
		self.width = self.label.get_rect().width
		self.height = self.label.get_rect().height
		self.pos_x = pos_x
		self.pos_y = pos_y
		self.position = pos_x, pos_y
 
	def set_position(self, x, y):
		self.position = (x, y)
		self.pos_x = x
		self.pos_y = y

	def set_font_color(self, rgb_tuple):
		self.font_color = rgb_tuple
		self.label = self.font.render(self.text, 1, self.font_color)
 
	def is_mouse_selection(self, (posx, posy)):
		if (posx >= self.pos_x and posx <= self.pos_x + self.width) and \
			(posy >= self.pos_y and posy <= self.pos_y + self.height):
			return True
		return False

# Generic Menu class 
class GameMenu():
	def __init__(self, screen, items, funcs, title, bg_color=(0, 0, 0), font="textures/MATRIX.ttf", font_size=60,
				font_color=(12, 222, 12)):
		self.mainloop = False

		self.screen = pygame.display.set_mode((1000, 900), 0, 32)

		self.scr_width = self.screen.get_rect().width
		self.scr_height = self.screen.get_rect().height
 
		self.bg_color = bg_color
		self.clock = pygame.time.Clock()
 
		self.font = pygame.font.Font(font, font_size)
		self.font_color = font_color

		self.titleFont = pygame.font.Font(font, font_size * 2)
		self.titleLabel = self.titleFont.render(title, True, self.font_color)
 
 		self.functions = funcs
		self.items = []
		for index, item in enumerate(items):
			menu_item = MenuItem(item, font, font_size, font_color)
		 
			# t_h: total height of text block
			t_h = len(items) * menu_item.height
			pos_x = (self.scr_width / 2) - (menu_item.width / 2)
			# This line includes a bug fix by Ariel (Thanks!)
			# Please check the comments section for an explanation
			pos_y = (self.scr_height / 2) - (t_h / 2) + ((index * 2) + index * menu_item.height) + 100
		 
			menu_item.set_position(pos_x, pos_y)
			self.items.append(menu_item)
 
	def run(self):
		self.mainloop = True

		self.screen = pygame.display.set_mode((1000, 900), 0, 32)

		while self.mainloop:
			self.clock.tick(60)
 
			self.update()
			self.render()
 
			pygame.display.flip()

	# Update menu items
	def update(self):
		for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.mainloop = False
				if event.type == pygame.MOUSEBUTTONDOWN:
					mousePos = pygame.mouse.get_pos()
					for item in self.items:
						if item.is_mouse_selection(mousePos):
							self.mainloop = False
							self.functions[item.text]()

	# Draw everything else
	def render(self):
		# Redraw the background
		self.screen.fill(self.bg_color)

		for item in self.items:
			if item.is_mouse_selection(pygame.mouse.get_pos()):
				item.set_font_color((255, 0, 0))
			else:
				item.set_font_color((12, 222, 12))
			self.screen.blit(item.label, item.position)

		# Draw Title
		self.screen.blit(self.titleLabel, (self.scr_width / 2 - self.titleLabel.get_rect().width / 2, 100))

class GameInfoMenu(GameMenu):
	def __init__(self, screen, items, funcs, title, msgs, bg_color=(0, 0, 0), font="textures/MATRIX.ttf", font_size=60,
				font_color=(12, 222, 12),):
		GameMenu.__init__(self, screen, items, funcs, title, bg_color, font, font_size, font_color)

		for item in self.items:
			currX = item.pos_x
			currY = item.pos_y

			item.set_position(currX, currY + 250)

		self.infoFont = pygame.font.Font(font, font_size * 2 / 3)

		self.msgs = []
		for x in msgs:
			self.msgs.append(self.infoFont.render(x, True, self.font_color))
	
	def render(self):
		GameMenu.render(self)

		pushDown = 0

		for item in self.msgs:
			self.screen.blit(item, (self.scr_width / 2 - item.get_rect().width / 2, self.scr_width / 3 - item.get_rect().height / 2 + pushDown))
			pushDown += item.get_rect().height

class HighScoreMenu(GameMenu):
	def __init__(self, screen, title, goBack, bg_color=(0, 0, 0), font="textures/MATRIX.ttf", font_size=60,
				font_color=(12, 222, 12),):
		GameMenu.__init__(self, screen, ['Reset', 'Back'], {'Reset': self.resetScores, 'Back': goBack}, title, bg_color, font, font_size, font_color)

		for item in self.items:
			currX = item.pos_x
			currY = item.pos_y

			item.set_position(currX, currY + 200)

		# try to read from a file, if that doesn't work then initalize it to the default and write it to the file
		try:
			f = open('highscores.json')
			self.highscores = json.loads(f.read())
		except IOError:
			self.highscores = [0, 0, 0, 0, 0]

			f = open('highscores.json', 'w')
			f.write(json.dumps(self.highscores, separators=(',', ':')))
			f.close()

	def render(self):
		GameMenu.render(self)
		heightOut = 300

		for score in self.highscores:
			outlabel = self.font.render(str(score), True, self.font_color)
			self.screen.blit(outlabel, (self.scr_width / 2 - outlabel.get_rect().width / 2, heightOut))
			heightOut = heightOut + outlabel.get_rect().height

	def resetScores(self):
		self.highscores = [0, 0, 0, 0, 0]

		f = open('highscores.json', 'w')
		f.write(json.dumps(self.highscores, separators=(',', ':')))
		f.close()

		# need to run again because selecting a menu option stops the loop!
		self.run()

	def addScore(self, score):
		self.highscores.append(score)
		self.highscores.sort(reverse=True)
		if len(self.highscores) > 5:
			self.highscores = self.highscores[:5]

		f = open('highscores.json', 'w')
		f.write(json.dumps(self.highscores, separators=(',', ':')))
		f.close()

class SettingsMenu(GameMenu):
	def __init__(self, screen, goBack, bg_color=(0, 0, 0), font="textures/MATRIX.ttf", font_size=60, font_color=(12, 222, 12)):
		GameMenu.__init__(self, screen, ['Move Right: ', 'Move Left: ', 'P2 Move Right: ', 'P2 Move Left: ', 'Quit: ', 'Defaults', 'Back'], {'Back': goBack}, 'Settings', bg_color, font, font_size, font_color)

		self.items[-1].set_position(self.items[-1].pos_x, self.items[-1].pos_y + 60)
		self.items[-2].set_position(self.items[-2].pos_x, self.items[-2].pos_y + 60)

		self.rebinding = {
			'right': False,
			'left': False,

			'p2right': False,
			'p2left': False,

			'quit': False
		}

		self.keys = None

		# import keys from JSON file, if that doesn't work set it to default and write it yourself
		try:
			f = open('keybinds.json')
			self.keys = json.loads(f.read())
		except IOError:
			self.keys = {
				'right': pygame.K_RIGHT,
				'left': pygame.K_LEFT,

				'p2right': pygame.K_d,
				'p2left': pygame.K_a,

				'quit': pygame.K_ESCAPE
			}

			f = open('keybinds.json', 'w')
			f.write(json.dumps(self.keys, separators=(',', ':')))
			f.close()


		self.functions['Move Right: '] = self.rebindRight
		self.functions['Move Left: '] = self.rebindLeft
		self.functions['P2 Move Right: '] = self.rebindP2Right
		self.functions['P2 Move Left: '] = self.rebindP2Left
		self.functions['Defaults'] = self.setToDefault
		self.functions['Quit: '] = self.rebindQuit

	def update(self):
		GameMenu.update(self)

		for key in self.rebinding:
			if self.rebinding[key]:
				pressed = pygame.key.get_pressed()

				for idx, item in enumerate(pressed):
					if item and not idx == pygame.K_NUMLOCK:
						self.keys[key] = idx
						self.rebinding[key] = False

						f = open('keybinds.json', 'w')
						f.write(json.dumps(self.keys, separators=(',', ':')))
						break

	def render(self):
		GameMenu.render(self)

		for key in self.keys:
			menuItem = None

			if(key == 'right'):
				menuItem = self.items[0]
			elif(key == 'left'):
				menuItem = self.items[1]
			elif(key == 'p2right'):
				menuItem = self.items[2]
			elif(key == 'p2left'):
				menuItem = self.items[3]
			elif(key == 'quit'):
				menuItem = self.items[4]

			if not menuItem == None:
				xPos = menuItem.pos_x + menuItem.width + 10
				yPos = menuItem.pos_y

				renderOut = None
				if not self.rebinding[key]:
					renderOut = self.font.render(pygame.key.name(self.keys[key]), True, menuItem.font_color)
				else:
					renderOut = self.font.render('...', True, menuItem.font_color)
				self.screen.blit(renderOut, (xPos, yPos))

	def rebindLeft(self):
		self.mainloop = True
		self.rebinding['left'] = True
	def rebindRight(self):
		self.mainloop = True
		self.rebinding['right'] = True
	def rebindP2Left(self):
		self.mainloop = True
		self.rebinding['p2left'] = True
	def rebindP2Right(self):
		self.mainloop = True
		self.rebinding['p2right'] = True
	def rebindQuit(self):
		self.mainloop = True
		self.rebinding['quit'] = True
	def setToDefault(self):
		self.mainloop = True
		self.keys = {
			'right': pygame.K_RIGHT,
			'left': pygame.K_LEFT,
			'p2right': pygame.K_d,
			'p2left': pygame.K_a,
			'quit': pygame.K_ESCAPE
		}

		f = open('keybinds.json', 'w')
		f.write(json.dumps(self.keys, separators=(',', ':')))