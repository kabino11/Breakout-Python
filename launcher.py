import pygame

import menu
import gameplay
from twoplayer import TwoPlayer

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 900

screen = pygame.display.set_mode((1000, 900), 0, 32)
pygame.display.set_caption('BREAKOUT')

def playGameOnce():
	game.run_game(settingsMenu.keys)

def playTwoPlayer():
	twoplayer.run_game(settingsMenu.keys)


def quit():
	print "Good bye!"
 
def Main_Menu():
	functions = {
		'New Game': playGameOnce,
		'Two-Player': playTwoPlayer,
		'High Scores': High_Score_Screen,
		'Settings': Settings_Menu,
		'Help': Help_Screen,
		'About': About_Screen,
		'Quit': quit
	}
 
	menu_items = ('New Game', 'Two-Player', 'High Scores', 'Settings', 'Help', 'About', 'Quit')
 
	gm = menu.GameMenu(screen, menu_items, functions, 'BREAKOUT')
	gm.run()

# create high score object
scoreMenu = menu.HighScoreMenu(screen, 'High Scores', Main_Menu)
settingsMenu = menu.SettingsMenu(screen, Main_Menu)

game = gameplay.BREAKOUT(Main_Menu, scoreMenu, settingsMenu.keys)
twoplayer = TwoPlayer(Main_Menu, settingsMenu.keys)

def Settings_Menu():
	settingsMenu.run()

def High_Score_Screen():
	scoreMenu.run()

def Help_Screen():
	functions = {
		'Back': Main_Menu
	}

	menu_items = ['Back']

	helpScreen = menu.GameInfoMenu(screen, menu_items, functions, 'HELP', ['Hit the ball with the paddle to win!', 'You will lose a life when you fail to hit the ball.', 'Point Distribution:', 'Yellow: 1pt, Orange: 2pts, Blue: 3pts, Green: 5pts', 'Row Cleared: 25pts', 'Pick-ups:', 'Green: Grows Paddle, Purple: Shrinks Paddle', 'Blue: slows down time, Red: speeds up time', 'All pick-ups will last for a limited amount of time', 'Pick-up duration is displayed on the paddle.'])
	helpScreen.run()

def About_Screen():
	functions = {
		'Back': Main_Menu
	}

	menu_items = ['Back']

	aboutScreen = menu.GameInfoMenu(screen, menu_items, functions, 'About', ["Made by Vance Larsen for CS 3430"])
	aboutScreen.run()

Main_Menu()