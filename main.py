import pygame as pg
import random
from utility import *
from sprites import *
from os import environ
from os import path
from settings import *
import sys

environ['SDL_VIDEO_CENTERED'] = '1' 

class Game:
	def __init__(self):
		pg.mixer.pre_init(44100, -16, 1, 512)
		pg.init()
		pg.mixer.init()
		self.screen = pg.display.set_mode((WIDTH_TOTAL, HEIGHT))
		pg.display.set_caption(TITLE)
		self.clock = pg.time.Clock()
		self.load_data()
		
	def load_data(self):
		#directories
		self.game_folder = path.dirname(__file__)
		self.img_folder = path.join(self.game_folder, "img")
		self.sound_folder = path.join(self.game_folder, 'sound')
		#spritesheets
		self.spritesheet = Spritesheet(path.join(self.img_folder, "towerDefense_tilesheet.png"))
		self.spritesheet_ui = Spritesheet(path.join(self.img_folder, "UIpackSheet_transparent.png"))
		#loading graphic
		load_all_images(self)
		load_explosion_animation(self)
		#loading audio
		self.impossible_sound = pg.mixer.Sound(path.join(self.sound_folder, 'impossible.wav'))
		self.machinegun_sound = pg.mixer.Sound(path.join(self.sound_folder, 'machinegun_shoot.wav'))
		self.d_machinegun_sound = pg.mixer.Sound(path.join(self.sound_folder, 'd_machinegun_shoot.wav'))
		self.r_louncher_sound = pg.mixer.Sound(path.join(self.sound_folder, 'r_louncher_shoot.wav'))
		self.explosion_sound = pg.mixer.Sound(path.join(self.sound_folder, 'explosion1.wav'))
		self.impossible_sound.set_volume(0.3)
		self.machinegun_sound.set_volume(0.1)
		self.d_machinegun_sound.set_volume(0.1)
		self.r_louncher_sound.set_volume(0.2)
		self.explosion_sound.set_volume(0.2)
		self.kills = 0
		
	def new(self):
		self.map = Map(path.join(self.game_folder, "map.txt"))   #load the map
		self.all_sprites = pg.sprite.LayeredUpdates()
		self.mobs = pg.sprite.Group()
		self.buttons = pg.sprite.Group()
		self.bullets = pg.sprite.Group()
		self.explosions = pg.sprite.Group()
		for row, tiles in enumerate(self.map.data): 
			for col, tile in enumerate(tiles):      
				Background_first_layer(self, tile, col, row)
		for row, tiles in enumerate(self.map.data): 
			for col, tile in enumerate(tiles):      
				if tile != "." and tile != "R":
					Background_second_layer(self, tile, col, row)
		for i in range(MOB_NUMBER):
			random_x = random.randrange(192, 256)
			random_y = random.randrange(-300, -100)
			Mob(self,random_x,random_y)
		self.info_panel = Info_panel(STARTING_COINS, self)
		Button(self, "machinegun", WIDTH_TOTAL - 120, 82, True, MACHINEGUN_PRICE)
		Button(self, "double_machinegun", WIDTH_TOTAL - 120, 132, False, DOUBLE_MACHINEGUN_PRICE)
		Button(self, "rocket_louncher", WIDTH_TOTAL - 120, 182, False, ROCKET_LOUNCHER_PRICE)
		pg.mixer.music.load(path.join(self.sound_folder, 'Xeon6.ogg'))
		pg.mixer.music.set_volume(0.3)
		pg.mixer.music.play(loops=-1)
		
	def run(self):
		self.playing = True
		while self.playing:
			self.dt = self.clock.tick(FPS)/1000   
			self.events()
			self.update()
			self.draw()
	
	def quit(self):
		pg.quit()
		sys.exit()

	def update(self):
		self.all_sprites.update()
		while len(self.mobs) < MOB_NUMBER:
			random_x = random.randrange(192, 256)
			random_y = random.randrange(-300, -100)
			Mob(self,random_x,random_y)
		now = pg.time.get_ticks()
		if now - self.info_panel.last_coin > COINS_SPAWN_RATE:
			self.info_panel.coins += 1
			self.info_panel.updated_coins = True
			self.info_panel.last_coin = now
					
	def events(self):
		for event in pg.event.get():
			if event.type == pg.QUIT:
				self.quit()
			if pg.mouse.get_focused():
				self.mouse_col = find_col()
				self.mouse_row = find_row()
				if is_tile_free(self.map.data, self.mouse_col, self.mouse_row):
							Grass_animation(self, self.mouse_col, self.mouse_row)
				if event.type == pg.MOUSEBUTTONDOWN:
					mouse_x, mouse_y = pg.mouse.get_pos() 
					for button in self.buttons:
						if button.x < mouse_x < button.x + 16 and   button.y <mouse_y< button.y + 16:
							button.checked = True
							for other_button in self.buttons:
								if other_button != button:
									other_button.checked = False
					if is_tile_free(self.map.data, self.mouse_col, self.mouse_row):
						for button in self.buttons:
							if button.checked:
								gun_type = button.gun
								gun_price = button.price
						if self.info_panel.coins - gun_price >= 0:
							Gun(self, gun_type, self.mouse_col*TILESIZE, self.mouse_row*TILESIZE)
							item = gun_type[0]
							self.map.data = replace_tile_data(self.map.data, self.mouse_col, self.mouse_row, item)
							self.info_panel.coins -= gun_price
							self.info_panel.updated_coins = True
						else:
							self.impossible_sound.play()
												
	def draw_grid(self):
		for x in range(0, WIDTH, TILESIZE):
			pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
		for y in range(0, HEIGHT, TILESIZE):
			pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))
			
	def draw(self):
		pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
		if self.info_panel.updated_coins:
			self.info_panel.draw("coins")
		if self.info_panel.updated_kills:
			self.info_panel.draw("kills")
		self.all_sprites.draw(self.screen)
		#self.draw_grid()
		pg.display.flip()
	
	def wait_for_key(self):
		waiting = True
		while waiting:
			self.clock.tick(FPS)
			for event in pg.event.get():
				if event.type == pg.QUIT:
					self.quit()
				if event.type == pg.KEYUP:
					waiting = False

	def show_menu(self):
		pg.mixer.music.load(path.join(self.sound_folder, 'Yippee.ogg'))
		pg.mixer.music.set_volume(0.3)
		pg.mixer.music.play(loops=-1)
		self.screen.fill(BGCOLOR)
		draw_text(self.screen, TITLE, 48, WIDTH_TOTAL / 2, HEIGHT / 4)
		draw_text(self.screen, "Build your towers and kill the enemies!", 22, WIDTH_TOTAL / 2, HEIGHT / 2)
		draw_text(self.screen, "kills: " + str(self.kills), 22, WIDTH_TOTAL / 2, 20)
		draw_text(self.screen, "Press a key to play", 22, WIDTH_TOTAL / 2, HEIGHT * 3 / 4)
		pg.display.flip()
		self.wait_for_key()
		pg.mixer.music.fadeout(500)



g = Game()
g.show_menu()
while True:
	g.new()
	g.run()
	g.show_menu()


