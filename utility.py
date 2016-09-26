import pygame as pg
from settings import *
from os import path

class Map:
	def __init__(self, filename):
		self.data = []
		with open(filename, "rt") as f:
			for line in f:
				self.data.append(line.strip())          #line.strip() delete from the line every not-characters symbols, like /n
		self.tilewidth = len(self.data[0])         #how many tiles width is the map
		self.tileheight = len(self.data)           #how many tiles height is the map
		self.width = self.tilewidth * TILESIZE     #how many pixel width is the map
		self.height = self.tileheight * TILESIZE   #how many pixels height is the map


class Spritesheet:
	#utility class for loading and parsing spritesheets
	def __init__(self, filename):
		self.spritesheet = pg.image.load(filename).convert()
	
	def get_image(self, x, y, width, height):
		image = pg.Surface((width, height))
		image.blit(self.spritesheet, (0,0), (x, y, width, height)) #take the (x, y, width, height) chunk of self.spritesheet and blit it onto the surface "image" in its corner (0,0)
		image.set_colorkey(BLACK)
		return image


def find_col():
	x = pg.mouse.get_pos()[0]
	return int(x/TILESIZE)
	

def find_row():
	y = pg.mouse.get_pos()[1]
	return int(y/TILESIZE)


def draw_text (surface, text, size, x, y):
	font_name = pg.font.match_font("arial")
	font = pg.font.Font(font_name, size)
	text_surface = font.render(text, True, WHITE) # True allows us to use Anti-aliased text on this surface
	text_rect = text_surface.get_rect()
	text_rect.midtop = (x,y)
	surface.blit(text_surface, text_rect)	


class Info_panel():
	def __init__(self, coins, game):
		self.coins = coins
		self.last_coin = pg.time.get_ticks()
		self.updated_coins = True
		self.updated_kills = True
		self.game = game
		draw_text(game.screen, "Coins: " + str(self.coins), 18, WIDTH_TOTAL - 70, 15)
		draw_text(game.screen, "= " + str(MACHINEGUN_PRICE), 16, WIDTH_TOTAL - 40, 80)
		draw_text(game.screen, "= " + str(DOUBLE_MACHINEGUN_PRICE), 16, WIDTH_TOTAL - 40, 130)
		draw_text(game.screen, "= " + str(ROCKET_LOUNCHER_PRICE), 16, WIDTH_TOTAL - 40, 180)
		draw_text(game.screen, "Kills: " + str(self.game.kills), 18, WIDTH_TOTAL - 70, 300)
		rect1 = game.icon_machinegun.get_rect()
		rect2 = game.icon_double_machinegun.get_rect()
		rect3 = game.icon_rocket_louncher.get_rect()
		rect1.x = WIDTH_TOTAL - 95
		rect1.y = 75
		rect2.x = WIDTH_TOTAL - 95
		rect2.y = 125
		rect3.x = WIDTH_TOTAL - 95
		rect3.y = 175
		game.screen.blit(game.icon_machinegun, rect1)
		game.screen.blit(pg.transform.rotate(game.icon_double_machinegun, -90), rect2)
		game.screen.blit(pg.transform.rotate(game.icon_rocket_louncher, -90), rect3)
	
	def draw(self, type):
		if type == "coins":
			#covers the previous value on the screen with a black surface
			surface = pg.Surface((80, 25))
			surface.fill(BGCOLOR)
			rect = surface.get_rect()
			rect.x = WIDTH_TOTAL - 110
			rect.y = 12
			self.game.screen.blit(surface, rect)
			#draw the new value
			draw_text(self.game.screen, "Coins: " + str(self.coins), 18, WIDTH_TOTAL - 70, 15)
			self.updated_coins = False
		elif type == "kills":
			#covers the previous value on the screen with a black surface
			surface = pg.Surface((80, 25))
			surface.fill(BGCOLOR)
			rect = surface.get_rect()
			rect.x = WIDTH_TOTAL - 110
			rect.y = 297
			self.game.screen.blit(surface, rect)
			#draw the new value
			draw_text(self.game.screen, "Kills: " + str(self.game.kills), 18, WIDTH_TOTAL - 70, 300)
			self.updated_kills = False
	
	
def is_tile_free(matrix, item_col, item_row):
	for row, tiles in enumerate(matrix): 
		for col, tile in enumerate(tiles):
			if item_col == col and item_row == row and tile == ".":
				return True
	return False 

	
def replace_tile_data(matrix, item_col, item_row, item ):
	new_matrix = []
	for row, tiles in enumerate(matrix): 
		new_row = []
		for col, tile in enumerate(tiles):
			if col == item_col and row == item_row:
				new_row.append(item)
			else:
				new_row.append(tile)
		new_matrix.append(new_row)
	return new_matrix
					

def load_all_images(game):
	game.rocket_img = game.spritesheet.get_image(1344, 640, TILESIZE, TILESIZE)
	mob_img = game.spritesheet.get_image(960, 640, TILESIZE, TILESIZE)
	game.mob_img = pg.transform.rotate(mob_img, -90)
	game.grass_animation = game.spritesheet.get_image(1216, 64, TILESIZE, TILESIZE)
	flame_img = game.spritesheet.get_image(1216, 768, TILESIZE, TILESIZE)
	game.flame_img = pg.transform.rotate(flame_img, -90)
	game.bullet_img = game.spritesheet.get_image(1408, 704, TILESIZE, TILESIZE)
	game.machinegun_img = game.spritesheet.get_image(1024, 768, TILESIZE, TILESIZE)
	double_machinegun_img = game.spritesheet.get_image(1280, 640, TILESIZE, TILESIZE)
	game.double_machinegun_img = pg.transform.rotate(double_machinegun_img, -90)
	rocket_louncher_img = game.spritesheet.get_image(1280, 512, TILESIZE, TILESIZE)
	game.rocket_louncher_img = pg.transform.rotate(rocket_louncher_img, -90)
	game.map = Map(path.join(game.game_folder, "map.txt"))
	game.icon_machinegun = pg.transform.scale(game.machinegun_img, (32, 32))
	icon_double_machinegun = pg.transform.scale(game.double_machinegun_img, (32, 32))
	game.icon_double_machinegun = pg.transform.rotate(icon_double_machinegun, 90)
	icon_rocket_louncher = pg.transform.scale(game.rocket_louncher_img, (32, 32))
	game.icon_rocket_louncher = pg.transform.rotate(icon_rocket_louncher, 90)
	game.button_unchecked_img = game.spritesheet_ui.get_image(55, 91, 14, 14)
	game.button_checked_img = game.spritesheet_ui.get_image(55, 109, 14, 14)


def load_explosion_animation(game):
	game.explosion_animation = []
	for i in range(5):
		file_name = "regularExplosion0{}.png".format(i)
		img = pg.image.load(path.join(game.img_folder, file_name)).convert()
		img.set_colorkey(BLACK)
		img = pg.transform.scale(img, (75, 75))
		game.explosion_animation.append(img)

